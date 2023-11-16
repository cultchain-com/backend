from rest_framework import serializers
from .models import BlogPost, BlogImage


class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = BlogPost
        fields = ['title', 'body', 'header_image', 'created_at', 'updated_at', 'author_name', 'category', 'keywords']


class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ['image']