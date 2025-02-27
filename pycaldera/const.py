"""Constants for the Caldera Spa API client."""

# API base URL
API_BASE_URL = "https://connectedspa.watkinsmfg.com/connextion"

# Authentication device info
AUTH_DEVICE_TYPE = "IOS"
AUTH_OS_TYPE = "17.4.1"
AUTH_DEVICE_TOKEN = "dummy_token:APA91bDummy0123456789"

# Pump speed constants
PUMP_OFF = 0
PUMP_LOW = 1
PUMP_HIGH = 2

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

# Default request timeout
DEFAULT_TIMEOUT = 10.0
