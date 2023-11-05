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

    class Meta:
        model = Committee
        fields = (
        'committee_id', 'total_members', 'yes_votes', 'no_votes', 'final_decision', 'committee_type', 'milestone_index',
        'committee_type_id', 'members')


class EventSerializer(serializers.ModelSerializer):
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
        fields = '__all__'


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