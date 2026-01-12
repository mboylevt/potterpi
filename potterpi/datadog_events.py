#!/usr/bin/env python3
"""
Datadog event logging integration for PotterPi
Sends custom events to Datadog for monitoring and alerting
"""

import logging
from typing import Dict, Optional

# Set up module-level logger
logger = logging.getLogger("PotterPi")

# Try to import datadog - make it optional
try:
    from datadog import api, initialize
    DATADOG_AVAILABLE = True
except ImportError:
    DATADOG_AVAILABLE = False
    logger.warning("Datadog library not available - events will not be sent")


class DatadogEvents:
    """Send events to Datadog for monitoring"""

    def __init__(self, api_key: Optional[str] = None, app_key: Optional[str] = None, enabled: bool = True):
        """
        Initialize Datadog events client

        Args:
            api_key: Datadog API key (optional, can use DD_API_KEY env var)
            app_key: Datadog APP key (optional, can use DD_APP_KEY env var)
            enabled: Whether to actually send events (default True)
        """
        self.enabled = enabled and DATADOG_AVAILABLE

        if not DATADOG_AVAILABLE:
            logger.info("Datadog integration disabled - library not installed")
            return

        if not self.enabled:
            logger.info("Datadog events disabled by configuration")
            return

        # Initialize datadog
        try:
            options = {}
            if api_key:
                options['api_key'] = api_key
            if app_key:
                options['app_key'] = app_key

            initialize(**options)
            logger.info("Datadog events initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Datadog: {e}")
            self.enabled = False

    def send_event(self, title: str, text: str, tags: Optional[list] = None,
                   alert_type: str = "info", priority: str = "normal") -> bool:
        """
        Send an event to Datadog

        Args:
            title: Event title
            text: Event description/body
            tags: Optional list of tags (e.g., ["spell:lumos", "source:potterpi"])
            alert_type: Type of alert - "error", "warning", "info", "success"
            priority: Priority - "normal" or "low"

        Returns:
            bool: True if event sent successfully
        """
        if not self.enabled:
            logger.debug(f"Datadog disabled - skipping event: {title}")
            return False

        try:
            # Add default tags
            if tags is None:
                tags = []
            if "source:potterpi" not in tags:
                tags.append("source:potterpi")

            # Send event
            api.Event.create(
                title=title,
                text=text,
                tags=tags,
                alert_type=alert_type,
                priority=priority
            )
            logger.debug(f"Sent Datadog event: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Datadog event '{title}': {e}")
            return False

    def spell_detected(self, spell_name: str, stats: Optional[Dict] = None) -> bool:
        """
        Send a spell detection event

        Args:
            spell_name: Name of the spell detected
            stats: Optional statistics about the spell

        Returns:
            bool: True if event sent successfully
        """
        text = f"Spell detected: {spell_name}"

        if stats:
            text += f"\n- Points: {stats.get('num_points', 'N/A')}"
            text += f"\n- Straightness: {stats.get('straightness', 'N/A'):.2f}"
            text += f"\n- Distance: {stats.get('straight_distance', 'N/A'):.1f}px"

        tags = [
            f"spell:{spell_name.lower().replace(' ', '_')}",
            "event_type:spell_detection"
        ]

        return self.send_event(
            title=f"Spell Detected: {spell_name}",
            text=text,
            tags=tags,
            alert_type="info"
        )

    def home_assistant_action(self, spell_name: str, action: str,
                             entity_id: str, success: bool) -> bool:
        """
        Send a Home Assistant action event

        Args:
            spell_name: Name of the spell that triggered the action
            action: Action performed (e.g., "switch.turn_on")
            entity_id: Entity ID acted upon
            success: Whether the action was successful

        Returns:
            bool: True if event sent successfully
        """
        alert_type = "success" if success else "error"
        status = "succeeded" if success else "failed"

        text = f"Home Assistant action {status}\n"
        text += f"- Spell: {spell_name}\n"
        text += f"- Action: {action}\n"
        text += f"- Entity: {entity_id}"

        tags = [
            f"spell:{spell_name.lower().replace(' ', '_')}",
            f"action:{action}",
            f"entity:{entity_id}",
            f"status:{status}",
            "event_type:home_assistant_action"
        ]

        return self.send_event(
            title=f"HA Action {status.title()}: {action}",
            text=text,
            tags=tags,
            alert_type=alert_type
        )


def test_datadog():
    """Test Datadog events integration"""
    import os

    # Check for API keys
    api_key = os.environ.get("DD_API_KEY")
    app_key = os.environ.get("DD_APP_KEY")

    if not api_key:
        print("ERROR: No Datadog API key found!")
        print("\nSet your Datadog credentials:")
        print("  export DD_API_KEY='your-api-key'")
        print("  export DD_APP_KEY='your-app-key'")
        return

    print("Testing Datadog events integration...")
    dd = DatadogEvents(api_key, app_key)

    # Test spell detection event
    print("\n1. Sending spell detection event...")
    test_stats = {
        "num_points": 15,
        "straightness": 0.95,
        "straight_distance": 234.5
    }
    success = dd.spell_detected("Horizontal Line Right", test_stats)
    print(f"   {'✓' if success else '✗'} Spell detection event")

    # Test successful HA action
    print("\n2. Sending successful HA action event...")
    success = dd.home_assistant_action(
        "Vertical Line Up",
        "switch.turn_off",
        "switch.ciarans_room_ceiling_fan",
        True
    )
    print(f"   {'✓' if success else '✗'} HA action success event")

    # Test failed HA action
    print("\n3. Sending failed HA action event...")
    success = dd.home_assistant_action(
        "Vertical Line Down",
        "switch.turn_on",
        "switch.ciarans_room_ceiling_fan",
        False
    )
    print(f"   {'✓' if success else '✗'} HA action failure event")

    print("\n" + "="*50)
    print("Check your Datadog Events stream at:")
    print("https://app.datadoghq.com/event/stream")
    print("="*50)


if __name__ == "__main__":
    test_datadog()
