"""
URL configuration for myproject project.
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('submit-request/', views.submit_request, name='submit_request'),
    path('requests/', views.requests, name='requests'),
    path('', views.index, name='index'),
]

