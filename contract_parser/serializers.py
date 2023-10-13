from rest_framework import serializers
from .models import Contract

class ContractABISerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['contract_name', 'address', 'abi', 'network', 'owner_address']
