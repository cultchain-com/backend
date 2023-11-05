from django.contrib import admin
from .models import BlogPost, BlogImage

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'header_image', 'created_at')
    search_fields = ('title', 'body')

@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'uploaded_at')