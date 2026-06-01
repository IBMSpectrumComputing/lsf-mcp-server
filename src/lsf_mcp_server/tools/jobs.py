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

"""Job management tools for LSF."""

import logging
from typing import Dict, Any, Optional
from ..lsf_client import LSFClient
from ..auth import AuthManager


logger = logging.getLogger(__name__)


class JobTools:
    """Tools for managing LSF jobs."""
    
    def __init__(self, client: LSFClient, auth: AuthManager):
        """
        Initialize job tools.
        
        Args:
            client: LSF API client
            auth: Authentication manager
        """
        self.client = client
        self.auth = auth
        
    def _build_bsub_command(
        self,
        command: str,
        job_name: Optional[str] = None,
        queue: Optional[str] = None,
        num_processors: Optional[int] = None,
        memory_mb: Optional[int] = None,
        wall_time: Optional[str] = None,
        output_file: Optional[str] = None,
        error_file: Optional[str] = None,
        working_directory: Optional[str] = None
    ) -> str:
        """Build a bsub command string from parameters."""
        cmd_parts = ["bsub"]
        
        if job_name:
            cmd_parts.append(f"-J {job_name}")
            
        if queue:
            cmd_parts.append(f"-q {queue}")
            
        if num_processors:
            cmd_parts.append(f"-n {num_processors}")
            
        if memory_mb:
            cmd_parts.append(f"-M {memory_mb}")
            
        if wall_time:
            cmd_parts.append(f"-W {wall_time}")
            
        if output_file:
            cmd_parts.append(f"-o {output_file}")
            
        if error_file:
            cmd_parts.append(f"-e {error_file}")
            
        if working_directory:
            cmd_parts.append(f"-cwd {working_directory}")
            
        cmd_parts.append(command)
        
        return " ".join(cmd_parts)
        
    async def submit_job(
        self,
        command: str,
        job_name: Optional[str] = None,
        queue: Optional[str] = None,
        num_processors: Optional[int] = None,
        memory_mb: Optional[int] = None,
        wall_time: Optional[str] = None,
        output_file: Optional[str] = None,
        error_file: Optional[str] = None,
        working_directory: Optional[str] = None,
        advanced_options: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit a job to LSF.
        
        Args:
            command: Command to execute
            job_name: Job name
            queue: Queue name
            num_processors: Number of processors
            memory_mb: Memory in MB
            wall_time: Wall time limit (HH:MM)
            output_file: Output file path
            error_file: Error file path
            working_directory: Working directory
            advanced_options: Advanced LSF options string
            
        Returns:
            Job submission result
        """
        await self.auth.ensure_authenticated()
        
        # Build the bsub command
        if advanced_options:
            lsf_command = f"bsub {advanced_options} {command}"
        else:
            lsf_command = self._build_bsub_command(
                command, job_name, queue, num_processors,
                memory_mb, wall_time, output_file, error_file,
                working_directory
            )
            
        logger.info("Submitting job: %s", lsf_command)
        
        try:
            response = await self.client.post(
                '/lsf/v1/cluster/usercmd',
                data={'command': lsf_command, 'env': ''},
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            result = response.json()
            logger.info("Job submitted successfully: %s", result)
            
            return {
                'success': True,
                'command': lsf_command,
                'result': result
            }
            
        except Exception as e:
            logger.error("Failed to submit job: %s", str(e))
            return {
                'success': False,
                'error': str(e),
                'command': lsf_command
            }
            
    async def query_jobs(
        self,
        job_id: Optional[str] = None,
        user: Optional[str] = None,
        queue: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query job status and information.
        
        Args:
            job_id: Specific job ID to query
            user: Filter by username
            queue: Filter by queue name
            status: Filter by job status
            
        Returns:
            Job information
        """
        await self.auth.ensure_authenticated()
        
        # Build bjobs command
        cmd_parts = ["bjobs"]
        
        if user:
            cmd_parts.append(f"-u {user}")
            
        if queue:
            cmd_parts.append(f"-q {queue}")
        
        if not job_id:
            # Show all jobs if no specific job ID
            cmd_parts.append("-a")
            
        # Request JSON output with detailed fields
        cmd_parts.append("-o 'jobid stat queue user job_name submit_time start_time finish_time run_time cpu_used mem max_mem' -json")
        
        # Job ID must come last
        if job_id:
            cmd_parts.append(job_id)
        
        lsf_command = " ".join(cmd_parts)
        logger.info("Querying jobs: %s", lsf_command)
        
        try:
            response = await self.client.post(
                '/lsf/v1/cluster/usercmd',
                data={'command': lsf_command, 'env': ''},
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            result = response.json()
            logger.info("Job query successful")
            
            return {
                'success': True,
                'command': lsf_command,
                'result': result
            }
            
        except Exception as e:
            logger.error("Failed to query jobs: %s", str(e))
            return {
                'success': False,
                'error': str(e),
                'command': lsf_command
            }
            
    async def kill_job(
        self,
        job_id: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Kill a running or pending job.
        
        Args:
            job_id: Job ID to kill
            force: Force kill the job
            
        Returns:
            Kill operation result
        """
        await self.auth.ensure_authenticated()
        
        # Build bkill command
        cmd_parts = ["bkill"]
        
        if force:
            cmd_parts.append("-r")
            
        cmd_parts.append(job_id)
        
        lsf_command = " ".join(cmd_parts)
        logger.info("Killing job: %s", lsf_command)
        
        try:
            response = await self.client.post(
                '/lsf/v1/cluster/usercmd',
                data={'command': lsf_command, 'env': ''},
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            result = response.json()
            logger.info("Job killed successfully: %s", result)
            
            return {
                'success': True,
                'job_id': job_id,
                'command': lsf_command,
                'result': result
            }
            
        except Exception as e:
            logger.error("Failed to kill job: %s", str(e))
            return {
                'success': False,
                'error': str(e),
                'job_id': job_id,
                'command': lsf_command
            }