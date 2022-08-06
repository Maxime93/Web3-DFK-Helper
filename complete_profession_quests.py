import datetime
import os
import sys
import yaml

from web3 import Web3

from lib.utils import utils
from lib.harmony.contracts import profession_quest

"""
PROFESSION QUESTS: FISHING AND FORAGING.
"""

def run(q: profession_quest.ProfessionQuest, cwd: str, address: utils.UserAddress, discord_configs: dict):
    messages = []
    terminate = False
    active_quests = q.get_account_active_quests(address.address)
    m = f"Completing active quests: {active_quests}"
    messages.append(m)
    logger.info(m)

    if not active_quests:
        m = "No active quests."
        messages.append(m)
        logger.info(m)
        terminate = True

    # Loop through heroes in quests
    # If multiple heroes on the same quest, completing the first one should be enough
    if not terminate:
        for active_quest in active_quests:
            # Checking if quest is done
            complete_time = active_quest.get("completeAtTime")
            if complete_time is None:
                m = "[Error] active quest not giving us a completed time"
                messages.append(m)
                logger.error(m)
                utils.post_message_discord(discord_configs["quest_channel"], "dfk", "\n".join(messages))
                sys.exit("Completed time Error")
            else:
                # If this quest is not done we don't complete!
                if datetime.datetime.fromtimestamp(complete_time) > datetime.datetime.now():
                    id = active_quest.get("id")
                    m = f"Quest {id} is not done, not completing yet"
                    messages.append(m)
                    logger.info(m)
                    continue

            # Completing quest
            try:
                m = f"Completing quest for {active_quest.get('heroes')}"
                messages.append(m)
                logger.info(m)
                tx_receipt = q.complete_quest(address, active_quest['heroes'][0])
            except Exception as e:
                m = f"Can't complete quest for {active_quest['heroes'][0]}. Error: {e}"
                messages.append(m)
                logger.warning(m)
                utils.post_message_discord(discord_configs["quest_channel"], "dfk", "\n".join(messages))
                sys.exit(e)

            message = f"Quest completed for {active_quest['heroes']}"
            # Check status code
            if tx_receipt['status'] != 1:
                message = f"Quest failed for {active_quest['heroes']}"

            utils.post_message_discord(discord_configs["quest_channel"], "dfk", message)
            utils.save_tx_receipt(tx_receipt, q.contract_address, cwd)
            message = f"tx hash: {tx_receipt['transactionHash']}"

    utils.post_message_discord(discord_configs["quest_channel"], "dfk", "\n".join(messages))

if __name__ == "__main__":
    # Set correct path for getting configs
    cwd = os.getcwd()
    path = "dev/personal/finance_code/dfkhelper"
    if not path in cwd:
        cwd = f"{cwd}/{path}"

    file_name = __file__.split("/")[-1]
    logger = utils.get_logger(file_name, cwd)

    # Get Harmony RPC
    harmony_config_path = f"{cwd}/configs/harmony/"
    with open(harmony_config_path + "rpcs.yml") as ymlfile:
        raw_rpcs = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Connect to Web3
    logger.info(f"Connecting to Web3: {raw_rpcs['ankr']}")
    w3 = Web3(Web3.HTTPProvider(raw_rpcs['ankr']))

    # Get quest object
    q = profession_quest.ProfessionQuest(w3, raw_rpcs['ankr'])

    # Get my harmony addresses
    logger.info(f"Getting addresses.")
    with open(harmony_config_path + "addresses.yml") as ymlfile:
        raw_addresses = yaml.load(ymlfile, Loader=yaml.FullLoader)
    my_address = raw_addresses[0] # {'address': '0x9291395f37CBBc1a17285e69C9A8a682bcf1882b', 'private_key': 'data'}
    user_address = utils.UserAddress(my_address["address"], my_address["private_key"])

    # Get discord configs
    with open(f"{cwd}/configs/discord.yml") as f:
        discord_configs = yaml.load(f, Loader=yaml.FullLoader)

    run(q, cwd, user_address, discord_configs)
