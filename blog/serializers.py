from rest_framework import serializers
from .models import BlogPost, BlogImage


class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = BlogPost
        fields = '__all__'


class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ['image']