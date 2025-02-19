"""Async client implementation for Caldera Spa API."""

import json
import logging
from asyncio import AbstractEventLoop
from typing import Any, Optional

import aiohttp
import pydantic
from aiohttp import ClientError, ClientSession

from .exceptions import (
    AuthenticationError,
    ConnectionError,
    InvalidParameterError,
    SpaControlError,
)
from .models import (
    AuthResponse,
    LiveSettings,
    LiveSettingsResponse,
    SpaResponseDato,
    SpaStatusResponse,
)

logger = logging.getLogger(__name__)

# Pump speed constants
PUMP_OFF = 0
PUMP_LOW = 1
PUMP_HIGH = 2


class AsyncCalderaClient:
    """Async client for interacting with Caldera Spa API."""

    BASE_URL = "https://connectedspa.watkinsmfg.com/connextion"

    def __init__(
        self,
        email: str,
        password: str,
        timeout: float = 10.0,
        debug: bool = False,
        session: Optional[ClientSession] = None,
        loop: Optional[AbstractEventLoop] = None,
    ) -> None:
        """Initialize the async Caldera client.

        Args:
            email: Email address for authentication
            password: Password for authentication
            timeout: Request timeout in seconds
            debug: Enable debug logging
            session: Optional aiohttp ClientSession to use
            loop: Optional asyncio event loop to use
        """
        self.email = email
        self.password = password
        self.timeout = timeout
        self._session = session
        self._loop = loop
        self._owns_session = False
        self._token: Optional[str] = None
        self._spa_id: Optional[int] = None
        self._hna_number: Optional[str] = None

        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    async def __aenter__(self) -> "AsyncCalderaClient":
        """Enter async context manager."""
        if self._session is None:
            self._session = aiohttp.ClientSession(loop=self._loop)
            self._owns_session = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager."""
        if self._session and self._owns_session:
            await self._session.close()
            self._session = None

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> tuple[dict[str, Any], dict[str, str]]:
        """Make an async HTTP request to the API.

        Returns:
            Tuple of (response_data, response_headers)
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        url = f"{self.BASE_URL}/{endpoint}"
        kwargs.setdefault("timeout", self.timeout)

        # Add Authorization header if we have a token (except for login)
        if self._token and not endpoint.endswith("auth/login"):
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {self._token}"
            kwargs["headers"] = headers

        try:
            logger.debug(f"Making async {method} request to {url}: {kwargs}")
            async with self._session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                data = await response.json()

                if data.get("statusCode") != 200:
                    raise SpaControlError(f"API error: {data.get('message')}")

                return data, dict(response.headers)

        except aiohttp.ClientResponseError as e:
            if e.status == 401:
                raise AuthenticationError("Authentication failed") from e
            raise ConnectionError(f"HTTP error: {str(e)}") from e

        except ClientError as e:
            raise ConnectionError(f"Connection error: {str(e)}") from e

        except json.JSONDecodeError as e:
            raise ConnectionError(f"Invalid JSON response: {str(e)}") from e

    async def authenticate(self) -> AuthResponse:
        """Authenticate with the Caldera API."""
        logger.info("Authenticating with Caldera API")
        try:
            data, headers = await self._make_request(
                "POST",
                "auth/login",
                json={
                    "emailAddress": self.email,
                    "password": self.password,
                    "deviceType": "IOS",
                    "osType": "17.4.1",
                    "mobileDeviceToken": "dummy_token:APA91bDummy0123456789",
                    "location": "",
                },
            )

            if not self._session:
                raise RuntimeError("Session not initialized")

            logger.debug(f"Authentication response: {json.dumps(data)}")

            token = headers.get("Authorization", "")

            if not token:
                raise AuthenticationError("No authentication token received")

            self._token = token  # Store just the raw token
            logger.debug(f"Received authentication token: {self._token}")
            logger.debug("Authentication successful")
            return AuthResponse(**data)

        except aiohttp.ClientResponseError as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise AuthenticationError("Authentication failed") from e
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise

    async def _ensure_auth(self) -> None:
        """Ensure we have a valid authentication token."""
        if not self._token:
            await self.authenticate()

    async def _ensure_spa_info(self) -> None:
        """Ensure we have the spa ID and HNA number."""
        if not self._hna_number or not self._spa_id:
            status = await self.get_spa_status()
            self._hna_number = status.hnaNumber
            self._spa_id = status.spaId

    def _parse_json_field(self, obj: dict, field_name: str) -> None:
        """Parse a JSON string field and replace it with the parsed object.

        Args:
            obj: Dictionary containing the field to parse
            field_name: Name of the field containing JSON string

        Raises:
            SpaControlError: If JSON parsing fails
        """
        if field_name in obj:
            try:
                json_str = obj[field_name]
                parsed_data = json.loads(json_str)
                obj[field_name] = parsed_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse {field_name}: {e}")
                raise SpaControlError(f"Invalid {field_name} format") from e

    async def get_spa_status(self) -> SpaResponseDato:
        """Get the current status of the spa.

        Returns:
            SpaResponseDato containing current spa state

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            SpaControlError: If the API returns an error
        """
        await self._ensure_auth()

        try:
            data, _ = await self._make_request("POST", "spa/my-spas", json={})
            # logger.debug(f"Spa status response: {json.dumps(data)}")

            # Pre-process the response to parse nested JSON
            if not isinstance(data, dict):
                raise SpaControlError("Invalid response format")

            response_data = data.get("data", {}).get("responseDto", [])
            if not response_data:
                raise SpaControlError("No spa data in response")

            # Parse nested JSON fields for each spa in the response
            for spa in response_data:
                # Parse thingWorxData in spaSettings
                if "spaSettings" in spa:
                    self._parse_json_field(spa["spaSettings"], "thingWorxData")

                # Parse fields in isConnectedData
                if "isConnectedData" in spa:
                    connected_data = spa["isConnectedData"]
                    self._parse_json_field(connected_data, "liveSettings")
                    self._parse_json_field(connected_data, "isDeviceConnected")

            # Now validate with pydantic
            response = SpaStatusResponse(**data)
            return response.data.responseDto[0]

        except aiohttp.ClientResponseError as e:
            logger.error(f"Failed to get spa status: {str(e)}")
            if e.status == 401:
                raise AuthenticationError("Authentication failed") from e
            raise ConnectionError(f"HTTP error: {str(e)}") from e
        except (KeyError, IndexError) as e:
            logger.error(f"Invalid response format: {str(e)}")
            raise SpaControlError("Unexpected API response format") from e
        except pydantic.ValidationError as e:
            logger.error(f"Invalid response data: {str(e)}")
            raise SpaControlError("Invalid spa status data received") from e
        except Exception as e:
            logger.error(f"Failed to get spa status: {str(e)}")
            raise ConnectionError(f"Unexpected error: {str(e)}") from e

    async def get_live_settings(self) -> LiveSettings:
        """Get current live settings from the spa.

        Returns:
            LiveSettings object containing current spa state

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            SpaControlError: If the API returns an error
        """
        await self._ensure_auth()
        await self._ensure_spa_info()

        try:
            data, _ = await self._make_request(
                "GET", "setting/live-spa-settings", params={"hnaNo": self._hna_number}
            )
            logger.debug(f"Live settings response: {json.dumps(data)}")

            # Pre-process the response to parse nested JSON
            if not isinstance(data, dict):
                raise SpaControlError("Invalid response format")

            # Parse the nested JSON string in data field
            self._parse_json_field(data, "data")

            # Now validate with pydantic
            response = LiveSettingsResponse(**data)
            if not response.data.rows:
                raise SpaControlError("No live settings data in response")

            return response.data.rows[0]

        except aiohttp.ClientResponseError as e:
            logger.error(f"Failed to get live settings: {str(e)}")
            if e.status == 401:
                raise AuthenticationError("Authentication failed") from e
            raise ConnectionError(f"HTTP error: {str(e)}") from e
        except pydantic.ValidationError as e:
            logger.error(f"Invalid response data: {str(e)}")
            raise SpaControlError("Invalid spa settings data received") from e
        except Exception as e:
            logger.error(f"Failed to get live settings: {str(e)}")
            raise ConnectionError(f"Unexpected error: {str(e)}") from e

    async def set_temperature(self, temperature: float, unit: str = "F") -> bool:
        """Set the target temperature for the spa.

        Args:
            temperature: Target temperature
            unit: Temperature unit ('F' or 'C')

        Returns:
            bool indicating success

        Raises:
            InvalidParameterError: If temperature is out of valid range
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            SpaControlError: If the API returns an error
        """
        if unit.upper() == "F":
            if not (80 <= temperature <= 104):
                raise InvalidParameterError(
                    "Temperature must be between 80°F and 104°F"
                )
        else:
            if not (26.5 <= temperature <= 40):
                raise InvalidParameterError(
                    "Temperature must be between 26.5°C and 40°C"
                )

        await self._ensure_auth()
        await self._ensure_spa_info()

        # Convert to Fahrenheit if needed
        if unit.upper() == "C":
            temperature = (temperature * 9 / 5) + 32

        # Hypothesize that 65535 is for 104 and 1 degree is 128
        # (based on observing that 102 might be 65280)
        temp_value = min(65535, 65536 - int((104 - temperature) * 128))

        logger.debug(
            f"Temperature encoding:\n"
            f"  Requested: {temperature}°F\n"
            f"  Current method: {temp_value} (0x{temp_value:04X})\n"
        )

        try:
            await self._make_request(
                "POST",
                "setting/send-my-spa-settings-to-thingWorx",
                params={"hnaNo": self._hna_number, "spaTempStatus": 1},
                json={"param": json.dumps({"usr_set_temperature": str(temp_value)})},
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set temperature: {str(e)}")
            raise

    async def set_lights(self, state: bool) -> bool:
        """Turn spa lights on or off.

        Args:
            state: True to turn lights on, False to turn off

        Returns:
            bool indicating success

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            SpaControlError: If the API returns an error
        """
        await self._ensure_auth()
        await self._ensure_spa_info()

        light_value = "1041" if state else "1040"
        logger.info(f"Setting lights {'on' if state else 'off'}")

        try:
            await self._make_request(
                "POST",
                "setting/send-my-spa-settings-to-thingWorx",
                params={"hnaNo": self._hna_number},
                json={"param": json.dumps({"usr_set_mz_light": light_value})},
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set lights: {str(e)}")
            raise

    async def set_pump(self, pump_number: int, speed: int) -> bool:
        """Control a jet pump.

        Args:
            pump_number: Pump number (1-3)
            speed: Pump speed (0=off, 1=low, 2=high)

        Returns:
            bool indicating success

        Raises:
            InvalidParameterError: If pump number or speed is invalid
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            SpaControlError: If the API returns an error
        """
        if not 1 <= pump_number <= 3:
            raise InvalidParameterError("Pump number must be 1, 2, or 3")
        if not 0 <= speed <= 2:
            raise InvalidParameterError("Speed must be 0 (off), 1 (low), or 2 (high)")

        await self._ensure_auth()
        await self._ensure_spa_info()

        param_name = f"usr_set_pump{pump_number}_speed"
        logger.info(f"Setting pump {pump_number} to speed {speed}")

        try:
            await self._make_request(
                "POST",
                "setting/send-my-spa-settings-to-thingWorx",
                params={"hnaNo": self._hna_number},
                json={"param": json.dumps({param_name: str(speed)})},
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set pump: {str(e)}")
            raise

    async def set_temp_lock(self, locked: bool) -> bool:
        """Lock or unlock temperature controls.

        Args:
            locked: True to lock, False to unlock

        Returns:
            bool indicating success

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            SpaControlError: If the API returns an error
        """
        await self._ensure_auth()
        await self._ensure_spa_info()

        logger.info(f"Setting temperature lock to {'locked' if locked else 'unlocked'}")

        try:
            await self._make_request(
                "POST",
                "setting/send-my-spa-settings-to-thingWorx",
                params={"hnaNo": self._hna_number},
                json={
                    "param": json.dumps(
                        {"usr_set_temp_lock_state": "2" if locked else "1"}
                    )
                },
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set temperature lock: {str(e)}")
            raise

    async def set_spa_lock(self, locked: bool) -> bool:
        """Lock or unlock all spa controls.

        Args:
            locked: True to lock, False to unlock

        Returns:
            bool indicating success

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            SpaControlError: If the API returns an error
        """
        await self._ensure_auth()
        await self._ensure_spa_info()

        logger.info(f"Setting spa lock to {'locked' if locked else 'unlocked'}")

        try:
            await self._make_request(
                "POST",
                "setting/send-my-spa-settings-to-thingWorx",
                params={"hnaNo": self._hna_number},
                json={
                    "param": json.dumps(
                        {"usr_set_spa_lock_state": "2" if locked else "1"}
                    )
                },
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set spa lock: {str(e)}")
            raise
