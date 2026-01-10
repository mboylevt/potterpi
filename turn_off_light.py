#!/usr/bin/env python3
"""
Quick script to turn off Elgato Key Light via Home Assistant
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from potterpi.homeassistant_api import HomeAssistantAPI

# Home Assistant connection details
HA_URL = "http://192.168.2.103:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiZjI3ZGUyZjJjNGI0ZDQxYmQ4ZTVkYmU4ZmI0NzU1OSIsImlhdCI6MTczNjI3OTc0NCwiZXhwIjoyMDUxNjM5NzQ0fQ.8_vJxvuqGqRFqp4YGVTEGqRQ3nN0fQXlnDQp_Wte_3I"

# Initialize API
api = HomeAssistantAPI(url=HA_URL, token=HA_TOKEN)

# Test connection
print("Testing Home Assistant connection...")
if not api.test_connection():
    print("ERROR: Could not connect to Home Assistant")
    sys.exit(1)

print("Connected to Home Assistant successfully!")

# Get all states to find the Elgato Key Light
print("\nFetching entities...")
states = api.get_states()

if states:
    # Look for Elgato Key Light
    elgato_lights = [s for s in states if 'elgato' in s.get('entity_id', '').lower() or
                     'key light' in s.get('attributes', {}).get('friendly_name', '').lower()]

    if elgato_lights:
        print("\nFound Elgato Key Light entities:")
        for light in elgato_lights:
            entity_id = light['entity_id']
            name = light['attributes'].get('friendly_name', entity_id)
            state = light['state']
            print(f"  - {entity_id} ({name}): {state}")

            # Turn off the light
            if state == 'on':
                print(f"\nTurning off {name}...")
                result = api.call_service('light', 'turn_off', {'entity_id': entity_id})
                if result:
                    print(f"✓ Successfully turned off {name}")
                else:
                    print(f"✗ Failed to turn off {name}")
            else:
                print(f"\n{name} is already off")
    else:
        print("\nNo Elgato Key Light found. Searching for all light entities...")
        lights = [s for s in states if s.get('entity_id', '').startswith('light.')]
        print(f"\nFound {len(lights)} light entities:")
        for light in lights[:10]:  # Show first 10
            entity_id = light['entity_id']
            name = light['attributes'].get('friendly_name', entity_id)
            state = light['state']
            print(f"  - {entity_id} ({name}): {state}")
else:
    print("Could not retrieve states from Home Assistant")
