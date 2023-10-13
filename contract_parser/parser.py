from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from .exceptions import SolidityError


class ContractParser:
    def __init__(self, contract):
        self.contract = contract
        self.network = contract.network
        self.owner_address = Web3.toChecksumAddress(contract.owner_address)
        self.web3 = Web3(HTTPProvider(self.network.mainnet_rpc_endpoint))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.contract_instance = self.web3.eth.contract(
            address=Web3.toChecksumAddress(self.contract.address),
            abi=self.contract.abi
        )

    def call(self, function_name, *args):
        try:
            contract_function = self.contract_instance.functions[function_name](*args)
            result = contract_function.call()
            return result
        except Exception as e:
            raise SolidityError(f'Error calling function {function_name} of contract {self.contract.contract_name}: {e}')

    def transact(self, function_name, *args):
        try:
            contract_function = self.contract_instance.functions[function_name](*args)
            gas_estimate = contract_function.estimateGas({'from': self.owner_address})

            # Prepare the transaction
            transaction = contract_function.buildTransaction({
                'from': self.owner_address,
                'gas': gas_estimate,
                'nonce': self.web3.eth.getTransactionCount(self.owner_address),
            })

            # Sign the transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=self.owner_private_key)

            # Send the transaction
            tx_hash = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
            return tx_hash
        except Exception as e:
            raise SolidityError(
                f'Error transacting function {function_name} of contract {self.contract.contract_name}: {e}')

    def get_event(self, event_name):
        try:
            event = self.contract_instance.events[event_name]
            return event
        except Exception as e:
            raise SolidityError(f'Error getting event {event_name} of contract {self.contract.contract_name}: {e}')
