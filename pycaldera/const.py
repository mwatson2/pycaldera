"""Constants for the Caldera Spa API client."""

# API base URL
API_BASE_URL = "https://connectedspa.watkinsmfg.com/connextion"

# Authentication device info
AUTH_DEVICE_TYPE = "IOS"
AUTH_OS_TYPE = "17.4.1"
AUTH_DEVICE_TOKEN = "dummy_token:APA91bDummy0123456789"

# Pump speed constants (public API values)
PUMP_OFF = 0
PUMP_LOW = 1
PUMP_HIGH = 2

# Internal API wire values (offset by 1 from public constants)
_PUMP_API_OFFSET = 1

# Temperature constraints
MIN_TEMP_F = 80
MAX_TEMP_F = 104
MIN_TEMP_C = 26.5
MAX_TEMP_C = 40

# Light control values
LIGHT_ON = "1041"
LIGHT_OFF = "1040"

# Lock state values
LOCK_DISABLED = "1"
LOCK_ENABLED = "2"

# Temperature encoding constants
TEMP_SCALE = 128  # 1 degree F = 128 units in API value
MAX_TEMP_VALUE = 65535  # Maximum temperature value (104°F)

# Default request timeout.
# The Caldera cloud API is occasionally slow: most requests complete in
# well under a second, but 10+ second responses are not unusual. A tight
# timeout manifests as spurious UpdateFailed cycles in downstream
# integrations, which flips every entity on a spa to unavailable and back
# every few minutes. 30 seconds gives enough headroom for the slow tail
# while still failing fast on a real outage.
DEFAULT_TIMEOUT = 30.0
