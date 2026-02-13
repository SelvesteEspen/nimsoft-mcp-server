#!/usr/bin/env python3
"""
DX UIM MCP Server
Provides tools to interact with Broadcom DX Unified Infrastructure Management API
"""

import os
import logging
from typing import Optional, Any
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dx-uim-mcp")


class UIMClient:
    """Client for interacting with DX UIM REST API"""

    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = True):
        """
        Initialize UIM API client

        Args:
            base_url: Base URL of UIM server (e.g., https://uim-server:8443)
            username: API username
            password: API password or token
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, password)
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.verify = verify_ssl

        # Common headers
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make HTTP request to UIM API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def get_devices(self, domain: Optional[str] = None, hub: Optional[str] = None) -> list:
        """
        Get list of devices/systems

        Args:
            domain: Filter by domain name
            hub: Filter by hub name
        """
        params = {}
        if domain:
            params['domain'] = domain
        if hub:
            params['hub'] = hub

        return self._make_request('GET', '/devices', params=params)

    def get_device_info(self, device_id: str) -> dict:
        """Get detailed information about a specific device"""
        return self._make_request('GET', f'/devices/{device_id}')

    def get_alarms(self,
                   severity: Optional[int] = None,
                   source: Optional[str] = None,
                   limit: int = 100) -> list:
        """
        Get alarms from UIM

        Args:
            severity: Filter by severity (0=clear, 1=info, 2=warning, 3=minor, 4=major, 5=critical)
            source: Filter by source/device
            limit: Maximum number of alarms to return
        """
        params = {}
        if limit:
            params['limit'] = limit
        if severity is not None:
            params['severity'] = severity
        if source:
            params['source'] = source

        return self._make_request('GET', '/alarms', params=params)

    def get_alarm_summary(self) -> dict:
        """Get alarm summary with counts by severity"""
        return self._make_request('GET', '/alarms/summary')

    def acknowledge_alarm(self, alarm_id: str, message: Optional[str] = None) -> dict:
        """
        Acknowledge an alarm

        Args:
            alarm_id: ID of the alarm to acknowledge
            message: Optional acknowledgment message
        """
        payload = {}
        if message:
            payload['message'] = message

        return self._make_request('PUT', f'/alarms/{alarm_id}/ack', json=payload)

    def accept_alarm(self, alarm_id: str) -> dict:
        """
        Accept an alarm

        Args:
            alarm_id: ID of the alarm to accept
        """
        return self._make_request('PUT', f'/alarms/{alarm_id}/accept')

    def assign_alarm(self, alarm_id: str, username: str) -> dict:
        """
        Assign an alarm to a user

        Args:
            alarm_id: ID of the alarm
            username: Username to assign the alarm to
        """
        return self._make_request('PUT', f'/alarms/{alarm_id}/assign/{username}')

    def get_metrics(self) -> list:
        """Get list of available metrics"""
        return self._make_request('GET', '/metrics')

    def get_metric_definitions(self) -> list:
        """Get complete list of UIM metric definitions"""
        return self._make_request('GET', '/configuration_items/metricdefinitions')

    def get_metric_by_id(self, metric_id: str) -> dict:
        """
        Get specific metric data by ID

        Args:
            metric_id: Metric identifier
        """
        return self._make_request('GET', f'/configuration_items/metrics/{metric_id}')

    def get_probes(self) -> list:
        """Get list of probes"""
        return self._make_request('GET', '/probes')

    def get_robots(self) -> list:
        """Get list of robots"""
        return self._make_request('GET', '/robots')


# Initialize MCP server
app = Server("dx-uim-mcp")

# Initialize UIM client (will be set from environment variables)
uim_client: Optional[UIMClient] = None


def init_uim_client():
    """Initialize UIM client from environment variables"""
    global uim_client

    base_url = os.getenv('UIM_BASE_URL')
    username = os.getenv('UIM_USERNAME')
    password = os.getenv('UIM_PASSWORD')
    verify_ssl = os.getenv('UIM_VERIFY_SSL', 'true').lower() == 'true'

    if not all([base_url, username, password]):
        raise ValueError("Missing required environment variables: UIM_BASE_URL, UIM_USERNAME, UIM_PASSWORD")

    uim_client = UIMClient(base_url, username, password, verify_ssl)
    logger.info(f"Initialized UIM client for {base_url}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="list_devices",
            description="List all devices/systems in DX UIM. Optionally filter by domain or hub.",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Filter by domain name (optional)"
                    },
                    "hub": {
                        "type": "string",
                        "description": "Filter by hub name (optional)"
                    }
                }
            }
        ),
        Tool(
            name="get_device_info",
            description="Get detailed information about a specific device by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device identifier"
                    }
                },
                "required": ["device_id"]
            }
        ),
        Tool(
            name="list_alarms",
            description="List alarms from DX UIM with optional filtering by severity and source",
            inputSchema={
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "integer",
                        "description": "Filter by severity: 0=clear, 1=info, 2=warning, 3=minor, 4=major, 5=critical",
                        "minimum": 0,
                        "maximum": 5
                    },
                    "source": {
                        "type": "string",
                        "description": "Filter by source/device name"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of alarms to return",
                        "default": 100
                    }
                }
            }
        ),
        Tool(
            name="get_alarm_summary",
            description="Get a summary of alarms with counts by severity level",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="acknowledge_alarm",
            description="Acknowledge an alarm by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "alarm_id": {
                        "type": "string",
                        "description": "The alarm identifier"
                    },
                    "message": {
                        "type": "string",
                        "description": "Optional acknowledgment message"
                    }
                },
                "required": ["alarm_id"]
            }
        ),
        Tool(
            name="accept_alarm",
            description="Accept an alarm by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "alarm_id": {
                        "type": "string",
                        "description": "The alarm identifier"
                    }
                },
                "required": ["alarm_id"]
            }
        ),
        Tool(
            name="assign_alarm",
            description="Assign an alarm to a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "alarm_id": {
                        "type": "string",
                        "description": "The alarm identifier"
                    },
                    "username": {
                        "type": "string",
                        "description": "Username to assign the alarm to"
                    }
                },
                "required": ["alarm_id", "username"]
            }
        ),
        Tool(
            name="list_metrics",
            description="List all available metrics in the system",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_metric_definitions",
            description="Get complete list of UIM metric definitions with their properties",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_metric_by_id",
            description="Get specific metric data by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric_id": {
                        "type": "string",
                        "description": "The metric identifier (e.g., 'M0AEA025E353AEC88F86A55481CDAFA6A')"
                    }
                },
                "required": ["metric_id"]
            }
        ),
        Tool(
            name="list_probes",
            description="List all probes in the UIM infrastructure",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_robots",
            description="List all robots in the UIM infrastructure",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    if uim_client is None:
        return [TextContent(
            type="text",
            text="Error: UIM client not initialized. Please check environment variables."
        )]

    try:
        if name == "list_devices":
            result = uim_client.get_devices(
                domain=arguments.get('domain'),
                hub=arguments.get('hub')
            )
            return [TextContent(
                type="text",
                text=f"Found {len(result)} devices:\n\n{format_json(result)}"
            )]

        elif name == "get_device_info":
            result = uim_client.get_device_info(arguments['device_id'])
            return [TextContent(
                type="text",
                text=f"Device Information:\n\n{format_json(result)}"
            )]

        elif name == "list_alarms":
            result = uim_client.get_alarms(
                severity=arguments.get('severity'),
                source=arguments.get('source'),
                limit=arguments.get('limit', 100)
            )
            return [TextContent(
                type="text",
                text=f"Found {len(result)} alarms:\n\n{format_json(result)}"
            )]

        elif name == "get_alarm_summary":
            result = uim_client.get_alarm_summary()
            return [TextContent(
                type="text",
                text=f"Alarm Summary:\n\n{format_json(result)}"
            )]

        elif name == "acknowledge_alarm":
            result = uim_client.acknowledge_alarm(
                arguments['alarm_id'],
                message=arguments.get('message')
            )
            return [TextContent(
                type="text",
                text=f"Alarm acknowledged successfully:\n\n{format_json(result)}"
            )]

        elif name == "accept_alarm":
            result = uim_client.accept_alarm(arguments['alarm_id'])
            return [TextContent(
                type="text",
                text=f"Alarm accepted successfully:\n\n{format_json(result)}"
            )]

        elif name == "assign_alarm":
            result = uim_client.assign_alarm(
                arguments['alarm_id'],
                arguments['username']
            )
            return [TextContent(
                type="text",
                text=f"Alarm assigned successfully to {arguments['username']}:\n\n{format_json(result)}"
            )]

        elif name == "list_metrics":
            result = uim_client.get_metrics()
            return [TextContent(
                type="text",
                text=f"Found {len(result)} metrics:\n\n{format_json(result)}"
            )]

        elif name == "get_metric_definitions":
            result = uim_client.get_metric_definitions()
            return [TextContent(
                type="text",
                text=f"Metric Definitions:\n\n{format_json(result)}"
            )]

        elif name == "get_metric_by_id":
            result = uim_client.get_metric_by_id(arguments['metric_id'])
            return [TextContent(
                type="text",
                text=f"Metric Data:\n\n{format_json(result)}"
            )]

        elif name == "list_probes":
            result = uim_client.get_probes()
            return [TextContent(
                type="text",
                text=f"Found {len(result)} probes:\n\n{format_json(result)}"
            )]

        elif name == "list_robots":
            result = uim_client.get_robots()
            return [TextContent(
                type="text",
                text=f"Found {len(result)} robots:\n\n{format_json(result)}"
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]

    except Exception as e:
        logger.error(f"Error executing tool '{name}': {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


def format_json(data: Any) -> str:
    """Format JSON data for display"""
    import json
    return json.dumps(data, indent=2)


async def main():
    """Main entry point"""
    # Initialize UIM client
    try:
        init_uim_client()
    except Exception as e:
        logger.error(f"Failed to initialize UIM client: {e}")
        raise

    # Run the server
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
