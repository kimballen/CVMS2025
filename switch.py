"""Support for CVMS2025 switches."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    hub = hass.data[DOMAIN][entry.entry_id]["hub"]

    async_add_entities([CVMSOutputSwitch(coordinator, hub, entry)])

class CVMSOutputSwitch(CoordinatorEntity, SwitchEntity):
    """Output switch for CVMS camera."""

    def __init__(self, coordinator, hub, entry):
        """Initialize the switch."""
        super().__init__(coordinator)
        self.hub = hub
        self._attr_unique_id = f"{entry.entry_id}_output_1"
        self._attr_name = f"CVMS2025 {hub.host} Output"

    @property
    def is_on(self):
        """Return true if the output is active."""
        if not self.coordinator.data or not self.coordinator.data["io_status"]:
            return None
            
        status = self.coordinator.data["io_status"]
        if "ports" in status:
            for port in status["ports"]:
                if port["type"] == "Output":
                    return port["state"] == "Active"
        return None

    async def async_turn_on(self, **kwargs):
        """Turn the output on."""
        await self.hass.async_add_executor_job(self.hub.set_output, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the output off."""
        await self.hass.async_add_executor_job(self.hub.set_output, False)
        await self.coordinator.async_request_refresh()
