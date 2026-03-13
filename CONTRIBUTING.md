# Contributing to LSF MCP Server

Thank you for your interest in contributing to the LSF MCP Server! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/lsf-mcp-server.git
   cd lsf-mcp-server
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/IBMSpectrumComputing/lsf-mcp-server.git
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Access to an LSF REST API server (for integration testing)
- Git

### Install Development Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package with development dependencies
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Run tests
pytest

# Check code style
python -m black --check src tests
python -m isort --check-only src tests
```

## Making Changes

### Branch Naming

Create a descriptive branch name:
- `feature/add-new-tool` - for new features
- `fix/authentication-bug` - for bug fixes
- `docs/update-readme` - for documentation updates
- `refactor/improve-error-handling` - for refactoring

```bash
git checkout -b feature/your-feature-name
```

### Commit Messages

Write clear, descriptive commit messages:

```
Short summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain what changed and why, not how.

- Bullet points are okay
- Use present tense ("Add feature" not "Added feature")
- Reference issues: "Fixes #123" or "Relates to #456"
```

### Keep Your Fork Updated

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Maximum line length: 100 characters (Black default)

### Code Formatting

Before committing, format your code:

```bash
# Format code
black src tests

# Sort imports
isort src tests
```

### Type Hints

- Use type hints for all function parameters and return values
- Use `Optional[Type]` for nullable values
- Use `Dict`, `List`, etc. from `typing` module

Example:
```python
from typing import Dict, Optional

async def get_job_info(job_id: str) -> Dict[str, Any]:
    """Get job information."""
    pass
```

### Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings
- Include parameter descriptions and return value documentation

Example:
```python
def submit_job(command: str, queue: Optional[str] = None) -> Dict[str, Any]:
    """
    Submit a job to the LSF cluster.
    
    Args:
        command: Command to execute
        queue: Queue name (optional)
        
    Returns:
        Job submission result with job ID and status
        
    Raises:
        ValueError: If command is empty
        AuthenticationError: If not authenticated
    """
    pass
```

### Error Handling

- Use specific exception types
- Provide meaningful error messages
- Log errors appropriately
- Return structured error responses

### Logging

- Use the `logging` module
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Include context in log messages
- Don't log sensitive information (passwords, tokens)

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lsf_mcp_server --cov-report=html

# Run specific test file
pytest tests/test_lsf_client.py

# Run specific test
pytest tests/test_lsf_client.py::TestLSFClient::test_client_initialization
```

### Writing Tests

- Write tests for all new features
- Write tests for bug fixes
- Aim for high code coverage (>80%)
- Use descriptive test names
- Mock external dependencies (LSF API)

Example:
```python
import pytest
from lsf_mcp_server.lsf_client import LSFClient

class TestLSFClient:
    """Test cases for LSFClient."""
    
    def test_client_initialization(self):
        """Test that client initializes with correct base URL."""
        client = LSFClient("http://example.com:8088")
        assert client.base_url == "http://example.com:8088"
```

### Test Coverage

Ensure your changes maintain or improve test coverage:

```bash
pytest --cov=lsf_mcp_server --cov-report=term-missing
```

## Submitting Changes

### Before Submitting

1. **Run tests**: Ensure all tests pass
   ```bash
   pytest
   ```

2. **Format code**: Run code formatters
   ```bash
   black src tests
   isort src tests
   ```

3. **Update documentation**: Update README.md or other docs if needed

4. **Add tests**: Include tests for new features or bug fixes

### Pull Request Process

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub:
   - Use a clear, descriptive title
   - Reference related issues (e.g., "Fixes #123")
   - Describe what changed and why
   - Include screenshots for UI changes (if applicable)

3. **Pull Request Template**:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Refactoring
   
   ## Testing
   - [ ] All tests pass
   - [ ] Added new tests
   - [ ] Updated documentation
   
   ## Related Issues
   Fixes #123
   ```

4. **Code Review**:
   - Address reviewer feedback
   - Make requested changes
   - Keep the PR focused and manageable

5. **Merge**:
   - Maintainers will merge once approved
   - Your branch will be deleted after merge

## Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Clear title**: Describe the issue concisely
2. **Description**: Detailed explanation of the problem
3. **Steps to reproduce**: Numbered steps to recreate the issue
4. **Expected behavior**: What should happen
5. **Actual behavior**: What actually happens
6. **Environment**:
   - Python version
   - Operating system
   - LSF version
   - MCP client being used
7. **Logs**: Relevant error messages or logs
8. **Screenshots**: If applicable

### Issue Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Configure server with...
2. Execute command...
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- Python version: 3.10
- OS: macOS 14.0
- LSF version: 10.1
- MCP client: IBM Bob

**Additional context**
Any other relevant information.
```

## Feature Requests

When requesting features:

1. **Use case**: Describe the problem you're trying to solve
2. **Proposed solution**: How you envision the feature working
3. **Alternatives**: Other solutions you've considered
4. **Additional context**: Any other relevant information

## Questions?

If you have questions about contributing:

- Open a GitHub issue with the "question" label
- Check existing issues and documentation first
- Be specific about what you need help with

## License

By contributing to this project, you agree that your contributions will be licensed under the Apache License 2.0.

## Recognition

Contributors will be recognized in:
- Release notes
- Project documentation
- GitHub contributors page

Thank you for contributing to the LSF MCP Server!