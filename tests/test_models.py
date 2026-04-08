"""Tests for pycaldera.models convenience properties."""

from unittest.mock import MagicMock

from pycaldera.models import LiveSettings, SpaResponseDato


def _make_live_settings(water_temp: float, set_temp: float) -> LiveSettings:
    """Build a LiveSettings instance with the given temperatures.

    Only the temperature fields are meaningful for these tests; the
    rest are populated with placeholder strings/values that satisfy
    the pydantic schema.
    """
    return LiveSettings(
        ctrl_head_water_temperature=water_temp,
        ctrl_head_set_temperature=set_temp,
        usr_set_temperature="0",
        usr_set_temperature_ack="False",
        ctrl_head_water_temperature_ack="True",
        temp_diff=0.0,
        feature_configuration_degree_celcius="False",
        usr_set_pump1_speed="0",
        usr_set_pump2_speed="0",
        usr_set_pump3_speed="0",
        usr_set_blower="0",
        usr_set_heat_pump="0",
        usr_set_light_state="0",
        usr_set_mz_light="0",
        usr_set_mz_ack="0",
        usr_set_temp_lock_state="1",
        usr_set_spa_lock_state="1",
        usr_set_clean_lock_state="1",
        filter_time_1="0",
        filter_time_2="0",
        usr_set_clean_cycle="0",
        usr_set_stm_state="0",
        audio_power="0",
        audio_source_selection="0",
        usr_set_audio_data="0",
        usr_set_audio_ack="0",
        mz_system_status="0",
        hawk_status_econ="0",
        g3_level2_errors="0",
        g3_clrmtr_test_data="0",
        lls_power_and_ready_ace_err="0",
        usr_set_system_reset="0",
        spa_usage="0",
        usr_spa_usage="0",
        salline_test="0",
        usr_set_tanas_menu_entry="0",
        usr_set_tanas_menu_entry_ack="0",
        usr_set_tanas_menu_entry_test="0",
        usr_set_tanas_menu_entry_boost="0",
        name="test",
        description="test",
        thingTemplate="test",
        tags=[],
    )


def _make_spa_response(rows):
    """Construct a SpaResponseDato with mocked nested structures.

    The convenience properties only touch ``isConnectedData.liveSettings.rows``
    so we mock the rest of the object graph aggressively to keep the
    test focused.
    """
    spa = MagicMock(spec=SpaResponseDato)
    spa.isConnectedData = MagicMock()
    spa.isConnectedData.liveSettings = MagicMock()
    spa.isConnectedData.liveSettings.rows = rows
    # Bind the real properties so they execute against our mock graph.
    spa.water_temperature = SpaResponseDato.water_temperature.fget(spa)
    spa.set_temperature = SpaResponseDato.set_temperature.fget(spa)
    return spa


def test_water_temperature_returns_live_value():
    """water_temperature reads from the first live settings row."""
    rows = [_make_live_settings(water_temp=103.0, set_temp=102.0)]
    spa = _make_spa_response(rows)

    assert spa.water_temperature == 103.0


def test_set_temperature_returns_live_value():
    """set_temperature reads from the first live settings row."""
    rows = [_make_live_settings(water_temp=103.0, set_temp=102.0)]
    spa = _make_spa_response(rows)

    assert spa.set_temperature == 102.0


def test_temperatures_none_when_no_rows():
    """Properties return None when the spa hasn't reported any rows."""
    spa = _make_spa_response(rows=[])

    assert spa.water_temperature is None
    assert spa.set_temperature is None
