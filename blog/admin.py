from django.contrib import admin
from .models import BlogPost, BlogImage
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.db import models

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'header_image', 'created_at')
    search_fields = ('title', 'body')
    formfield_overrides = {
        models.TextField: {'widget': CKEditorUploadingWidget},
    }

@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'uploaded_at')
