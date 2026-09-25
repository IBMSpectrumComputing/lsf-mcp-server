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

"""LSF REST API client for making HTTP requests."""

import base64
import logging
from typing import Any, Dict, Optional
import httpx


logger = logging.getLogger(__name__)


class LSFClient:
    """HTTP client for LSF REST API."""
    
    def __init__(self, base_url: str, timeout: float = 30.0, ca_cert: Optional[str] = None):
        """
        Initialize LSF API client.
        
        Args:
            base_url: Base URL of the LSF REST API (e.g., http://host:8088)
            timeout: Request timeout in seconds
            ca_cert: Path to CA certificate file for SSL verification (optional)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session_token: Optional[str] = None
        is_https = self.base_url.lower().startswith('https://')
        ssl_verify = (ca_cert if ca_cert else True) if is_https else False
        self._client = httpx.AsyncClient(timeout=timeout, verify=ssl_verify)
        
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
        
    def set_session_token(self, token: str):
        """Set the session token for authenticated requests."""
        self.session_token = token
        
    def clear_session_token(self):
        """Clear the session token."""
        self.session_token = None
        
    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get headers for requests, including session token if available.
        
        Args:
            additional_headers: Additional headers to include
            
        Returns:
            Dictionary of headers
        """
        headers = {}
        
        if self.session_token:
            headers['Authorization'] = self.session_token
            
        if additional_headers:
            headers.update(additional_headers)
            
        return headers
        
    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make an HTTP request to the LSF API.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint (e.g., /v1/cluster)
            **kwargs: Additional arguments to pass to httpx
            
        Returns:
            HTTP response
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        # Merge headers
        headers = self._get_headers(kwargs.pop('headers', None))
        
        logger.debug(f"{method} {url}")
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            logger.debug(f"Response status: {response.status_code}")
            
            # Raise for 4xx and 5xx status codes
            response.raise_for_status()
            
            return response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise
            
    async def get(self, endpoint: str, **kwargs) -> httpx.Response:
        """Make a GET request."""
        return await self.request('GET', endpoint, **kwargs)
        
    async def post(self, endpoint: str, **kwargs) -> httpx.Response:
        """Make a POST request."""
        return await self.request('POST', endpoint, **kwargs)
        
    async def delete(self, endpoint: str, **kwargs) -> httpx.Response:
        """Make a DELETE request."""
        return await self.request('DELETE', endpoint, **kwargs)
        
    @staticmethod
    def encode_path(path: str) -> str:
        """
        Encode a file path to base64 for use in API endpoints.
        
        Args:
            path: File path to encode
            
        Returns:
            Base64 encoded path
        """
        return base64.b64encode(path.encode()).decode()
        
    @staticmethod
    def decode_path(encoded_path: str) -> str:
        """
        Decode a base64 encoded file path.
        
        Args:
            encoded_path: Base64 encoded path
            
        Returns:
            Decoded file path
        """
        return base64.b64decode(encoded_path.encode()).decode()