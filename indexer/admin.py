from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Event)
admin.site.register(Milestone)
admin.site.register(Committee)
admin.site.register(CommitteeMembership)
admin.site.register(ValidatorRequest)
admin.site.register(Donation)
admin.site.register(WithdrawRequest)
admin.site.register(FundRelease)