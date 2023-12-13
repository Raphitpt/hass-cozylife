import voluptuous as vol
from homeassistant import config_entries
import hass
import logging
from .const import DOMAIN
from io import StringIO
from ipaddress import ip_address
from custom_components.cozylife.tcp_client import tcp_client


def ips(start, end):
    '''Return IPs in IPv4 range, inclusive. from stackoverflow'''
    start_int = int(ip_address(start).packed.hex(), 16)
    end_int = int(ip_address(end).packed.hex(), 16)
    return [ip_address(ip).exploded for ip in range(start_int, end_int + 1)]

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required('start_ip', description="Adresse IP de début"): str,
    vol.Required('end_ip', description="Adresse IP de fin"): str,
    vol.Required('port', description="Port de l'appareil", default=5555): int,
    # Ajoutez d'autres options deconfiguration au besoin
})

async def process_config_data(user_input):
    start_ip = user_input['start_ip']
    end_ip = user_input['end_ip']

    probelist = ips(start_ip, end_ip)

    lights_buf = StringIO()
    switches_buf = StringIO()

    devices_data = []

    for ip in probelist:
        a = tcp_client(ip, timeout=0.1)
        a._initSocket()

        if a._connect:
            device_info = a._device_info(hass)
            device_info_data = {
                'ip': ip,
                'unique_id': f'cozylife_{a._device_id[-4:]}',
                'did': a._device_id,
                'pid': a._pid,
                'dmn': a._device_model_name,
                'dpid': a._dpid,
                'device_type': a._device_type_code,
                'icon': a._icon,
            }

            devices_data.append(device_info_data)

            device_info_str = f'  - ip: {ip}\n'
            device_info_str += f'    unique_id: cozylife_{a._device_id[-4:]}\n'
            device_info_str += f'    did: {a._device_id}\n'
            device_info_str += f'    pid: {a._pid}\n'
            device_info_str += f'    dmn: {a._device_model_name}\n'
            device_info_str += f'    dpid: {a._dpid}\n'
            device_info_str += f'    device_type: {a._device_type_code}\n'
            device_info_str += f'    icon: {a._icon}\n'

            if a._device_type_code == '01':
                lights_buf.write(device_info_str)
            elif a._device_type_code == '00':
                switches_buf.write(device_info_str)

    lights_config = lights_buf.getvalue()
    switches_config = switches_buf.getvalue()

    _LOGGER.info(f'lights:\n- platform: cozylife\n  lights:\n{lights_config}')
    _LOGGER.info(f'switch:\n- platform: cozylife\n  switches:\n{switches_config}')

    return {
        'devices': devices_data,
        'lights_config': lights_config,
        'switches_config': switches_config,
    }

async def discover_cozy_life_devices(start_ip, end_ip):
    probelist = ips(start_ip, end_ip)

    available_ips = []

    for ip in probelist:
        _LOGGER.info(f"Scanning IP: {ip}")
        a = tcp_client(ip, timeout=0.1)
        a._initSocket()

        if a._connect:
            available_ips.append(ip)

    return available_ips

class CozyLifeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_discovery(self, user_input=None):
        """Handle discovery."""
        if user_input is not None:
            config_data = await process_config_data(user_input)
            self.hass.data[DOMAIN] = config_data
            return self.async_create_entry(title='CozyLife Demo', data={})
            
        start_ip = user_input.get('start_ip')
        end_ip = user_input.get('end_ip')

        if not start_ip or not end_ip:
            return self.async_abort(reason='missing_start_end_ip')

        available_ips = await discover_cozy_life_devices(start_ip, end_ip)

        _LOGGER.debug("Available IPs: %s", available_ips)
        if not available_ips:
            return self.async_abort(reason='no_devices_found')

        return self.async_show_form(
            step_id='discovery',
            data_schema=vol.Schema({
                vol.Required('start_ip', description="Adresse IP de début", default=start_ip): str,
                vol.Required('end_ip', description="Adresse IP de fin", default=end_ip): str,
                vol.Required('port', description="Port de l'appareil", default=5555): int,
            }),
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step when the user initializes a new integration."""
        errors = {}

        if user_input is not None:
            # Validez les options de configuration fournies
            if not await self._is_valid_configuration(user_input):
                errors['base'] = 'invalid_configuration'
            else:
                # La configuration est valide, créez une entrée pour l'intégration
                config_data = await process_config_data(user_input)
                self.hass.data[DOMAIN] = config_data
                return self.async_create_entry(title='CozyLife Demo', data={})

        # Affichez le formulaire à l'utilisateur
        return self.async_show_form(
            step_id='user',
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    async def _is_valid_configuration(self, user_input):
        """Validez les options de configuration."""
        # Implémentez votre logique de validation ici
        
        return True
