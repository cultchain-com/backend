from django.urls import path
from .views import *

urlpatterns = [
    path('events/', EventList.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetail.as_view(), name='event-detail'),
    path('leaderboard/creators/', CreatorLeaderboardView.as_view(), name='creator-leaderboard'),
    path('leaderboard/validators/', ValidatorLeaderboardView.as_view(), name='validator-leaderboard'),
    path('leaderboard/donors/', DonorLeaderboardView.as_view(), name='donor-leaderboard'),
    path('committees/', CommitteeListView.as_view(), name='committee-list'),
    path('committees/<int:committee_id>/', CommitteeDetailView.as_view(), name='committee-detail'),
    path('events/<int:event_id>/donors/', EventDonorsView.as_view(), name='event-donors'),
    path('wallets/<str:wallet_address>/donations/', WalletDonationHistoryView.as_view(), name='wallet-donation-history'),
    path('wallets/<str:wallet_address>/events/', WalletCreatedEventsView.as_view(), name='wallet-created-events'),
    path('wallets/<str:wallet_address>/committees/', WalletCommitteesView.as_view(), name='wallet-committees'),
    path('wallets/<str:identifier>/', UserProfileDetailView.as_view(), name='user_profile_detail'),
    path('search/', GlobalSearchView.as_view(), name='global_search'),
]