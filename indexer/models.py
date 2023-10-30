from django.db import models
from user_profile.models import UserProfile
from .contract_enums import EventCategory, EventMilestoneStatus


class Event(models.Model):
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    target_amount = models.BigIntegerField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(null=True)
    collected_amount = models.DecimalField(max_digits=40, decimal_places=0)
    rating_sum = models.BigIntegerField()
    rating_count = models.BigIntegerField()
    category = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in EventCategory])  # Enum choices
    status = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in EventMilestoneStatus])  # Enum choices
    committee_id = models.BigIntegerField()
    is_fundraising_over = models.BooleanField()
    token_uri = models.URLField(null=True)

    def __str__(self):
        return self.name


class Milestone(models.Model):
    event = models.ForeignKey(Event, related_name='milestones', on_delete=models.CASCADE)
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    milestone_index = models.BigIntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField()
    spended_amount = models.DecimalField(max_digits=40, decimal_places=0)
    target_amount = models.DecimalField(max_digits=40, decimal_places=0)
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(null=True)
    rating_sum = models.BigIntegerField()
    rating_count = models.BigIntegerField()
    committee_id = models.BigIntegerField()
    completed = models.BooleanField()
    is_fund_released = models.BooleanField()
    status = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in EventMilestoneStatus])

    class Meta:
        unique_together = ('event', 'milestone_index')

    def __str__(self):
        return self.name


class Committee(models.Model):
    COMMITTEE_TYPE_CHOICES = [
        ('Event', 'Event'),
        ('Milestone', 'Milestone'),
        ('Validator', 'Validator'),
    ]

    committee_id = models.BigIntegerField(unique=True)  # Corresponds to the committeeId in the contract
    total_members = models.PositiveIntegerField()
    yes_votes = models.PositiveIntegerField(default=0)
    no_votes = models.PositiveIntegerField(default=0)
    final_decision = models.BooleanField(null=True, blank=True)
    committee_type = models.CharField(max_length=10, choices=COMMITTEE_TYPE_CHOICES)
    milestone_index = models.PositiveIntegerField(default=0)
    committee_type_id = models.PositiveIntegerField(default=0)

    # ForeignKey relationships
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True)
    # validator_request = models.ForeignKey(ValidatorRequest, on_delete=models.SET_NULL, null=True, blank=True)  # Uncomment this once you have the ValidatorRequest model

    # ManyToMany relationship with UserProfile to represent committee members
    members = models.ManyToManyField(UserProfile, related_name='committees', through='CommitteeMembership')

    class Meta:
        verbose_name = "Committee"
        verbose_name_plural = "Committees"


class CommitteeMembership(models.Model):
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
    member = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    has_voted = models.BooleanField(default=False)
    decision = models.BooleanField(default=False)  # True for yes, False for no
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('committee', 'member')


class Report(models.Model):
    event = models.ForeignKey(Event, related_name='reports', on_delete=models.CASCADE)
    reporter = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter.name} for {self.event.name}"


class ValidatorRequest(models.Model):
    applicant = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    staking_amount = models.DecimalField(max_digits=40, decimal_places=0)
    reputation_score = models.PositiveIntegerField()
    ipfs_hash = models.CharField(max_length=46)
    validation_status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')])
    committee_id = models.PositiveIntegerField()


class EventFeedback(models.Model):
    event = models.ForeignKey(Event, related_name='feedbacks', on_delete=models.CASCADE)
    feedback_provider = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.feedback_provider.name} for {self.event.name}"


class Donation(models.Model):
    donor = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=40, decimal_places=0)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    message = models.TextField()

    class Meta:
        unique_together = ['donor', 'amount', 'event', 'timestamp', 'message']

    def __str__(self):
        return f"{self.donor.wallet_address} donated {self.amount} to {self.event}"


class WithdrawRequest(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=40, decimal_places=0)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.event} requested withdrawal of {self.amount}"


class FundRelease(models.Model):
    RELEASE_TYPES = [
        ('Creator', 'Creator'),
        ('Validator', 'Validator'),
        ('Platform', 'Platform')
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=40, decimal_places=0)
    release_type = models.CharField(max_length=10, choices=RELEASE_TYPES)
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)  # Null for platform

    def __str__(self):
        return f"{self.amount} released to {self.release_type} for {self.event}"
