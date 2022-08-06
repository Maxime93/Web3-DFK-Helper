import os
import yaml

from web3 import Web3

from lib.utils import utils
from lib.harmony.contracts import profession_quest
from lib.harmony.contracts import profession_quest_beta
from lib.harmony.contracts import hero


if __name__ == "__main__":
    # Set correct path for getting configs
    cwd = os.getcwd()
    path = "dev/personal/finance_code/dfkhelper"
    if not path in cwd:
        cwd = f"{cwd}/{path}"

    # Get Harmony RPC
    harmony_config_path = f"{cwd}/configs/harmony/"
    with open(harmony_config_path + "rpcs.yml") as ymlfile:
        rpcs = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Connect to Web3
    rpc = rpcs['ankr']
    w3 = Web3(Web3.HTTPProvider(rpc))

    # Get my harmony addresses
    with open(harmony_config_path + "addresses.yml") as ymlfile:
        raw_addresses = yaml.load(ymlfile, Loader=yaml.FullLoader)
    my_address = raw_addresses[0] # # Format {'address': '..', 'private_key': '..'}
    user_address = utils.UserAddress(my_address["address"], my_address["private_key"])

    # Get quest object
    q = profession_quest.ProfessionQuest(w3, rpc)
    # Get quest beta object
    qb = profession_quest_beta.ProfessionQuestBetaContract(w3, rpc)
    # Get hero object
    h = hero.HeroContract(w3, rpc)

    # Get discord configs
    with open(f"{cwd}/configs/discord.yml") as f:
        discord_configs = yaml.load(f, Loader=yaml.FullLoader)

    hero_211785 = h.get_hero(211785)
    print(hero_211785)

    better_hero = hero.human_readable_hero(hero_211785)
    import pprint
    pprint.pprint(better_hero)

    myheroes = h.get_users_heroes(user_address)
    pprint.pprint(myheroes)