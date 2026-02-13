#!/usr/bin/env python3
"""
Test script for UIM Client
Demonstrates basic usage of the UIMClient class
"""

import os
from dotenv import load_dotenv
from server import UIMClient

# Load environment variables
load_dotenv()


def main():
    """Test UIM client functionality"""

    # Initialize client
    base_url = os.getenv('UIM_BASE_URL')
    username = os.getenv('UIM_USERNAME')
    password = os.getenv('UIM_PASSWORD')
    verify_ssl = os.getenv('UIM_VERIFY_SSL', 'true').lower() == 'true'

    if not all([base_url, username, password]):
        print("Error: Missing required environment variables")
        print("Please ensure UIM_BASE_URL, UIM_USERNAME, and UIM_PASSWORD are set in .env")
        return

    print(f"Connecting to UIM server at {base_url}...")
    client = UIMClient(base_url, username, password, verify_ssl)

    try:
        # Test 1: List devices
        print("\n=== Testing list_devices ===")
        devices = client.get_devices()
        print(f"Found {len(devices)} devices")
        if devices:
            print(f"First device: {devices[0]}")

        # Test 2: List alarms
        print("\n=== Testing list_alarms ===")
        alarms = client.get_alarms(limit=10)
        print(f"Found {len(alarms)} alarms")
        if alarms:
            print(f"First alarm: {alarms[0]}")

        # Test 3: Get device info (if we have devices)
        if devices:
            print("\n=== Testing get_device_info ===")
            device_id = devices[0].get('id') or devices[0].get('device_id')
            if device_id:
                device_info = client.get_device_info(device_id)
                print(f"Device info: {device_info}")

        print("\n[SUCCESS] All tests completed successfully!")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
