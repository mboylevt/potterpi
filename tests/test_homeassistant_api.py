#!/usr/bin/env python3
"""
Tests for Home Assistant API module
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from potterpi.homeassistant_api import HomeAssistantAPI
from unittest.mock import Mock, patch, MagicMock


class TestHomeAssistantAPI:
    """Test cases for HomeAssistantAPI class"""

    def setup_method(self):
        """Set up test fixture"""
        self.api = HomeAssistantAPI(
            url="http://test.local:8123",
            token="test_token_123"
        )

    def test_initialization(self):
        """Test API initialization"""
        assert self.api.url == "http://test.local:8123"
        assert self.api.headers["Authorization"] == "Bearer test_token_123"
        assert self.api.headers["Content-Type"] == "application/json"

    def test_url_strips_trailing_slash(self):
        """Test that trailing slash is removed from URL"""
        api = HomeAssistantAPI(url="http://test.local:8123/", token="test")
        assert api.url == "http://test.local:8123"

    @patch('potterpi.homeassistant_api.requests.get')
    def test_test_connection_success(self, mock_get):
        """Test successful connection test"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "API running.",
            "version": "2024.1.0"
        }
        mock_get.return_value = mock_response

        result = self.api.test_connection()

        assert result is True
        mock_get.assert_called_once_with(
            "http://test.local:8123/api/",
            headers=self.api.headers,
            timeout=5
        )

    @patch('potterpi.homeassistant_api.requests.get')
    def test_test_connection_failure(self, mock_get):
        """Test failed connection test"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = self.api.test_connection()

        assert result is False

    @patch('potterpi.homeassistant_api.requests.get')
    def test_test_connection_exception(self, mock_get):
        """Test connection test with network exception"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = self.api.test_connection()

        assert result is False

    @patch('potterpi.homeassistant_api.requests.post')
    def test_fire_event_success(self, mock_post):
        """Test successful event firing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        event_data = {"test": "data", "value": 123}
        result = self.api.fire_event("test_event", event_data)

        assert result is True
        mock_post.assert_called_once_with(
            "http://test.local:8123/api/events/test_event",
            headers=self.api.headers,
            json=event_data,
            timeout=5
        )

    @patch('potterpi.homeassistant_api.requests.post')
    def test_fire_event_no_data(self, mock_post):
        """Test firing event without data"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.fire_event("test_event")

        assert result is True
        # Should pass empty dict
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"] == {}

    @patch('potterpi.homeassistant_api.requests.post')
    def test_fire_event_failure(self, mock_post):
        """Test failed event firing"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = self.api.fire_event("test_event", {"data": "test"})

        assert result is False

    @patch('potterpi.homeassistant_api.requests.post')
    def test_call_service_success(self, mock_post):
        """Test successful service call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service_data = {"entity_id": "light.test"}
        result = self.api.call_service("light", "turn_on", service_data)

        assert result is True
        mock_post.assert_called_once_with(
            "http://test.local:8123/api/services/light/turn_on",
            headers=self.api.headers,
            json=service_data,
            timeout=5
        )

    @patch('potterpi.homeassistant_api.requests.post')
    def test_call_service_no_data(self, mock_post):
        """Test service call without data"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.call_service("homeassistant", "restart")

        assert result is True
        call_args = mock_post.call_args
        assert call_args[1]["json"] == {}

    @patch('potterpi.homeassistant_api.requests.get')
    def test_get_states_success(self, mock_get):
        """Test successful states retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"entity_id": "light.test", "state": "on"},
            {"entity_id": "switch.test", "state": "off"}
        ]
        mock_get.return_value = mock_response

        result = self.api.get_states()

        assert result is not None
        assert len(result) == 2
        assert result[0]["entity_id"] == "light.test"

    @patch('potterpi.homeassistant_api.requests.get')
    def test_get_states_failure(self, mock_get):
        """Test failed states retrieval"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = self.api.get_states()

        assert result is None

    @patch.object(HomeAssistantAPI, 'fire_event')
    def test_trigger_spell_action_with_stats(self, mock_fire_event):
        """Test triggering spell action with statistics"""
        mock_fire_event.return_value = True

        spell_stats = {
            "num_points": 25,
            "straightness": 0.87,
            "straight_distance": 145.3
        }

        result = self.api.trigger_spell_action("Horizontal Line Right", spell_stats)

        assert result is True
        mock_fire_event.assert_called_once()

        call_args = mock_fire_event.call_args
        assert call_args[0][0] == "potterpi_spell_cast"

        event_data = call_args[0][1]
        assert event_data["spell"] == "Horizontal Line Right"
        assert event_data["source"] == "potterpi"
        assert event_data["points"] == 25
        assert event_data["straightness"] == 0.87
        assert event_data["distance"] == 145.3

    @patch.object(HomeAssistantAPI, 'fire_event')
    def test_trigger_spell_action_without_stats(self, mock_fire_event):
        """Test triggering spell action without statistics"""
        mock_fire_event.return_value = True

        result = self.api.trigger_spell_action("Vertical Line Up")

        assert result is True
        mock_fire_event.assert_called_once()

        call_args = mock_fire_event.call_args
        event_data = call_args[0][1]
        assert event_data["spell"] == "Vertical Line Up"
        assert event_data["source"] == "potterpi"
        assert "points" not in event_data or event_data["points"] is None

    @patch('potterpi.homeassistant_api.requests.post')
    def test_timeout_handling(self, mock_post):
        """Test that timeouts are properly handled"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Connection timeout")

        result = self.api.fire_event("test_event")

        assert result is False

    @patch('potterpi.homeassistant_api.requests.post')
    def test_connection_error_handling(self, mock_post):
        """Test that connection errors are properly handled"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        result = self.api.call_service("light", "turn_on")

        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
