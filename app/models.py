from django.db import models
from django.contrib.auth.models import User

class Request(models.Model):
    STAGE_CHOICES = [
        ('Pending Review', 'Pending Review'),
        ('Under Review - Triage', 'Under Review - Triage'),
        ('Under Review - Governance', 'Under Review - Governance'),
        ('Under Review - Final Governance', 'Under Review - Final Governance'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    REQUEST_TYPE_CHOICES = [
        ('Not Yet Decided', 'Not Yet Decided'),
        ('Process Improvement', 'Process Improvement'),
        ('IT Governance', 'IT Governance'),
        ('AI Governance', 'AI Governance'),
        ('ERP Governance', 'ERP Governance'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default='Pending Review')
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES, default='Not Yet Decided')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
