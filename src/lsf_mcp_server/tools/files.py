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

"""File operation tools for LSF."""

import httpx
import logging
import os
from typing import Dict, Any, Optional

from ..lsf_client import LSFClient
from ..auth import AuthManager


logger = logging.getLogger(__name__)


class FileTools:
    """Tools for file operations on LSF server."""

    def __init__(self, client: LSFClient, auth: AuthManager):
        """
        Initialize file tools.

        Args:
            client: LSF API client
            auth: Authentication manager
        """
        self.client = client
        self.auth = auth

    async def upload_file(
        self,
        local_path: str,
        remote_path: str
    ) -> Dict[str, Any]:
        """
        Upload a file to the LSF server.

        Args:
            local_path: Path to local file
            remote_path: Destination path on LSF server

        Returns:
            Upload result
        """
        await self.auth.ensure_authenticated()

        logger.info("Uploading file: %s -> %s", local_path, remote_path)

        try:
            # Check if local file exists
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file not found: {local_path}")

            # Read file content
            with open(local_path, 'rb') as f:
                file_content = f.read()

            # Prepare multipart form data
            files = {
                'file': (os.path.basename(local_path), file_content)
            }
            data = {
                'path': remote_path
            }

            response = await self.client.post(
                '/lsf/v1/files',
                files=files,
                data=data
            )

            result = response.json()
            logger.info("File uploaded successfully")

            return {
                'success': True,
                'local_path': local_path,
                'remote_path': remote_path,
                'result': result
            }

        except Exception as e:
            logger.error("Failed to upload file: %s", str(e))
            return {
                'success': False,
                'error': str(e),
                'local_path': local_path,
                'remote_path': remote_path
            }

    async def download_file(
        self,
        remote_path: str,
        local_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download a file from the LSF server.

        Args:
            remote_path: Path on LSF server
            local_path: Local destination path (optional)

        Returns:
            Download result with file content or saved path
        """
        await self.auth.ensure_authenticated()

        logger.info("Downloading file: %s", remote_path)

        try:
            # Encode the remote path as base64
            encoded_path = self.client.encode_path(remote_path)

            response = await self.client.get(f'/lsf/v1/files/{encoded_path}')

            # If local_path is provided, save to file
            if local_path:
                with open(local_path, 'wb') as f:
                    f.write(response.content)

                logger.info("File downloaded and saved to: %s", local_path)

                return {
                    'success': True,
                    'remote_path': remote_path,
                    'local_path': local_path,
                    'size_bytes': len(response.content)
                }
            else:
                # Return content as text
                logger.info("File downloaded successfully")

                return {
                    'success': True,
                    'remote_path': remote_path,
                    'content': response.text,
                    'size_bytes': len(response.content)
                }

        except Exception as e:
            logger.error("Failed to download file: %s", str(e))
            return {
                'success': False,
                'error': str(e),
                'remote_path': remote_path
            }

    async def list_files(self, path: str) -> Dict[str, Any]:
        """
        List files in a directory on the LSF server.

        Args:
            path: Directory path to list

        Returns:
            List of files with metadata
        """
        await self.auth.ensure_authenticated()

        logger.info("Listing files in: %s", path)

        try:
            response = await self.client.get(
                '/lsf/v1/files',
                params={'path': path}
            )

            result = response.json()
            logger.info("Files listed successfully")

            return {
                'success': True,
                'path': path,
                'result': result
            }

        except Exception as e:
            logger.error("Failed to list files: %s", str(e))
            return {
                'success': False,
                'error': str(e),
                'path': path
            }

    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file on the LSF server.

        Args:
            file_path: Path to file to delete

        Returns:
            Deletion result
        """
        await self.auth.ensure_authenticated()

        logger.info("Deleting file: %s", file_path)

        try:
            # Encode the file path as base64
            encoded_path = self.client.encode_path(file_path)

            response = await self.client.delete(f'/lsf/v1/files/{encoded_path}')

            result = response.json()
            logger.info("File deleted successfully")

            return {
                'success': True,
                'file_path': file_path,
                'result': result
            }
        except Exception as e:
            logger.error("Failed to delete file: %s", str(e))
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
