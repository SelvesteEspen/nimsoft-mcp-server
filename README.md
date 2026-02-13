# DX UIM MCP Server

A Model Context Protocol (MCP) server for interacting with Broadcom DX Unified Infrastructure Management (UIM) API. This server enables Claude to monitor devices, manage alarms, and retrieve performance metrics from your UIM environment.

## Features

- **Device Monitoring**: List and query devices/systems in your UIM infrastructure
- **Alarm Management**: Retrieve, filter, and acknowledge alarms
- **Metrics Retrieval**: Fetch QoS (Quality of Service) performance data
- **Flexible Authentication**: Support for username/password authentication
- **Comprehensive API Coverage**: Access to key UIM REST API endpoints

## Available Tools

### Device Management

#### 1. `list_devices`
List all devices/systems in DX UIM with optional filtering.

**Parameters:**
- `domain` (optional): Filter by domain name
- `hub` (optional): Filter by hub name

**Example:**
```json
{
  "domain": "production",
  "hub": "hub01"
}
```

#### 2. `get_device_info`
Get detailed information about a specific device.

**Parameters:**
- `device_id` (required): The device identifier

**Example:**
```json
{
  "device_id": "server-prod-01"
}
```

### Alarm Management

#### 3. `list_alarms`
List alarms with filtering options.

**Parameters:**
- `severity` (optional): Filter by severity (0=clear, 1=info, 2=warning, 3=minor, 4=major, 5=critical)
- `source` (optional): Filter by source/device name
- `limit` (optional): Maximum number of alarms to return (default: 100)

**Example:**
```json
{
  "severity": 4,
  "limit": 50
}
```

#### 4. `get_alarm_summary`
Get a summary of alarms with counts by severity level.

**Parameters:** None

#### 5. `acknowledge_alarm`
Acknowledge an alarm by its ID.

**Parameters:**
- `alarm_id` (required): The alarm identifier
- `message` (optional): Acknowledgment message

**Example:**
```json
{
  "alarm_id": "alarm-12345",
  "message": "Investigating the issue"
}
```

#### 6. `accept_alarm`
Accept an alarm by its ID.

**Parameters:**
- `alarm_id` (required): The alarm identifier

#### 7. `assign_alarm`
Assign an alarm to a specific user.

**Parameters:**
- `alarm_id` (required): The alarm identifier
- `username` (required): Username to assign the alarm to

**Example:**
```json
{
  "alarm_id": "alarm-12345",
  "username": "john.doe"
}
```

### Metrics & Monitoring

#### 8. `list_metrics`
List all available metrics in the system.

**Parameters:** None

#### 9. `get_metric_definitions`
Get complete list of UIM metric definitions with their properties.

**Parameters:** None

#### 10. `get_metric_by_id`
Get specific metric data by its ID.

**Parameters:**
- `metric_id` (required): The metric identifier

**Example:**
```json
{
  "metric_id": "M0AEA025E353AEC88F86A55481CDAFA6A"
}
```

### Infrastructure

#### 11. `list_probes`
List all probes in the UIM infrastructure.

**Parameters:** None

#### 12. `list_robots`
List all robots in the UIM infrastructure.

**Parameters:** None

## Installation

### Prerequisites
- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip
- Access to a DX UIM server with REST API enabled
- Valid UIM API credentials

### Setup Steps

1. **Clone or navigate to this repository:**
   ```bash
   cd d:\Python\nimsoft-mcp-server
   ```

2. **Install dependencies:**

   **Using uv (recommended):**
   ```bash
   # Install uv if you haven't already
   # Windows (PowerShell):
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Then install dependencies
   uv pip install -e .
   ```

   **Using pip (alternative):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file in the project root with your UIM credentials:
   ```env
   UIM_BASE_URL=https://your-uim-server.company.com/uimapi
   UIM_USERNAME=your_username
   UIM_PASSWORD=your_password
   UIM_VERIFY_SSL=true
   ```

   See `.env.example` for a template.

   **Note:** The `UIM_BASE_URL` should be the full API URL including the `/uimapi` path.

4. **Test the server:**

   **Using uv:**
   ```bash
   uv run python server.py
   ```

   **Using Python directly:**
   ```bash
   python server.py
   ```

   Or run the test client:
   ```bash
   uv run python test_client.py
   # or
   python test_client.py
   ```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `UIM_BASE_URL` | Full API URL including /uimapi path (e.g., https://your-uim-server.company.com/uimapi) | Yes | - |
| `UIM_USERNAME` | API username | Yes | - |
| `UIM_PASSWORD` | API password or token | Yes | - |
| `UIM_VERIFY_SSL` | Verify SSL certificates (true/false) | No | true |

### SSL Certificate Verification

If your UIM server uses self-signed certificates, you can disable SSL verification by setting:
```env
UIM_VERIFY_SSL=false
```

**Note:** Disabling SSL verification is not recommended for production environments.

## Using with Claude Desktop

To use this MCP server with Claude Desktop, add it to your Claude configuration:

### Windows
Edit `%APPDATA%\Claude\claude_desktop_config.json`:

**Using uv (recommended):**
```json
{
  "mcpServers": {
    "dx-uim": {
      "command": "uv",
      "args": ["run", "python", "d:\\Python\\nimsoft-mcp-server\\server.py"],
      "env": {
        "UIM_BASE_URL": "https://your-uim-server.company.com/uimapi",
        "UIM_USERNAME": "your_username",
        "UIM_PASSWORD": "your_password",
        "UIM_VERIFY_SSL": "true"
      }
    }
  }
}
```

**Using Python directly:**
```json
{
  "mcpServers": {
    "dx-uim": {
      "command": "python",
      "args": ["d:\\Python\\nimsoft-mcp-server\\server.py"],
      "env": {
        "UIM_BASE_URL": "https://your-uim-server.company.com/uimapi",
        "UIM_USERNAME": "your_username",
        "UIM_PASSWORD": "your_password",
        "UIM_VERIFY_SSL": "true"
      }
    }
  }
}
```

### macOS
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

**Using uv (recommended):**
```json
{
  "mcpServers": {
    "dx-uim": {
      "command": "uv",
      "args": ["run", "python", "/path/to/nimsoft-mcp-server/server.py"],
      "env": {
        "UIM_BASE_URL": "https://your-uim-server.company.com/uimapi",
        "UIM_USERNAME": "your_username",
        "UIM_PASSWORD": "your_password",
        "UIM_VERIFY_SSL": "true"
      }
    }
  }
}
```

**Using Python directly:**
```json
{
  "mcpServers": {
    "dx-uim": {
      "command": "python3",
      "args": ["/path/to/nimsoft-mcp-server/server.py"],
      "env": {
        "UIM_BASE_URL": "https://your-uim-server.company.com/uimapi",
        "UIM_USERNAME": "your_username",
        "UIM_PASSWORD": "your_password",
        "UIM_VERIFY_SSL": "true"
      }
    }
  }
}
```

### Linux
Edit `~/.config/Claude/claude_desktop_config.json` with the same structure as macOS (both uv and Python methods work).

## API Compatibility

This server is designed to work with DX UIM (formerly CA UIM/Nimsoft) REST API. The implementation is based on the official API endpoints:

**API Base URL:** `https://your-uim-server.company.com/uimapi`

**API Documentation:** [Swagger UI](https://your-uim-server.company.com/uimapi/swagger-ui/index.html)

**Supported Endpoints:**
- `/devices` - Device management
- `/alarms` - Alarm management and operations
- `/metrics` - Metrics and performance data
- `/probes` - Probe inventory
- `/robots` - Robot configuration
- `/configuration_items/metricdefinitions` - Metric definitions

**Authentication:** Basic Authentication (username/password)

The API uses standard HTTP methods:
- `GET` - Retrieve data
- `POST` - Create or filter data
- `PUT` - Update or modify data
- `DELETE` - Remove data

Consult the Swagger documentation for detailed endpoint specifications and request/response schemas.

## Troubleshooting

### Connection Issues
- Verify your `UIM_BASE_URL` is correct and the server is accessible
- Check that the REST API is enabled on your UIM server
- Ensure firewall rules allow access to the UIM API port (typically 8443)

### Authentication Failures
- Confirm your username and password are correct
- Check that the user has appropriate API permissions in UIM
- Some UIM installations may require an API token instead of a password

### SSL Certificate Errors
- If using self-signed certificates, set `UIM_VERIFY_SSL=false`
- For production, consider installing the UIM server's CA certificate in your system trust store

### API Endpoint Errors
- Different UIM versions may use different API paths
- Check your UIM documentation for the correct REST API endpoints
- The server logs will show the exact URLs being called for debugging

## Development

### Project Structure
```
nimsoft-mcp-server/
├── server.py           # Main MCP server implementation
├── test_client.py      # Test script for API client
├── pyproject.toml      # Project configuration (uv/pip)
├── requirements.txt    # Python dependencies (pip)
├── .env               # Environment variables (create from .env.example)
├── .env.example       # Example environment configuration
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

### Using uv for Development

**Install development dependencies:**
```bash
uv pip install -e ".[dev]"
```

**Run the server:**
```bash
uv run python server.py
```

**Run tests:**
```bash
uv run python test_client.py
```

**Format code with Ruff (if dev dependencies installed):**
```bash
uv run ruff format server.py
```

**Check code with Ruff:**
```bash
uv run ruff check server.py
```

### Extending the Server

To add new tools:

1. Add a method to the `UIMClient` class for the API call
2. Add a new `Tool` definition in `list_tools()`
3. Add the handler logic in `call_tool()`

### Logging

The server uses Python's built-in logging. To increase verbosity, modify the logging level in `server.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- Store credentials securely using environment variables or a secrets manager
- Use SSL/TLS for all API communications (set `UIM_VERIFY_SSL=true`)
- Limit API user permissions to only what's necessary
- Rotate API credentials regularly
- Never commit `.env` files with real credentials to version control

## License

This project is provided as-is for use with Broadcom DX UIM environments.

## Support

For issues related to:
- **This MCP server**: Open an issue in this repository
- **DX UIM API**: Consult Broadcom DX UIM documentation
- **Claude/MCP**: Visit the Anthropic documentation

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Acknowledgments

Built using:
- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- [Broadcom DX Unified Infrastructure Management](https://www.broadcom.com/products/software/aiops/unified-infrastructure-management)
