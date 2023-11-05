from django.urls import path
from .views import *

urlpatterns = [
    path('contact/', ContactMessageCreate.as_view(), name='contact-message-create'),
    path('faqs/', FAQListView.as_view(), name='faq-list'),
]