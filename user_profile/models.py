from django.db import models


class UserProfile(models.Model):
    USER_TYPES = [
        ('Personal', 'Personal'),
        ('Corporate', 'Corporate')
    ]

    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='Personal')
    wallet_address = models.CharField(max_length=42, unique=True)
    bio = models.TextField(blank=True, null=True, description="User biography")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # User type
    is_donor = models.BooleanField(default=False)
    is_validator = models.BooleanField(default=False)
    is_creator = models.BooleanField(default=False)

    # social links
    twitter_link = models.URLField(blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)

    # Fields specific to corporate users
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_registration_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.wallet_address
