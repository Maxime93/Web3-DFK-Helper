import json
import os
import yaml

import pandas as pd

from lib.contracts.harmony import hero
from lib.utils import utils

CLASSES = [
    'Warrior',
    'Knight',
    'Thief',
    'Archer',
    'Priest',
    'Wizard',
    'Monk',
    'Pirate',
    'Berserker',
    'Seer',
    'Paladin *',
    'Dark Knight *',
    'Summoner *',
    'Ninja *',
    'Shapeshifter *',
    'Dragoon **',
    'Sage **',
    'Dread Knight ***'
]

ABILITIES = [
    'strength',
    'wisdom',
    'intelligence',
    'vitality',
    'luck',
    'dexterity',
    'endurance',
    'agility'
]
def get_stats(cwd):
    stats_dir = f'{cwd}/lib/hero_score/stats'
    stats_dfs = {}
    for filename in os.listdir(stats_dir):
        f = os.path.join(stats_dir, filename)
        if os.path.isfile(f):
            stat = f.split('/')[-1].split('.')[0]
            df = pd.read_csv(f)
            stats_dfs[stat] = df
    return stats_dfs

def get_hero(hero_id, rpc):
    hero_data = hero.get_hero(hero_id, rpc)
    return hero_data

if __name__ == "__main__":
    # Set correct path for getting configs
    cwd = os.getcwd()
    path = "dev/personal/finance_code/dfkhelper"
    if not path in cwd:
        cwd = f"{cwd}/{path}"

    # Get Harmony RPC
    harmony_config_path = f"{cwd}/configs/harmony/"
    with open(harmony_config_path + "rpcs.yml") as ymlfile:
        raw_rpcs = yaml.load(ymlfile, Loader=yaml.FullLoader)

    stats_dfs = get_stats(cwd)
    _hero = get_hero(157978, raw_rpcs['ankr'])

    import pprint
    hero_info = hero.human_readable_hero(_hero)
    print(json.dumps(hero_info))

    pprint.pprint(hero_info)
