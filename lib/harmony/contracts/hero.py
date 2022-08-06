import copy
import json

from web3 import Web3

from lib.harmony.abis.heros import hero_contract_address, hero_abi
from lib.harmony.chain import Harmony
from lib.utils import utils

class HeroContract(Harmony):
    'For interacting with heros'
    def __init__(self, w3: Web3, rpc: str):
        super().__init__(w3, rpc, hero_contract_address, json.loads(hero_abi))

    # Transactions (state change)
    # def transfer(self, contract_address, hero_id, owner_private_key, owner_nonce, receiver_address, gas_price_gwei, tx_timeout_seconds, rpc_address, logger=None):
    #     owner = contract.functions.ownerOf(hero_id).call()
    #     if logger is not None:
    #         logger.info("Hero's owner " + str(owner))

    #     if owner != account.address:
    #         raise Exception("Owner mismatch")

    #     tx = contract.functions.transferFrom(owner, receiver_address, hero_id).buildTransaction(
    #         {'gasPrice': w3.toWei(gas_price_gwei, 'gwei'), 'nonce': owner_nonce})
    #     if logger is not None:
    #         logger.debug("Signing transaction")
    #     signed_tx = w3.eth.account.sign_transaction(tx, private_key=owner_private_key)
    #     if logger is not None:
    #         logger.debug("Sending transaction " + str(tx))
    #     ret = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    #     if logger is not None:
    #         logger.debug("Transaction successfully sent !")
    #         logger.info("Waiting for transaction " + block_explorer_link(contract_address, signed_tx.hash.hex()) + " to be mined")
    #     tx_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash=signed_tx.hash, timeout=tx_timeout_seconds, poll_latency=2)
    #     if logger is not None:
    #         logger.info("Transaction mined !")
    #     logger.info(str(tx_receipt))


    # Calls
    def get_owner(self, hero_id: int):
        return str(self.contract.functions.ownerOf(hero_id).call())


    def get_users_heroes(self, user_address: utils.UserAddress):
        return self.contract.functions.getUserHeroes(Web3.toChecksumAddress(user_address.address)).call()


    def is_approved_for_all(self, owner: utils.UserAddress, operator: utils.UserAddress):
        return self.contract.functions.isApprovedForAll(Web3.toChecksumAddress(owner.address), Web3.toChecksumAddress(operator.address)).call()


    def get_hero(self, hero_id: int):
        """Get hero information

        Args:
            hero_id (int):

        Returns:
            _type_: _description_
        """
        contract_entry = self.contract.functions.getHero(hero_id).call()

        hero = {}
        tuple_index = 0

        hero['id'] = contract_entry[tuple_index]
        tuple_index = tuple_index + 1

        # SummoningInfo
        summoning_info = {}
        summoning_info['summonedTime'] = contract_entry[tuple_index][0]
        summoning_info['nextSummonTime'] = contract_entry[tuple_index][1]
        summoning_info['summonerId'] = contract_entry[tuple_index][2]
        summoning_info['assistantId'] = contract_entry[tuple_index][3]
        summoning_info['summons'] = contract_entry[tuple_index][4]
        summoning_info['maxSummons'] = contract_entry[tuple_index][5]

        hero['summoningInfo'] = summoning_info
        tuple_index = tuple_index + 1

        # HeroInfo
        hero_info = {}
        hero_info['statGenes'] = contract_entry[tuple_index][0]
        hero_info['visualGenes'] = contract_entry[tuple_index][1]
        hero_info['rarity'] = contract_entry[tuple_index][2]
        hero_info['shiny'] = contract_entry[tuple_index][3]
        hero_info['generation'] = contract_entry[tuple_index][4]
        hero_info['firstName'] = contract_entry[tuple_index][5]
        hero_info['lastName'] = contract_entry[tuple_index][6]
        hero_info['shinyStyle'] = contract_entry[tuple_index][7]
        hero_info['class'] = contract_entry[tuple_index][8]
        hero_info['subClass'] = contract_entry[tuple_index][9]

        hero['info'] = hero_info
        tuple_index = tuple_index + 1

        # HeroState
        hero_state = {}
        hero_state['staminaFullAt'] = contract_entry[tuple_index][0]
        hero_state['hpFullAt'] = contract_entry[tuple_index][1]
        hero_state['mpFullAt'] = contract_entry[tuple_index][2]
        hero_state['level'] = contract_entry[tuple_index][3]
        hero_state['xp'] = contract_entry[tuple_index][4]
        hero_state['currentQuest'] = contract_entry[tuple_index][5]
        hero_state['sp'] = contract_entry[tuple_index][6]
        hero_state['status'] = contract_entry[tuple_index][7]

        hero['state'] = hero_state
        tuple_index = tuple_index + 1

        # HeroStats
        hero_stats = {}
        hero_stats['strength'] = contract_entry[tuple_index][0]
        hero_stats['intelligence'] = contract_entry[tuple_index][1]
        hero_stats['wisdom'] = contract_entry[tuple_index][2]
        hero_stats['luck'] = contract_entry[tuple_index][3]
        hero_stats['agility'] = contract_entry[tuple_index][4]
        hero_stats['vitality'] = contract_entry[tuple_index][5]
        hero_stats['endurance'] = contract_entry[tuple_index][6]
        hero_stats['dexterity'] = contract_entry[tuple_index][7]
        hero_stats['hp'] = contract_entry[tuple_index][8]
        hero_stats['mp'] = contract_entry[tuple_index][9]
        hero_stats['stamina'] = contract_entry[tuple_index][10]

        hero['stats'] = hero_stats
        tuple_index = tuple_index + 1

        # primary HeroStatGrowth
        hero_primary_stat_growth = {}
        hero_primary_stat_growth['strength'] = contract_entry[tuple_index][0]
        hero_primary_stat_growth['intelligence'] = contract_entry[tuple_index][1]
        hero_primary_stat_growth['wisdom'] = contract_entry[tuple_index][2]
        hero_primary_stat_growth['luck'] = contract_entry[tuple_index][3]
        hero_primary_stat_growth['agility'] = contract_entry[tuple_index][4]
        hero_primary_stat_growth['vitality'] = contract_entry[tuple_index][5]
        hero_primary_stat_growth['endurance'] = contract_entry[tuple_index][6]
        hero_primary_stat_growth['dexterity'] = contract_entry[tuple_index][7]
        hero_primary_stat_growth['hpSm'] = contract_entry[tuple_index][8]
        hero_primary_stat_growth['hpRg'] = contract_entry[tuple_index][9]
        hero_primary_stat_growth['hpLg'] = contract_entry[tuple_index][10]
        hero_primary_stat_growth['mpSm'] = contract_entry[tuple_index][11]
        hero_primary_stat_growth['mpRg'] = contract_entry[tuple_index][12]
        hero_primary_stat_growth['mpLg'] = contract_entry[tuple_index][13]

        hero['primaryStatGrowth'] = hero_primary_stat_growth
        tuple_index = tuple_index + 1

        # secondary HeroStatGrowth
        hero_secondary_stat_growth = {}
        hero_secondary_stat_growth['strength'] = contract_entry[tuple_index][0]
        hero_secondary_stat_growth['intelligence'] = contract_entry[tuple_index][1]
        hero_secondary_stat_growth['wisdom'] = contract_entry[tuple_index][2]
        hero_secondary_stat_growth['luck'] = contract_entry[tuple_index][3]
        hero_secondary_stat_growth['agility'] = contract_entry[tuple_index][4]
        hero_secondary_stat_growth['vitality'] = contract_entry[tuple_index][5]
        hero_secondary_stat_growth['endurance'] = contract_entry[tuple_index][6]
        hero_secondary_stat_growth['dexterity'] = contract_entry[tuple_index][7]
        hero_secondary_stat_growth['hpSm'] = contract_entry[tuple_index][8]
        hero_secondary_stat_growth['hpRg'] = contract_entry[tuple_index][9]
        hero_secondary_stat_growth['hpLg'] = contract_entry[tuple_index][10]
        hero_secondary_stat_growth['mpSm'] = contract_entry[tuple_index][11]
        hero_secondary_stat_growth['mpRg'] = contract_entry[tuple_index][12]
        hero_secondary_stat_growth['mpLg'] = contract_entry[tuple_index][13]

        hero['secondaryStatGrowth'] = hero_secondary_stat_growth
        tuple_index = tuple_index + 1

        # HeroProfessions
        hero_professions = {}
        hero_professions['mining'] = contract_entry[tuple_index][0]
        hero_professions['gardening'] = contract_entry[tuple_index][1]
        hero_professions['foraging'] = contract_entry[tuple_index][2]
        hero_professions['fishing'] = contract_entry[tuple_index][3]

        hero['professions'] = hero_professions

        return hero


def human_readable_hero(raw_hero, hero_male_first_names=None, hero_female_first_names=None, hero_last_names=None):
    readable_hero = copy.deepcopy(raw_hero)

    readable_hero['info']['rarity'] = parse_rarity(readable_hero['info']['rarity'])
    readable_hero['info']['class'] = parse_class(readable_hero['info']['class'])
    readable_hero['info']['subClass'] = parse_class(readable_hero['info']['subClass'])

    # visualGenes
    readable_hero['info']['visualGenes'] = parse_visual_genes(readable_hero['info']['visualGenes'])

    # statsGenes
    readable_hero['info']['statGenes'] = parse_stat_genes(readable_hero['info']['statGenes'])

    # names
    if readable_hero['info']['visualGenes']['gender'] == 'male':
        if hero_male_first_names is not None:
            readable_hero['info']['firstName'] = hero_male_first_names[readable_hero['info']['firstName']]
    else:
        if hero_female_first_names is not None:
            readable_hero['info']['firstName'] = hero_female_first_names[readable_hero['info']['firstName']]

    if hero_last_names is not None:
        readable_hero['info']['lastName'] = hero_last_names[readable_hero['info']['lastName']]

    return readable_hero

FAIL_ON_NOT_FOUND = False

ALPHABET = '123456789abcdefghijkmnopqrstuvwx'

CRYSTALEVALE_HERO_OFFSET = 1_000_000_000_000

rarity = {
    0: "common",
    1: "uncommon",
    2: "rare",
    3: "legendary",
    4: "mythic",
}

_class = {
    0: "warrior",
    1: "knight",
    2: "thief",
    3: "archer",
    4: "priest",
    5: "wizard",
    6: "monk",
    7: "pirate",
    8: "berserker",
    9: "seer",
    16: "paladin",
    17: "darkknight",
    18: "summoner",
    19: "ninja",
    20: "shapeshifter",
    24: "dragoon",
    25: "sage",
    28: "dreadknight"
}

visual_traits = {
    0: 'gender',
    1: 'headAppendage',
    2: 'backAppendage',
    3: 'background',
    4: 'hairStyle',
    5: 'hairColor',
    6: 'visualUnknown1',
    7: 'eyeColor',
    8: 'skinColor',
    9: 'appendageColor',
    10: 'backAppendageColor',
    11: 'visualUnknown2'
}

stat_traits = {
    0: 'class',
    1: 'subClass',
    2: 'profession',
    3: 'passive1',
    4: 'passive2',
    5: 'active1',
    6: 'active2',
    7: 'statBoost1',
    8: 'statBoost2',
    9: 'statsUnknown1',
    10: 'element',
    11: 'statsUnknown2'
}

professions = {
    0: 'mining',
    2: 'gardening',
    4: 'fishing',
    6: 'foraging',
}

stats = {
    0: 'strength',
    2: 'agility',
    4: 'intelligence',
    6: 'wisdom',
    8: 'luck',
    10: 'vitality',
    12: 'endurance',
    14: 'dexterity'
}

elements = {
    0: 'fire',
    2: 'water',
    4: 'earth',
    6: 'wind',
    8: 'lightning',
    10: 'ice',
    12: 'light',
    14: 'dark',
}


def cv2sd_cv_hero_id(cv_hero_id):
    return cv_hero_id - CRYSTALEVALE_HERO_OFFSET


def sd2cv_cv_hero_id(cv_hero_id):
    return cv_hero_id + CRYSTALEVALE_HERO_OFFSET


def parse_rarity(id):
    value = rarity.get(id, None)
    if FAIL_ON_NOT_FOUND and value is None:
        raise Exception("Rarity not found")
    return value


def parse_class(id):
    value = _class.get(id, None)
    if FAIL_ON_NOT_FOUND and value is None:
        raise Exception("Class not found")
    return value


def parse_profession(id):
    value = professions.get(id, None)
    if FAIL_ON_NOT_FOUND and value is None:
        raise Exception("Profession not found")
    return value


def parse_stat(id):
    value = stats.get(id, None)
    if FAIL_ON_NOT_FOUND and value is None:
        raise Exception("Stat not found")
    return value


def parse_element(id):
    value = elements.get(id, None)
    if FAIL_ON_NOT_FOUND and value is None:
        raise Exception("Element not found")
    return value


def genes2traits(genes):
    traits = []

    stat_raw_kai = "".join(__genesToKai(genes).split(' '))
    for ki in range(0, len(stat_raw_kai)):
        kai = stat_raw_kai[ki]
        value_num = __kai2dec(kai)
        traits.append(value_num)

    assert len(traits) == 48
    arranged_traits = [[], [], [], []]
    for i in range(0, 12):
        index = i << 2
        for j in range(0, len(arranged_traits)):
            arranged_traits[j].append(traits[index + j])

    arranged_traits.reverse()
    return arranged_traits


def parse_stat_genes(genes):
    traits = genes2traits(genes)
    stats = parse_stat_trait(traits[0])
    r1 = parse_stat_trait(traits[1])
    r2 = parse_stat_trait(traits[2])
    r3 = parse_stat_trait(traits[3])

    stats['r1'] = r1
    stats['r2'] = r2
    stats['r3'] = r3
    stats['raw'] = genes

    return stats


def parse_stat_trait(trait):

    if len(trait) != 12:
        raise Exception("Traits must be an array of 12")

    stats = {}
    for i in range(0, 12):
        stat_trait = stat_traits.get(i, None)
        stats[stat_trait] = trait[i]

    stats['class'] = parse_class(stats['class'])
    stats['subClass'] = parse_class(stats['subClass'])

    stats['profession'] = parse_profession(stats['profession'])

    stats['passive1'] = parse_class(stats['passive1'])
    stats['passive2'] = parse_class(stats['passive2'])
    stats['active1'] = parse_class(stats['active1'])
    stats['active2'] = parse_class(stats['active2'])

    stats['statBoost1'] = parse_stat(stats['statBoost1'])
    stats['statBoost2'] = parse_stat(stats['statBoost2'])
    stats['statsUnknown1'] = stats.get(stats['statsUnknown1'], None)  # parse_stat(stat_genes['statsUnknown1'])
    stats['statsUnknown2'] = stats.get(stats['statsUnknown2'], None)  # parse_stat(stat_genes['statsUnknown2'])

    stats['element'] = parse_element(stats['element'])

    return stats


def parse_visual_genes(genes):
    visual_genes = {}
    visual_genes['raw'] = genes

    visual_raw_kai = "".join(__genesToKai(visual_genes['raw']).split(' '))

    for ki in range(0, len(visual_raw_kai)):
        stat_trait = visual_traits.get(int(ki / 4), None)
        kai = visual_raw_kai[ki]
        value_num = __kai2dec(kai)
        visual_genes[stat_trait] = value_num

    visual_genes['gender'] = 'male' if visual_genes['gender'] == 1 else 'female'
    return visual_genes


def hero2str(hero):

    if isinstance(hero['info']['class'], int):
        c = parse_class(hero['info']['class'])
        sc = parse_class(hero['info']['subClass'])
        r = parse_rarity(hero['info']['rarity'])
        l = hero['state']['level']
    else:
        c = hero['info']['class']
        sc = hero['info']['subClass']
        r = hero['info']['rarity']
        l = hero['state']['level']

    return str(hero['id']) + " " + r.title() + " " + c.title() + "/" + sc.title() + " lvl " + str(l)


def __genesToKai(genes):
    BASE = len(ALPHABET)

    buf = ''
    while genes >= BASE:
        mod = int(genes % BASE)
        buf = ALPHABET[int(mod)] + buf
        genes = (genes - mod) // BASE

    # Add the last 4 (finally).
    buf = ALPHABET[int(genes)] + buf

    # Pad with leading 1s.
    buf = buf.rjust(48, '1')
    buf = buf[0:48]

    return ' '.join(buf[i:i + 4] for i in range(0, len(buf), 4))


def __kai2dec(kai):
    return ALPHABET.index(kai)


def parse_names(names_raw_string):
    names_raw_string = names_raw_string\
        .replace("\\xf3", "ó") \
        .replace("\\xf2", "ò") \
        .replace("\\xe9", "é") \
        .replace("\\xe1", "á") \
        .replace("\\xc9", "É") \
        .replace("\\xed", "í") \
        .replace("\\xfa", "ú") \
        .replace("\\xec", "ì")

    if "\\x" in names_raw_string:
        raise Exception("Unhandled unicode found")

    return json.loads(names_raw_string)