"""Data models for Caldera Spa API."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class AuthResponse(BaseModel):
    """Response from authentication endpoint."""

    statusCode: int
    message: str
    data: dict
    timeStamp: str
    nTime: str


class LiveSettings(BaseModel):
    """Live settings from the spa ThingWorx system."""

    # Temperature settings
    ctrl_head_water_temperature: float
    ctrl_head_set_temperature: float
    usr_set_temperature: str
    usr_set_temperature_ack: str
    ctrl_head_water_temperature_ack: str
    temp_diff: float
    feature_configuration_degree_celcius: str

    # Pump settings
    usr_set_pump1_speed: str
    usr_set_pump2_speed: str
    usr_set_pump3_speed: str
    usr_set_blower: str
    usr_set_heat_pump: str

    # Light settings
    usr_set_light_state: str
    usr_set_mz_light: str
    usr_set_mz_ack: str

    # Lock states
    usr_set_temp_lock_state: str
    usr_set_spa_lock_state: str
    usr_set_clean_lock_state: str

    # Filter and cleaning
    filter_time_1: str
    filter_time_2: str
    usr_set_clean_cycle: str
    usr_set_stm_state: str

    # Audio settings
    audio_power: str
    audio_source_selection: str
    usr_set_audio_data: str
    usr_set_audio_ack: str

    # System status
    mz_system_status: str
    hawk_status_econ: str
    g3_level2_errors: str
    g3_clrmtr_test_data: str
    lls_power_and_ready_ace_err: str
    usr_set_system_reset: str

    # Usage tracking
    spa_usage: str
    usr_spa_usage: str
    salline_test: str

    # Menu entries
    usr_set_tanas_menu_entry: str
    usr_set_tanas_menu_entry_ack: str
    usr_set_tanas_menu_entry_test: str
    usr_set_tanas_menu_entry_boost: str

    # Metadata
    name: str
    description: str
    thingTemplate: str
    tags: list[dict[str, str]]


class LiveSettingsFieldDefinition(BaseModel):
    """Definition of a field in live settings."""

    name: str
    description: str = ""
    baseType: str
    ordinal: int
    aspects: dict[str, Any]


class LiveSettingsDataShape(BaseModel):
    """Shape of the live settings data."""

    fieldDefinitions: dict[str, LiveSettingsFieldDefinition]


class LiveSettingsData(BaseModel):
    """Parsed live settings data structure."""

    dataShape: LiveSettingsDataShape
    rows: list[LiveSettings]


class LiveSettingsResponse(BaseModel):
    """Response from the live settings endpoint."""

    statusCode: int
    message: str
    data: LiveSettingsData
    oldUserData: Optional[Any] = None
    timeStamp: str
    nTime: str


class SpaDetails(BaseModel):
    """Details about a specific spa model."""

    Brand: str
    Series: str
    Model: str


class LightSettings(BaseModel):
    """Light configuration for the spa."""

    Lights: bool
    Bartop: bool
    Dimming: str
    Underwater_Main_Light: bool
    Water_Feature: bool
    Lighting_Type: str
    Exterior_Light: bool


class JetPumps(BaseModel):
    """Configuration of jet pumps."""

    Jet_Pump_1: str
    Jet_Pump_2: str
    Jet_Pump_3: str


class OptionalFeatures(BaseModel):
    """Optional spa features."""

    Audio: bool
    CoolZoneTM: bool
    FreshWater_Salt_SystemTM: bool = Field(alias="FreshWater Salt SystemTM")


class SpaConfiguration(BaseModel):
    """Complete spa configuration."""

    Control_Box: str = Field(alias="Control Box")
    Circulation_Pump: str = Field(alias="Circulation Pump")
    SPA_Details: SpaDetails
    JET_PUMPS: JetPumps = Field(alias="JET PUMPS")
    Summer_Timer: str = Field(alias="Summer_Timer")
    Lights: LightSettings
    OPTIONAL_FEATURES: OptionalFeatures = Field(alias="OPTIONAL FEATURES")


class SpaSettings(BaseModel):
    """Settings configuration for the spa."""

    id: int
    thingWorxData: SpaConfiguration  # Changed from str to SpaConfiguration
    tempLock: bool
    spaLock: bool
    filterStatus: Optional[str]
    cleanUpCycle: bool
    summerTimer: bool
    units: Optional[str]
    spaEmailNotification: bool
    promotionEmailNotification: bool
    spaPushNotification: bool
    createdAt: str
    updatedAt: str
    userTempratureUnit: bool
    promotionPushNotification: bool


class DeviceConnectionRow(BaseModel):
    """Single row of device connection data."""

    result: bool


class ThingWorxResponse(BaseModel):
    """Generic ThingWorx response structure."""

    dataShape: dict  # Keep as dict since it's metadata we don't need
    rows: list


class ThingWorxLiveSettings(ThingWorxResponse):
    """Live settings from ThingWorx system."""

    rows: list[LiveSettings]  # Override rows type for live settings


class ThingWorxDeviceConnection(ThingWorxResponse):
    """Device connection status from ThingWorx system."""

    rows: list[DeviceConnectionRow]  # Override rows type for device connection


class IsConnectedData(BaseModel):
    """Connection status data for the spa."""

    liveSettings: ThingWorxLiveSettings
    isDeviceConnected: ThingWorxDeviceConnection


class SpaResponseDato(BaseModel):
    """Individual spa response data."""

    spaId: int
    spaName: str
    spaSerialNumber: str
    hnaNumber: str
    snaNumber: str
    output: Optional[str]
    address: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postalCode: Optional[str]
    status: str
    spaSettings: SpaSettings
    spaTempStatus: int
    installationDate: str
    spaOwnerStatus: str
    invitationMailStatus: str
    isConnectedData: IsConnectedData
    userId: int
    firstName: str
    lastName: str
    emailAddress: str
    userTempratureUnit: bool


class ResponseData(BaseModel):
    """Data field for spa status response."""

    responseDto: list[SpaResponseDato]
    unReadNotificationCount: int


class SpaStatusResponse(BaseModel):
    """Complete response from spa status endpoint."""

    statusCode: int
    message: str
    data: ResponseData
    oldUserData: list
    timeStamp: str
    nTime: str
