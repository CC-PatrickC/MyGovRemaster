from django.contrib import admin
from .models import Request, RequestAttachment, TriageNotesHistory

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['request_id', 'title', 'department', 'request_type', 'priority', 'stage', 'created_by', 'created_at']
    list_filter = ['request_type', 'priority', 'stage', 'department', 'created_at']
    search_fields = ['request_id', 'title', 'description', 'department', 'triage_notes']
    readonly_fields = ['request_id', 'created_at', 'updated_at']

@admin.register(RequestAttachment)
class RequestAttachmentAdmin(admin.ModelAdmin):
    list_display = ['request', 'original_filename', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['original_filename', 'request__request_id', 'request__title']
    readonly_fields = ['uploaded_at']

@admin.register(TriageNotesHistory)
class TriageNotesHistoryAdmin(admin.ModelAdmin):
    list_display = ['request', 'submitted_by', 'submitted_at']
    list_filter = ['submitted_at']
    search_fields = ['notes', 'request__request_id', 'request__title', 'submitted_by__username']
    readonly_fields = ['submitted_at']
