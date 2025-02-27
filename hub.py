"""CVMS2025 Camera hub for coordinating IO operations."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from .io import read_io_status, read_temperature, set_output_state

_LOGGER = logging.getLogger(__name__)

class CVMSHub:
    """Hub to handle communication with the camera."""

    def __init__(self, hass, host: str, username: str, password: str) -> None:
        """Initialize the hub."""
        self.hass = hass
        self.host = host
        self.username = username
        self.password = password
        self._io_status = None
        self._temperature = None
        self.last_update = None

    def test_connection(self) -> bool:
        """Test connectivity to the camera."""
        try:
            status = read_io_status(self.host, self.username, self.password)
            return status is not None
        except Exception:  # pylint: disable=broad-except
            return False

    async def async_update(self) -> dict:
        """Update data from camera."""
        try:
            # Run IO operations in executor to avoid blocking
            self._io_status = await self.hass.async_add_executor_job(
                read_io_status,
                self.host,
                self.username,
                self.password
            )
            
            self._temperature = await self.hass.async_add_executor_job(
                read_temperature,
                self.host,
                self.username,
                self.password
            )
            
            self.last_update = datetime.now()
            
            # Return data that will be shared through coordinator
            return {
                "io_status": self._io_status,
                "temperature": self._temperature
            }
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.error("Error updating camera data: %s", str(e))
            return {
                "io_status": None,
                "temperature": None
            }

    def get_temperature(self) -> Optional[float]:
        """Get the current temperature."""
        return self._temperature

    def get_io_status(self) -> Optional[Dict[str, Any]]:
        """Get the current IO status."""
        return self._io_status

    def set_output(self, state: bool) -> bool:
        """Set output state."""
        try:
            return set_output_state(
                self.host,
                self.username,
                self.password,
                "1",
                "on" if state else "off"
            )
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.error("Error setting output state: %s", str(e))
            return False
