#!/usr/bin/env python3
"""
Home Assistant API integration for PotterPi
Triggers Home Assistant services when spells are detected
"""

import requests
import json
import logging
from typing import Dict, Optional

# Set up module-level logger
logger = logging.getLogger("PotterPi")

class HomeAssistantAPI:
    """Interface to Home Assistant REST API"""

    def __init__(self, url: str, token: str, spell_actions: Optional[Dict] = None):
        """
        Initialize Home Assistant API client

        Args:
            url: Base URL of Home Assistant (e.g., "http://192.168.2.103:8123")
            token: Long-lived access token
            spell_actions: Optional dict mapping spell names to HA service calls
        """
        self.url = url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.spell_actions = spell_actions or {}
        logger.info(f"HomeAssistantAPI initialized for {self.url}")
        if self.spell_actions:
            logger.info(f"Loaded {len(self.spell_actions)} spell action mappings")
    
    def test_connection(self) -> bool:
        """
        Test connection to Home Assistant

        Returns:
            bool: True if connection successful
        """
        logger.info("Testing connection to Home Assistant...")
        try:
            response = requests.get(
                f"{self.url}/api/",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Connected to Home Assistant v{data.get('version', 'unknown')}")
                logger.debug(f"HA Response: {data.get('message', 'N/A')}")
                return True
            else:
                logger.error(f"Connection failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def fire_event(self, event_type: str, event_data: Optional[Dict] = None) -> bool:
        """
        Fire a custom event in Home Assistant

        Args:
            event_type: Name of the event (e.g., "potterpi_spell_cast")
            event_data: Optional data to include with event

        Returns:
            bool: True if successful
        """
        logger.debug(f"Firing event '{event_type}' with data: {event_data}")
        try:
            url = f"{self.url}/api/events/{event_type}"
            response = requests.post(
                url,
                headers=self.headers,
                json=event_data or {},
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Successfully fired event: {event_type}")
                return True
            else:
                logger.error(f"Failed to fire event {event_type}: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error firing event {event_type}: {e}")
            return False
    
    def call_service(self, domain: str, service: str, service_data: Optional[Dict] = None) -> bool:
        """
        Call a Home Assistant service

        Args:
            domain: Service domain (e.g., "light", "switch", "notify")
            service: Service name (e.g., "turn_on", "turn_off")
            service_data: Optional service parameters

        Returns:
            bool: True if successful
        """
        logger.debug(f"Calling service {domain}.{service} with data: {service_data}")
        try:
            url = f"{self.url}/api/services/{domain}/{service}"
            response = requests.post(
                url,
                headers=self.headers,
                json=service_data or {},
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Successfully called service: {domain}.{service}")
                return True
            else:
                logger.error(f"Failed to call service {domain}.{service}: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling service {domain}.{service}: {e}")
            return False
    
    def get_states(self) -> Optional[list]:
        """
        Get all entity states from Home Assistant

        Returns:
            list: List of entity states, or None on error
        """
        logger.debug("Fetching all entity states from Home Assistant")
        try:
            response = requests.get(
                f"{self.url}/api/states",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                states = response.json()
                logger.debug(f"Successfully retrieved {len(states)} entity states")
                return states
            else:
                logger.error(f"Failed to get states: HTTP {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting states: {e}")
            return None
    
    def trigger_spell_action(self, spell_name: str, spell_stats: Optional[Dict] = None) -> bool:
        """
        Trigger a spell action in Home Assistant
        If spell has a configured action, calls the service; otherwise fires an event

        Args:
            spell_name: Name of the spell that was cast
            spell_stats: Optional statistics about the spell

        Returns:
            bool: True if successful
        """
        logger.info(f"Triggering Home Assistant action for spell: {spell_name}")

        # Check if this spell has a configured action
        if spell_name in self.spell_actions:
            action = self.spell_actions[spell_name]
            domain = action.get("domain")
            service = action.get("service")
            entity_id = action.get("entity_id")

            if domain and service and entity_id:
                logger.info(f"Calling {domain}.{service} for {entity_id}")
                service_data = {"entity_id": entity_id}
                success = self.call_service(domain, service, service_data)

                # Also fire event for logging/automation purposes
                event_data = {
                    "spell": spell_name,
                    "source": "potterpi",
                    "action": f"{domain}.{service}",
                    "entity_id": entity_id
                }
                if spell_stats:
                    event_data.update({
                        "points": spell_stats.get("num_points"),
                        "straightness": spell_stats.get("straightness"),
                        "distance": spell_stats.get("straight_distance")
                    })
                self.fire_event("potterpi_spell_cast", event_data)

                return success
            else:
                logger.error(f"Invalid spell action config for {spell_name}: {action}")
                return False
        else:
            # No configured action - just fire event
            event_data = {
                "spell": spell_name,
                "source": "potterpi"
            }

            if spell_stats:
                event_data.update({
                    "points": spell_stats.get("num_points"),
                    "straightness": spell_stats.get("straightness"),
                    "distance": spell_stats.get("straight_distance")
                })

            return self.fire_event("potterpi_spell_cast", event_data)


def test_api():
    """Test the Home Assistant API"""
    import os
    
    # Load credentials from environment or config file
    ha_url = os.environ.get("HA_URL", "http://192.168.2.103:8123")
    ha_token = os.environ.get("HA_TOKEN")
    
    if not ha_token:
        print("ERROR: No Home Assistant token found!")
        print("\nTo create a long-lived access token:")
        print("1. Open Home Assistant in your browser")
        print("2. Click your profile (bottom left)")
        print("3. Scroll down to 'Long-Lived Access Tokens'")
        print("4. Click 'Create Token'")
        print("5. Give it a name like 'PotterPi'")
        print("6. Copy the token and set it:")
        print(f"   export HA_TOKEN='your-token-here'")
        print("\nThen run this test again.")
        return
    
    print(f"Testing connection to Home Assistant at {ha_url}...")
    api = HomeAssistantAPI(ha_url, ha_token)
    
    # Test connection
    if not api.test_connection():
        print("\nConnection test FAILED!")
        return
    
    print("\n" + "="*50)
    print("Connection test PASSED!")
    print("="*50)
    
    # Test firing a spell event
    print("\nTesting spell event...")
    test_stats = {
        "num_points": 25,
        "straightness": 0.87,
        "straight_distance": 145.3
    }
    
    success = api.trigger_spell_action("Horizontal Line Right", test_stats)
    if success:
        print("✓ Successfully fired spell event!")
        print("\nYou can create automations in Home Assistant that trigger on:")
        print("  Event type: potterpi_spell_cast")
        print("  Event data: spell, source, points, straightness, distance")
    else:
        print("✗ Failed to fire spell event")
    
    # List some entities
    print("\nFetching entities from Home Assistant...")
    states = api.get_states()
    if states:
        print(f"Found {len(states)} entities")
        print("\nFirst 5 entities:")
        for state in states[:5]:
            entity_id = state.get('entity_id', 'unknown')
            friendly_name = state.get('attributes', {}).get('friendly_name', entity_id)
            current_state = state.get('state', 'unknown')
            print(f"  - {entity_id} ({friendly_name}): {current_state}")
    
    print("\n" + "="*50)
    print("Home Assistant API test complete!")
    print("="*50)


if __name__ == "__main__":
    test_api()
