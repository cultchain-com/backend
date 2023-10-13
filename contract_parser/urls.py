from django.urls import path
from .views import *

urlpatterns = [
    path('import_abi/', ImportContractABIView.as_view(), name='import_abi'),
]
