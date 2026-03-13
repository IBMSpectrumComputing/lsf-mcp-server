# LSF MCP Server - Tool Reference

This document provides detailed reference information for all tools provided by the LSF MCP Server.

## Job Management Tools

### submit_job

Submit a job to the LSF cluster.

**Parameters:**
- `command` (required): Command to execute
- `job_name` (optional): Job name
- `queue` (optional): Queue name
- `num_processors` (optional): Number of processors
- `memory_mb` (optional): Memory in MB
- `wall_time` (optional): Wall time limit (HH:MM format)
- `output_file` (optional): Standard output file path
- `error_file` (optional): Standard error file path
- `working_directory` (optional): Working directory
- `advanced_options` (optional): Full LSF options string for advanced control

**Example Response:**
```json
{
  "success": true,
  "command": "bsub -J myjob hostname",
  "result": {
    "jobId": "12345",
    "status": "submitted"
  }
}
```

### query_jobs

Query job status and information.

**Parameters:**
- `job_id` (optional): Specific job ID to query
- `user` (optional): Filter by username
- `queue` (optional): Filter by queue name
- `status` (optional): Filter by job status

**Example Response:**
```json
{
  "success": true,
  "result": {
    "jobs": [
      {
        "jobid": "12345",
        "stat": "RUN",
        "queue": "normal",
        "user": "username",
        "job_name": "myjob"
      }
    ]
  }
}
```

### kill_job

Kill a running or pending job.

**Parameters:**
- `job_id` (required): Job ID to kill
- `force` (optional): Force kill (default: false)

## Cluster Information Tools

### list_hosts

List LSF cluster hosts.

**Parameters:**
- `host_name` (optional): Specific host to query

### list_queues

List available LSF queues.

**Parameters:**
- `queue_name` (optional): Specific queue to query

### check_load

Check system load on hosts.

**Parameters:**
- `host_name` (optional): Specific host to check

### list_host_info

Get detailed host information.

**Parameters:**
- `host_name` (optional): Specific host to query

### get_cluster_id

Get LSF cluster identifier and version.

**Parameters:** None

### get_cluster_info

Get comprehensive cluster information via API.

**Parameters:** None

## File Operation Tools

### upload_file

Upload a file to the LSF server.

**Parameters:**
- `local_path` (required): Path to local file
- `remote_path` (required): Destination path on LSF server

### download_file

Download a file from the LSF server.

**Parameters:**
- `remote_path` (required): Path on LSF server
- `local_path` (optional): Local destination (returns content if not provided)

### list_files

List files in a directory.

**Parameters:**
- `path` (required): Directory path to list

### delete_file

Delete a file on the LSF server.

**Parameters:**
- `file_path` (required): Path to file to delete