"""Tests for the synchronous client."""

import unittest
from unittest.mock import MagicMock, patch

from pycaldera.client import CalderaClient
from pycaldera.models import AuthResponse, LiveSettings


class TestCalderaClient(unittest.TestCase):
    """Tests for the synchronous client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = CalderaClient("test@example.com", "password")

    @patch("pycaldera.client.CalderaClient._run_coroutine")
    def test_authenticate(self, mock_run_coroutine):
        """Test authenticate method."""
        auth_response = AuthResponse(
            statusCode=200,
            message="Success",
            data={},
            timeStamp="2023-01-01T00:00:00Z",
            nTime="123456789",
        )

        # Set up the return value for _run_coroutine
        mock_run_coroutine.return_value = auth_response

        # Call the method
        result = self.client.authenticate()

        # Verify the result
        self.assertEqual(result.statusCode, 200)
        self.assertEqual(result.message, "Success")

        # Verify that _run_coroutine was called once
        mock_run_coroutine.assert_called_once()

    @patch("pycaldera.client.CalderaClient._run_coroutine")
    def test_set_temperature(self, mock_run_coroutine):
        """Test set_temperature method."""
        # Set up the return value for _run_coroutine
        mock_run_coroutine.return_value = True

        # Call the method
        result = self.client.set_temperature(100, "F")

        # Verify the result
        self.assertTrue(result)

        # Verify that _run_coroutine was called once
        mock_run_coroutine.assert_called_once()

    @patch("pycaldera.client.CalderaClient._run_coroutine")
    def test_set_lights(self, mock_run_coroutine):
        """Test set_lights method."""
        # Set up the return value for _run_coroutine
        mock_run_coroutine.return_value = True

        # Call the method
        result = self.client.set_lights(True)

        # Verify the result
        self.assertTrue(result)

        # Verify that _run_coroutine was called once
        mock_run_coroutine.assert_called_once()

    @patch("pycaldera.client.CalderaClient.close")
    def test_context_manager(self, mock_close):
        """Test context manager support."""
        # Use the client as a context manager
        with self.client as client:
            # Verify we get the client instance back
            self.assertEqual(client, self.client)

        # Verify close was called
        mock_close.assert_called_once()

    @patch("pycaldera.client.CalderaClient._run_coroutine")
    def test_set_temperature_with_wait(self, mock_run_coroutine):
        """Test setting temperature with wait for acknowledgment."""
        # Set up the return value for _run_coroutine
        mock_run_coroutine.return_value = True

        # Call the method with wait_for_ack=True
        result = self.client.set_temperature(
            temperature=100,
            unit="F",
            wait_for_ack=True,
            polling_interval=1.0,
            polling_timeout=30.0,
        )

        # Verify the result
        self.assertTrue(result)

        # Verify that _run_coroutine was called once
        mock_run_coroutine.assert_called_once()

    @patch("pycaldera.client.CalderaClient._run_coroutine")
    def test_wait_for_temperature_ack(self, mock_run_coroutine):
        """Test waiting for temperature acknowledgment."""
        # Create a mock LiveSettings object to return
        live_settings = MagicMock(spec=LiveSettings)
        live_settings.ctrl_head_water_temperature_ack = "True"
        live_settings.ctrl_head_set_temperature = "100.0"

        # Set up the return value for _run_coroutine
        mock_run_coroutine.return_value = live_settings

        # Call the wait_for_temperature_ack method
        result = self.client.wait_for_temperature_ack(
            expected_temp=100.0, interval=1.0, timeout=30.0
        )

        # Verify the result
        self.assertEqual(result, live_settings)

        # Verify that _run_coroutine was called once
        mock_run_coroutine.assert_called_once()
