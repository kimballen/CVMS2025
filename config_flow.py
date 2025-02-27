"""Config flow for CVMS2025 Camera IO."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from . import hub

class CVMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CVMS2025."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the connection
                camera = hub.CVMSHub(
                    self.hass,
                    user_input[CONF_HOST],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD]
                )
                if await self.hass.async_add_executor_job(camera.test_connection):
                    return self.async_create_entry(
                        title=f"Camera {user_input[CONF_HOST]}",
                        data=user_input
                    )
                else:
                    errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
