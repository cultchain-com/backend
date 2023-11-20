from rest_framework import serializers
from .models import Event, Milestone, Committee, CommitteeMembership, Report, ValidatorRequest, EventFeedback, Donation, WithdrawRequest, FundRelease
from user_profile.models import *


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'


class CommitteeMembershipSerializer(serializers.ModelSerializer):
    member_wallet_address = serializers.CharField(source='member.wallet_address')

    class Meta:
        model = CommitteeMembership
        fields = ('member_wallet_address', 'has_voted', 'decision', 'feedback')


class CommitteeSerializer(serializers.ModelSerializer):
    members = CommitteeMembershipSerializer(source='committeemembership_set', many=True)
    related_object = serializers.SerializerMethodField()

    class Meta:
        model = Committee
        fields = '__all__'

    def get_related_object(self, obj):
        # Determine the related object based on committee_type and return its serialized data
        if obj.committee_type == 'Event':
            event = Event.objects.filter(committee_id=obj.committee_type_id).first()
            return EventSerializer(event).data if event else None
        elif obj.committee_type == 'Milestone':
            milestone = Milestone.objects.filter(event__committee_id=obj.committee_type_id, milestone_index=obj.milestone_index).first()
            return MilestoneSerializer(milestone).data if milestone else None
        elif obj.committee_type == 'Validator':
            validator_request = ValidatorRequest.objects.filter(committee_id=obj.committee_type_id).first()
            return ValidatorRequestSerializer(validator_request).data if validator_request else None
        return None


class EventSerializer(serializers.ModelSerializer):
    creator_wallet_address = serializers.CharField(source='creator.wallet_address', read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)
    committees = CommitteeSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class DonationSerializer(serializers.ModelSerializer):
    donor_wallet_address = serializers.CharField(source='donor.wallet_address')

    class Meta:
        model = Donation
        fields = ['donor_wallet_address', 'amount', 'timestamp', 'message']


class CreatorLeaderboardSerializer(serializers.Serializer):
    creator__wallet_address = serializers.CharField()
    number_of_created_events = serializers.IntegerField()
    total_money_raised = serializers.DecimalField(max_digits=40, decimal_places=0)


class ValidatorLeaderboardSerializer(serializers.Serializer):
    member__wallet_address = serializers.CharField()
    number_of_committees = serializers.IntegerField()
    total_earned = serializers.DecimalField(max_digits=40, decimal_places=0)


class DonorLeaderboardSerializer(serializers.Serializer):
    donor__wallet_address = serializers.CharField()
    number_of_donations = serializers.IntegerField()
    total_donated = serializers.DecimalField(max_digits=40, decimal_places=0)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'user_type', 'wallet_address', 'name', 'bio', 'profile_picture', 'email', 'phone_number',
            'date_joined', 'is_donor', 'is_validator', 'is_creator',
            'twitter_link', 'facebook_link', 'instagram_link', 'linkedin_link',
            'company_name', 'company_registration_number'
        ]
        read_only_fields = ['wallet_address', 'date_joined']  # These fields should not be updated

    def update(self, instance, validated_data):
        # Add custom update logic here if necessary
        return super().update(instance, validated_data)


class ValidatorRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidatorRequest
        fields = '__all__'


class WithdrawRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawRequest
        fields = '__all__'


class FundReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundRelease
        fields = '__all__'