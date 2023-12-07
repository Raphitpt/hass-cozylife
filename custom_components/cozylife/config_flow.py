import voluptuous as vol
import ipaddress
from homeassistant import config_entries

from .const import DOMAIN

DATA_SCHEMA = vol.Schema({
    vol.Required('ip_start', description="IP de début"): str,
    vol.Required('ip_end', description="IP de fin"): str,
    vol.Required('port', description="Port de l'appareil", default=5555): int,
    # Ajoutez d'autres options de configuration au besoin
})

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
    
class CozyLifeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a CozyLife Local Pull config flow."""

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
        ip_start = user_input['ip_start']
        ip_end = user_input['ip_end']
        port = user_input['port']

        # Vérifiez si les adresses IP sont au format correct
        if not is_valid_ip(ip_start) or not is_valid_ip(ip_end):
            return False

        # Vérifiez si le port est dans une plage valide (par exemple, entre 1 et 65535)
        if not 1 <= port <= 65535:
            return False

        return True
    


    async def async_step_discovery(self, user_input=None):
        """Handle discovery step."""
        if user_input is not None:
            # L'utilisateur a choisi un appareil découvert, traitez les données
            return self.async_create_entry(title='CozyLife Demo', data=user_input)

        # Affichez une liste d'appareils découverts
        return self.async_show_form(
            step_id='discovery',
            data_schema=vol.Schema({
                vol.Required('discovered_device', description="Appareil découvert"): str,
            }),
        )
