from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Request

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
