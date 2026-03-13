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

"""LSF MCP Server - MCP server for IBM Spectrum LSF."""

__version__ = "0.1.0"

# Don't import server module here to avoid circular import issues
# when running with python -m lsf_mcp_server.server
# Users should import directly: from lsf_mcp_server.server import LSFMCPServer, main

__all__ = ['__version__']