import os
import sys
import time
import yaml

import pandas as pd
from typing import List

from web3 import Web3

from configs.harmony import hero_matrix
from lib.utils import utils
from lib.harmony.contracts import profession_quest
from lib.harmony.contracts import hero


"""
PROFESSION QUESTS: FISHING AND MINING.
"""

def decide_hero_status(heros_state: dict, discord_configs: dict) -> dict:
    for hero_id in heros_state:
        ready_to_quest = False
        stamina = heros_state[hero_id].get("stamina")
        message = f"[Start profession]\nhero: {hero_id} ; stamina: {stamina} ; "

        if heros_state[hero_id].get("hero_quest", 0) is None and (heros_state[hero_id].get("stamina_ratio", 0) == 1.0):
            message += "ready to quest"
            ready_to_quest = True
        else:
            False

        utils.post_message_discord(discord_configs["quest_channel"], "dfk", message)
        heros_state[hero_id]['ready'] = ready_to_quest
    return heros_state

def get_hero_info(q: profession_quest.ProfessionQuest, h: hero.HeroContract, heros: list) -> List[str]:
    heros_state = {}
    for hero_id in heros:
        hero_info = h.get_hero(hero_id)
        logger.info(hero_info)
        hero_stats = hero_info.get("stats")
        if hero_stats is None:
            logger.error(f"Can't get max stamina for hero {hero_id}")
            continue
        hero_stamnina = hero_stats.get('stamina')
        if hero_stamnina is None:
            logger.error(f"Can't get max stamina for hero {hero_id}")
            continue

        heros_state[hero_id] = heros_state.get(hero_id, dict())
        heros_state[hero_id]['stamina'] = q.get_current_stamina(hero_id)
        heros_state[hero_id]['stamina_ratio'] = float(heros_state[hero_id]['stamina']) / float(hero_stamnina)
        heros_state[hero_id]['hero_quest'] = q.get_hero_quest(hero_id)
        heros_state[hero_id]['hero_to_quest'] = q.hero_to_quest(hero_id)
    return heros_state

def run(q: profession_quest.ProfessionQuest, h: hero.HeroContract, cwd: str, address: utils.UserAddress, discord_configs: dict):
    messages = []
    m = "Start profession, fishing & foraging"
    messages.append(m)
    logger.info(m)

    # Getting heros
    heros_path = f"{cwd}/configs/harmony/heros.yml"
    with open(heros_path) as ymlfile:
        heros = yaml.load(ymlfile, Loader=yaml.FullLoader)
    logger.info(heros)

    quest_contract_addresses = q.get_quest_contracts()

    quests_allowed = ['fishing', 'foraging']
    hmatrix = pd.DataFrame(hero_matrix.matrix, columns=hero_matrix.cols)

    # Sending heroes on quest
    for quest in quests_allowed:
        m = f"Attempting to go on {quest} quest"
        messages.append(m)
        logger.info(m)
        heros_to_send = hmatrix[hmatrix["quest-training-profession"] == quest]
        hero_ids = heros_to_send['hero_id'].tolist()
        if not hero_ids:
            m = f"No heroes available for {quest}"
            messages.append(m)
            logger.info(m)
            continue

        hero_state = decide_hero_status(get_hero_info(q, h, hero_ids), discord_configs)
        logger.info(hero_state)

        m = f"Sending {hero_ids} to quest."
        messages.append(m)
        logger.info(m)
        selected_heros = []
        for hero in hero_ids:
            if hero_state[hero].get("ready"):
                selected_heros.append(hero)
            else:
                m = f"{hero} already questing or out of stamina"
                messages.append(m)
                logger.info(f"{hero} already questing or out of stamina")
                continue

        if not selected_heros:
            m = f"No heroes ready for {quest}"
            messages.append(m)
            logger.info(f"No heroes ready for {quest}")
            continue

        attempts = 5
        level = 0
        quest_address = Web3.toChecksumAddress(q.quest_contracts[quest])
        if quest_address not in quest_contract_addresses:
            m = f"Wrong contract address for {quest}"
            messages.append(m)
            logger.error(m)
            continue

        m = f"Starting {quest} for {selected_heros}"
        messages.append(m)
        logger.info(m)
        tx_receipt = q.multi_start_quest(address, [quest_address], [selected_heros], [attempts], [level])
        time.sleep(3)

        # Save tx to data
        utils.save_tx_receipt(tx_receipt, q.contract_address, cwd)
        message = f"tx hash: {tx_receipt['transactionHash']}"
        utils.post_message_discord(discord_configs["quest_channel"], "dfk", message)

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
        rpcs = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Connect to Web3
    rpc = rpcs['ankr']
    logger.info(f"Connecting to Web3: {rpc}")
    w3 = Web3(Web3.HTTPProvider(rpc))

    # Get my harmony addresses
    logger.info(f"Getting addresses")
    with open(harmony_config_path + "addresses.yml") as ymlfile:
        raw_addresses = yaml.load(ymlfile, Loader=yaml.FullLoader)
    my_address = raw_addresses[0] # # Format {'address': '..', 'private_key': '..'}
    user_address = utils.UserAddress(my_address["address"], my_address["private_key"])

    # Get quest object
    q = profession_quest.ProfessionQuest(w3, rpc)
    # Get hero object
    h = hero.HeroContract(w3, rpc)

    # Get discord configs
    with open(f"{cwd}/configs/discord.yml") as f:
        discord_configs = yaml.load(f, Loader=yaml.FullLoader)

    run(q, h, cwd, user_address, discord_configs)
