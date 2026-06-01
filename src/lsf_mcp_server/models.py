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

"""Pydantic models for request/response validation."""

from typing import Optional
from pydantic import BaseModel, Field


class JobSubmitRequest(BaseModel):
    """Request model for job submission."""

    command: str = Field(..., description="Command to execute")
    job_name: Optional[str] = Field(None, description="Job name")
    queue: Optional[str] = Field(None, description="Queue name")
    num_processors: Optional[int] = Field(None, description="Number of processors", ge=1)
    memory_mb: Optional[int] = Field(None, description="Memory in MB", ge=1)
    wall_time: Optional[str] = Field(None, description="Wall time limit (HH:MM format)")
    output_file: Optional[str] = Field(None, description="Standard output file path")
    error_file: Optional[str] = Field(None, description="Standard error file path")
    working_directory: Optional[str] = Field(None, description="Working directory")
    advanced_options: Optional[str] = Field(None, description="Advanced LSF options string")


class JobQueryRequest(BaseModel):
    """Request model for job query."""

    job_id: Optional[str] = Field(None, description="Specific job ID to query")
    user: Optional[str] = Field(None, description="Filter by username")
    queue: Optional[str] = Field(None, description="Filter by queue name")
    status: Optional[str] = Field(None, description="Filter by job status")


class JobKillRequest(BaseModel):
    """Request model for killing a job."""

    job_id: str = Field(..., description="Job ID to kill")
    force: bool = Field(False, description="Force kill the job")


class FileUploadRequest(BaseModel):
    """Request model for file upload."""

    local_path: str = Field(..., description="Local file path to upload")
    remote_path: str = Field(..., description="Remote destination path on LSF server")


class FileDownloadRequest(BaseModel):
    """Request model for file download."""

    remote_path: str = Field(..., description="Remote file path on LSF server")
    local_path: Optional[str] = Field(None, description="Local destination path (optional)")


class FileListRequest(BaseModel):
    """Request model for listing files."""

    path: str = Field(..., description="Directory path to list")


class FileDeleteRequest(BaseModel):
    """Request model for file deletion."""

    file_path: str = Field(..., description="File path to delete")


class LSFCommandRequest(BaseModel):
    """Request model for executing LSF commands."""

    command: str = Field(..., description="LSF command to execute")
    parse_json: bool = Field(True, description="Whether to parse JSON output")


class HostListRequest(BaseModel):
    """Request model for listing hosts."""

    host_name: Optional[str] = Field(None, description="Specific host name to query")


class QueueListRequest(BaseModel):
    """Request model for listing queues."""

    queue_name: Optional[str] = Field(None, description="Specific queue name to query")


class LoadCheckRequest(BaseModel):
    """Request model for checking system load."""

    host_name: Optional[str] = Field(None, description="Specific host to check")


class HostInfoRequest(BaseModel):
    """Request model for host information."""

    host_name: Optional[str] = Field(None, description="Specific host name to query")
