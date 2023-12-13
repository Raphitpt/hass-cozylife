# -*- coding: utf-8 -*-
import json
import socket
from typing import Union, Any
import logging
from .utils import get_pid_list, get_sn  # Vérifiez l'importation de vos modules

CMD_INFO = 0
CMD_QUERY = 2
CMD_SET = 3
CMD_LIST = [CMD_INFO, CMD_QUERY, CMD_SET]
_LOGGER = logging.getLogger(__name__)


class tcp_client(object):
    def __init__(self, ip, timeout=0.01):
        self._ip = ip
        self._port = 5555
        self._connect = None  # socket
        self.timeout = timeout
        self._device_id = str
        self._pid = str
        self._device_type_code = str
        self._icon = str
        self._device_model_name = str
        self._dpid = []
        self._sn = str

    def disconnect(self):
        if self._connect:
            try:
                self._connect.shutdown(socket.SHUT_RDWR)
                self._connect.close()
            except Exception as e:
                _LOGGER.error("Error while disconnecting: %s", str(e))
        self._connect = None

    def __del__(self):
        self.disconnect()

    def _initSocket(self):
        """Initialize socket connection."""
        self._connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect.settimeout(self.timeout)

        try:
            self._connect.connect((self._ip, self._port))
        except Exception as e:
            _LOGGER.error("_initSocket error, ip=%s, error=%s", self._ip, str(e))
            self.disconnect()
            self._connect = None

    @property
    def check(self) -> bool:
        return True

    @property
    def dpid(self):
        return self._dpid

    @property
    def device_model_name(self):
        return self._device_model_name

    @property
    def icon(self):
        return self._icon

    @property
    def device_type_code(self) -> str:
        return self._device_type_code

    @property
    def device_id(self):
        return self._device_id

    def _device_info(self) -> None:
        self._only_send(CMD_INFO, {})
        try:
            resp = self._connect.recv(1024)
            resp_json = json.loads(resp.strip())
        except Exception as e:
            _LOGGER.info('_device_info.recv.error: %s', str(e))
            return None

        if resp_json.get('msg') is None or type(resp_json['msg']) is not dict:
            _LOGGER.info('_device_info.recv.error1')
            return None

        if resp_json['msg'].get('did') is None:
            _LOGGER.info('_device_info.recv.error2')
            return None
        self._device_id = resp_json['msg']['did']

        if resp_json['msg'].get('pid') is None:
            _LOGGER.info('_device_info.recv.error3')
            return None

        self._pid = resp_json['msg']['pid']

        pid_list = get_pid_list()

        for item in pid_list:
            match = False
            for item1 in item['device_model']:
                if item1['device_product_id'] == self._pid:
                    match = True
                    self._icon = item1['icon']
                    self._device_model_name = item1['device_model_name']
                    self._dpid = item1['dpid']
                    break

            if match:
                self._device_type_code = item['device_type_code']
                break

        _LOGGER.info(self._device_id)
        _LOGGER.info(self._device_type_code)
        _LOGGER.info(self._pid)
        _LOGGER.info(self._device_model_name)
        _LOGGER.info(self._icon)

    def _get_package(self, cmd: int, payload: dict) -> bytes:
        self._sn = get_sn()
        if CMD_SET == cmd:
            message = {
                'pv': 0,
                'cmd': cmd,
                'sn': self._sn,
                'msg': {
                    'attr': [int(item) for item in payload.keys()],
                    'data': payload,
                }
            }
        elif CMD_QUERY == cmd:
            message = {
                'pv': 0,
                'cmd': cmd,
                'sn': self._sn,
                'msg': {
                    'attr': [0],
                }
            }
        elif CMD_INFO == cmd:
            message = {
                'pv': 0,
                'cmd': cmd,
                'sn': self._sn,
                'msg': {}
            }
        else:
            raise Exception('CMD is not valid')

        payload_str = json.dumps(message, separators=(',', ':',))
        _LOGGER.info(f'_package={payload_str}')
        return bytes(payload_str + "\r\n", encoding='utf8')

    def _send_receiver(self, cmd: int, payload: dict) -> Union[dict, Any]:
        try:
            self._connect.send(self._get_package(cmd, payload))
        except Exception as e:
            _LOGGER.error("Error sending data: %s", str(e))
            return None

        try:
            i = 10
            while i > 0:
                res = self._connect.recv(1024)
                i -= 1
                if self._sn in str(res):
                    payload = json.loads(res.strip())
                    if not payload or not payload.get('msg') or not isinstance(payload['msg'], dict):
                        return None

                    if not payload['msg'].get('data') or not isinstance(payload['msg']['data'], dict):
                        return None

                    return payload['msg']['data']

            return None

        except Exception as e:
            _LOGGER.info(f'_only_send.recv.error: %s', str(e))
            return None

    def _only_send(self, cmd: int, payload: dict) -> None:
        try:
            self._connect.send(self._get_package(cmd, payload))
        except Exception as e:
            _LOGGER.error("Error sending data: %s", str(e))
            self.disconnect()
            self._initSocket()
            self._connect.send(self._get_package(cmd, payload))

    def control(self, payload: dict) -> bool:
        self._only_send(CMD_SET, payload)
        return True

    def query(self) -> dict:
        return self._send_receiver(CMD_QUERY, {})
