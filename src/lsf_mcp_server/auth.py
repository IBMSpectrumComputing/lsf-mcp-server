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

"""Authentication management for LSF REST API."""

import logging
from typing import Dict, Optional
from .lsf_client import LSFClient


logger = logging.getLogger(__name__)


class AuthManager:
    """Manages authentication with LSF REST API."""

    def __init__(self, client: LSFClient, username: str, password: str):
        """
        Initialize authentication manager.

        Args:
            client: LSF API client
            username: LSF username
            password: LSF password
        """
        self.client = client
        self.username = username
        self.password = password
        self.session_info: Optional[Dict] = None

    async def login(self) -> Dict:
        """
        Authenticate with LSF REST API.

        Returns:
            Session information from the API

        Raises:
            Exception: If authentication fails
        """
        logger.info("Logging in as user: {self.username}")

        try:
            response = await self.client.post(
                '/lsf/v1/auth/logon',
                json={
                    'name': self.username,
                    'originalName': self.username,
                    'pass': self.password
                }
            )

            session_data = response.json()

            # Extract session token from response
            # The token is typically in the Set-Cookie header or response body
            if 'token' in session_data:
                token = session_data['token']
            else:
                # Try to extract from cookies
                cookies = response.cookies
                if 'LSF_SESSION' in cookies:
                    token = cookies['LSF_SESSION']
                else:
                    raise Exception("No session token found in response")

            self.client.set_session_token(token)
            self.session_info = session_data

            logger.info("Successfully authenticated with LSF API")
            return session_data

        except Exception as e:
            logger.error("Authentication failed: %s", str(e))
            raise Exception(f"Failed to authenticate with LSF API: {str(e)}")

    async def logout(self):
        """
        Log out from LSF REST API.

        Raises:
            Exception: If logout fails
        """
        if not self.session_info:
            logger.warning("No active session to logout")
            return

        logger.info("Logging out from LSF API")

        try:
            await self.client.post('/lsf/v1/auth/logout')
            self.client.clear_session_token()
            self.session_info = None
            logger.info("Successfully logged out")

        except Exception as e:
            logger.error("Logout failed: %s", str(e))
            # Clear session anyway
            self.client.clear_session_token()
            self.session_info = None

    async def ensure_authenticated(self):
        """
        Ensure we have a valid session, re-authenticate if needed.

        This method can be called before making API requests to ensure
        the session is still valid.
        """
        if not self.session_info:
            await self.login()

    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return self.session_info is not None
