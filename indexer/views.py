from django.db.models import Count, Sum
from rest_framework import generics
from .models import *
from user_profile.models import *
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import *
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.decorators import api_view


class EventList(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset


class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class CreatorLeaderboardView(generics.ListAPIView):
    serializer_class = CreatorLeaderboardSerializer

    def get_queryset(self):
        return Event.objects.values('creator__wallet_address').annotate(
            number_of_created_events=Count('id'),
            total_money_raised=Sum('collected_amount')
        ).order_by('-total_money_raised')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ValidatorLeaderboardView(generics.ListAPIView):
    serializer_class = ValidatorLeaderboardSerializer

    def get_queryset(self):
        # Step 1: Get the number of committees each validator has been a part of
        committee_counts = CommitteeMembership.objects.values('member') \
            .annotate(number_of_committees=Count('committee')) \
            .order_by('member')

        # Convert the queryset to a dictionary for easier lookup
        committee_counts_dict = {item['member']: item['number_of_committees'] for item in committee_counts}

        # Step 2: Get the total earnings for each validator
        validator_earnings = FundRelease.objects.filter(release_type='Validator') \
            .values('recipient') \
            .annotate(total_earned=Sum('amount')) \
            .order_by('-total_earned')

        # Merge the two results
        for item in validator_earnings:
            item['number_of_committees'] = committee_counts_dict.get(item['recipient'], 0)

        return validator_earnings

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DonorLeaderboardView(generics.ListAPIView):
    serializer_class = DonorLeaderboardSerializer

    def get_queryset(self):
        return Donation.objects.values('donor__wallet_address').annotate(
            number_of_donations=Count('id'),
            total_donated=Sum('amount')
        ).order_by('-total_donated')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommitteeDetailView(generics.RetrieveAPIView):
    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer
    lookup_field = 'committee_id'


class CommitteeListView(generics.ListAPIView):
    # queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer

    def get_queryset(self):
        return Committee.objects.all().select_related('event', 'milestone')


class EventDonorsView(generics.ListAPIView):
    serializer_class = DonationSerializer

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        return Donation.objects.filter(event__id=event_id)


class WalletDonationHistoryView(generics.ListAPIView):
    serializer_class = DonationSerializer

    def get_queryset(self):
        wallet_address = self.kwargs['wallet_address']
        return Donation.objects.filter(donor__wallet_address=wallet_address)


class WalletCreatedEventsView(generics.ListAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        wallet_address = self.kwargs['wallet_address']
        return Event.objects.filter(creator__wallet_address=wallet_address)


class WalletCommitteesView(generics.ListAPIView):
    serializer_class = CommitteeSerializer
    # Define the manual parameter for Swagger
    status_param = openapi.Parameter(
        'status',
        in_=openapi.IN_QUERY,
        description="Status of the committee. Options: 'ongoing' or 'past'. Default is 'ongoing'.",
        type=openapi.TYPE_STRING,
        enum=['ongoing', 'past']
    )

    @swagger_auto_schema(manual_parameters=[status_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        wallet_address = self.kwargs['wallet_address']
        status = self.request.query_params.get('status', 'ongoing')  # Default to 'ongoing' if not provided

        # Get all committees for the wallet address
        committees = Committee.objects.filter(members__wallet_address=wallet_address)

        if status == 'ongoing':
            # Filter out committees where the user has already voted
            return committees.filter(committeemembership__has_voted=False, committeemembership__member__wallet_address=wallet_address)
        elif status == 'past':
            # Filter for committees where the user has voted
            return committees.filter(committeemembership__has_voted=True, committeemembership__member__wallet_address=wallet_address)
        else:
            # Return all committees if an invalid status is provided
            return committees


class GlobalSearchView(APIView):

    @swagger_auto_schema(
        operation_description="Global search across multiple models.",
        manual_parameters=[
            openapi.Parameter(
                name='query',
                in_=openapi.IN_QUERY,
                description="Search term.",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: "Search results"},
    )

    def get(self, request):
        query = request.query_params.get('query', '')

        # Search in Event model
        events = Event.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

        # Search in Milestone model
        milestones = Milestone.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

        # Serialize and return the results
        event_serializer = EventSerializer(events, many=True)
        milestone_serializer = MilestoneSerializer(milestones, many=True)

        return Response({
            'events': event_serializer.data,
            'milestones': milestone_serializer.data,
        })


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @swagger_auto_schema(
        operation_description="Retrieve or update a user profile.",
        manual_parameters=[
            openapi.Parameter(
                name='identifier',
                in_=openapi.IN_PATH,
                description="Unique identifier for the user. This can be either the user's ID or their wallet address.",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: UserProfileSerializer(),
            404: "User not found",
            400: "Invalid input"
        }
    )
    def get_object(self):
        identifier = self.kwargs.get('identifier')
        try:
            # First, try to retrieve by ID
            obj = UserProfile.objects.get(id=identifier)
        except (UserProfile.DoesNotExist, ValueError):  # ValueError will catch non-integer IDs
            # If not found by ID, try to retrieve by wallet_address
            obj = get_object_or_404(UserProfile, wallet_address=identifier)
        self.check_object_permissions(self.request, obj)
        return obj


class ValidatorRequestListView(generics.ListAPIView):
    queryset = ValidatorRequest.objects.all()
    serializer_class = ValidatorRequestSerializer


class EventWithdrawRequestListView(generics.ListAPIView):
    serializer_class = WithdrawRequestSerializer

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        return WithdrawRequest.objects.filter(event__id=event_id)


class EventFundReleaseListView(generics.ListAPIView):
    serializer_class = FundReleaseSerializer

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        return FundRelease.objects.filter(event__id=event_id)


class EventCategoryListView(generics.ListAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        category = self.kwargs['category']
        return Event.objects.filter(category=category)


@api_view(['GET'])
def total_amount_raised(request):
    total = Event.objects.aggregate(Sum('collected_amount'))
    return Response({'total_amount_raised': total['collected_amount__sum']})


@api_view(['GET'])
def analytics_summary(request):
    total_events = Event.objects.count()
    total_milestones = Milestone.objects.count()
    total_donations = Donation.objects.count()

    return Response({
        'total_events': total_events,
        'total_milestones': total_milestones,
        'total_donations': total_donations,
    })
