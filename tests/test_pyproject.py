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

"""Tests for pyproject.toml version constraints."""

import pathlib
import re
import importlib.metadata
from packaging.version import Version


PYPROJECT = pathlib.Path(__file__).parent.parent / "pyproject.toml"


class TestPyprojectVersionConstraints:
    """Verify pyproject.toml declares correct dependency versions."""

    def _get_dependency_line(self, package: str) -> str:
        """Return the raw dependency string for a package from pyproject.toml."""
        text = PYPROJECT.read_text()
        match = re.search(rf'"{package}[^"]*"', text)
        assert match, f"Dependency '{package}' not found in pyproject.toml"
        return match.group(0).strip('"')

    def test_mcp_requires_v2_or_higher(self):
        """mcp dependency must specify >=2.0.0 (not 1.x)."""
        dep = self._get_dependency_line("mcp")
        # Must contain >=2 — e.g. "mcp>=2.0.0"
        assert re.search(r">=\s*2\.", dep), (
            f"Expected mcp>=2.x in pyproject.toml, got: {dep}"
        )

    def test_mcp_does_not_allow_v1(self):
        """mcp dependency must not allow 1.x installs."""
        dep = self._get_dependency_line("mcp")
        # Ensure there's no >=1. without an upper bound blocker
        assert not re.search(r">=\s*1\.", dep), (
            f"mcp dependency still allows 1.x: {dep}"
        )

    def test_httpx_requires_0_27_or_higher(self):
        """httpx must be >=0.27.0 (ssl.SSLContext support)."""
        dep = self._get_dependency_line("httpx")
        assert re.search(r">=\s*0\.2[7-9]|>=\s*0\.[3-9]|>=\s*[1-9]\.", dep), (
            f"Expected httpx>=0.27.x in pyproject.toml, got: {dep}"
        )

    def test_pydantic_requires_v2(self):
        """pydantic must be >=2.0.0 (mcp 2.x requires pydantic v2)."""
        dep = self._get_dependency_line("pydantic")
        assert re.search(r">=\s*2\.", dep), (
            f"Expected pydantic>=2.x in pyproject.toml, got: {dep}"
        )

    def test_python_requires_3_10_or_higher(self):
        """requires-python must be >=3.10 (union type hints used in lsf_client.py)."""
        text = PYPROJECT.read_text()
        match = re.search(r'requires-python\s*=\s*"([^"]+)"', text)
        assert match, "requires-python not found in pyproject.toml"
        spec = match.group(1)
        assert re.search(r">=\s*3\.1[0-9]", spec), (
            f"Expected requires-python>=3.10, got: {spec}"
        )


class TestInstalledVersions:
    """Verify the actually-installed package versions match constraints."""

    def test_installed_mcp_is_v2_or_higher(self):
        """Installed mcp package must be version 2.0.0 or higher."""
        version = Version(importlib.metadata.version("mcp"))
        assert version >= Version("2.0.0"), (
            f"Installed mcp version {version} is below 2.0.0"
        )

    def test_installed_httpx_is_0_27_or_higher(self):
        """Installed httpx must be >=0.27.0."""
        version = Version(importlib.metadata.version("httpx"))
        assert version >= Version("0.27.0"), (
            f"Installed httpx version {version} is below 0.27.0"
        )

    def test_installed_pydantic_is_v2(self):
        """Installed pydantic must be version 2.x."""
        version = Version(importlib.metadata.version("pydantic"))
        assert version >= Version("2.0.0"), (
            f"Installed pydantic version {version} is below 2.0.0"
        )

    def test_mcp_types_is_installed(self):
        """mcp_types must be installed (bundled with mcp 2.x)."""
        version = importlib.metadata.version("mcp_types")
        assert version is not None
        assert Version(version) >= Version("2.0.0")
