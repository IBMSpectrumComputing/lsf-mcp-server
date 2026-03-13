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
```

### Run Specific Test

```bash
pytest tests/test_lsf_client.py::TestLSFClient::test_client_initialization
```

## Test Structure

- `test_lsf_client.py` - Tests for the LSF REST API client
- More test files to be added for:
  - Authentication (`test_auth.py`)
  - Job tools (`test_jobs.py`)
  - Cluster tools (`test_cluster.py`)
  - File tools (`test_files.py`)
  - Server (`test_server.py`)

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