import datetime
import errno
import json
import logging
import os

from web3 import Web3

from typing import Tuple
from attributedict.collections import AttributeDict

from discord_webhook import DiscordWebhook

logging_map = {'DEBUG': logging.DEBUG,
               'INFO': logging.INFO,
               'WARNING': logging.WARNING,
               'ERROR': logging.ERROR}

class UserAddress:
    def __init__(self, address: str, key: str) -> None:
        self.address = address
        self.key = key

def get_logger(file_name: str, cwd: str, log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(file_name)
    logger.setLevel(log_level)

    log_directory, log_file_name = create_log_directory(file_name, cwd)
    log_format = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s",datefmt="%H:%M:%S")

    file_handler = logging.FileHandler(log_directory + "/" + log_file_name)
    file_handler.setLevel(logging_map[log_level])
    file_handler.setFormatter(log_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

def create_log_directory(file_name: str, cwd: str) -> Tuple[str, str]:
    date = datetime.datetime.now()
    log_directory = date.strftime(f'{cwd}/logs/%Y_%m_%d')
    create_directories(log_directory)
    log_file_name = date.strftime('{}_%d_%m_%Y_%H_%M.log'.format(file_name))
    return log_directory, log_file_name

def create_directories(file_path: str):
    try:
        os.makedirs(file_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def post_message_discord(url, username: str, message: str):
    webhook = DiscordWebhook(
        url=url,
        username=username,
        content=message
    )
    webhook.execute()

def tx_to_json(tx: AttributeDict) -> str:
    return json.loads(Web3.toJSON(tx))

def save_tx_receipt(tx_receipt, contract_address, cwd):
    d = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    h = tx_receipt['transactionHash'].hex()
    file_name = f"/{d}_{h}.json"
    file_path = f"{cwd}/data/transactions/{contract_address}"
    create_directories(file_path)
    tx_receipt_dict = tx_to_json(tx_receipt)
    with open(file_path+file_name, "w") as f:
        json.dump(tx_receipt_dict, f)
