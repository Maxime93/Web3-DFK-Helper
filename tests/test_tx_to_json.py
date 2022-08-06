import pytest

from lib.utils import utils
from mock import tx

@pytest.fixture
def tx_object():
    return tx.tx

def test_convert_tx():
    tx_dict = utils.tx_to_json(tx.tx)
    assert isinstance(tx_dict, dict) == True
