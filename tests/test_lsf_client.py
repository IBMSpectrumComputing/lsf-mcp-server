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

import ssl
import pytest
from unittest.mock import MagicMock, patch
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

    # ------------------------------------------------------------------
    # SSL context tests (httpx 0.28+ requires SSLContext, not path string)
    # ------------------------------------------------------------------

    def test_ssl_disabled_for_http(self):
        """HTTP URL must pass verify=False to httpx — no SSL."""
        import httpx
        with patch("httpx.AsyncClient") as mock_client_cls:
            LSFClient("http://example.com:8088")
            _, kwargs = mock_client_cls.call_args
            assert kwargs["verify"] is False

    def test_ssl_default_for_https_no_cert(self):
        """HTTPS URL with no ca_cert must pass verify=True (system trust store)."""
        with patch("httpx.AsyncClient") as mock_client_cls:
            LSFClient("https://example.com:8443")
            _, kwargs = mock_client_cls.call_args
            assert kwargs["verify"] is True

    def test_ssl_context_created_for_https_with_cert(self):
        """HTTPS URL + ca_cert must call ssl.create_default_context(cafile=...)."""
        mock_ctx = MagicMock(spec=ssl.SSLContext)
        with patch("ssl.create_default_context", return_value=mock_ctx) as mock_create, \
             patch("httpx.AsyncClient") as mock_client_cls:
            LSFClient("https://example.com:8443", ca_cert="/path/to/ca.pem")
            mock_create.assert_called_once_with(cafile="/path/to/ca.pem")
            _, kwargs = mock_client_cls.call_args
            assert kwargs["verify"] is mock_ctx

    def test_ssl_verify_is_ssl_context_not_string(self):
        """verify= must be an ssl.SSLContext, never a bare path string."""
        mock_ctx = MagicMock(spec=ssl.SSLContext)
        with patch("ssl.create_default_context", return_value=mock_ctx), \
             patch("httpx.AsyncClient") as mock_client_cls:
            LSFClient("https://example.com:8443", ca_cert="/path/to/ca.pem")
            _, kwargs = mock_client_cls.call_args
            assert not isinstance(kwargs["verify"], str), (
                "verify= must not be a path string — httpx 0.28 deprecates that"
            )

    def test_ssl_context_loads_ca_file(self, tmp_path):
        """ssl.create_default_context loads the CA cert file from disk."""
        # Write a minimal self-signed PEM so create_default_context doesn't error
        import subprocess, sys
        cert_file = tmp_path / "ca.pem"
        result = subprocess.run(
            [
                sys.executable, "-c",
                (
                    "from cryptography import x509\n"
                    "from cryptography.x509.oid import NameOID\n"
                    "from cryptography.hazmat.primitives import hashes, serialization\n"
                    "from cryptography.hazmat.primitives.asymmetric import rsa\n"
                    "import datetime, pathlib\n"
                    "key = rsa.generate_private_key(public_exponent=65537, key_size=2048)\n"
                    "subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'test')])\n"
                    "cert = (x509.CertificateBuilder()\n"
                    "    .subject_name(subject).issuer_name(issuer)\n"
                    "    .public_key(key.public_key())\n"
                    "    .serial_number(x509.random_serial_number())\n"
                    "    .not_valid_before(datetime.datetime.utcnow())\n"
                    "    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=1))\n"
                    "    .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)\n"
                    "    .sign(key, hashes.SHA256()))\n"
                    f"pathlib.Path(r'{cert_file}').write_bytes(cert.public_bytes(serialization.Encoding.PEM))\n"
                ),
            ],
            capture_output=True,
        )
        if result.returncode != 0:
            pytest.skip("cryptography package not available for cert generation")

        # Should not raise — create_default_context must load the file successfully
        with patch("httpx.AsyncClient"):
            client = LSFClient("https://example.com:8443", ca_cert=str(cert_file))
        assert client is not None

    def test_ssl_invalid_cert_path_raises(self):
        """Non-existent ca_cert path must raise at init time, not silently ignore."""
        with patch("httpx.AsyncClient"), pytest.raises((FileNotFoundError, ssl.SSLError)):
            LSFClient("https://example.com:8443", ca_cert="/does/not/exist/ca.pem")


@pytest.mark.asyncio
async def test_client_close():
    """Test that client can be closed."""
    client = LSFClient("http://example.com:8088")
    await client.close()
    # If no exception is raised, the test passes
