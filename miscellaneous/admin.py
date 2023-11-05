from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'updated_at')
    search_fields = ('question',)


admin.site.register(ContactMessage)