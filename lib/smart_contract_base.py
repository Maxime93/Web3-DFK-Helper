import json
from web3 import Web3

class BaseContract:
    """Base class for any class that implelements contracts
    Chain classes can also inherit this class
    """
    def __init__(self, w3: Web3, rpc: str, contract_address: str, abi: dict):
        self.w3 = w3
        self.contract_address = Web3.toChecksumAddress(contract_address)
        self.rpc = rpc
        self.abi = abi
        self.contract = w3.eth.contract(self.contract_address, abi=self.abi)

    def get_nonce(self, address):
        return self.w3.eth.getTransactionCount(address)

    def get_abi_schema(self, function_name: str):
        for function_signature in self.abi:
            if function_signature['name'] == function_name:
                return function_signature
        return None

    def map_output(self, raw_result: list, function_name: str):
        abi = self.get_abi_schema(function_name)
        if abi is None:
            return raw_result
        mapped_result = {}
        for i in range(len(raw_result)):
            if isinstance(raw_result[i], tuple):
                for j in range(len(raw_result[i])):
                    mapped_result[abi['outputs'][0]['components'][i]['components'][j]['name']] = raw_result[i][j]
            else:
                mapped_result[abi['outputs'][0]['components'][i]['name']] = raw_result[i]
        return mapped_result
