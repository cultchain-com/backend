from django.urls import path
from .views import BlogPostListCreateView, BlogPostDetailView, BlogImageUploadView

urlpatterns = [
    path('posts/', BlogPostListCreateView.as_view(), name='blogpost-list'),
    path('posts/<int:pk>/', BlogPostDetailView.as_view(), name='blogpost-detail'),
    path('upload-image/', BlogImageUploadView.as_view(), name='blogimage-upload'),
]