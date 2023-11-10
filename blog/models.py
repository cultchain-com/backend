from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    body = RichTextField()
    header_image = models.ImageField(upload_to='post_headers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class BlogImage(models.Model):
    image = models.ImageField(upload_to='blog_images')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} uploaded on {self.uploaded_at}"
