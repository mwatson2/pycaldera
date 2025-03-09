"""Tests for the synchronous client."""

import unittest
from unittest.mock import MagicMock, patch

from pycaldera.client import CalderaClient
from pycaldera.models import AuthResponse


class TestCalderaClient(unittest.TestCase):
    """Tests for the synchronous client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = CalderaClient("test@example.com", "password")

    @patch("pycaldera.client.AsyncCalderaClient")
    @patch("pycaldera.client.asyncio.new_event_loop")
    def test_authenticate(self, mock_new_loop, mock_async_client):
        """Test authenticate method."""
        # Setup mocks
        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop

        mock_instance = MagicMock()
        mock_async_client.return_value = mock_instance

        auth_response = AuthResponse(
            statusCode=200,
            message="Success",
            data={},
            timeStamp="2023-01-01T00:00:00Z",
            nTime="123456789",
        )

        # Set up the return value for run_until_complete
        mock_loop.run_until_complete.return_value = auth_response

        # Call the method
        result = self.client.authenticate()

        # Verify the result
        self.assertEqual(result.statusCode, 200)
        self.assertEqual(result.message, "Success")

        # The implementation should call run_until_complete twice
        # (once for the method and once for cleanup)
        self.assertEqual(2, mock_loop.run_until_complete.call_count)

    @patch("pycaldera.client.AsyncCalderaClient")
    @patch("pycaldera.client.asyncio.new_event_loop")
    def test_set_temperature(self, mock_new_loop, mock_async_client):
        """Test set_temperature method."""
        # Setup mocks
        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop

        mock_instance = MagicMock()
        mock_async_client.return_value = mock_instance

        # Set up the return value for run_until_complete
        mock_loop.run_until_complete.return_value = True

        # Call the method
        result = self.client.set_temperature(100, "F")

        # Verify the result
        self.assertTrue(result)

        # The implementation should call run_until_complete twice
        # (once for the method and once for cleanup)
        self.assertEqual(2, mock_loop.run_until_complete.call_count)

    @patch("pycaldera.client.AsyncCalderaClient")
    @patch("pycaldera.client.asyncio.new_event_loop")
    def test_set_lights(self, mock_new_loop, mock_async_client):
        """Test set_lights method."""
        # Setup mocks
        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop

        mock_instance = MagicMock()
        mock_async_client.return_value = mock_instance

        # Set up the return value for run_until_complete
        mock_loop.run_until_complete.return_value = True

        # Call the method
        result = self.client.set_lights(True)

        # Verify the result
        self.assertTrue(result)

        # The implementation should call run_until_complete twice
        # (once for the method and once for cleanup)
        self.assertEqual(2, mock_loop.run_until_complete.call_count)

    @patch("pycaldera.client.CalderaClient.close")
    def test_context_manager(self, mock_close):
        """Test context manager support."""
        # Use the client as a context manager
        with self.client as client:
            # Verify we get the client instance back
            self.assertEqual(client, self.client)

        # Verify close was called
        mock_close.assert_called_once()
