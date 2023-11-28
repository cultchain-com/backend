"""
URL configuration for cultchian_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import BlogPostSitemap

sitemaps = {
    'blog': BlogPostSitemap,
    # Add other sitemaps here
}

schema_view = get_schema_view(
    openapi.Info(
        title="Cultchain API",
        default_version='v1',
        description="Cultchain API description",
        terms_of_service="https://www.cultchain.com/terms/",
        contact=openapi.Contact(email="info@cultchain.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/', include([
        path('admin/', admin.site.urls),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('ckeditor/', include('ckeditor_uploader.urls')),

        path('indexer/', include('indexer.urls')),
        path('mics/', include('miscellaneous.urls')),
        path('blog/', include('blog.urls')),

        path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    ]))
]

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
