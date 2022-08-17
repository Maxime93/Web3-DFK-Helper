import json
import logging
from web3 import Web3

from typing import List

from lib.harmony.abis.profession_quest_v1 import profession_v1_abi, profession_v1_address
from lib.harmony.abis.gardening import gardening_address
from lib.harmony.abis.mining import mining_jewel_address
from lib.harmony.chain import Harmony
from lib.utils import utils
from lib.utils.utils import UserAddress

class ProfessionQuestBetaContract(Harmony):
    'For gardening and mining quests'
    def __init__(self, w3: Web3, rpc: str):
        super().__init__(w3, rpc, profession_v1_address, json.loads(profession_v1_abi))

        # The multi_start_quest uses one of the contracts below.
        # This contract (self.contract_address) calls another contract (specific to a profession)
        self.quest_contracts = {
            "gardening": gardening_address,
            "mining": mining_jewel_address
        }

    # Helper
    def parse_complete_quest_receipt(self, tx_receipt):
        quest_result = {}

        quest_reward = self.contract.events.QuestReward().processReceipt(tx_receipt)
        quest_result['reward'] = quest_reward

        quest_xp = self.contract.events.QuestXP().processReceipt(tx_receipt)
        quest_result['xp'] = quest_xp

        return quest_result

    # Calls
    def hero_to_quest_id(self, hero_id: int):
        result = self.contract.functions.heroToQuest(hero_id).call()
        return result

    def get_active_quest(self, address: str):
        result = self.contract.functions.getActiveQuests(address).call()

        if isinstance(result, list):
            mapped_results = []
            for r in result:
                mapped_results.append(self.map_output(r, "getActiveQuests"))
            return mapped_results
        else:
            mapped_result = self.map_output(result, "getActiveQuests")
            return mapped_result

    def get_hero_quest(self, hero_id: int):

        result = self.contract.functions.getHeroQuest(hero_id).call()
        if result[0] <= 0:
            return None

        return result

    def get_hero(self, hero_id: int):
        result = self.contract.functions.getHero(hero_id).call()
        mapped_result = self.map_output(result, "getHero")
        return mapped_result

    def get_quest(self, quest_id):
        result = self.contract.functions.getQuest(quest_id).call()

        if result[0] <= 0:
            return None

        return result


    def get_quest_data(self, quest_id):
        result = self.contract.functions.getQuestData(quest_id).call()
        return result


    def quest_address_to_type(self, quest_address: str):
        result = self.contract.functions.questAddressToType(quest_address).call()
        return result


    def get_current_stamina(self, hero_id: int):
        result = self.contract.functions.getCurrentStamina(hero_id).call()
        return result


    # Transactions (state change)
    def start_quest(self, quest: str, hero_ids: List[int], attempts: List[int], address: utils.UserAddress, logger):
        # Check if ask one of the correct quests
        if quest not in self.quest_contracts.keys():
            raise Exception(f"Sorry, only {self.quest_contracts.values()} quests supported")

        # Get my account
        account = self.w3.eth.account.privateKeyToAccount(address.key)
        self.w3.eth.default_account = account.address

        # Get gas price & nonce
        gas = self.get_gas_price()
        nonce = self.get_nonce(address.address)

        # Make transaction
        transaction = self.contract.functions.startQuest(
            hero_ids, self.quest_contracts[quest], attempts
        ).buildTransaction(
            {'gasPrice': gas, 'nonce': nonce})

        logger.debug("Signing transaction")
        signed_transaction = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=address.key
        )

        logger.debug("Sending transaction " + str(transaction))
        tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        logger.debug("Transaction successfully sent !")
        logger.info(
            "Waiting for transaction " + self.block_explorer_link(signed_transaction.hash.hex()) + " to be mined")

        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info("Transaction mined !")

        return tx_receipt


    def start_quest_with_data(self, quest: str, data, hero_ids: List[int], attempts: int, address: UserAddress, logger: logging.Logger):
        if quest not in self.quest_contracts.keys():
            raise Exception(f"Sorry, only {self.quest_contracts.values()} quests supported")

        # Get my account
        account = self.w3.eth.account.privateKeyToAccount(address.key)
        self.w3.eth.default_account = account.address

        # Get gas price & nonce
        gas = self.get_gas_price()
        nonce = self.get_nonce(address.address)

        if type(data) != tuple:
            raise Exception("Quest data must be a tuple")

        if len(data) != 12:
            raise Exception("Invalid quest data length (expected 12 but was "+str(len(data))+")")

        transaction = self.contract.functions.startQuestWithData(
                hero_ids, self.quest_contracts['gardening'],
                attempts, data
            ).buildTransaction(
            {'gasPrice': gas, 'nonce': nonce})

        logger.debug("Signing transaction")
        signed_transaction = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=address.key
        )
        logger.debug("Sending transaction " + str(transaction))
        tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        logger.debug("Transaction successfully sent !")
        logger.info(
            "Waiting for transaction " + self.block_explorer_link(signed_transaction.hash.hex()) + " to be mined")

        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info("Transaction mined !")

        return tx_receipt


    def complete_quest(self, hero_id: int, address: UserAddress, logger: logging.Logger):
        # Get my account
        account = self.w3.eth.account.privateKeyToAccount(address.key)
        self.w3.eth.default_account = account.address

        # Get gas price & nonce
        gas = self.get_gas_price()
        nonce = self.get_nonce(address.address)

        tx = self.contract.functions.completeQuest(hero_id).buildTransaction(
            {'gasPrice': gas, 'nonce': nonce})

        logger.debug("Signing transaction")
        signed_transaction = self.w3.eth.account.sign_transaction(tx, private_key=address.key)
        logger.debug("Sending transaction " + str(tx))
        tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        logger.debug("Transaction successfully sent !")
        logger.info(
            "Waiting for transaction " + self.block_explorer_link(signed_transaction.hash.hex()) + " to be mined")
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info("Transaction mined !")

        return tx_receipt

    def cancel_quest(self, hero_id: int, address: UserAddress, logger:logging.Logger):
         # Get my account
        account = self.w3.eth.account.privateKeyToAccount(address.key)
        self.w3.eth.default_account = account.address

        # Get gas price & nonce
        gas = self.get_gas_price()
        nonce = self.get_nonce(address.address)

        transaction = self.contract.functions.cancelQuest(hero_id).buildTransaction(
            {'gasPrice': gas, 'nonce': nonce})

        logger.debug("Signing transaction")
        signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key=address.key)
        logger.debug("Sending transaction " + str(transaction))
        tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        logger.debug("Transaction successfully sent !")
        logger.info(
            "Waiting for transaction " + self.block_explorer_link(signed_transaction.hash.hex()) + " to be mined")
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info("Transaction mined !")

        return tx_receipt
