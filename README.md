# pycaldera

Python client library for controlling Caldera spas via their cloud API.

## Installation

```bash
pip install pycaldera
```

## Usage

```python
import asyncio
from pycaldera import AsyncCalderaClient, PUMP_OFF, PUMP_LOW, PUMP_HIGH


async def main():
    async with AsyncCalderaClient("email@example.com", "password") as spa:
        # Get current spa status
        status = await spa.get_spa_status()
        print(f"Current temperature: {status.ctrl_head_water_temperature}°F")

        # Get detailed live settings
        settings = await spa.get_live_settings()
        print(f"Target temperature: {settings.ctrl_head_set_temperature}°F")

        # Control the spa
        await spa.set_temperature(102)  # Set temperature to 102°F
        await spa.set_pump(1, PUMP_HIGH)  # Set pump 1 to high speed
        await spa.set_lights(True)  # Turn on the lights


asyncio.run(main())
```

## API Reference

### AsyncCalderaClient

Main client class for interacting with the spa. All operations must be performed within an async context manager:

```python
async with AsyncCalderaClient(
    email="email@example.com",
    password="password",
    timeout=10.0,  # Optional: request timeout in seconds
    debug=False,  # Optional: enable debug logging
) as spa:
    # All spa operations must be inside this block
    await spa.get_spa_status()
    await spa.set_temperature(102)
    # etc...
```

### Temperature Control

```python
async with spa as client:
    # Set temperature (80-104°F or 26.5-40°C)
    await client.set_temperature(102)  # Fahrenheit
    await client.set_temperature(39, "C")  # Celsius
```

### Pump Control

```python
async with spa as client:
    # Set pump speed
    await client.set_pump(1, PUMP_HIGH)  # Set pump 1 to high speed
    await client.set_pump(2, PUMP_LOW)  # Set pump 2 to low speed
    await client.set_pump(3, PUMP_OFF)  # Turn off pump 3
```

### Light Control

```python
async with spa as client:
    await client.set_lights(True)  # Turn lights on
    await client.set_lights(False)  # Turn lights off
```

### Status & Settings

```python
async with spa as client:
    # Get basic spa status
    status = await client.get_spa_status()
    print(f"Spa name: {status.spaName}")
    print(f"Current temp: {status.ctrl_head_water_temperature}°F")
    print(f"Online: {status.status == 'ONLINE'}")

    # Get detailed live settings
    settings = await client.get_live_settings()
    print(f"Target temp: {settings.ctrl_head_set_temperature}°F")
    print(f"Pump 1 speed: {settings.usr_set_pump1_speed}")
    print(f"Lights on: {settings.usr_set_light_state}")
```

## Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

The pre-commit hooks will run automatically on git commit, checking:
- Code formatting (Black)
- Import sorting (isort)
- Type checking (mypy)
- Linting (pylint, ruff)
- YAML/TOML syntax
- Trailing whitespace and file endings

## License

MIT License - see LICENSE file for details.
