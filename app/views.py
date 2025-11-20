from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Request, RequestAttachment, TriageNotesHistory, RequestChangeHistory
from .forms import RequestEditForm, TriageRequestEditForm

def index(request):
    """Home page view."""
    # Check if user is in Triage Group, Triage Group Lead, or is a SuperUser
    can_view_triage = False
    can_view_governance = False
    is_end_user = False
    triage_requests = []
    
    if request.user.is_authenticated:
        # SuperUsers can see all sections
        if request.user.is_superuser:
            can_view_triage = True
            can_view_governance = True
        else:
            user_groups = request.user.groups.values_list('name', flat=True)
            can_view_triage = 'Triage Group' in user_groups or 'Triage Group Lead' in user_groups
            
            # End users are authenticated users who are NOT superusers and NOT in triage groups
            if not can_view_triage:
                is_end_user = True
            else:
                # Users with triage groups can also view governance
                can_view_governance = True
        
        if can_view_triage:
            # Get requests for Triage Requests section
            triage_requests = Request.objects.filter(
                stage__in=['Pending Review', 'Under Review - Triage']
            )
    
    # Get requests for Under Review - Governance section
    governance_requests = []
    if can_view_governance:
        governance_requests = Request.objects.filter(
            stage='Under Review - Governance'
        )
    
    # Get requests for Under Review - Final Governance section (all authenticated users can see this)
    final_governance_requests = []
    if request.user.is_authenticated:
        final_governance_requests = Request.objects.filter(
            stage='Under Review - Final Governance'
        )
    
    # Get user's own requests for MyRequests section
    my_requests = []
    if request.user.is_authenticated:
        my_requests = Request.objects.filter(created_by=request.user)
    
    context = {
        'can_view_triage': can_view_triage,
        'can_view_governance': can_view_governance,
        'is_end_user': is_end_user,
        'triage_requests': triage_requests,
        'governance_requests': governance_requests,
        'final_governance_requests': final_governance_requests,
        'my_requests': my_requests,
    }
    return render(request, 'app/index.html', context)

def login_view(request):
    """Login page view."""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'app/login.html', {'form': form})

def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

def submit_request(request):
    """Submit Request page view."""
    return render(request, 'app/submit_request.html')

def requests(request):
    """Requests page view."""
    return render(request, 'app/requests.html')

def view_request(request, request_id):
    """View request details (read-only) for non-triage requests."""
    request_obj = get_object_or_404(Request, id=request_id)
    
    # Check if this is a governance request
    is_governance = request_obj.stage == 'Under Review - Governance'
    
    # Get attachments, triage notes history, and change history for governance requests
    attachments = []
    triage_notes_history = []
    change_history = []
    
    if is_governance:
        attachments = request_obj.attachments.all()
        triage_notes_history = request_obj.triage_notes_history.all()
        change_history = request_obj.change_history.all()
    
    context = {
        'request_obj': request_obj,
        'attachments': attachments,
        'triage_notes_history': triage_notes_history,
        'change_history': change_history,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return appropriate partial template for AJAX
        if is_governance:
            template = 'app/partials/governance_request_view.html'
        else:
            template = 'app/partials/request_view.html'
        return render(request, template, context)
    else:
        # Return full page (fallback)
        return render(request, 'app/request_view.html', context)

def edit_request(request, request_id):
    """Edit request view for modal."""
    request_obj = get_object_or_404(Request, id=request_id)
    
    # Check if this is a triage request (Pending Review or Under Review - Triage)
    is_triage = request_obj.stage in ['Pending Review', 'Under Review - Triage']
    FormClass = TriageRequestEditForm if is_triage else RequestEditForm
    
    if request.method == 'POST':
        # IMPORTANT: Refresh from database to get current state, then store old values
        # This ensures we capture the actual database state before any form processing
        request_obj.refresh_from_db()
        
        tracked_fields = []
        old_values = {}
        if is_triage:
            tracked_fields = ['title', 'description', 'department', 'stage', 'request_type', 'priority']
            # Store old values from database BEFORE form processing
            for field in tracked_fields:
                if hasattr(request_obj, field):
                    old_value = getattr(request_obj, field)
                    old_values[field] = str(old_value).strip() if old_value is not None else ''
        
        form = FormClass(request.POST, instance=request_obj)
        if form.is_valid():
            
            # Save triage notes history if triage_notes is provided
            if is_triage:
                # Get new notes from form
                new_notes = form.cleaned_data.get('triage_notes', '')
                if new_notes is None:
                    new_notes = ''
                new_notes = str(new_notes).strip()
                
                # Get old notes from database (before saving)
                old_notes = request_obj.triage_notes or ''
                if old_notes:
                    old_notes = str(old_notes).strip()
                else:
                    old_notes = ''
                
                # Create history entry if new notes are not empty
                # Only create if different from old to avoid duplicates on unchanged saves
                if new_notes and new_notes != old_notes:
                    TriageNotesHistory.objects.create(
                        request=request_obj,
                        notes=new_notes,
                        submitted_by=request.user
                    )
                elif new_notes and new_notes == old_notes:
                    # Notes are the same - check if there's already a history entry with this exact content
                    # If not, create one (in case the notes were set directly without history)
                    existing_history = TriageNotesHistory.objects.filter(
                        request=request_obj,
                        notes=new_notes
                    ).first()
                    if not existing_history:
                        TriageNotesHistory.objects.create(
                            request=request_obj,
                            notes=new_notes,
                            submitted_by=request.user
                        )
            
            # Save the form
            form.save()
            
            # Track field changes after saving
            if is_triage and tracked_fields:
                # Get new values from form.cleaned_data (before refresh_from_db overwrites them)
                # This ensures we're comparing POST data with old database values
                for field in tracked_fields:
                    if field in form.cleaned_data:
                        new_value = form.cleaned_data.get(field, '')
                        new_value = str(new_value).strip() if new_value is not None else ''
                        old_value = old_values.get(field, '').strip()
                        
                        # Only create history if value changed
                        if new_value != old_value:
                            # Get human-readable field name
                            field_display = field.replace('_', ' ').title()
                            if hasattr(form.fields[field], 'label') and form.fields[field].label:
                                field_display = form.fields[field].label
                            
                            # Truncate long values for display (keep full value in DB)
                            old_display = old_value[:200] if old_value else '(empty)'
                            new_display = new_value[:200] if new_value else '(empty)'
                            
                            RequestChangeHistory.objects.create(
                                request=request_obj,
                                field_name=field_display,
                                old_value=old_display,
                                new_value=new_display,
                                changed_by=request.user
                            )
                
                # Refresh to get updated data (after creating history)
                request_obj.refresh_from_db()
            
            # Refresh the request object to get updated data
            request_obj.refresh_from_db()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return updated form HTML with history
                from django.template.loader import render_to_string
                template_name = 'app/partials/triage_request_form.html' if is_triage else 'app/partials/request_form.html'
                attachments = request_obj.attachments.all()
                
                # Get fresh history after save - force a new query
                if is_triage:
                    # Force a fresh query by getting the request ID and querying directly
                    triage_notes_history = TriageNotesHistory.objects.filter(request=request_obj).order_by('-submitted_at')
                    change_history = RequestChangeHistory.objects.filter(request=request_obj).order_by('-changed_at')
                else:
                    triage_notes_history = []
                    change_history = []
                
                form_html = render_to_string(template_name, {
                    'form': FormClass(instance=request_obj), 
                    'request_obj': request_obj, 
                    'attachments': attachments,
                    'triage_notes_history': triage_notes_history,
                    'change_history': change_history
                }, request=request)
                return JsonResponse({'success': True, 'message': 'Request updated successfully.', 'form_html': form_html})
            messages.success(request, 'Request updated successfully.')
            return redirect('index')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = FormClass(instance=request_obj)
    
    # Return form HTML for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        template_name = 'app/partials/triage_request_form.html' if is_triage else 'app/partials/request_form.html'
        attachments = request_obj.attachments.all()
        triage_notes_history = request_obj.triage_notes_history.all() if is_triage else []
        change_history = request_obj.change_history.all() if is_triage else []
        form_html = render_to_string(template_name, {
            'form': form, 
            'request_obj': request_obj, 
            'attachments': attachments, 
            'triage_notes_history': triage_notes_history,
            'change_history': change_history
        }, request=request)
        return JsonResponse({'form_html': form_html})
    
    attachments = request_obj.attachments.all()
    triage_notes_history = request_obj.triage_notes_history.all() if is_triage else []
    change_history = request_obj.change_history.all() if is_triage else []
    return render(request, 'app/edit_request.html', {
        'form': form, 
        'request_obj': request_obj, 
        'attachments': attachments,
        'triage_notes_history': triage_notes_history,
        'change_history': change_history
    })

@login_required
@require_http_methods(["POST"])
def upload_attachment(request, request_id):
    """Upload attachment for a request."""
    request_obj = get_object_or_404(Request, id=request_id)
    
    if 'file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)
    
    uploaded_file = request.FILES['file']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_FILES = 5
    
    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        return JsonResponse({'success': False, 'error': f'File size exceeds 10MB limit. File size: {uploaded_file.size / (1024*1024):.2f}MB'}, status=400)
    
    # Check total attachment count
    current_count = request_obj.attachments.count()
    if current_count >= MAX_FILES:
        return JsonResponse({'success': False, 'error': f'Maximum of {MAX_FILES} files allowed per request'}, status=400)
    
    attachment = RequestAttachment.objects.create(
        request=request_obj,
        file=uploaded_file,
        original_filename=uploaded_file.name,
        uploaded_by=request.user
    )
    
    return JsonResponse({
        'success': True,
        'attachment': {
            'id': attachment.id,
            'filename': attachment.original_filename,
            'url': attachment.file.url,
            'uploaded_at': attachment.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@login_required
@require_http_methods(["POST"])
def archive_request(request, request_id):
    """Archive a request by changing its stage to 'Archived'."""
    request_obj = get_object_or_404(Request, id=request_id)
    
    # Check if user has permission (Triage Group, Triage Group Lead, or SuperUser)
    if not request.user.is_superuser:
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'Triage Group' not in user_groups and 'Triage Group Lead' not in user_groups:
            return JsonResponse({'success': False, 'error': 'You do not have permission to archive requests.'}, status=403)
    
    try:
        data = json.loads(request.body)
        reason = data.get('reason', '').strip()
        
        if not reason:
            return JsonResponse({'success': False, 'error': 'Reason is required.'}, status=400)
        
        # Store old stage for change history
        old_stage = request_obj.stage
        
        # Update stage to Archived
        request_obj.stage = 'Archived'
        request_obj.save()
        
        # Create change history entry
        RequestChangeHistory.objects.create(
            request=request_obj,
            field_name='stage',
            old_value=old_stage,
            new_value='Archived',
            changed_by=request.user
        )
        
        # Add reason to triage notes if it exists, or create a note
        if request_obj.triage_notes:
            request_obj.triage_notes += f"\n\n[Archived by {request.user.get_full_name() or request.user.username}]: {reason}"
        else:
            request_obj.triage_notes = f"[Archived by {request.user.get_full_name() or request.user.username}]: {reason}"
        request_obj.save()
        
        return JsonResponse({'success': True, 'message': 'Request archived successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["POST"])
def delete_attachment(request, attachment_id):
    """Delete an attachment."""
    attachment = get_object_or_404(RequestAttachment, id=attachment_id)
    
    # Check if user has permission (uploader or superuser)
    if attachment.uploaded_by != request.user and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    attachment.file.delete()  # Delete the actual file
    attachment.delete()  # Delete the database record
    
    return JsonResponse({'success': True})
