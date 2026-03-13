# LSF MCP Server - Deployment Guide

This guide provides detailed instructions for deploying the LSF MCP Server with various MCP-compatible clients.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Client-Specific Configuration](#client-specific-configuration)
   - [IBM Bob](#ibm-bob)
   - [Claude Desktop](#claude-desktop)
   - [Watson Orchestrate](#watson-orchestrate)
   - [LibreChat](#librechat)
   - [Generic MCP Clients](#generic-mcp-clients)
5. [Troubleshooting](#troubleshooting)

## Overview

The LSF MCP Server is a Model Context Protocol (MCP) server that provides tools for managing IBM Spectrum LSF through the LSF REST API. It follows the standard MCP protocol and works with any MCP-compatible client.

### What is MCP?

The Model Context Protocol (MCP) is an open protocol that enables AI assistants to securely access tools and data sources. MCP servers run locally on your machine and communicate with AI clients via standard input/output (stdio).

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Local Machine                      │
│                                                             │
│  ┌────────────────┐         stdio          ┌──────────────┐ │
│  │   MCP Client   │◄──────────────────────►│  LSF MCP     │ │
│  │  (AI Assistant)│   (stdin/stdout)       │   Server     │ │
│  └────────────────┘                        └──────┬───────┘ │
│                                                   │         │
└───────────────────────────────────────────────────┼─────────┘
                                                    │
                                                    │ HTTPS
                                                    ▼
                                    ┌────────────────────────────┐
                                    │   LSF REST API Server      │
                                    │ lsf-server.example.com     │
                                    │         :8088              │
                                    └────────────────────────────┘
```

## Prerequisites

Before installing the LSF MCP Server, ensure you have:

1. **Python 3.10 or higher**
   ```bash
   python3 --version  # Should show 3.10 or higher
   ```

2. **Access to an LSF REST API server**
   - LSF REST API URL (e.g., `http://lsf-server.example.com:8088`)
   - Valid LSF credentials (username and password)

3. **An MCP-compatible client** (one of):
   - IBM Bob
   - Claude Desktop
   - Watson Orchestrate
   - LibreChat
   - Any other MCP-compatible client

## Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/IBMSpectrumComputing/lsf-mcp-server.git
cd lsf-mcp-server
```

### 2. Create Virtual Environment

```bash
# Create virtual environment with Python 3.10+
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

### 4. Verify Installation

```bash
python -c "from lsf_mcp_server.server import LSFMCPServer; print('✓ Installation successful')"
```

## Client-Specific Configuration

### IBM Bob

IBM Bob is an AI coding assistant that supports MCP servers.

#### Configuration File Location

```
~/Library/Application Support/IBM Bob/User/globalStorage/ibm.bob-code/settings/mcp_settings.json
```

#### Configuration Steps

1. **Open the MCP settings file:**
   ```bash
   open ~/Library/Application\ Support/IBM\ Bob/User/globalStorage/ibm.bob-code/settings/mcp_settings.json
   ```

2. **Add the LSF MCP server configuration:**
   ```json
   {
     "mcpServers": {
       "lsf": {
         "command": "/absolute/path/to/lsf-mcp-server/venv/bin/python",
         "args": ["-m", "lsf_mcp_server.server"],
         "env": {
           "LSF_SERVER_URL": "http://lsf-server.example.com:8088",
           "LSF_USERNAME": "your-lsf-username",
           "LSF_PASSWORD": "your-lsf-password"
         }
       }
     }
   }
   ```

3. **Important notes:**
   - Replace `/absolute/path/to/lsf-mcp-server` with the actual path
   - Use the **absolute path** to the Python binary in your virtual environment
   - Replace `your-lsf-username` and `your-lsf-password` with your actual credentials
   - Replace `lsf-server.example.com:8088` with your LSF REST API URL

4. **Restart IBM Bob** to load the new MCP server

#### Verification

Ask IBM Bob:
```
What MCP servers are available?
```

Or try a simple command:
```
Get the LSF cluster ID
```

---

### Claude Desktop

Claude Desktop is Anthropic's desktop application that supports MCP servers.

#### Configuration File Location

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

On Windows:
```
%APPDATA%\Claude\claude_desktop_config.json
```

#### Configuration Steps

1. **Open the Claude Desktop config file:**
   ```bash
   # macOS
   open ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Windows
   notepad %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Add the LSF MCP server configuration:**
   ```json
   {
     "mcpServers": {
       "lsf": {
         "command": "/path/to/lsf-mcp-server/venv/bin/python",
         "args": ["-m", "lsf_mcp_server.server"],
         "env": {
           "LSF_SERVER_URL": "http://lsf-server.example.com:8088",
           "LSF_USERNAME": "your_username",
           "LSF_PASSWORD": "your_password"
         }
       }
     }
   }
   ```

3. **Important notes:**
   - Use the **absolute path** to the Python binary in your virtual environment
   - On Windows, use forward slashes or escaped backslashes in paths
   - Replace credentials with your actual LSF credentials

4. **Restart Claude Desktop** completely (quit and reopen)

#### Verification

After restarting Claude Desktop:
1. Look for MCP server indicators in the UI
2. Try asking: "What LSF tools are available?"
3. Test with: "Get the LSF cluster ID"

#### Troubleshooting Claude Desktop

**Error: "Connection closed" or "MCP error -32000"**

1. **Verify Python path:**
   ```bash
   ls -la /path/to/lsf-mcp-server/venv/bin/python
   ```

2. **Test server manually:**
   ```bash
   cd /path/to/lsf-mcp-server
   source venv/bin/activate
   export LSF_SERVER_URL="http://lsf-server.example.com:8088"
   export LSF_USERNAME="your_username"
   export LSF_PASSWORD="your_password"
   python -m lsf_mcp_server.server
   ```
   Press Ctrl+C to stop.

3. **Check Claude Desktop logs:**
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp*.log
   
   # Windows
   type %LOCALAPPDATA%\Claude\logs\mcp*.log
   ```

---

### Watson Orchestrate

Watson Orchestrate is IBM's AI orchestration platform that supports MCP servers.

#### Configuration

Watson Orchestrate typically uses a configuration file or environment-based setup for MCP servers.

#### Configuration Steps

1. **Locate Watson Orchestrate configuration directory:**
   ```bash
   # Typical location (may vary by installation)
   ~/.watson-orchestrate/config/
   ```

2. **Create or edit MCP configuration file:**
   ```bash
   # Create mcp_config.json
   nano ~/.watson-orchestrate/config/mcp_config.json
   ```

3. **Add LSF MCP server configuration:**
   ```json
   {
     "mcpServers": {
       "lsf": {
         "command": "/path/to/lsf-mcp-server/venv/bin/python",
         "args": ["-m", "lsf_mcp_server.server"],
         "env": {
           "LSF_SERVER_URL": "http://lsf-server.example.com:8088",
           "LSF_USERNAME": "your_username",
           "LSF_PASSWORD": "your_password"
         }
       }
     }
   }
   ```

4. **Restart Watson Orchestrate** to load the configuration

#### Alternative: Environment Variables

If Watson Orchestrate supports environment-based configuration:

```bash
export WATSON_ORCHESTRATE_MCP_LSF_COMMAND="/path/to/venv/bin/python"
export WATSON_ORCHESTRATE_MCP_LSF_ARGS="-m lsf_mcp_server.server"
export LSF_SERVER_URL="http://lsf-server.example.com:8088"
export LSF_USERNAME="your_username"
export LSF_PASSWORD="your_password"
```

#### Verification

1. Check Watson Orchestrate's MCP server list
2. Try executing an LSF command through Watson Orchestrate
3. Verify in Watson Orchestrate logs

---

### LibreChat

LibreChat is an open-source AI chat platform that supports MCP servers.

#### Configuration File Location

LibreChat typically uses a configuration file in its installation directory:
```
/path/to/librechat/.env
```
or
```
/path/to/librechat/config/mcp.json
```

#### Configuration Steps

1. **Locate LibreChat configuration:**
   ```bash
   cd /path/to/librechat
   ```

2. **Edit MCP configuration file:**
   ```bash
   # If using JSON config
   nano config/mcp.json
   
   # If using .env file
   nano .env
   ```

3. **Add LSF MCP server (JSON format):**
   ```json
   {
     "mcpServers": {
       "lsf": {
         "command": "/path/to/lsf-mcp-server/venv/bin/python",
         "args": ["-m", "lsf_mcp_server.server"],
         "env": {
           "LSF_SERVER_URL": "http://lsf-server.example.com:8088",
           "LSF_USERNAME": "your_username",
           "LSF_PASSWORD": "your_password"
         }
       }
     }
   }
   ```

4. **Or add to .env file:**
   ```bash
   MCP_LSF_COMMAND=/path/to/lsf-mcp-server/venv/bin/python
   MCP_LSF_ARGS=-m lsf_mcp_server.server
   LSF_SERVER_URL=http://lsf-server.example.com:8088
   LSF_USERNAME=your_username
   LSF_PASSWORD=your_password
   ```

5. **Restart LibreChat:**
   ```bash
   # If using Docker
   docker-compose restart
   
   # If running directly
   npm restart
   ```

#### Verification

1. Open LibreChat in your browser
2. Check for LSF MCP server in available tools
3. Try a test command: "Get LSF cluster ID"

---

### Generic MCP Clients

For any MCP-compatible client that follows the MCP protocol:

#### Standard Configuration Format

Most MCP clients use a similar JSON configuration format:

```json
{
  "mcpServers": {
    "lsf": {
      "command": "/absolute/path/to/python",
      "args": ["-m", "lsf_mcp_server.server"],
      "env": {
        "LSF_SERVER_URL": "http://lsf-server.example.com:8088",
        "LSF_USERNAME": "your_username",
        "LSF_PASSWORD": "your_password"
      }
    }
  }
}
```

#### Key Configuration Elements

1. **command**: Absolute path to Python binary in virtual environment
2. **args**: Module execution argument (`-m lsf_mcp_server.server`)
3. **env**: Environment variables for LSF connection

#### Manual Testing

You can test the MCP server manually using stdio:

```bash
cd /path/to/lsf-mcp-server
source venv/bin/activate
export LSF_SERVER_URL="http://lsf-server.example.com:8088"
export LSF_USERNAME="your_username"
export LSF_PASSWORD="your_password"
python -m lsf_mcp_server.server
```

The server will start and wait for MCP protocol messages on stdin.

## Troubleshooting

### Common Issues Across All Clients

#### Issue: "Missing required environment variables"

**Cause:** LSF_SERVER_URL, LSF_USERNAME, or LSF_PASSWORD not set

**Solution:**
1. Verify all three environment variables are in your client's configuration
2. Check for typos in variable names
3. Ensure values are not empty strings

#### Issue: "ModuleNotFoundError: No module named 'mcp'"

**Cause:** Dependencies not installed or wrong Python version

**Solution:**
1. Ensure Python 3.10+ is being used
2. Activate virtual environment
3. Reinstall dependencies:
   ```bash
   cd /path/to/lsf-mcp-server
   source venv/bin/activate
   pip install -e .
   ```

#### Issue: "Failed to authenticate with LSF API"

**Cause:** Invalid credentials or LSF server unreachable

**Solution:**
1. Verify LSF username and password are correct
2. Check LSF server URL is accessible:
   ```bash
   curl http://lsf-server.example.com:8088/lsf/v1/cluster
   ```
3. Ensure LSF REST API service is running
4. Check network connectivity to LSF server

#### Issue: Server starts but tools don't work

**Cause:** Authentication or network issues

**Solution:**
1. Test authentication manually:
   ```bash
   cd /path/to/lsf-mcp-server
   source venv/bin/activate
   python test_lsf_connection.py  # If available
   ```

2. Check LSF server logs for errors

3. Verify network connectivity:
   ```bash
   ping lsf-server.example.com
   ```

### Client-Specific Troubleshooting

#### IBM Bob

- Check Bob's output panel for error messages
- Verify the Python path points to the venv Python binary
- Restart Bob after configuration changes

#### Claude Desktop

- Check Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log`
- Ensure Claude Desktop is completely quit and restarted
- Verify file permissions on config file

#### Watson Orchestrate

- Check Watson Orchestrate logs
- Verify MCP configuration file location
- Ensure Watson Orchestrate has permissions to execute Python

#### LibreChat

- Check LibreChat container logs: `docker-compose logs`
- Verify environment variables are loaded
- Restart LibreChat service after configuration changes


