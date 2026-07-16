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

from typing_extensions import assert_never

SUPPORTED_PY_VERSIONS = ("310", "311", "312", "313", "314")
SUPPORTED_PLATFORMS = ("win64", "linux64", "macos64", "macosm164")

WASM_SUPPORTED_PY_VERSIONS = ("313",)
WASM_PLATFORM = "pyodide_2025_0_wasm32"
WASM_TEMPLATE = "https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-{BINARY_VERSION}%2B{BUILD_COMMIT}-cp{PYNUMBER}-cp{PYNUMBER}-{PLATFORM}.whl"


class TestPackageSupportedPlatforms:
    @staticmethod
    def get_required_urls() -> list[str]:
        IOS_REPO = Path(__file__).parents[3]
        makefile = IOS_REPO / "src/ifcopenshell-python/Makefile"
        text = makefile.read_text()

        def find_make_var(var_name: str) -> str:
            line = next(l for l in text.splitlines() if l.startswith(f"{var_name}:="))
            return line.partition(":=")[2]

        BINARY_VERSION = find_make_var("BINARY_VERSION")
        BUILD_COMMIT = find_make_var("BUILD_COMMIT")
        # Build workflows upload artifacts using a 7-char short SHA.
        assert (
            l := len(BUILD_COMMIT)
        ) == 7, f"BUILD_COMMIT must be a 7-char short SHA, got {BUILD_COMMIT!r} (length {l})"

        required_urls: list[str] = []

        base_kwargs = {
            "BINARY_VERSION": BINARY_VERSION,
            "BUILD_COMMIT": BUILD_COMMIT,
        }

        # Non-WASM binaries.
        URL_TYPES = ("IOS_URL", "IFCCONVERT_URL")
        for url_type in URL_TYPES:
            url_template = find_make_var(url_type)
            url_template = url_template.replace("$(", "{").replace(")", "}")
            for platform in SUPPORTED_PLATFORMS:
                kwargs = base_kwargs | {"PLATFORM": platform}

                if url_type == "IOS_URL":
                    for pyver in SUPPORTED_PY_VERSIONS:
                        url = url_template.format(**kwargs, PYNUMBER=pyver)
                        required_urls.append(url)

                elif url_type == "IFCCONVERT_URL":
                    url = url_template.format(**kwargs)
                    required_urls.append(url)

                else:
                    assert_never(url_type)

        # WASM wheels.
        for pyver in WASM_SUPPORTED_PY_VERSIONS:
            url = WASM_TEMPLATE.format(
                PYNUMBER=pyver,
                PLATFORM=WASM_PLATFORM,
                BINARY_VERSION=BINARY_VERSION,
                BUILD_COMMIT=BUILD_COMMIT,
            )
            required_urls.append(url)

        return required_urls

    @staticmethod
    def get_missing_urls_fast(urls: list[str]) -> list[str]:
        """Check `urls` against the build listing page.

        Fast, but the listing page can lag behind what's actually on S3, so this may report URLs as
        missing that do exist.
        """
        # We don't use requests in ifcopenshell, so we use Python builtin stuff.
        parsed = urlparse("https://builds.ifcopenshell.org")
        conn = http.client.HTTPSConnection(parsed.netloc)
        conn.request("GET", parsed.path)
        response = conn.getresponse()
        build_html = response.read().decode("utf-8")
        conn.close()

        return [url for url in urls if url not in build_html]

    @staticmethod
    def get_missing_urls_slow(urls: list[str]) -> list[str]:
        """Check `urls` directly with a HEAD request each.

        Slow, but more reliable.
        """
        missing_urls: list[str] = []
        for url in urls:
            parsed = urlparse(url)
            conn = http.client.HTTPSConnection(parsed.netloc)
            conn.request("HEAD", parsed.path)
            response = conn.getresponse()
            response.read()
            conn.close()
            if response.status != 200:
                missing_urls.append(url)

        return missing_urls

    def test_run(self) -> None:
        required_urls = self.get_required_urls()
        maybe_missing_urls = self.get_missing_urls_fast(required_urls)
        missing_urls = self.get_missing_urls_slow(maybe_missing_urls)

        assert not missing_urls
