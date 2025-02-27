"""Support for CVMS2025 binary sensors."""
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
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
    """Set up binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    hub = hass.data[DOMAIN][entry.entry_id]["hub"]

    entities = []
    
    # Add input sensors
    status = hub.get_io_status()
    if status and "ports" in status:
        for port in status["ports"]:
            if port["type"] == "Input":
                entities.append(
                    CVMSInputSensor(
                        coordinator,
                        hub,
                        entry,
                        port["port"]
                    )
                )

    async_add_entities(entities)

class CVMSInputSensor(CoordinatorEntity, BinarySensorEntity):
    """Input sensor for CVMS camera."""

    _attr_device_class = BinarySensorDeviceClass.OPENING  # Changed from GENERIC to OPENING

    def __init__(self, coordinator, hub, entry, input_number):
        """Initialize the sensor.""" 
        super().__init__(coordinator)
        self.hub = hub
        self.input_number = input_number
        self._attr_unique_id = f"{entry.entry_id}_input_{input_number}"
        self._attr_name = f"CVMS2025 {hub.host} Input {input_number}"

    @property
    def is_on(self):
        """Return true if the input is active."""
        if not self.coordinator.data or not self.coordinator.data["io_status"]:
            return None
            
        status = self.coordinator.data["io_status"]
        if "ports" in status:
            for port in status["ports"]:
                if port["type"] == "Input" and port["port"] == self.input_number:
                    return port["state"] == "Active"
        return None
