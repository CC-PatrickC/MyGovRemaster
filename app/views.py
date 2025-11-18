from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Request, RequestAttachment, TriageNotesHistory
from .forms import RequestEditForm, TriageRequestEditForm

def index(request):
    """Home page view."""
    # Check if user is in Triage Group, Triage Group Lead, or is a SuperUser
    can_view_triage = False
    triage_requests = []
    
    if request.user.is_authenticated:
        # SuperUsers can see all sections
        if request.user.is_superuser:
            can_view_triage = True
        else:
            user_groups = request.user.groups.values_list('name', flat=True)
            can_view_triage = 'Triage Group' in user_groups or 'Triage Group Lead' in user_groups
        
        if can_view_triage:
            # Get requests for Triage Requests section
            triage_requests = Request.objects.filter(
                stage__in=['Pending Review', 'Under Review - Triage']
            )
    
    # Get requests for Under Review - Governance section
    governance_requests = Request.objects.filter(
        stage='Under Review - Governance'
    )
    
    # Get requests for Under Review - Final Governance section
    final_governance_requests = Request.objects.filter(
        stage='Under Review - Final Governance'
    )
    
    context = {
        'can_view_triage': can_view_triage,
        'triage_requests': triage_requests,
        'governance_requests': governance_requests,
        'final_governance_requests': final_governance_requests,
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

def edit_request(request, request_id):
    """Edit request view for modal."""
    request_obj = get_object_or_404(Request, id=request_id)
    
    # Check if this is a triage request (Pending Review or Under Review - Triage)
    is_triage = request_obj.stage in ['Pending Review', 'Under Review - Triage']
    FormClass = TriageRequestEditForm if is_triage else RequestEditForm
    
    if request.method == 'POST':
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
                old_notes = str(old_notes).strip()
                
                # Create history entry if new notes are not empty and different from old
                if new_notes and new_notes != old_notes:
                    TriageNotesHistory.objects.create(
                        request=request_obj,
                        notes=new_notes,
                        submitted_by=request.user
                    )
            
            form.save()
            
            # Refresh the request object to get updated data
            request_obj.refresh_from_db()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return updated form HTML with history
                from django.template.loader import render_to_string
                template_name = 'app/partials/triage_request_form.html' if is_triage else 'app/partials/request_form.html'
                attachments = request_obj.attachments.all()
                # Get fresh history after save - convert to list to ensure it's evaluated
                triage_notes_history = list(request_obj.triage_notes_history.all()) if is_triage else []
                form_html = render_to_string(template_name, {
                    'form': FormClass(instance=request_obj), 
                    'request_obj': request_obj, 
                    'attachments': attachments,
                    'triage_notes_history': triage_notes_history
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
        form_html = render_to_string(template_name, {
            'form': form, 
            'request_obj': request_obj, 
            'attachments': attachments,
            'triage_notes_history': triage_notes_history
        }, request=request)
        return JsonResponse({'form_html': form_html})
    
    attachments = request_obj.attachments.all()
    triage_notes_history = request_obj.triage_notes_history.all() if is_triage else []
    return render(request, 'app/edit_request.html', {
        'form': form, 
        'request_obj': request_obj, 
        'attachments': attachments,
        'triage_notes_history': triage_notes_history
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
def delete_attachment(request, attachment_id):
    """Delete an attachment."""
    attachment = get_object_or_404(RequestAttachment, id=attachment_id)
    
    # Check if user has permission (uploader or superuser)
    if attachment.uploaded_by != request.user and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    attachment.file.delete()  # Delete the actual file
    attachment.delete()  # Delete the database record
    
    return JsonResponse({'success': True})
