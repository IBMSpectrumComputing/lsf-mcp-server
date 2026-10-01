# LSF MCP Server Tests

This directory contains the test suite for the LSF MCP Server.

## Running Tests

### Install Test Dependencies

```bash
pip install -e ".[dev]"
```

This installs the package with development dependencies including:
- pytest
- pytest-asyncio
- pytest-httpx

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=lsf_mcp_server --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_lsf_client.py
pytest tests/test_server.py
pytest tests/test_pyproject.py
```

### Run Specific Test

```bash
pytest tests/test_lsf_client.py::TestLSFClient::test_client_initialization
pytest tests/test_server.py::TestHandleCallTool::test_all_tools_are_routed
pytest tests/test_pyproject.py::TestInstalledVersions::test_installed_mcp_is_v2_or_higher
```

## Test Structure

- `test_lsf_client.py` — Tests for the LSF REST API client (`LSFClient`): initialization,
  authentication, and HTTP interaction with the LSF REST API.

- `test_server.py` — Tests for the MCP server (`LSFMCPServer`):
  - **`TestMcpImports`** — Verifies that `mcp` 2.x types (`Tool`, `ListToolsResult`,
    `CallToolResult`, `TextContent`, `CallToolRequestParams`, `PaginatedRequestParams`) are
    importable via `from mcp import types`. Guards against `mcp_types` regressions.
  - **`TestLSFMCPServerInit`** — Validates server construction: raises `ValueError` when
    required environment variables (`LSF_SERVER_URL`, `LSF_USERNAME`, `LSF_PASSWORD`) are
    missing, and confirms that `_tools` is fully populated with the correct `types.Tool`
    instances and input schemas when all variables are present.
  - **`TestHandleListTools`** — Confirms `_handle_list_tools` returns a `ListToolsResult`
    whose tools list is identical to `server._tools`.
  - **`TestHandleCallTool`** — Covers the tool dispatch layer: unknown tool names return
    `isError=True` with a JSON error body; successful calls return a `CallToolResult` with
    a single `TextContent` containing valid JSON; exceptions are caught and returned as
    errors rather than propagated. A parametrized test exercises routing for all 13
    registered tools.

- `test_pyproject.py` — Tests for `pyproject.toml` version constraints and the installed
  runtime environment:
  - **`TestPyprojectVersionConstraints`** — Parses `pyproject.toml` directly and asserts
    that `mcp>=2.0.0`, `httpx>=0.27.0`, `pydantic>=2.0.0`, and `requires-python>=3.10`
    are declared. Prevents accidental downgrade of version floors.
  - **`TestInstalledVersions`** — Uses `importlib.metadata` to confirm the *currently
    installed* `mcp`, `httpx`, `pydantic`, and `mcp_types` packages all meet the minimum
    version requirements at test time.

> **Note:** `test_auth.py`, `test_jobs.py`, `test_cluster.py`, and `test_files.py` are
> planned for future addition.

## Writing Tests

When adding new tests:

1. Follow the existing test structure
2. Use descriptive test names that explain what is being tested
3. Include docstrings for test classes and methods
4. Use pytest fixtures for common setup
5. Mock external dependencies (LSF API calls)
6. Test both success and failure cases

## Mocking LSF API

Use `pytest-httpx` to mock HTTP requests to the LSF REST API:

```python
import pytest
from httpx import Response

@pytest.mark.asyncio
async def test_api_call(httpx_mock):
    httpx_mock.add_response(
        url="http://example.com/lsf/v1/cluster",
        json={"cluster": "test"}
    )
    # Your test code here
```

## Contributing

Please ensure all tests pass before submitting a pull request:

```bash
pytest
```

Add tests for any new features or bug fixes.