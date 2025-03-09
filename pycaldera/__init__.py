"""Python client for Caldera Spa Connexion API."""

from .__meta__ import __version__
from .async_client import AsyncCalderaClient
from .client import CalderaClient
from .const import PUMP_HIGH, PUMP_LOW, PUMP_OFF
from .exceptions import (
    AuthenticationError,
    CalderaError,
    ConnectionError,
    InvalidParameterError,
    SpaControlError,
)
from .models import LiveSettings

__all__ = [
    "AsyncCalderaClient",
    "CalderaClient",
    "LiveSettings",
    "PUMP_OFF",
    "PUMP_LOW",
    "PUMP_HIGH",
    "CalderaError",
    "AuthenticationError",
    "ConnectionError",
    "SpaControlError",
    "InvalidParameterError",
    "__version__",
]
