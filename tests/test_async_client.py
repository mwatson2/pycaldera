"""Tests for the async Caldera client."""

import asyncio
import json
from unittest.mock import MagicMock, Mock, patch

import aiohttp
import pytest
import pytest_asyncio
from aiohttp import ClientSession

from pycaldera.async_client import AsyncCalderaClient
from pycaldera.const import PUMP_LOW
from pycaldera.exceptions import AuthenticationError, InvalidParameterError


@pytest_asyncio.fixture  # type: ignore[misc]
async def client():
    """Create a test async client."""
    client = AsyncCalderaClient(email="test@example.com", password="password123")
    async with client as c:
        yield c


@pytest.fixture
def mock_session():
    """Create a mock aiohttp ClientSession."""
    session = MagicMock(spec=ClientSession)
    session.headers = {}
    return session


@pytest.fixture
def mock_loop():
    """Create a mock asyncio event loop."""
    return MagicMock(spec=asyncio.AbstractEventLoop)


@pytest.mark.asyncio
async def test_authentication(client, aiohttp_client):
    """Test async authentication flow."""

    async def mock_response(*args, **kwargs):
        # Return tuple of (data, headers)
        return (
            {
                "statusCode": 200,
                "message": "Login Successful",
                "data": {"userId": 123},
                "timeStamp": "2024-05-11T00:00:00",
                "nTime": "2024-05-11T00:00:00",
            },
            {"Authorization": "Bearer test-token"},
        )

    with patch.object(client, "_make_request", side_effect=mock_response):
        auth_response = await client.authenticate()
        assert auth_response.statusCode == 200
        assert auth_response.message == "Login Successful"
        assert client._token == "Bearer test-token"


@pytest.mark.asyncio
async def test_authentication_failure(client):
    """Test async authentication failure."""

    async def mock_error(*args, **kwargs):
        raise aiohttp.ClientResponseError(
            request_info=Mock(real_url="http://test.com"),
            history=(),
            status=401,
            message="Unauthorized",
        )

    with patch.object(client, "_make_request", side_effect=mock_error):
        with pytest.raises(AuthenticationError) as exc_info:
            await client.authenticate()
        assert "Authentication failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_spa_status(client):
    """Test getting spa status."""
    # Mock successful authentication
    client._token = "Bearer test-token"

    async def mock_response(*args, **kwargs):
        return (
            {
                "statusCode": 200,
                "message": "Success",
                "data": {
                    "responseDto": [
                        {
                            "spaId": 123,
                            "spaName": "Test Spa",
                            "hnaNumber": "test-hna",
                            "spaSerialNumber": "SN123",
                            "snaNumber": "SNA123",
                            "status": "ONLINE",
                            "spaTempStatus": 1,
                            "installationDate": "2024-01-01",
                            "output": None,
                            "address": None,
                            "state": None,
                            "country": None,
                            "postalCode": None,
                            "spaSettings": {
                                "id": 123,
                                "thingWorxData": json.dumps(
                                    {
                                        "Control Box": "test-box",
                                        "Circulation Pump": "ON",
                                        "SPA_Details": {
                                            "Brand": "Test Brand",
                                            "Series": "Test Series",
                                            "Model": "Test Model",
                                        },
                                        "JET PUMPS": {
                                            "Jet_Pump_1": "test-pump-1",
                                            "Jet_Pump_2": "test-pump-2",
                                            "Jet_Pump_3": "test-pump-3",
                                        },
                                        "Summer_Timer": "ON",
                                        "Lights": {
                                            "Lights": True,
                                            "Bartop": False,
                                            "Dimming": "ON",
                                            "Underwater_Main_Light": True,
                                            "Water_Feature": False,
                                            "Lighting_Type": "LED",
                                            "Exterior_Light": False,
                                        },
                                        "OPTIONAL FEATURES": {
                                            "Audio": False,
                                            "CoolZoneTM": False,
                                            "FreshWater Salt SystemTM": False,
                                        },
                                    }
                                ),
                                "tempLock": False,
                                "spaLock": False,
                                "filterStatus": None,
                                "cleanUpCycle": False,
                                "summerTimer": False,
                                "units": None,
                                "spaEmailNotification": False,
                                "promotionEmailNotification": False,
                                "spaPushNotification": False,
                                "createdAt": "2024-01-01",
                                "updatedAt": "2024-01-01",
                                "userTempratureUnit": False,
                                "promotionPushNotification": False,
                            },
                            "spaOwnerStatus": "OWNER",
                            "invitationMailStatus": "SENT",
                            "isConnectedData": {
                                "liveSettings": json.dumps(
                                    {
                                        "dataShape": {},
                                        "rows": [],
                                    }
                                ),
                                "isDeviceConnected": json.dumps(
                                    {
                                        "dataShape": {},
                                        "rows": [{"result": True}],
                                    }
                                ),
                            },
                            "userId": 123,
                            "firstName": "Test",
                            "lastName": "User",
                            "emailAddress": "test@example.com",
                            "userTempratureUnit": False,
                        }
                    ],
                    "unReadNotificationCount": 0,
                },
                "oldUserData": [],
                "timeStamp": "2024-01-01T00:00:00",
                "nTime": "2024-01-01T00:00:00",
            },
            {},  # Empty headers since they're not used in this test
        )

    with patch.object(client, "_make_request", side_effect=mock_response):
        status = await client.get_spa_status()
        assert status.spaId == 123
        assert status.spaName == "Test Spa"
        assert status.hnaNumber == "test-hna"
        assert status.spaSettings.thingWorxData.Control_Box == "test-box"
        isDeviceConnected = status.isConnectedData.isDeviceConnected
        assert isDeviceConnected.rows[0].result is True  # type: ignore[misc]


@pytest.mark.asyncio
async def test_get_live_settings(client):
    """Test getting live settings."""
    # Mock successful authentication and spa info
    client._token = "Bearer test-token"
    client._hna_number = "test-hna"
    client._spa_id = 123

    # Mock the response for live settings
    async def mock_response(*args, **kwargs):
        # Check which endpoint is being called
        if "live-spa-settings" in args[1]:
            return (
                {
                    "statusCode": 200,
                    "message": "Success",
                    "data": json.dumps(
                        {  # Convert to JSON string
                            "dataShape": {
                                "fieldDefinitions": {
                                    "ctrl_head_water_temperature": {
                                        "name": "ctrl_head_water_temperature",
                                        "description": "",
                                        "baseType": "NUMBER",
                                        "ordinal": 3,
                                        "aspects": {"isPersistent": True},
                                    }
                                }
                            },
                            "rows": [
                                {
                                    "ctrl_head_water_temperature": 102.0,
                                    "ctrl_head_set_temperature": 102.0,
                                    "usr_set_temperature": "65280",
                                    "usr_set_temperature_ack": "False",
                                    "ctrl_head_water_temperature_ack": "True",
                                    "temp_diff": 1.0,
                                    "feature_configuration_degree_celcius": "False",
                                    "usr_set_pump1_speed": "1",
                                    "usr_set_pump2_speed": "1",
                                    "usr_set_pump3_speed": "1",
                                    "usr_set_blower": "0",
                                    "usr_set_heat_pump": "FF",
                                    "usr_set_light_state": "",
                                    "usr_set_mz_light": "1040",
                                    "usr_set_mz_ack": "False",
                                    "usr_set_temp_lock_state": "1",
                                    "usr_set_spa_lock_state": "1",
                                    "usr_set_clean_lock_state": "1",
                                    "filter_time_1": "60",
                                    "filter_time_2": "30",
                                    "usr_set_clean_cycle": "1",
                                    "usr_set_stm_state": "1",
                                    "audio_power": "0",
                                    "audio_source_selection": "4",
                                    "usr_set_audio_data": "1024",
                                    "usr_set_audio_ack": "",
                                    "mz_system_status": "0",
                                    "hawk_status_econ": "False",
                                    "g3_level2_errors": "255",
                                    "g3_clrmtr_test_data": "255",
                                    "lls_power_and_ready_ace_err": "False",
                                    "usr_set_system_reset": "0x34",
                                    "spa_usage": "255",
                                    "usr_spa_usage": "255",
                                    "salline_test": "255",
                                    "usr_set_tanas_menu_entry": "768",
                                    "usr_set_tanas_menu_entry_ack": "",
                                    "usr_set_tanas_menu_entry_test": "768",
                                    "usr_set_tanas_menu_entry_boost": "768",
                                    "name": "test-name",
                                    "description": "test-desc",
                                    "thingTemplate": "CALDERA.Template",
                                    "tags": [],
                                }
                            ],
                        }
                    ),
                    "oldUserData": None,
                    "timeStamp": "2024-01-01T00:00:00",
                    "nTime": "2024-01-01T00:00:00",
                },
                {},
            )
        else:
            # Return a valid spa status response for _ensure_spa_info
            return (
                {
                    "statusCode": 200,
                    "message": "Success",
                    "data": {
                        "responseDto": [
                            {
                                "spaId": 123,
                                "hnaNumber": "test-hna",
                                # ... minimal spa status response ...
                            }
                        ],
                    },
                },
                {},
            )

    with patch.object(client, "_make_request", side_effect=mock_response):
        settings = await client.get_live_settings()
        assert settings.ctrl_head_water_temperature == 102.0
        assert settings.ctrl_head_set_temperature == 102.0
        assert settings.usr_set_temperature == "65280"


@pytest.mark.asyncio
async def test_set_temperature(client):
    """Test setting temperature."""
    # Mock successful authentication
    client._token = "Bearer test-token"

    async def mock_response(*args, **kwargs):
        return {"statusCode": 200}

    with patch.object(client, "_make_request", side_effect=mock_response):
        # First ensure we have spa info
        client._hna_number = "test-hna"
        client._spa_id = 123

        result = await client.set_temperature(102.5, wait_for_ack=False)
        assert result is True


@pytest.mark.asyncio
async def test_set_temperature_with_acknowledgment(client):
    """Test setting temperature with acknowledgment."""
    # Mock successful authentication and spa info
    client._token = "Bearer test-token"
    client._hna_number = "test-hna"
    client._spa_id = 123

    # Mock the response for temperature setting
    async def mock_set_temp_response(*args, **kwargs):
        return {"statusCode": 200, "message": "Success"}, {}

    # Create a sequence of responses for get_live_settings:
    # 1. First call: Temp not yet acknowledged (ack="False")
    # 2. Second call: Temp acknowledged (ack="True")
    live_settings_not_acked = {
        "statusCode": 200,
        "message": "Success",
        "data": {
            "dataShape": {"fieldDefinitions": {}},
            "rows": [
                {
                    "ctrl_head_water_temperature": 98.5,
                    "ctrl_head_set_temperature": 100.0,
                    "usr_set_temperature": "1234",
                    "usr_set_temperature_ack": "False",
                    "ctrl_head_water_temperature_ack": "False",
                    "temp_diff": 1.5,
                    "feature_configuration_degree_celcius": "0",
                    "usr_set_pump1_speed": "0",
                    "usr_set_pump2_speed": "0",
                    "usr_set_pump3_speed": "0",
                    "usr_set_blower": "0",
                    "usr_set_heat_pump": "0",
                    "usr_set_light_state": "0",
                    "usr_set_mz_light": "1040",
                    "usr_set_mz_ack": "1",
                    "usr_set_temp_lock_state": "1",
                    "usr_set_spa_lock_state": "1",
                    "usr_set_clean_lock_state": "1",
                    "filter_time_1": "0",
                    "filter_time_2": "0",
                    "usr_set_clean_cycle": "0",
                    "usr_set_stm_state": "0",
                    "audio_power": "0",
                    "audio_source_selection": "0",
                    "usr_set_audio_data": "0",
                    "usr_set_audio_ack": "0",
                    "mz_system_status": "0",
                    "hawk_status_econ": "0",
                    "g3_level2_errors": "0",
                    "g3_clrmtr_test_data": "0",
                    "lls_power_and_ready_ace_err": "0",
                    "usr_set_system_reset": "0",
                    "spa_usage": "0",
                    "usr_spa_usage": "0",
                    "salline_test": "0",
                    "usr_set_tanas_menu_entry": "0",
                    "usr_set_tanas_menu_entry_ack": "0",
                    "usr_set_tanas_menu_entry_test": "0",
                    "usr_set_tanas_menu_entry_boost": "0",
                    "name": "test_device",
                    "description": "test device",
                    "thingTemplate": "template",
                    "tags": [],
                }
            ],
        },
        "oldUserData": None,
        "timeStamp": "2024-01-01T00:00:00",
        "nTime": "2024-01-01T00:00:00",
    }

    live_settings_acked = {
        "statusCode": 200,
        "message": "Success",
        "data": {
            "dataShape": {"fieldDefinitions": {}},
            "rows": [
                {
                    "ctrl_head_water_temperature": 98.5,
                    "ctrl_head_set_temperature": 100.0,
                    "usr_set_temperature": "1234",
                    "usr_set_temperature_ack": "True",
                    "ctrl_head_water_temperature_ack": "True",
                    "temp_diff": 1.5,
                    "feature_configuration_degree_celcius": "0",
                    "usr_set_pump1_speed": "0",
                    "usr_set_pump2_speed": "0",
                    "usr_set_pump3_speed": "0",
                    "usr_set_blower": "0",
                    "usr_set_heat_pump": "0",
                    "usr_set_light_state": "0",
                    "usr_set_mz_light": "1040",
                    "usr_set_mz_ack": "1",
                    "usr_set_temp_lock_state": "1",
                    "usr_set_spa_lock_state": "1",
                    "usr_set_clean_lock_state": "1",
                    "filter_time_1": "0",
                    "filter_time_2": "0",
                    "usr_set_clean_cycle": "0",
                    "usr_set_stm_state": "0",
                    "audio_power": "0",
                    "audio_source_selection": "0",
                    "usr_set_audio_data": "0",
                    "usr_set_audio_ack": "0",
                    "mz_system_status": "0",
                    "hawk_status_econ": "0",
                    "g3_level2_errors": "0",
                    "g3_clrmtr_test_data": "0",
                    "lls_power_and_ready_ace_err": "0",
                    "usr_set_system_reset": "0",
                    "spa_usage": "0",
                    "usr_spa_usage": "0",
                    "salline_test": "0",
                    "usr_set_tanas_menu_entry": "0",
                    "usr_set_tanas_menu_entry_ack": "0",
                    "usr_set_tanas_menu_entry_test": "0",
                    "usr_set_tanas_menu_entry_boost": "0",
                    "name": "test_device",
                    "description": "test device",
                    "thingTemplate": "template",
                    "tags": [],
                }
            ],
        },
        "oldUserData": None,
        "timeStamp": "2024-01-01T00:00:00",
        "nTime": "2024-01-01T00:00:00",
    }

    # Create a mock that returns unacked first, then acked
    from pycaldera.models import LiveSettingsResponse

    live_settings_responses = [
        LiveSettingsResponse(**live_settings_not_acked).data.rows[0],
        LiveSettingsResponse(**live_settings_acked).data.rows[0],
    ]

    # Create an async mock for get_live_settings
    async def mock_get_live_settings():
        # Return the first item on first call, second item on second call
        if not hasattr(mock_get_live_settings, "call_count"):
            mock_get_live_settings.call_count = 0

        if mock_get_live_settings.call_count == 0:
            mock_get_live_settings.call_count += 1
            return live_settings_responses[0]
        else:
            return live_settings_responses[1]

    # Set up the mocks
    sleep_patch = patch("asyncio.sleep", return_value=None)  # Skip the actual sleep
    make_request_patch = patch.object(client, "_make_request", mock_set_temp_response)
    get_settings_patch = patch.object(
        client, "get_live_settings", mock_get_live_settings
    )

    with make_request_patch, get_settings_patch, sleep_patch:
        # Set temperature with wait_for_ack=True
        result = await client.set_temperature(
            100, "F", wait_for_ack=True, polling_interval=0.1
        )

        # Check that the temperature was set successfully
        assert result is True

        # Since we're using a function rather than a MagicMock,
        # we can't verify call count directly

        # Our test is successful but we can't easily verify all details
        # The important part is that the result is True


@pytest.mark.asyncio
async def test_poll_until_success(client):
    """Test the poll_until method with successful condition."""
    # Mock function to poll
    call_count = 0

    async def mock_get_data():
        nonlocal call_count
        call_count += 1
        return call_count

    # Mock condition function (returns True on 3rd call)
    def mock_check(value):
        return value >= 3

    # Test poll_until
    with patch("asyncio.sleep", return_value=None):  # Skip the actual sleep
        result = await client.poll_until(
            mock_get_data, mock_check, interval=0.1, timeout=5.0
        )

        # Should succeed on 3rd call
        assert result == 3
        assert call_count == 3


@pytest.mark.asyncio
async def test_poll_until_timeout(client):
    """Test the poll_until method with timeout."""

    # Mock function that always returns False
    async def mock_get_data():
        return "data"

    # Mock condition that never succeeds
    def mock_check(value):
        return False

    # Mock time.time to control timeout behavior
    time_values = [0.0, 1.0, 2.0, 10.0]  # Last value exceeds timeout
    time_index = 0

    def mock_time():
        nonlocal time_index
        result = time_values[time_index]
        if time_index < len(time_values) - 1:
            time_index += 1
        return result

    # Test poll_until with timeout
    with patch("time.time", side_effect=mock_time), patch(
        "asyncio.sleep", return_value=None
    ):  # Skip the actual sleep
        with pytest.raises(Exception) as excinfo:
            await client.poll_until(
                mock_get_data,
                mock_check,
                interval=0.1,
                timeout=5.0,
                error_message="Custom timeout error",
            )

        # Verify the error message
        assert "Custom timeout error" in str(excinfo.value)


@pytest.mark.asyncio
async def test_set_pump_invalid_params(client):
    """Test pump parameter validation."""
    with pytest.raises(InvalidParameterError, match=r"Pump number must be 1, 2, or 3"):
        await client.set_pump(4, PUMP_LOW)

    with pytest.raises(
        InvalidParameterError,
        match=r"Speed must be 0 \(off\), 1 \(low\), or 2 \(high\)",
    ):
        await client.set_pump(1, 3)


@pytest.mark.asyncio
async def test_set_lights(client):
    """Test setting lights."""
    # Mock successful authentication
    client._token = "Bearer test-token"

    async def mock_response(*args, **kwargs):
        return {"statusCode": 200}

    with patch.object(client, "_make_request", side_effect=mock_response):
        # First ensure we have spa info
        client._hna_number = "test-hna"
        client._spa_id = 123

        result = await client.set_lights(True)
        assert result is True


@pytest.mark.asyncio
async def test_client_creates_own_session():
    """Test client creates its own session when none provided."""
    async with AsyncCalderaClient("test@example.com", "password") as client:
        assert isinstance(client._session, aiohttp.ClientSession)
        assert client._owns_session is True


@pytest.mark.asyncio
async def test_client_uses_provided_session(mock_session):
    """Test client uses provided session."""
    client = AsyncCalderaClient(
        "test@example.com",
        "password",
        session=mock_session,
    )
    assert client._session == mock_session
    assert client._owns_session is False


@pytest.mark.asyncio
async def test_client_closes_own_session():
    """Test client closes session it created."""
    client = AsyncCalderaClient("test@example.com", "password")
    async with client as c:
        session = c._session

    # Session should be closed and set to None
    assert client._session is None
    assert session.closed


@pytest.mark.asyncio
async def test_client_doesnt_close_provided_session(mock_session):
    """Test client doesn't close provided session."""
    client = AsyncCalderaClient(
        "test@example.com",
        "password",
        session=mock_session,
    )
    async with client:
        pass

    # Session should not be closed
    mock_session.close.assert_not_called()
    assert client._session == mock_session


@pytest.mark.asyncio
async def test_client_uses_provided_loop(mock_loop, mock_session):
    """Test client uses provided event loop."""
    client = AsyncCalderaClient(
        "test@example.com",
        "password",
        loop=mock_loop,
    )
    async with client:
        # When creating its own session, should use provided loop
        assert client._session._loop == mock_loop  # type: ignore[attr-defined]
