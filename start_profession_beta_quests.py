import datetime
import os
import sys
import time
import yaml

import pandas as pd

from typing import List
from web3 import Web3


from configs.harmony import hero_matrix
from lib.utils import utils
from lib.harmony.contracts import profession_quest_beta
from lib.harmony.contracts import hero

"""
PROFESSION QUESTS: MINING AND GARDENING.
"""

QUESTS_ALLOWED = ['gardening', 'mining']

def decide_hero_status(heros_state: dict, discord_configs: dict) -> dict:
    for hero_id in heros_state:
        d = datetime.datetime.now()
        ready_to_quest = False
        stamina = heros_state[hero_id].get("stamina")
        message = f"[Start profession beta]\nhero: {hero_id} ; stamina: {stamina} ; "

        if (heros_state[hero_id].get("hero_quest", 0) is None) and (heros_state[hero_id].get("stamina_full_at", d) < d):
            message += "ready to quest"
            ready_to_quest = True
        else:
            False

        utils.post_message_discord(discord_configs["quest_channel"], "dfk", message)
        heros_state[hero_id]['ready'] = ready_to_quest
    return heros_state

def get_hero_info(q: profession_quest_beta.ProfessionQuestBetaContract, h: hero.HeroContract, heros: list) -> List[str]:
    heros_state = {}
    for hero_id in heros:
        hero_info = h.get_hero(hero_id)
        logger.info(hero_info)
        hero_state = hero_info.get("state")
        if hero_state is None:
            logger.error(f"Can't get hero state for: {hero_id}")
            continue
        hero_stamina_full_at = hero_state.get('staminaFullAt')
        if hero_stamina_full_at is None:
            logger.error(f"Can't get stamnina_full_at for hero {hero_id}")
            continue

        hero_max_stamina = hero_state.get('staminaFullAt')
        if hero_max_stamina is None:
            logger.error(f"Can't get stamnina_full_at for hero {hero_id}")
            continue

        heros_state[hero_id] = heros_state.get(hero_id, dict())
        heros_state[hero_id]['stamina'] = q.get_current_stamina(hero_id)
        heros_state[hero_id]['stamina'] = hero_max_stamina
        heros_state[hero_id]['stamina_full_at'] = datetime.datetime.fromtimestamp(int(hero_stamina_full_at))
        heros_state[hero_id]['hero_quest'] = q.get_hero_quest(hero_id)
        heros_state[hero_id]['hero_to_quest'] = q.hero_to_quest_id(hero_id)
    return heros_state

def run(q: profession_quest_beta.ProfessionQuestBetaContract, h: hero.HeroContract, cwd: str, address: utils.UserAddress, discord_configs: dict):
    messages = []
    m = "Start profession, mining & gardening"
    messages.append(m)
    logger.info(m)

    # Getting heros
    heros_path = f"{cwd}/configs/harmony/heros.yml"
    with open(heros_path) as ymlfile:
        heros = yaml.load(ymlfile, Loader=yaml.FullLoader)
    logger.info(heros)

    hmatrix = pd.DataFrame(hero_matrix.matrix, columns=hero_matrix.cols)

    # Sending heroes on quest
    for quest in QUESTS_ALLOWED:
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

        attempts = 1

        for starter_hero in selected_heros:
            m = f"Starting {quest} for {starter_hero} - {attempts} atempts"
            messages.append(m)
            logger.info(m)
            tx_receipt = q.start_quest([starter_hero], attempts, address, logger)
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
        raw_rpcs = yaml.load(ymlfile, Loader=yaml.FullLoader)
    rpc = raw_rpcs['ankr']

    # Connect to Web3
    logger.info(f"Connecting to Web3: {rpc}")
    w3 = Web3(Web3.HTTPProvider(rpc))

    # Get my harmony addresses
    logger.info(f"Getting addresses.")
    with open(harmony_config_path + "addresses.yml") as ymlfile:
        raw_addresses = yaml.load(ymlfile, Loader=yaml.FullLoader)
    my_address = raw_addresses[0] # {'address': '0x9291395f37CBBc1a17285e69C9A8a682bcf1882b', 'private_key': 'data'}
    user_address = utils.UserAddress(my_address["address"], my_address["private_key"])

    # Get discord configs
    with open(f"{cwd}/configs/discord.yml") as f:
        discord_configs = yaml.load(f, Loader=yaml.FullLoader)

    # Get quest object
    q = profession_quest_beta.ProfessionQuestBetaContract(w3, rpc)
    # Get hero object
    h = hero.HeroContract(w3, rpc)

    run(q, h, cwd, user_address, discord_configs)
