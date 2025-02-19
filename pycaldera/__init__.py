"""Python client for Caldera Spa Connexion API."""

from .async_client import AsyncCalderaClient
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
    "LiveSettings",
    "CalderaError",
    "AuthenticationError",
    "ConnectionError",
    "SpaControlError",
    "InvalidParameterError",
]
__version__ = "0.1.0"
