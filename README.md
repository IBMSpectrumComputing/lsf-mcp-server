# LSF MCP Server

A Model Context Protocol (MCP) server for IBM Spectrum LSF that provides comprehensive job management and file operation capabilities through the LSF REST API.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Job Management](#job-management)
  - [Cluster Information](#cluster-information)
  - [File Operations](#file-operations)
  - [Complete Workflow Example](#complete-workflow-example)
- [Tool Reference](#tool-reference)
- [Architecture](#architecture)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Support](#support)
- [Version](#version)
- [Changelog](#changelog)

## Features

### Job Management (3 tools)
- **submit_job** - Submit jobs with simple or advanced options
- **query_jobs** - Query job status with flexible filtering
- **kill_job** - Terminate running or pending jobs

### Cluster Information (6 tools)
- **list_hosts** - List cluster hosts with status and load
- **list_queues** - List available queues and their configuration
- **check_load** - Check system load on hosts
- **list_host_info** - Get detailed host information
- **get_cluster_id** - Get LSF cluster identifier and version
- **get_cluster_info** - Get comprehensive cluster information via API

### File Operations (4 tools)
- **upload_file** - Upload files to LSF server
- **download_file** - Download files from LSF server
- **list_files** - List files in directories
- **delete_file** - Delete files on LSF server

## Requirements

- Python 3.10 or higher
- Access to an LSF REST API server
- LSF credentials (username and password)

## Installation

### 1. Clone or Download

```bash
# Clone the repository or download and extract the source code
cd lsf-mcp-server
```

### 2. Create Virtual Environment

```bash
# Use Python 3.10 or higher
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

## Configuration

The LSF MCP Server is configured through your MCP client's configuration file. The exact location and format depends on your client.

### Standard Configuration Format

Most MCP clients use a similar JSON configuration format:

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

### Configuration Parameters

- `command`: **Absolute path** to the Python binary in your virtual environment
- `args`: Module execution argument (`-m lsf_mcp_server.server`)
- `env`: Environment variables for LSF connection
  - `LSF_SERVER_URL`: Your LSF REST API server URL
  - `LSF_USERNAME`: Your LSF username
  - `LSF_PASSWORD`: Your LSF password

### Client-Specific Setup

For detailed configuration instructions for your specific MCP client, see [DEPLOYMENT.md](DEPLOYMENT.md):
- IBM Bob
- Claude Desktop
- Watson Orchestrate
- LibreChat
- Generic MCP clients

## Usage

Once configured, you can interact with the LSF MCP server through your MCP client using natural language. Here are some examples:

### Job Management

**Submit a simple job:**
```
Submit a job to run 'sleep 100' on the LSF cluster
```

**Submit a job with specific resources:**
```
Submit a job named 'my-analysis' to run 'python analyze.py' on queue 'normal' with 4 processors and 8GB memory
```

**Submit a job with advanced options:**
```
Submit a job with advanced options: -J myjob -q normal -n 8 -R "span[ptile=4]" -W 2:00 ./run.sh
```

**Query all jobs:**
```
Show me all my LSF jobs
```

**Query a specific job:**
```
What's the status of job 12345?
```

**Query jobs in a queue:**
```
Show me all jobs in the 'normal' queue
```

**Kill a job:**
```
Kill job 12345
```

### Cluster Information

**List all hosts:**
```
List all hosts in the LSF cluster
```

**Check specific host:**
```
Show me information about host node01
```

**List queues:**
```
What queues are available?
```

**Check system load:**
```
What's the current load on the cluster?
```

**Get cluster ID:**
```
What's the LSF cluster ID?
```

### File Operations

**Upload a file:**
```
Upload mydata.txt to /home/user/data/ on the LSF server
```

**Download a file:**
```
Download /home/user/results.txt from the LSF server
```

**List files:**
```
List files in /home/user/jobs/ on the LSF server
```

**Delete a file:**
```
Delete /home/user/temp/old_file.txt on the LSF server
```

### Complete Workflow Example

This example demonstrates a complete data processing workflow: uploading input data, running a processing job, and downloading the results.

**Scenario**: Process a CSV file containing sales data and generate a statistical report.

#### Sample Input File (sales_data.csv)
```csv
date,product,quantity,price
2024-01-01,Widget A,10,29.99
2024-01-02,Widget B,5,49.99
2024-01-03,Widget A,8,29.99
2024-01-04,Widget C,15,19.99
2024-01-05,Widget B,12,49.99
```

#### Step 1: Upload Input File

**Command:**
```
Upload sales_data.csv to /home/user/jobs/input/sales_data.csv on the LSF server
```

**Expected Response:**
```
✓ File uploaded successfully
  Local: ./sales_data.csv
  Remote: /home/user/jobs/input/sales_data.csv
  Size: 245 bytes
```

#### Step 2: Submit Processing Job

**Command:**
```
Submit a job named 'sales-analysis' to run 'python /home/user/scripts/analyze.py /home/user/jobs/input/sales_data.csv /home/user/jobs/output/sales_report.txt' on queue 'normal' with 1 processor and 2GB memory
```

**Expected Response:**
```
✓ Job submitted successfully
  Job ID: 12345
  Job Name: sales-analysis
  Queue: normal
  Status: PEND
  Command: python /home/user/scripts/analyze.py /home/user/jobs/input/sales_data.csv /home/user/jobs/output/sales_report.txt
```

**Check Job Status:**
```
What's the status of job 12345?
```

**Status Response:**
```
Job 12345 (sales-analysis)
  Status: DONE
  Queue: normal
  Started: 2024-01-05 10:30:15
  Finished: 2024-01-05 10:30:45
  Runtime: 30 seconds
  Exit Code: 0
```

#### Step 3: Download Results

**Command:**
```
Download /home/user/jobs/output/sales_report.txt from the LSF server to ./sales_report.txt
```

**Expected Response:**
```
✓ File downloaded successfully
  Remote: /home/user/jobs/output/sales_report.txt
  Local: ./sales_report.txt
  Size: 412 bytes
```

**Output File Content (sales_report.txt):**
```
Sales Data Analysis Report
==========================
Generated: 2024-01-05 10:30:45

Summary Statistics:
- Total Records: 5
- Total Quantity Sold: 50 units
- Total Revenue: $1,799.55
- Average Order Value: $359.91

Product Breakdown:
- Widget A: 18 units, $539.82
- Widget B: 17 units, $849.83
- Widget C: 15 units, $299.85

Analysis complete.
```

This workflow demonstrates the typical pattern for batch processing on LSF clusters: prepare your input data locally, upload it to the cluster, submit a job to process it, monitor the job status, and download the results when complete.

## Tool Reference

For detailed information about all available tools, their parameters, and response formats, see [TOOLS.md](TOOLS.md).

**Quick Summary:**
- **Job Management**: submit_job, query_jobs, kill_job
- **Cluster Information**: list_hosts, list_queues, check_load, list_host_info, get_cluster_id, get_cluster_info
- **File Operations**: upload_file, download_file, list_files, delete_file

## Architecture

The LSF MCP server runs locally on your machine and communicates with:
1. **Your MCP Client** via stdio (standard input/output)
2. **LSF REST API** via HTTP/HTTPS

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Local Machine                      │
│                                                             │
│  ┌────────────────┐         stdio          ┌──────────────┐ │
│  │   MCP Client   │◄──────────────────────►│  LSF MCP     │ │
│  │ (AI Assistant) │   (stdin/stdout)       │   Server     │ │
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

The server follows the Model Context Protocol (MCP) standard and works with any MCP-compatible client including IBM Bob, Claude Desktop, Watson Orchestrate, LibreChat, and others.

## Security Considerations

1. **Plain Text Storage**: Credentials in configuration files are stored in plain text. This is standard for MCP servers but requires proper file permissions.

2. **Shared Systems**: Do not use on shared/multi-user systems without additional security measures.

3. **Backup Security**: Ensure backups of configuration files are also secured.

### Additional Resources

For more security guidance, see [DEPLOYMENT.md](DEPLOYMENT.md#security-considerations).

## Troubleshooting

### Server Won't Start

**Problem:** MCP server fails to start

**Solutions:**
1. Check that all environment variables are set correctly in `mcp_settings.json`
2. Verify Python 3.10+ is being used
3. Ensure the virtual environment is activated
4. Check the LSF server URL is accessible

### Authentication Fails

**Problem:** Cannot authenticate with LSF server

**Solutions:**
1. Verify your LSF username and password are correct
2. Check that the LSF REST API server is running
3. Ensure you have network access to the LSF server
4. Check the server logs for detailed error messages

### Tool Execution Fails

**Problem:** Tools return errors

**Solutions:**
1. Check that you're authenticated (server handles this automatically)
2. Verify the LSF command syntax is correct
3. Ensure you have permissions for the requested operation
4. Check the LSF server logs for more details

## License

See LICENSE file for details.

## Support

This code is provided as-is without official support from IBM. For issues, questions, or contributions, please refer to the project repository.

## Version

Current version: 0.1.0

## Changelog

### 0.1.0 (2026-02-25)
- Initial release
- 13 tools for LSF job management, cluster information, and file operations
- Support for LSF REST API authentication
- Comprehensive error handling
- Full MCP protocol implementation
