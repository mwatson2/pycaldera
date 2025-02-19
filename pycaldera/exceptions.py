"""Custom exceptions for the Caldera client."""


class CalderaError(Exception):
    """Base exception for all Caldera client errors."""

    pass


class AuthenticationError(CalderaError):
    """Raised when authentication fails."""

    pass


class ConnectionError(CalderaError):
    """Raised when connection to the spa fails."""

    pass


class SpaControlError(CalderaError):
    """Raised when a control operation fails."""

    pass


class InvalidParameterError(CalderaError):
    """Raised when an invalid parameter is provided."""

    pass
