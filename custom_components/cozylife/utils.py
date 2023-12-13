import json
import time
import requests
import logging
from homeassistant.helpers.aiohttp_client import async_get_clientsession
_LOGGER = logging.getLogger(__name__)


def get_sn() -> str:
    """
    message sn
    :return: str
    """
    return str(int(round(time.time() * 1000)))

# cache get_pid_list result for many calls
_CACHE_PID = []

async def get_pid_list(lang='en') -> list:
    """
    http://doc.doit/project-12/doc-95/
    :param lang:
    :return:
    """
    global _CACHE_PID
    if len(_CACHE_PID) != 0:
        return _CACHE_PID

    domain = 'api-us.doiting.com'
    protocol = 'http'
    url_prefix = protocol + '://' + domain
    res = requests.get(url_prefix + '/api/device_product/model', {
        'lang': lang
    }, timeout=3)
    
    if 200 != res.status_code:
        _LOGGER.info('get_pid_list.result is none')
        return []
    
    try:
        pid_list = res.json()
    except json.JSONDecodeError as e:
        _LOGGER.error(f'Error decoding JSON response: {e}')
        return []

    if pid_list.get('ret') is None or pid_list['ret'] != '1':
        _LOGGER.info('get_pid_list.result is not as expected')
        return []

    info = pid_list.get('info')
    if info is None or not isinstance(info, dict) or info.get('list') is None or not isinstance(info['list'], list):
        _LOGGER.info('get_pid_list.result structure is not as expected')
        return []

    _CACHE_PID = info['list']
    return _CACHE_PID