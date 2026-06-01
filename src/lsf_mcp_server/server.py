# Copyright 2026 IBM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Main MCP server implementation for LSF."""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .lsf_client import LSFClient
from .auth import AuthManager
from .tools import JobTools, ClusterTools, FileTools


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class LSFMCPServer:
    """MCP Server for LSF operations."""

    def __init__(self):
        """Initialize the LSF MCP server."""
        self.server = Server("lsf-mcp-server")

        # Get configuration from environment
        self.lsf_url = os.getenv('LSF_SERVER_URL')
        self.lsf_username = os.getenv('LSF_USERNAME')
        self.lsf_password = os.getenv('LSF_PASSWORD')

        if not all([self.lsf_url, self.lsf_username, self.lsf_password]):
            raise ValueError(
                "Missing required environment variables: "
                "LSF_SERVER_URL, LSF_USERNAME, LSF_PASSWORD"
            )

        # Initialize LSF client and auth
        self.client = LSFClient(self.lsf_url)
        self.auth = AuthManager(self.client, self.lsf_username, self.lsf_password)

        # Initialize tool handlers
        self.job_tools = JobTools(self.client, self.auth)
        self.cluster_tools = ClusterTools(self.client, self.auth)
        self.file_tools = FileTools(self.client, self.auth)

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP server handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="submit_job",
                    description="Submit a job to the LSF cluster. Supports both simple mode (common parameters) and advanced mode (full LSF options).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Command to execute"
                            },
                            "job_name": {
                                "type": "string",
                                "description": "Job name (optional)"
                            },
                            "queue": {
                                "type": "string",
                                "description": "Queue name (optional)"
                            },
                            "num_processors": {
                                "type": "integer",
                                "description": "Number of processors (optional)"
                            },
                            "memory_mb": {
                                "type": "integer",
                                "description": "Memory in MB (optional)"
                            },
                            "wall_time": {
                                "type": "string",
                                "description": "Wall time limit in HH:MM format (optional)"
                            },
                            "output_file": {
                                "type": "string",
                                "description": "Standard output file path (optional)"
                            },
                            "error_file": {
                                "type": "string",
                                "description": "Standard error file path (optional)"
                            },
                            "working_directory": {
                                "type": "string",
                                "description": "Working directory (optional)"
                            },
                            "advanced_options": {
                                "type": "string",
                                "description": "Advanced LSF options string for full control (optional)"
                            }
                        },
                        "required": ["command"]
                    }
                ),
                Tool(
                    name="query_jobs",
                    description="Query job status and information. Can filter by job ID, user, queue, or status.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_id": {
                                "type": "string",
                                "description": "Specific job ID to query (optional)"
                            },
                            "user": {
                                "type": "string",
                                "description": "Filter by username (optional)"
                            },
                            "queue": {
                                "type": "string",
                                "description": "Filter by queue name (optional)"
                            },
                            "status": {
                                "type": "string",
                                "description": "Filter by job status (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="kill_job",
                    description="Kill a running or pending job.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_id": {
                                "type": "string",
                                "description": "Job ID to kill"
                            },
                            "force": {
                                "type": "boolean",
                                "description": "Force kill the job (optional, default: false)"
                            }
                        },
                        "required": ["job_id"]
                    }
                ),
                Tool(
                    name="list_hosts",
                    description="List LSF cluster hosts with their status and load information.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "host_name": {
                                "type": "string",
                                "description": "Specific host name to query (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="list_queues",
                    description="List available LSF queues with their configuration and status.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "queue_name": {
                                "type": "string",
                                "description": "Specific queue name to query (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="check_load",
                    description="Check system load on LSF cluster hosts.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "host_name": {
                                "type": "string",
                                "description": "Specific host to check (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="list_host_info",
                    description="Get detailed host information including resources and configuration.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "host_name": {
                                "type": "string",
                                "description": "Specific host name to query (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_cluster_id",
                    description="Get LSF cluster identifier and version information.",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_cluster_info",
                    description="Get comprehensive LSF cluster information via API.",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="upload_file",
                    description="Upload a file to the LSF server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "local_path": {
                                "type": "string",
                                "description": "Path to local file to upload"
                            },
                            "remote_path": {
                                "type": "string",
                                "description": "Destination path on LSF server"
                            }
                        },
                        "required": ["local_path", "remote_path"]
                    }
                ),
                Tool(
                    name="download_file",
                    description="Download a file from the LSF server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "remote_path": {
                                "type": "string",
                                "description": "Path on LSF server"
                            },
                            "local_path": {
                                "type": "string",
                                "description": "Local destination path (optional, returns content if not provided)"
                            }
                        },
                        "required": ["remote_path"]
                    }
                ),
                Tool(
                    name="list_files",
                    description="List files in a directory on the LSF server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path to list"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="delete_file",
                    description="Delete a file on the LSF server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to file to delete"
                            }
                        },
                        "required": ["file_path"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
            """Handle tool calls."""
            try:
                # Route to appropriate tool handler
                match name:
                    case "submit_job":
                        result = await self.job_tools.submit_job(**arguments)
                    case "query_jobs":
                        result = await self.job_tools.query_jobs(**arguments)
                    case "kill_job":
                        result = await self.job_tools.kill_job(**arguments)
                    case "list_hosts":
                        result = await self.cluster_tools.list_hosts(**arguments)
                    case "list_queues":
                        result = await self.cluster_tools.list_queues(**arguments)
                    case "check_load":
                        result = await self.cluster_tools.check_load(**arguments)
                    case "list_host_info":
                        result = await self.cluster_tools.list_host_info(**arguments)
                    case "get_cluster_id":
                        result = await self.cluster_tools.get_cluster_id()
                    case "get_cluster_info":
                        result = await self.cluster_tools.get_cluster_info()
                    case "upload_file":
                        result = await self.file_tools.upload_file(**arguments)
                    case "download_file":
                        result = await self.file_tools.download_file(**arguments)
                    case "list_files":
                        result = await self.file_tools.list_files(**arguments)
                    case "delete_file":
                        result = await self.file_tools.delete_file(**arguments)
                    case _:
                        raise ValueError(f"Unknown tool: {name}")

                # Format result as JSON string
                result_text = json.dumps(result, indent=2)

                return [TextContent(type="text", text=result_text)]

            except Exception as e:
                logger.error("Error executing tool %s: %s", name, str(e))
                error_result = {
                    "success": False,
                    "error": str(e),
                    "tool": name
                }
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    async def run(self):
        """Run the MCP server."""
        logger.info("Starting LSF MCP Server")
        logger.info("LSF Server URL: %s", self.lsf_url)
        logger.info("LSF Username: %s", self.lsf_username)

        try:
            # Don't authenticate immediately - let ensure_authenticated() handle it
            # This prevents the server from crashing if LSF is temporarily unavailable
            logger.info("LSF MCP Server initialized (authentication will occur on first request)")

            # Run the server
            async with stdio_server() as (read_stream, write_stream):
                logger.info("LSF MCP Server is ready")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )

        except Exception as e:
            logger.error("Server error: %s", str(e))
            raise
        finally:
            # Cleanup
            try:
                if self.auth.is_authenticated():
                    await self.auth.logout()
                await self.client.close()
                logger.info("LSF MCP Server shutdown complete")
            except Exception as e:
                logger.error("Error during cleanup: %s", str(e))


def main():
    """Main entry point."""
    try:
        server = LSFMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error("Fatal error: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()