from django.contrib import admin
from .models import Request

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'request_type', 'stage', 'created_by', 'created_at']
    list_filter = ['request_type', 'stage', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
