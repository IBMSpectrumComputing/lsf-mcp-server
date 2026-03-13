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

"""Tests for LSF client."""

import pytest
from lsf_mcp_server.lsf_client import LSFClient


class TestLSFClient:
    """Test cases for LSFClient."""
    
    def test_client_initialization(self):
        """Test that client initializes with correct base URL."""
        client = LSFClient("http://example.com:8088")
        assert client.base_url == "http://example.com:8088"
        assert client.session_token is None
        
    def test_client_strips_trailing_slash(self):
        """Test that trailing slash is removed from base URL."""
        client = LSFClient("http://example.com:8088/")
        assert client.base_url == "http://example.com:8088"
        
    def test_set_session_token(self):
        """Test setting session token."""
        client = LSFClient("http://example.com:8088")
        client.set_session_token("test-token-123")
        assert client.session_token == "test-token-123"
        
    def test_clear_session_token(self):
        """Test clearing session token."""
        client = LSFClient("http://example.com:8088")
        client.set_session_token("test-token-123")
        client.clear_session_token()
        assert client.session_token is None
        
    def test_encode_path(self):
        """Test path encoding to base64."""
        path = "/home/user/test.txt"
        encoded = LSFClient.encode_path(path)
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        
    def test_decode_path(self):
        """Test path decoding from base64."""
        path = "/home/user/test.txt"
        encoded = LSFClient.encode_path(path)
        decoded = LSFClient.decode_path(encoded)
        assert decoded == path
        
    def test_get_headers_without_token(self):
        """Test headers without session token."""
        client = LSFClient("http://example.com:8088")
        headers = client._get_headers()
        assert "Authorization" not in headers
        
    def test_get_headers_with_token(self):
        """Test headers with session token."""
        client = LSFClient("http://example.com:8088")
        client.set_session_token("test-token-123")
        headers = client._get_headers()
        assert headers["Authorization"] == "test-token-123"
        
    def test_get_headers_with_additional(self):
        """Test headers with additional headers."""
        client = LSFClient("http://example.com:8088")
        additional = {"Content-Type": "application/json"}
        headers = client._get_headers(additional)
        assert headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_client_close():
    """Test that client can be closed."""
    client = LSFClient("http://example.com:8088")
    await client.close()
    # If no exception is raised, the test passes

# Made with Bob
