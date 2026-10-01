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

"""Tests for LSF MCP server — mcp 2.x import and handler behaviour."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Expected tool names — must match server._build_tool_list() exactly
# ---------------------------------------------------------------------------
EXPECTED_TOOLS = [
    "submit_job",
    "query_jobs",
    "kill_job",
    "list_hosts",
    "list_queues",
    "check_load",
    "list_host_info",
    "get_cluster_id",
    "get_cluster_info",
    "upload_file",
    "download_file",
    "list_files",
    "delete_file",
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def lsf_env(monkeypatch):
    """Set the required LSF environment variables for every test in this module."""
    monkeypatch.setenv("LSF_SERVER_URL", "http://fake-lsf:8088")
    monkeypatch.setenv("LSF_USERNAME", "testuser")
    monkeypatch.setenv("LSF_PASSWORD", "testpass")


@pytest.fixture
def server():
    """Return an LSFMCPServer instance with httpx calls patched out."""
    with patch("httpx.AsyncClient"):
        from lsf_mcp_server.server import LSFMCPServer
        return LSFMCPServer()


# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------

class TestMcpImports:
    """Verify mcp 2.x types are importable via 'from mcp import types'."""

    def test_mcp_types_module_importable(self):
        """'from mcp import types' must not raise ImportError."""
        from mcp import types  # noqa: F401

    def test_tool_class_present(self):
        from mcp import types
        assert hasattr(types, "Tool")

    def test_list_tools_result_present(self):
        from mcp import types
        assert hasattr(types, "ListToolsResult")

    def test_call_tool_result_present(self):
        from mcp import types
        assert hasattr(types, "CallToolResult")

    def test_text_content_present(self):
        from mcp import types
        assert hasattr(types, "TextContent")

    def test_call_tool_request_params_present(self):
        from mcp import types
        assert hasattr(types, "CallToolRequestParams")

    def test_paginated_request_params_present(self):
        from mcp import types
        assert hasattr(types, "PaginatedRequestParams")

    def test_server_module_imports_without_error(self):
        """Importing LSFMCPServer must not raise (catches mcp_types regression)."""
        with patch("httpx.AsyncClient"):
            from lsf_mcp_server.server import LSFMCPServer  # noqa: F401


# ---------------------------------------------------------------------------
# Initialisation tests
# ---------------------------------------------------------------------------

class TestLSFMCPServerInit:
    """Test LSFMCPServer construction."""

    def test_init_raises_without_env_vars(self, monkeypatch):
        """Missing env vars must raise ValueError immediately."""
        monkeypatch.delenv("LSF_SERVER_URL", raising=False)
        monkeypatch.delenv("LSF_USERNAME", raising=False)
        monkeypatch.delenv("LSF_PASSWORD", raising=False)
        with patch("httpx.AsyncClient"), pytest.raises(ValueError, match="Missing required"):
            from lsf_mcp_server.server import LSFMCPServer
            LSFMCPServer()

    def test_init_raises_missing_url(self, monkeypatch):
        monkeypatch.delenv("LSF_SERVER_URL", raising=False)
        with patch("httpx.AsyncClient"), pytest.raises(ValueError):
            from lsf_mcp_server.server import LSFMCPServer
            LSFMCPServer()

    def test_init_raises_missing_username(self, monkeypatch):
        monkeypatch.delenv("LSF_USERNAME", raising=False)
        with patch("httpx.AsyncClient"), pytest.raises(ValueError):
            from lsf_mcp_server.server import LSFMCPServer
            LSFMCPServer()

    def test_init_raises_missing_password(self, monkeypatch):
        monkeypatch.delenv("LSF_PASSWORD", raising=False)
        with patch("httpx.AsyncClient"), pytest.raises(ValueError):
            from lsf_mcp_server.server import LSFMCPServer
            LSFMCPServer()

    def test_init_succeeds_with_all_env_vars(self, server):
        """Construction with all env vars set must not raise."""
        assert server is not None

    def test_tools_list_is_populated(self, server):
        """_tools must be a non-empty list after construction."""
        assert isinstance(server._tools, list)
        assert len(server._tools) > 0

    def test_tools_list_completeness(self, server):
        """_tools must contain exactly the expected tool names."""
        from mcp import types
        tool_names = [t.name for t in server._tools]
        assert tool_names == EXPECTED_TOOLS

    def test_tools_are_mcp_tool_instances(self, server):
        """Every entry in _tools must be a types.Tool instance."""
        from mcp import types
        for tool in server._tools:
            assert isinstance(tool, types.Tool), f"{tool!r} is not a types.Tool"

    def test_each_tool_has_input_schema(self, server):
        """Every tool must have a non-empty input_schema dict."""
        for tool in server._tools:
            assert isinstance(tool.input_schema, dict), f"{tool.name} has no input_schema"
            assert tool.input_schema.get("type") == "object"


# ---------------------------------------------------------------------------
# Handler tests
# ---------------------------------------------------------------------------

class TestHandleListTools:
    """Tests for _handle_list_tools."""

    @pytest.mark.asyncio
    async def test_returns_list_tools_result(self, server):
        """Must return a ListToolsResult."""
        from mcp import types
        result = await server._handle_list_tools(None, None)
        assert isinstance(result, types.ListToolsResult)

    @pytest.mark.asyncio
    async def test_tools_match_build_list(self, server):
        """Returned tools must be identical to server._tools."""
        result = await server._handle_list_tools(None, None)
        assert result.tools == server._tools

    @pytest.mark.asyncio
    async def test_tool_count(self, server):
        """Must return exactly the expected number of tools."""
        result = await server._handle_list_tools(None, None)
        assert len(result.tools) == len(EXPECTED_TOOLS)


class TestHandleCallTool:
    """Tests for _handle_call_tool."""

    def _make_params(self, name: str, arguments: dict | None = None):
        """Build a CallToolRequestParams-like object."""
        params = MagicMock()
        params.name = name
        params.arguments = arguments or {}
        return params

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_is_error(self, server):
        """Calling an unknown tool name must return isError=True."""
        from mcp import types
        params = self._make_params("nonexistent_tool")
        result = await server._handle_call_tool(None, params)
        assert isinstance(result, types.CallToolResult)
        assert result.is_error is True

    @pytest.mark.asyncio
    async def test_unknown_tool_content_is_text(self, server):
        """Error result content must be a TextContent item."""
        from mcp import types
        params = self._make_params("nonexistent_tool")
        result = await server._handle_call_tool(None, params)
        assert len(result.content) == 1
        assert isinstance(result.content[0], types.TextContent)

    @pytest.mark.asyncio
    async def test_unknown_tool_error_body_is_json(self, server):
        """Error result text must be valid JSON with 'error' key."""
        params = self._make_params("nonexistent_tool")
        result = await server._handle_call_tool(None, params)
        body = json.loads(result.content[0].text)
        assert "error" in body
        assert body["tool"] == "nonexistent_tool"

    @pytest.mark.asyncio
    async def test_successful_tool_returns_call_tool_result(self, server):
        """A successful tool call must return a CallToolResult with isError falsy."""
        from mcp import types
        fake_result = {"success": True, "data": "ok"}
        server.job_tools.query_jobs = AsyncMock(return_value=fake_result)
        params = self._make_params("query_jobs", {})
        result = await server._handle_call_tool(None, params)
        assert isinstance(result, types.CallToolResult)
        assert not result.is_error

    @pytest.mark.asyncio
    async def test_successful_tool_content_is_text_content(self, server):
        """Successful result must contain exactly one TextContent item."""
        from mcp import types
        fake_result = {"success": True}
        server.job_tools.submit_job = AsyncMock(return_value=fake_result)
        params = self._make_params("submit_job", {"command": "sleep 10"})
        result = await server._handle_call_tool(None, params)
        assert len(result.content) == 1
        assert isinstance(result.content[0], types.TextContent)
        assert result.content[0].type == "text"

    @pytest.mark.asyncio
    async def test_successful_tool_content_is_valid_json(self, server):
        """Successful result text must be valid JSON matching the tool return value."""
        fake_result = {"success": True, "job_id": "12345"}
        server.job_tools.kill_job = AsyncMock(return_value=fake_result)
        params = self._make_params("kill_job", {"job_id": "12345"})
        result = await server._handle_call_tool(None, params)
        body = json.loads(result.content[0].text)
        assert body == fake_result

    @pytest.mark.asyncio
    async def test_tool_exception_returns_is_error(self, server):
        """If a tool raises, the result must have isError=True, not propagate."""
        server.cluster_tools.list_hosts = AsyncMock(side_effect=RuntimeError("boom"))
        params = self._make_params("list_hosts", {})
        result = await server._handle_call_tool(None, params)
        assert result.is_error is True
        body = json.loads(result.content[0].text)
        assert "boom" in body["error"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool_name,mock_attr,tool_args", [
        ("submit_job",     ("job_tools",     "submit_job"),     {"command": "echo hi"}),
        ("query_jobs",     ("job_tools",     "query_jobs"),     {}),
        ("kill_job",       ("job_tools",     "kill_job"),       {"job_id": "1"}),
        ("list_hosts",     ("cluster_tools", "list_hosts"),     {}),
        ("list_queues",    ("cluster_tools", "list_queues"),    {}),
        ("check_load",     ("cluster_tools", "check_load"),     {}),
        ("list_host_info", ("cluster_tools", "list_host_info"), {}),
        ("get_cluster_id", ("cluster_tools", "get_cluster_id"), {}),
        ("get_cluster_info",("cluster_tools","get_cluster_info"),{}),
        ("upload_file",    ("file_tools",    "upload_file"),    {"local_path": "/a", "remote_path": "/b"}),
        ("download_file",  ("file_tools",    "download_file"),  {"remote_path": "/b"}),
        ("list_files",     ("file_tools",    "list_files"),     {"path": "/b"}),
        ("delete_file",    ("file_tools",    "delete_file"),    {"file_path": "/b"}),
    ])
    async def test_all_tools_are_routed(self, server, tool_name, mock_attr, tool_args):
        """Every registered tool name must route to its handler without error."""
        from mcp import types
        obj_name, method_name = mock_attr
        tool_obj = getattr(server, obj_name)
        setattr(tool_obj, method_name, AsyncMock(return_value={"success": True}))
        params = self._make_params(tool_name, tool_args)
        result = await server._handle_call_tool(None, params)
        assert isinstance(result, types.CallToolResult)
        assert not result.is_error
        getattr(tool_obj, method_name).assert_awaited_once()
