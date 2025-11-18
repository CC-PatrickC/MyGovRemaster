"""
URL configuration for myproject project.
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('submit-request/', views.submit_request, name='submit_request'),
    path('requests/', views.requests, name='requests'),
    path('edit-request/<int:request_id>/', views.edit_request, name='edit_request'),
    path('upload-attachment/<int:request_id>/', views.upload_attachment, name='upload_attachment'),
    path('delete-attachment/<int:attachment_id>/', views.delete_attachment, name='delete_attachment'),
    path('', views.index, name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

