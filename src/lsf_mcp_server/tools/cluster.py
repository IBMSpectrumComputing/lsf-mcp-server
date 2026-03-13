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

"""Cluster information tools for LSF."""

import logging
from typing import Dict, Any, Optional
from ..lsf_client import LSFClient
from ..auth import AuthManager


logger = logging.getLogger(__name__)


class ClusterTools:
    """Tools for LSF cluster information and monitoring."""
    
    def __init__(self, client: LSFClient, auth: AuthManager):
        """
        Initialize cluster tools.
        
        Args:
            client: LSF API client
            auth: Authentication manager
        """
        self.client = client
        self.auth = auth
        
    async def _execute_lsf_command(self, command: str) -> Dict[str, Any]:
        """
        Execute an LSF command via the API.
        
        Args:
            command: LSF command to execute
            
        Returns:
            Command execution result
        """
        await self.auth.ensure_authenticated()
        
        logger.info(f"Executing LSF command: {command}")
        
        try:
            response = await self.client.post(
                '/lsf/v1/cluster/usercmd',
                data={'command': command, 'env': ''},
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            result = response.json()
            logger.info(f"Command executed successfully")
            
            return {
                'success': True,
                'command': command,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Failed to execute command: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'command': command
            }
            
    async def list_hosts(self, host_name: Optional[str] = None) -> Dict[str, Any]:
        """
        List LSF cluster hosts using bhosts command.
        
        Args:
            host_name: Specific host name to query (optional)
            
        Returns:
            Host information
        """
        cmd = "bhosts -o 'HOST_NAME STATUS jl_u MAX NJOBS RUN SSUSP USUSP RSV' -json"
        if host_name:
            cmd = f"bhosts {host_name} -o 'HOST_NAME STATUS jl_u MAX NJOBS RUN SSUSP USUSP RSV' -json"
        
        return await self._execute_lsf_command(cmd)
        
    async def list_queues(self, queue_name: Optional[str] = None) -> Dict[str, Any]:
        """
        List LSF queues using bqueues command.
        
        Args:
            queue_name: Specific queue name to query (optional)
            
        Returns:
            Queue information
        """
        cmd = "bqueues -o 'QUEUE_NAME PRIO STATUS MAX NJOBS PEND RUN SUSP' -json"
        if queue_name:
            cmd = f"bqueues {queue_name} -o 'QUEUE_NAME PRIO STATUS MAX NJOBS PEND RUN SUSP' -json"
        
        return await self._execute_lsf_command(cmd)
        
    async def check_load(self, host_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Check system load using lsload command.
        
        Args:
            host_name: Specific host to check (optional)
            
        Returns:
            Load information
        """
        cmd = "lsload -o 'HOST_NAME status r15s r1m r15m ut pg ls it tmp swp mem' -json"
        if host_name:
            cmd = f"lsload {host_name} -o 'HOST_NAME status r15s r1m r15m ut pg ls it tmp swp mem' -json"
        
        return await self._execute_lsf_command(cmd)
        
    async def list_host_info(self, host_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed host information using lshosts command.
        
        Args:
            host_name: Specific host name to query (optional)
            
        Returns:
            Detailed host information
        """
        cmd = "lshosts -o 'HOST_NAME type model cpuf ncpus maxmem maxswp server RESOURCES' -json"
        if host_name:
            cmd = f"lshosts {host_name} -o 'HOST_NAME type model cpuf ncpus maxmem maxswp server RESOURCES' -json"
        
        return await self._execute_lsf_command(cmd)
        
    async def get_cluster_id(self) -> Dict[str, Any]:
        """
        Get LSF cluster identifier using lsid command.
        
        Returns:
            Cluster ID and version information
        """
        cmd = "lsid"
        return await self._execute_lsf_command(cmd)
        
    async def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get LSF cluster information via API endpoint.
        
        Returns:
            Cluster configuration and status
        """
        await self.auth.ensure_authenticated()
        
        logger.info("Getting cluster information via API")
        
        try:
            response = await self.client.get('/lsf/v1/cluster')
            result = response.json()
            
            logger.info("Cluster information retrieved successfully")
            
            return {
                'success': True,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster info: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }