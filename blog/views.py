from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import BlogPost, BlogImage
from .serializers import BlogPostSerializer, BlogImageSerializer


class BlogPostListCreateView(generics.ListCreateAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer


class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer


class BlogImageUploadView(generics.CreateAPIView):
    queryset = BlogImage.objects.all()
    serializer_class = BlogImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogPostByCategoryView(generics.ListAPIView):
    serializer_class = BlogPostSerializer

    def get_queryset(self):
        """
        This view should return a list of all blog posts
        for the category as determined by the category parameter in the URL.
        """
        category = self.kwargs['category']
        return BlogPost.objects.filter(category=category)