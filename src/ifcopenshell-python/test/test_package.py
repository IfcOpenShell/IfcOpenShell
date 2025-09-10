# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import http.client
from pathlib import Path
from urllib.parse import urlparse

import pytest
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element
import test.bootstrap

# Where it's also reflected:
# - .github/workflows/ci-ifcopenshell-python.yml
# - .github/workflows/ci-ifcopenshell-python-pypi.yml
# - src/ifcopenshell-python/Makefile (PYVERSION check)
SUPPORTED_PY_VERSIONS = ("39", "310", "311", "312", "313")
SUPPORTED_PLATFORMS = ("win64", "linux64", "macos64", "macosm164")


class TestPackageSupportedPlatforms:
    def test_run(self) -> None:
        IOS_REPO = Path(__file__).parents[3]
        makefile = IOS_REPO / "src/ifcopenshell-python/Makefile"
        text = makefile.read_text()

        # We don't use requests in ifcopenshell, so we use Python builtin stuff.
        parsed = urlparse("https://builds.ifcopenshell.org")
        conn = http.client.HTTPSConnection(parsed.netloc)
        conn.request("GET", parsed.path)
        response = conn.getresponse()
        build_html = response.read().decode("utf-8")

        def find_make_var(var_name: str) -> str:
            line = next(l for l in text.splitlines() if l.startswith(f"{var_name}:="))
            return line.partition(":=")[2]

        BINARY_VERSION = find_make_var("BINARY_VERSION")
        URL_TYPES = ("IOS_URL", "IFCCONVERT_URL")

        missing_urls: set[str] = set()
        for url_type in URL_TYPES:
            url_template = find_make_var(url_type)
            url_template = url_template.replace("$(", "{").replace(")", "}")
            for platform in SUPPORTED_PLATFORMS:
                for pyver in SUPPORTED_PY_VERSIONS:
                    url = url_template.format(PYNUMBER=pyver, PLATFORM=platform, BINARY_VERSION=BINARY_VERSION)
                    if url not in build_html:
                        missing_urls.add(url)

        assert not missing_urls
