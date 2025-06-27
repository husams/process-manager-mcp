# Process Manager MCP Server

> **⚠️ Experimental Project**: This is an experimental MCP server under active development. Features and APIs may change without notice. Use with caution in production environments.

A Model Context Protocol (MCP) server that provides AI assistants with safe process management capabilities. This server allows LLMs to monitor, query, and manage system processes with built-in security restrictions.

## Overview

The Process Manager MCP server leverages the [`psutil`](https://github.com/giampaolo/psutil) library to provide comprehensive process management tools while maintaining security boundaries. By default, it restricts access to processes owned by the current user, with optional root access controls.

## Features

### 🔍 Process Discovery
- **List Processes**: View all running processes for a specific user
- **Find by Pattern**: Search processes using regex patterns in names or command lines
- **Port-based Lookup**: Find processes listening on specific ports

### 📊 Process Information
- **Detailed Process Info**: Get comprehensive process details including memory usage, CPU stats, and more
- **User Context**: Automatic filtering to user-owned processes for security

### ⚡ Process Management
- **Safe Termination**: Terminate processes with proper permission checks
- **User Information**: Get current user context (username, UID, GID)

### 🔒 Security Features
- **User Isolation**: By default, only shows processes owned by the current user
- **Root Protection**: Configurable protection against accessing/modifying root processes
- **Permission Validation**: Proper access controls for sensitive operations

## Installation

### Prerequisites
- Python 3.12 or higher
- [`uv`](https://docs.astral.sh/uv/) package manager (recommended)

### Using uv (Recommended)
```bash
# Clone or navigate to the project directory
cd process-manager-mcp

# Install dependencies
uv sync

# Activate the virtual environment to use mcp commands
source .venv/bin/activate

# Now you can use mcp commands directly
mcp dev server.py

# Alternatively, run without activating the environment
uv run server.py
```

### Using pip
```bash
# Install dependencies
pip install mcp[cli] psutil>=7.0.0

# Run the server
python server.py
```

## Configuration

### Environment Variables

- **`ALLOW_ROOT`**: Set to `"Y"` to enable access to root-owned processes (default: disabled)
  ```bash
  export ALLOW_ROOT=Y
  ```

## Available Tools

### `list_processes(username: Optional[str] = None)`
Lists all running processes for the specified user (defaults to current user).

**Example:**
```python
# List current user's processes
list_processes()

# List specific user's processes  
list_processes(username="john")
```

### `find_processes(pattern: str, username: Optional[str] = None)`
Find processes using regex pattern matching against process names and command lines.

**Example:**
```python
# Find all Python processes
find_processes(pattern="python")

# Find processes with "server" in the name
find_processes(pattern=".*server.*")
```

### `get_process_info(pid: int)`
Get detailed information about a specific process by PID.

**Example:**
```python
# Get info for process with PID 1234
get_process_info(pid=1234)
```

### `terminate_process(pid: int)`
Safely terminate a process by PID (respects user permissions).

**Example:**
```python
# Terminate process with PID 5678
terminate_process(pid=5678)
```

### `get_process_by_port(port: int, protocol: str = 'tcp', username: Optional[str] = None)`
Find the process listening on a specific port and protocol.

**Example:**
```python
# Find process listening on port 8080
get_process_by_port(port=8080)

# Find UDP process on port 53
get_process_by_port(port=53, protocol="udp")
```

### `get_user_info()`
Get current user information including username, UID, and GID.

**Example:**
```python
# Get current user details
get_user_info()
```

## Example Prompts

Once the server is running and connected to your AI assistant, you can use natural language prompts like these:

### Process Discovery
```
"Show me all my running processes"

"Find all Python processes currently running"

"What process is listening on port 8080?"

"Search for any processes with 'server' in their name"

"List all processes that contain 'node' in their command line"
```

### Process Information
```
"Give me detailed information about process 1234"

"What's my current user ID and group information?"

"Show me which user owns process 5678"

"Tell me about the memory usage of my Python processes"
```

### Process Management
```
"Kill the process running on port 3000"

"Terminate process with PID 9999"

"Stop all my Python processes that match 'test_script'"

"Find and terminate the process using port 8080"
```

### Troubleshooting & Monitoring
```
"Help me find what's using port 80"

"Show me all my background processes"

"Find any zombie or defunct processes I own"

"What processes are consuming the most memory?"

"Check if there are any Python processes still running after I thought I stopped them"
```

### Advanced Queries
```
"Find all my processes that have 'docker' in their command line and show their details"

"List processes listening on ports between 3000 and 4000"

"Show me processes that were started recently"

"Help me identify which process might be causing high CPU usage"
```

### Security & Permissions
```
"Show me my user information and what processes I can access"

"Check if there are any root processes I can see"

"Verify that I can only see my own processes"
```

## Usage with MCP Clients

### Claude Desktop
Install the server for use with Claude Desktop (requires activated environment):

```bash
# First, activate the environment
source .venv/bin/activate

# Install with default settings
mcp install server.py

# Install with custom name and root access
mcp install server.py --name "Process Manager" -v ALLOW_ROOT=Y
```

### Development and Testing
Use the MCP development tools for testing and debugging (requires activated environment):

```bash
# First, activate the environment
source .venv/bin/activate

# Run in development mode with MCP Inspector
mcp dev server.py

# The command will output a URL like:
# Open http://localhost:3000 to access the MCP Inspector
# Visit this URL in your browser to interactively test all tools
```

The MCP Inspector provides a web interface where you can:
- View all available tools and their schemas
- Test tools with different parameters
- See real-time responses and error handling
- Debug server behavior during development

## Security Considerations

### Default Security Model
- **User Isolation**: Only processes owned by the current user are accessible by default
- **Root Protection**: Root processes are protected unless explicitly enabled via `ALLOW_ROOT=Y`
- **Permission Validation**: All operations respect system permissions

### Enabling Root Access
⚠️ **Warning**: Enabling root access (`ALLOW_ROOT=Y`) allows the server to view and potentially terminate system-critical processes. Use with extreme caution and only in controlled environments.

```bash
# Enable root access (use carefully!)
export ALLOW_ROOT=Y
uv run server.py
```

### Best Practices
1. **Principle of Least Privilege**: Only enable root access when absolutely necessary
2. **Environment Isolation**: Use in containerized or sandboxed environments when possible
3. **Audit Logging**: Monitor server usage in production environments
4. **User Context**: Always specify username parameters when working with multi-user systems

## Dependencies

This server is built using the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) and relies on:

- **[mcp[cli]](https://github.com/modelcontextprotocol/python-sdk)** ≥1.10.1: Official MCP Python SDK with CLI tools
- **[psutil](https://github.com/giampaolo/psutil)** ≥7.0.0: Cross-platform library for system and process utilities

## Error Handling

The server includes comprehensive error handling for common scenarios:

- **No Such Process**: Graceful handling when PIDs become invalid
- **Access Denied**: Clear messages when permission is insufficient  
- **Invalid Patterns**: Regex validation with helpful error messages
- **Network Errors**: Robust handling of network connection queries

## Contributing

This project follows the Model Context Protocol standards. Contributions should:

1. Maintain security-first design principles
2. Include proper error handling and logging
3. Follow the existing code style and patterns
4. Add appropriate tests for new functionality

## License

This project is part of the MCP ecosystem. Please refer to the main repository for licensing information.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/) - Main MCP documentation
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Official Python SDK
- [MCP Servers](https://github.com/modelcontextprotocol/servers) - Collection of MCP servers
- [psutil](https://github.com/giampaolo/psutil) - Cross-platform process utilities library
