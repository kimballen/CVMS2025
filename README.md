# Siemens CVMS2025-IR Camera Integration for Home Assistant

A custom Home Assistant integration for Siemens CVMS2025-IR network cameras that provides control and monitoring of digital I/O ports and temperature sensors.

## Features

- 🌡️ Temperature monitoring
- 📡 Digital input monitoring
- 🔌 Digital output control
- 🔄 Automatic state updates via polling
- ⚙️ Easy configuration through Home Assistant UI
- 🔒 Basic authentication support
- 🚀 Asynchronous communication and state updates

## Components

- Binary sensors for digital inputs
- Switch entity for digital output control
- Temperature sensor with °C readings
- Coordinator for managing state updates
- Config flow for easy setup

## Installation

1. Copy the `custom_components/cvms2025` folder to your Home Assistant configuration directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click "+ ADD INTEGRATION"
5. Search for "CVMS2025 Camera IO"

## Configuration

Required parameters:

```yaml
host: IP address of your camera
username: Camera login username
password: Camera login password
```

## Requirements

- Home Assistant 2023.x or newer
- CVMS2025 network camera
- Network connectivity to camera
- Python Requests library

## State Updates

The integration polls the camera every 30 seconds (configurable) to update:
- Input states (active/inactive)
- Output state (active/inactive)
- Temperature readings

## Development

The integration uses modern Home Assistant patterns including:
- Config Flow for UI-based setup
- DataUpdateCoordinator for state management
- Async operations for better performance
- Entity platforms for sensors and switches

