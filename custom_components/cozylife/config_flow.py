"""Config flow for CozyLife Local Pull integration."""
import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN

DATA_SCHEMA = vol.Schema({
    vol.Required('ip_address', description="Adresse IP de l'appareil"): str,
    vol.Required('port', description="Port de l'appareil", default=5555): int,
    # Ajoutez d'autres options de configuration au besoin
})

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
        # Implémentez votre logique de validation ici
        return True
