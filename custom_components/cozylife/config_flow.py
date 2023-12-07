import voluptuous as vol
from homeassistant import config_entries
import logging
from .const import DOMAIN
from custom_components.cozylife.tcp_client import tcp_client
from homeassistant.helpers import config_entry_flow

DATA_SCHEMA = vol.Schema({
    vol.Required('start_ip', description="Adresse IP de début"): str,
    vol.Required('end_ip', description="Adresse IP de fin"): str,
    vol.Required('port', description="Port de l'appareil", default=5555): int,
    # Ajoutez d'autres options de configuration au besoin
})

async def discover_cozy_life_devices(start_ip, end_ip):
    probelist = ips(start_ip, end_ip)

    available_ips = []

    for ip in probelist:
        print(f"Scanning IP: {ip}")
        a = tcp_client(ip, timeout=0.1)

        a._initSocket()

        if a._connect:
            available_ips.append(ip)

    return available_ips

class CozyLifeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_discovery(self, user_input=None):
        """Handle discovery."""
        if user_input is not None:
            # Ici, vous pouvez traiter les adresses IP découvertes et ajouter des options pour l'utilisateur

            # par exemple, une liste déroulante avec les adresses IP découvertes


            # Créez la configuration à ajouter
            config_data = {
                'ip_address': user_input['selected_ip'],
                'port': user_input['port'],  # Vous devez également ajouter une option pour le port
            }

            # Ajoutez l'entrée de configuration
            return self.async_create_entry(title='CozyLife Demo', data=config_data)

        # Ici, vous pouvez rechercher les appareils disponibles et pré-remplir une liste déroulante
        start_ip = user_input.get('start_ip')
        end_ip = user_input.get('end_ip')

        if not start_ip or not end_ip:
            return self.async_abort(reason='missing_start_end_ip')

        available_ips = await discover_cozy_life_devices(start_ip, end_ip)  # Vous devez implémenter cette fonction
        _LOGGER.debug("Available IPs: %s", available_ips)
        if not available_ips:
            return self.async_abort(reason='no_devices_found')

        return self.async_show_form(
            step_id='discovery',
            data_schema=vol.Schema({
                vol.Required('selected_ip', description="Sélectionnez l'adresse IP", default=available_ips[0]): vol.In(available_ips),
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
                return self.async_create_entry(title='CozyLife Demo', data=user_input)

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
