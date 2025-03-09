"""Synchronous client implementation for Caldera Spa API."""

import asyncio
import logging
from typing import Optional

from .async_client import AsyncCalderaClient
from .const import DEFAULT_TIMEOUT
from .models import AuthResponse, LiveSettings, SpaResponseDato

logger = logging.getLogger(__name__)


class CalderaClient:
    """Synchronous client for interacting with Caldera Spa API."""

    def __init__(
        self,
        email: str,
        password: str,
        timeout: float = DEFAULT_TIMEOUT,
        debug: bool = False,
    ) -> None:
        """Initialize the synchronous Caldera client.

        Args:
            email: Email address for authentication
            password: Password for authentication
            timeout: Request timeout in seconds
            debug: Enable debug logging
        """
        self.email = email
        self.password = password
        self.timeout = timeout
        self.debug = debug
        self._async_client: Optional[AsyncCalderaClient] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _init_async_client(self) -> None:
        """Initialize the async client if not already initialized."""
        if self._async_client is None:
            self._loop = asyncio.new_event_loop()
            self._async_client = AsyncCalderaClient(
                email=self.email,
                password=self.password,
                timeout=self.timeout,
                debug=self.debug,
                loop=self._loop,
            )

    def _run_coroutine(self, coro):
        """Run a coroutine in the event loop.

        Args:
            coro: The coroutine to run

        Returns:
            The result of the coroutine
        """
        self._init_async_client()

        # These assertions help type checking understand that these are not None
        if self._loop is None or self._async_client is None:
            raise RuntimeError("Failed to initialize async client")

        async def wrapped_coro():
            # The assertion above ensures self._async_client is not None
            async with self._async_client:
                return await coro()

        # Create the coroutine object first, then run it
        coroutine_obj = wrapped_coro()
        try:
            return self._loop.run_until_complete(coroutine_obj)
        finally:
            # Make sure to close the event loop properly if we're done
            if coroutine_obj.cr_await is None:
                try:
                    # The assertion above ensures self._async_client is not None
                    self._loop.run_until_complete(
                        self._async_client.__aexit__(None, None, None)
                    )
                    self._loop.close()
                    self._loop = None
                    self._async_client = None
                except Exception:
                    # If we can't close properly, just continue
                    pass

    def authenticate(self) -> AuthResponse:
        """Authenticate with the Caldera API.

        Returns:
            AuthResponse with authentication result

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
        """
        return self._run_coroutine(lambda: self._async_client.authenticate())  # type: ignore[union-attr]

    def get_spa_status(self) -> SpaResponseDato:
        """Get the current status of the spa.

        Returns:
            SpaResponseDato containing current spa state

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            SpaControlError: If the API returns an error
        """
        return self._run_coroutine(lambda: self._async_client.get_spa_status())  # type: ignore[union-attr]

    def get_live_settings(self) -> LiveSettings:
        """Get current live settings from the spa.

        Returns:
            LiveSettings object containing current spa state

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            SpaControlError: If the API returns an error
        """
        return self._run_coroutine(lambda: self._async_client.get_live_settings())  # type: ignore[union-attr]

    def set_temperature(
        self,
        temperature: float,
        unit: str = "F",
        wait_for_ack: bool = False,
        polling_interval: float = 2.0,
        polling_timeout: float = 60.0,
    ) -> bool:
        """Set the target temperature for the spa.

        Args:
            temperature: Target temperature
            unit: Temperature unit ('F' or 'C')
            wait_for_ack: Whether to wait for acknowledgment from the spa
            polling_interval: Time in seconds between polls when waiting for
                acknowledgment
            polling_timeout: Maximum time in seconds to wait for acknowledgment

        Returns:
            bool indicating success

        Raises:
            InvalidParameterError: If temperature is out of valid range
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            SpaControlError: If the API returns an error or acknowledgment times out
        """
        return self._run_coroutine(
            lambda: self._async_client.set_temperature(  # type: ignore[union-attr]
                temperature, unit, wait_for_ack, polling_interval, polling_timeout
            )
        )

    def wait_for_temperature_ack(
        self,
        expected_temp: Optional[float] = None,
        interval: float = 2.0,
        timeout: float = 60.0,
    ) -> LiveSettings:
        """Wait for the spa to acknowledge the temperature setting.

        Args:
            expected_temp: The expected temperature in Fahrenheit (optional)
            interval: Time in seconds between polls
            timeout: Maximum time in seconds to poll before timing out

        Returns:
            LiveSettings object with the acknowledged temperature

        Raises:
            SpaControlError: If acknowledgment times out
        """
        return self._run_coroutine(
            lambda: self._async_client.wait_for_temperature_ack(  # type: ignore[union-attr]
                expected_temp, interval, timeout
            )
        )

    def set_lights(self, state: bool) -> bool:
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
        return self._run_coroutine(lambda: self._async_client.set_lights(state))  # type: ignore[union-attr]

    def set_pump(self, pump_number: int, speed: int) -> bool:
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
        return self._run_coroutine(
            lambda: self._async_client.set_pump(pump_number, speed)  # type: ignore[union-attr]
        )

    def set_temp_lock(self, locked: bool) -> bool:
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
        return self._run_coroutine(lambda: self._async_client.set_temp_lock(locked))  # type: ignore[union-attr]

    def set_spa_lock(self, locked: bool) -> bool:
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
        return self._run_coroutine(lambda: self._async_client.set_spa_lock(locked))  # type: ignore[union-attr]

    def close(self) -> None:
        """Close the client and free any resources."""
        if self._loop and self._async_client:
            try:
                self._loop.run_until_complete(
                    self._async_client.__aexit__(None, None, None)
                )
                self._loop.close()
            except Exception:
                pass
            finally:
                self._loop = None
                self._async_client = None

    def __enter__(self) -> "CalderaClient":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        self.close()
