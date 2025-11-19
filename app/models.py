from django.db import models
from django.contrib.auth.models import User

class Request(models.Model):
    STAGE_CHOICES = [
        ('Pending Review', 'Pending Review'),
        ('Under Review - Triage', 'Under Review - Triage'),
        ('Under Review - Governance', 'Under Review - Governance'),
        ('Under Review - Final Governance', 'Under Review - Final Governance'),
        ('Approved', 'Recommended'),
        ('Rejected', 'Not Recommended'),
    ]
    
    REQUEST_TYPE_CHOICES = [
        ('Not Yet Decided', 'Not Yet Decided'),
        ('Process Improvement', 'Process Improvement'),
        ('IT Governance', 'IT Governance'),
        ('AI Governance', 'AI Governance'),
        ('ERP Governance', 'ERP Governance'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Top', 'Top'),
    ]
    
    request_id = models.CharField(max_length=5, unique=True, editable=False, blank=True, null=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.CharField(max_length=200, blank=True)
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default='Pending Review')
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES, default='Not Yet Decided')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Normal')
    triage_notes = models.TextField(blank=True, null=True, help_text="Notes from the triage group")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scoring_notes = models.TextField(blank=True, null=True, help_text="Notes related to project scoring or evaluation")
    final_priority = models.IntegerField(null=True, blank=True, help_text="Project ranking (lower number = higher priority)")
    final_score = models.FloatField(null=True, blank=True, help_text="Final score")
    strategic_alignment = models.IntegerField(null=True, blank=True, help_text="Strategic alignment score (1-5)")
    cost_benefit = models.IntegerField(null=True, blank=True, help_text="Cost benefit score (1-5)")
    user_impact = models.IntegerField(null=True, blank=True, help_text="User impact and adoption score (1-5)")
    ease_of_implementation = models.IntegerField(null=True, blank=True, help_text="Ease of implementation score (1-5)")
    vendor_reputation_support = models.IntegerField(null=True, blank=True, help_text="Vendor reputation and support score (1-5)")
    security_compliance = models.IntegerField(null=True, blank=True, help_text="Security and compliance score (1-5)")
    student_centered = models.IntegerField(null=True, blank=True, help_text="Student-centered score (1-5)")
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.request_id:
            # Get the highest existing request_id
            last_request = Request.objects.order_by('-request_id').first()
            if last_request and last_request.request_id:
                try:
                    last_id = int(last_request.request_id)
                    next_id = last_id + 1
                except ValueError:
                    next_id = 1
            else:
                next_id = 1
            
            # Format as 5-digit string with leading zeros
            self.request_id = f"{next_id:05d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.request_id} - {self.title}" if self.request_id else self.title


class RequestAttachment(models.Model):
    """Model for storing file attachments for requests."""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='request_attachments/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.request.request_id} - {self.original_filename}"


class TriageNotesHistory(models.Model):
    """Model for tracking triage notes history."""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='triage_notes_history')
    notes = models.TextField(help_text="Triage notes at the time of submission")
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name_plural = 'Triage Notes History'
    
    def __str__(self):
        return f"{self.request.request_id} - {self.submitted_by.username} - {self.submitted_at}"


class RequestChangeHistory(models.Model):
    """Model for tracking all changes made to requests."""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='change_history')
    field_name = models.CharField(max_length=100, help_text="Name of the field that was changed")
    old_value = models.TextField(blank=True, null=True, help_text="Previous value")
    new_value = models.TextField(blank=True, null=True, help_text="New value")
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Request Change History'
    
    def __str__(self):
        return f"{self.request.request_id} - {self.field_name} - {self.changed_by.username} - {self.changed_at}"
