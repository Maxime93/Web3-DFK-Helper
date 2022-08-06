import requests
import sys
from web3 import Web3

from lib.smart_contract_base import BaseContract

class Harmony(BaseContract):
    def __init__(self, w3: Web3, rpc: str, contract_address: str, abi: str):
        super().__init__(w3, rpc, contract_address, abi)
        self.explorer_url = "https://explorer.harmony.one"

    def block_explorer_link(self, txid: str):
        return f"{self.explorer_url}/tx/{txid}"

    def get_gas_price(self):
        json_data = {
            'jsonrpc': '2.0',
            'method': 'hmyv2_gasPrice',
            'params': [],
            'id': 1,
        }

        response = requests.post(self.rpc, json=json_data)
        try:
            gas = response.json()['result']
        except Exception as e:
            sys.exit(f"Can't get gas! Error: {e}")
        return gas
