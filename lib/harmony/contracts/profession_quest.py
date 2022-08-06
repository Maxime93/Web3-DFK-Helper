import json
import sys
from typing import List

from web3 import Web3

from lib.harmony.abis.profession_quest import ABI, CONTRACT_ADDRESS
from lib.harmony.chain import Harmony
from lib.utils.utils import UserAddress

class ProfessionQuest(Harmony):
    'For fishing and foraging quests'
    def __init__(self, w3: Web3, rpc: str):
        super().__init__(w3, rpc, CONTRACT_ADDRESS, json.loads(ABI))

        # The multi_start_quest uses one of the contracts below.
        # This contract (self.contract_address) calls another contract (specific to a profession)
        self.quest_contracts = {
            "fishing": "0xADFFD2A255B3792873a986895c6312e8FbacFc8B",
            "foraging": "0xB465F4590095daD50FEe6Ee0B7c6700AC2b04dF8"
        }

    # Helpers
    def parse_complete_quest_receipt(self, tx_receipt):
        print(type(tx_receipt))
        quest_result = {}

        quest_reward = self.contract.events.QuestReward().processReceipt(tx_receipt)
        quest_result['reward'] = quest_reward

        quest_xp = self.contract.events.QuestXP().processReceipt(tx_receipt)
        quest_result['xp'] = quest_xp

        return quest_result

    # Calls
    def get_hero_quest(self, hero_id: int):
        """Get current quest info that hero is on

        Args:
            hero_id (int):

        Returns:
            dict: example
            {'attempts': 5,
            'completeAtTime': 1650904289,
            'heroes': [161429, 157978],
            'id': 100343997,
            'level': 0,
            'player': '0x9291395f37CBBc1a17285e69C9A8a682bcf1882b',
            'questAddress': '0xADFFD2A255B3792873a986895c6312e8FbacFc8B',
            'startAtTime': 1650903959,
            'startBlock': 25728021,
            'status': 1}
        """
        result = self.contract.functions.getHeroQuest(hero_id).call()
        if result[0] <= 0:
            return None
        mapped_result = self.map_output(result, "getHeroQuest")
        return mapped_result

    def get_current_stamina(self, hero_id: int):
        result = self.contract.functions.getCurrentStamina(hero_id).call()
        return result

    def get_quest_contracts(self):
        result = self.contract.functions.getQuestContracts().call()
        return result

    def hero_to_quest(self, hero_id: int):
        """Maps a hero id to a quest_id

        Args:
            hero_id (int): id of a hero

        Returns:
            int: id of quest
        """
        result = self.contract.functions.heroToQuest(hero_id).call()
        return result

    def get_account_active_quests(self, my_address: str) -> List:
        """Getting info about hero quests.

        Args:
            my_address (str): harmony address

        Returns:
            List: info about active quests
            [{'id': 100343997,
             'questAddress': '0xADFFD2A255B3792873a986895c6312e8FbacFc8B',
             'level': 0, 'heroes': [161429, 157978],
             'player': '0x9291395f37CBBc1a17285e69C9A8a682bcf1882b', 'startBlock': 25728021,
             'startAtTime': 1650903959,
             'completeAtTime': 1650904289,
             'attempts': 5, 'status': 1}]
        """
        result = self.contract.functions.getAccountActiveQuests(my_address).call()
        if isinstance(result, list):
            mapped_results = []
            for r in result:
                mapped_results.append(self.map_output(r, "getAccountActiveQuests"))
            return mapped_results
        else:
            mapped_result = self.map_output(result, "getAccountActiveQuests")
            return mapped_result

    # Transactions (state change)
    def multi_start_quest(self, address: UserAddress, quest_address: str, hero_ids: List[int], attempts: int, level: int):
        # Get my account
        account = self.w3.eth.account.privateKeyToAccount(address.key)
        self.w3.eth.default_account = account.address

        # Get gas price & nonce
        gas = self.get_gas_price()
        nonce = self.get_nonce(address.address)

        # Make transaction
        transaction = self.contract.functions.multiStartQuest(
            quest_address, hero_ids, attempts, level
        ).buildTransaction(
            {
                "nonce": nonce,
                "gasPrice": gas
            }
        )

        # Sign transaction
        signed_transaction = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=address.key
        )

        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(tx_receipt)
        return tx_receipt

    def complete_quest(self, address: UserAddress, hero_id:str):

        # Get my account
        account = self.w3.eth.account.privateKeyToAccount(address.key)
        self.w3.eth.default_account = account.address

        # Get gas price & nonce
        gas = self.get_gas_price()
        nonce = self.get_nonce(address.address)

        # Make transaction
        transaction = self.contract.functions.completeQuest(hero_id).buildTransaction(
            {
                "nonce": nonce,
                "gasPrice": gas
            }
        )

        # Sign transaction
        signed_transaction = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=address.key
        )

        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(tx_receipt)
        return tx_receipt
