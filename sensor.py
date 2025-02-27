"""Support for CVMS2025 sensors."""
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    hub = hass.data[DOMAIN][entry.entry_id]["hub"]

    entities = [CVMSTemperatureSensor(coordinator, hub, entry)]
    
    async_add_entities(entities)

class CVMSTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Temperature sensor for CVMS camera."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "°C"

    def __init__(self, coordinator, hub, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.hub = hub
        self._attr_unique_id = f"{entry.entry_id}_temperature"
        self._attr_name = f"CVMS2025 {hub.host} Temperature"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data["temperature"]
