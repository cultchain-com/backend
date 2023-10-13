from django.db import models
from web3 import Web3
from web3.middleware import geth_poa_middleware
import requests.exceptions


class Network(models.Model):
    name = models.CharField(max_length=50)
    currency = models.CharField(max_length=50)
    chainId = models.IntegerField(default=1)
    rpc_endpoint = models.URLField()
    explorer = models.URLField()
    is_testnet = models.BooleanField()

    def __str__(self):
        return "%s-TESTNET" % self.name if self.is_testnet else "%s-MAINNET" % self.name

    def test_connection(self, rpc_endpoint):
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_endpoint))
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            block = web3.eth.get_block('latest')
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False

    def save(self, *args, **kwargs):
        if not self.test_connection(self.rpc_endpoint):
            raise ValueError('Could not connect to the RPC endpoint')

        super().save(*args, **kwargs)


class Contract(models.Model):
    CONTRACT_TYPES = [
        ('CharityEvent', 'CharityEvent'),
        ('Fundraising', 'Fundraising'),
        ('RandomizedCommittee', 'RandomizedCommittee'),
        ('Validator', 'Validator'),
        ('CultChainNFT', 'CultChainNFT'),
        ('CultChainToken', 'CultChainToken'),
    ]

    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    contract_name = models.CharField(max_length=50)
    address = models.CharField(max_length=42)
    abi = models.JSONField()
    network = models.ForeignKey(Network, on_delete=models.PROTECT)
    owner_address = models.CharField(max_length=42)
    deployed_at_block = models.IntegerField(default=0)
    last_processed_event_block = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:  # This means the object is being created, not updated
            self.last_processed_event_block = self.deployed_at_block
        super(Contract, self).save(*args, **kwargs)

    def __str__(self):
        return "%s on %s-TESTNET" % (self.contract_name, self.network.name) if self.network.is_testnet else \
            "%s on %s-MAINNET" % (self.contract_name, self.network.name)

    def get_event_names(self):
        return [item['name'] for item in self.abi if item['type'] == 'event']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        event_names = self.get_event_names()
        for event_name in event_names:
            ContractEvent.objects.create(contract=self, event_name=event_name)


class ContractEvent(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.DO_NOTHING, related_name='events')
    event_name = models.CharField(max_length=50)

    def __str__(self):
        return "%s of %s on %s-TESTNET" % (self.event_name, self.contract.contract_name, self.contract.network.name) \
            if self.contract.network.is_testnet\
            else "%s of %s on %s-MAINNET" % (self.event_name, self.contract.contract_name, self.contract.network.name)
