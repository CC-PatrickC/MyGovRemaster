from django import forms
from .models import Request

class TriageRequestEditForm(forms.ModelForm):
    """Form for editing triage requests - excludes scoring fields."""
    class Meta:
        model = Request
        fields = [
            'title',
            'description',
            'department',
            'stage',
            'request_type',
            'priority',
            'triage_notes',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'stage': forms.Select(attrs={'class': 'form-control'}),
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'triage_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        labels = {
            'title': 'Title',
            'description': 'Description',
            'department': 'Department',
            'stage': 'Stage',
            'request_type': 'Request Type',
            'priority': 'Priority',
            'triage_notes': 'Triage Notes',
        }

class RequestEditForm(forms.ModelForm):
    """Full form for editing requests with all fields."""
    class Meta:
        model = Request
        fields = [
            'title',
            'description',
            'department',
            'stage',
            'request_type',
            'priority',
            'scoring_notes',
            'final_priority',
            'final_score',
            'strategic_alignment',
            'cost_benefit',
            'user_impact',
            'ease_of_implementation',
            'vendor_reputation_support',
            'security_compliance',
            'student_centered',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'stage': forms.Select(attrs={'class': 'form-control'}),
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'scoring_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'final_priority': forms.NumberInput(attrs={'class': 'form-control'}),
            'final_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'strategic_alignment': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'cost_benefit': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'user_impact': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'ease_of_implementation': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'vendor_reputation_support': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'security_compliance': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'student_centered': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }

