# MISP MCP Server

A simple Model Context Protocol (MCP) server that exposes MISP (Malware Information Sharing Platform) IOC retrieval functions to MCP-compatible clients like Claude Desktop.

## Features

- **Get Recent IOCs**: Retrieve IOCs added to MISP in the last 24 hours
- **IOC Summary**: Get statistics and counts by IOC type
- **Filter by Type**: Get IOCs filtered by specific types (IP, domain, URL, etc.)
- **Save to File**: Export IOCs to JSON files
- **Connection Check**: Verify MISP connectivity and configuration

## Prerequisites

- Python 3.8+
- Access to a MISP instance
- MISP API key with appropriate permissions

## Installation

1. **Clone or download the project files**:
   ```bash
   git clone <your-repo-url>
   cd misp-mcp-server
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file with your MISP credentials:
   ```env
   MISP_URL=https://your-misp-instance.com
   MISP_API_KEY=your-api-key-here
   ```

## Usage

### Running the MCP Server

```bash
python misp_mcp_server.py
```

The server will start and listen for MCP connections via STDIO.

### Connecting to Claude Desktop

Add the following to your Claude Desktop MCP configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "misp-server": {
      "command": "python",
      "args": ["/absolute/path/to/misp_mcp_server.py"],
      "env": {
        "MISP_URL": "https://your-misp-instance.com",
        "MISP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Testing with MCP Inspector

```bash
# Install MCP tools (optional)
pip install mcp

# Run the inspector
mcp-inspector python misp_mcp_server.py
```

## Available Tools

### `get_recent_iocs()`
Get all IOCs from MISP added in the last 24 hours.

**Returns**: List of IOC dictionaries with fields: value, type, timestamp, category, tags, event

### `get_ioc_summary()`
Get summary statistics of recent IOCs.

**Returns**: Dictionary with total count, counts by type, and sample IOCs

### `get_iocs_by_type(ioc_type: str)`
Filter IOCs by a specific type.

**Parameters**:
- `ioc_type`: Type of IOC to filter for (e.g., 'ip-dst', 'domain', 'url', 'md5', 'sha256')

**Returns**: List of IOCs matching the specified type

### `save_iocs_to_file(filename: str = None)`
Save recent IOCs to a JSON file.

**Parameters**:
- `filename`: Optional custom filename (auto-generated if not provided)

**Returns**: Status dictionary with save results

### `check_misp_connection()`
Verify MISP connection and configuration.

**Returns**: Connection status and configuration information

## Available Resources

### `misp://server-info`
Get information about the MCP server, including available tools and descriptions.

## Example Interactions

Once connected to Claude Desktop, you can ask:

- *"Get a summary of recent IOCs from MISP"*
- *"Show me all IP address IOCs from the last 24 hours"*
- *"Save the recent IOCs to a file called 'threats_today.json'"*
- *"Check if my MISP connection is working properly"*
- *"How many domain IOCs were added recently?"*

## File Structure

```
misp-mcp-server/
├── misp_to_json.py          # Original MISP IOC retrieval functions
├── misp_mcp_server.py       # MCP server implementation
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .env                    # Environment variables (create this)
└── .env.example           # Example environment file
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MISP_URL` | URL of your MISP instance | Yes |
| `MISP_API_KEY` | Your MISP API authentication key | Yes |

### MISP Permissions

Your MISP API key needs the following permissions:
- Read access to attributes
- Access to events (for context)
- Tag viewing permissions (if using tags)

## Troubleshooting

### Common Issues

**"MISP_API_KEY not found"**
- Ensure your `.env` file is in the same directory as the script
- Verify the API key is correctly formatted

**"Failed to connect to MISP"**
- Check your `MISP_URL` in the `.env` file
- Verify the MISP instance is accessible from your network
- Check for SSL certificate issues (script uses `ssl=False` for local instances)

**"No IOCs found"**
- This is normal if no IOCs were added in the last 24 hours
- Check your MISP instance for recent activity

**Pydantic validation errors**
- Ensure you're using fastmcp 2.0 or later
- Check that all function parameters have proper type hints

### Debug Mode

Enable debug logging by adding this to the top of `misp_mcp_server.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Adding New Tools

To add a new MCP tool, decorate a function with `@mcp.tool()`:

```python
@mcp.tool()
def your_new_function(param: str) -> dict:
    """Description of what this tool does"""
    # Your implementation here
    return {"result": "success"}
```

### Adding New Resources

To add a new MCP resource, use `@mcp.resource()`:

```python
@mcp.resource("misp://your-resource")
def your_resource() -> str:
    """Resource description"""
    return "Resource content"
```

## License

This project is provided as-is for educational and operational use. Ensure compliance with your organization's security policies when handling IOC data.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with MCP inspector
5. Submit a pull request

## Support

For issues related to:
- **MCP Protocol**: Check the [Model Context Protocol documentation](https://modelcontextprotocol.io/)
- **FastMCP**: Visit the [FastMCP documentation](https://gofastmcp.com/)
- **MISP API**: Consult the [PyMISP documentation](https://pymisp.readthedocs.io/)

---

**Note**: This server is designed for internal use with trusted MISP instances. Always follow your organization's security guidelines when handling threat intelligence data.