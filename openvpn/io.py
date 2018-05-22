import json
from json import JSONDecodeError
from pathlib import Path

from openvpn.utils import is_str, OpenVPNError


BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / 'config.json'
CONFIG_MAP = {
    'aws_access_key_id': is_str,
    'aws_secret_access_key': is_str,
    'region_name': is_str,
    'instance_id': is_str,
    'hosted_zone_id': is_str,
    'domain': is_str,
}


def read_config() -> dict:
    if not CONFIG_PATH.exists():
        raise OpenVPNError('no such file')

    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.loads(f.read())
    except JSONDecodeError as e:
        raise OpenVPNError('config/read: failed (invalid json)') from e

    for key, validator in CONFIG_MAP.items():
        if key not in config:
            raise OpenVPNError(f'config/read: failed (non-existing key "{key}")')
        elif not validator(config[key]):
            raise OpenVPNError(f'config/read: failed (invalid format of "{key}")')
    return config
