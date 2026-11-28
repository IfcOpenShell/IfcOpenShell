# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020-2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

include ../vars.mk

LAST_COMMIT_HASH:=$(shell git rev-parse HEAD)
LAST_COMMIT_DATE:=$(shell git show -s --format=%cI)
LAST_GIT_BRANCH:=$(shell git rev-parse --abbrev-ref HEAD)

SUPPORTED_PYVERSIONS := py311 py313
# Blender extensions platform allows just one build per platform per version,
# so we add suffix for different Python versions builds.
SEMVER_SUFFIX:=
# Blender 4.5 LTS is supported until July 2027 - https://www.blender.org/releases/4-5/
BLENDER_VERSION_MIN_py311:=4.5.0
# Blender 5.1+ requires Python 3.13.
BLENDER_VERSION_MIN_py313:=5.1.0

ifdef PYVERSION
ifeq ($(filter $(PYVERSION),$(SUPPORTED_PYVERSIONS)),)
$(error Unsupported PYVERSION=$(PYVERSION). Must be one of $(SUPPORTED_PYVERSIONS))
endif
ifndef BLENDER_VERSION_MIN_$(PYVERSION)
$(error BLENDER_VERSION_MIN_$(PYVERSION) is not set)
endif

PYMINOR:=$(subst py3,,$(PYVERSION))
PYLIBDIR:=python3.$(PYMINOR)
PYNUMBER:=3$(PYMINOR)
endif # def PYVERSION

IFCMERGE_VERSION:=2026-04-07

SUPPORTED_PLATFORMS := linux macosm1 win

ifdef PLATFORM
ifeq ($(filter $(PLATFORM),$(SUPPORTED_PLATFORMS)),)
$(error Unsupported PLATFORM=$(PLATFORM). Must be one of $(SUPPORTED_PLATFORMS))
endif

ifeq ($(PLATFORM), linux)
BLENDER_PLATFORM:=linux-x64
endif

ifeq ($(PLATFORM), macosm1)
BLENDER_PLATFORM:=macos-arm64
endif

ifeq ($(PLATFORM), win)
BLENDER_PLATFORM:=windows-x64
endif

endif # def PLATFORM

PIP_COOLDOWN_ARGS=--uploaded-prior-to=P7D

# Current build commit hash.
OLD:=7b8f129
.PHONY: bump
bump:
ifndef NEW
	$(error ERROR: 'NEW' variable is not set (should be set with new commit hash). \
		Example use for 'bump' command: 'make bump NEW=0123456')
endif
	cd . && $(SED) -b "s/$(OLD)/$(NEW)/" Makefile
	cd ../ifcopenshell-python/ && $(SED) -b "s/$(OLD)/$(NEW)/" Makefile
	# Verify the builds for the new commit are uploaded.
	cd ../ifcopenshell-python/ && uvx pytest -p no:pytest-blender test/test_package.py

.PHONY: dist
dist:
ifndef PLATFORM
	$(error PLATFORM is not set. Example values: $(SUPPORTED_PLATFORMS))
endif
ifndef PYVERSION
	$(error PYVERSION is not set. Example values: $(SUPPORTED_PYVERSIONS))
endif
	rm -rf build
	mkdir -p build
	mkdir -p dist
	cp -r bonsai build/

	# To scope any build-time dependencies
	cd build && $(PYTHON) -m venv env
	# Must bump pip as older versions trust some stale compromised CA certificates (see eMudhra CA incident).
	cd build && . env/$(VENV_ACTIVATE) && $(PYTHON) -m pip install --upgrade pip
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) install build

	mkdir -p build/wheels
	# Provides IfcOpenShell Python functionality
	cd ../ifcopenshell-python && make dist PLATFORM=$(PLATFORM)64 PYVERSION=$(PYVERSION) && mv dist/*.whl ../bonsai/build/wheels/
	cd ../bcf && make dist && mv dist/*.whl ../bonsai/build/wheels/
	cd ../ifcclash && make dist && mv dist/*.whl ../bonsai/build/wheels/
	cd ../ifctester && make dist && mv dist/*.whl ../bonsai/build/wheels/
	cd ../ifcfm && make dist && mv dist/*.whl ../bonsai/build/wheels/
	cd ../bsdd && make dist && mv dist/*.whl ../bonsai/build/wheels/
	cd ../ifcdiff && make dist && mv dist/*.whl ../bonsai/build/wheels/
	cd ../ifccsv && make dist && mv dist/*.whl ../bonsai/build/wheels/
	cd ../ifcpatch && make dist && mv dist/*.whl ../bonsai/build/wheels/
	cd ../ifc4d && make dist && mv dist/*.whl ../bonsai/build/wheels/
	cd ../ifc5d && make dist && mv dist/*.whl ../bonsai/build/wheels/
	cd ../ifccityjson && make dist && mv dist/*.whl ../bonsai/build/wheels/

	# Third-party wheels are locked in bundled-wheels/uv.lock.
	uv run --script scripts/uv-lock-download.py --lock bundled-wheels/uv.lock --platform $(PLATFORM) --python $(PYMINOR) --dest build/wheels

	# odfpy doesn't come with its own wheel, so whee'l (get it?) create it ourselves!
	# See https://github.com/eea/odfpy/issues/132
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) wheel odfpy $(PIP_COOLDOWN_ARGS) --wheel-dir=./wheels
	# jQuery is required for web UI functionality
	cd build/bonsai/bim/data/webui/static/js/ && wget --no-verbose https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js

	# Tabulator renders the schedule and costing tables in the web UI.
	# Pinned to 6.5.2, the version unpkg's unversioned URL currently resolves
	# to, so a future upstream release can't silently change table behaviour.
	cd build/bonsai/bim/data/webui/static/js/ && wget https://unpkg.com/tabulator-tables@6.5.2/dist/js/tabulator.min.js
	cd build/bonsai/bim/data/webui/static/css/ && wget https://unpkg.com/tabulator-tables@6.5.2/dist/css/tabulator_site.min.css
	cd build/bonsai/bim/data/webui/static/css/ && wget https://unpkg.com/tabulator-tables@6.5.2/dist/css/tabulator_site_dark.min.css

	# Socket.IO client is required for the web UI's realtime connection to Blender
	cd build/bonsai/bim/data/webui/static/js/ && wget https://cdn.socket.io/4.0.0/socket.io.min.js

	# Font Awesome provides the icons used throughout the web UI.
	# The CSS references these webfonts by relative path, so both must ship together.
	cd build/bonsai/bim/data/webui/static/css/ && wget https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css
	mkdir -p build/bonsai/bim/data/webui/static/webfonts
	cd build/bonsai/bim/data/webui/static/webfonts/ && wget https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/webfonts/fa-brands-400.ttf
	cd build/bonsai/bim/data/webui/static/webfonts/ && wget https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/webfonts/fa-brands-400.woff2
	cd build/bonsai/bim/data/webui/static/webfonts/ && wget https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/webfonts/fa-regular-400.ttf
	cd build/bonsai/bim/data/webui/static/webfonts/ && wget https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/webfonts/fa-regular-400.woff2
	cd build/bonsai/bim/data/webui/static/webfonts/ && wget https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/webfonts/fa-solid-900.ttf
	cd build/bonsai/bim/data/webui/static/webfonts/ && wget https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/webfonts/fa-solid-900.woff2
	cd build/bonsai/bim/data/webui/static/webfonts/ && wget https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/webfonts/fa-v4compatibility.ttf
	cd build/bonsai/bim/data/webui/static/webfonts/ && wget https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/webfonts/fa-v4compatibility.woff2

	# SVG.js and svg-pan-zoom render and pan/zoom the drawings viewer in the web UI
	cd build/bonsai/bim/data/webui/static/js/ && wget https://cdnjs.cloudflare.com/ajax/libs/svg.js/3.1.1/svg.min.js
	cd build/bonsai/bim/data/webui/static/js/ && wget https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js

	# Bootstrap provides layout and the collapsible panels in the drawings viewer
	cd build/bonsai/bim/data/webui/static/css/ && wget https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css
	cd build/bonsai/bim/data/webui/static/js/ && wget https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js

	# Bonsai's own branding images used across the web UI
	mkdir -p build/bonsai/bim/data/webui/static/images
	cd build/bonsai/bim/data/webui/static/images/ && wget https://bonsaibim.org/assets/images/favicon-blender.png
	cd build/bonsai/bim/data/webui/static/images/ && wget https://bonsaibim.org/assets/images/blender/blender-logo.png

	# Provides jsgantt-improved supports for web-based construction sequencing gantt charts
	cd build/bonsai/bim/data/gantt/ && wget --no-verbose https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js
	cd build/bonsai/bim/data/gantt/ && wget --no-verbose https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css

	# Provides IFCJSON functionality. Upstream (IFCJSON-Team) is dormant and has no wheel
	# packaging, so we maintain our own fork under the IfcOpenShell organisation.
	cd build && . env/$(VENV_ACTIVATE) && $(PYTHON) -m pip wheel "git+https://github.com/IfcOpenShell/IFC2JSON_python.git@main" --no-deps -w wheels/

	# Brickschema requires pkg_resources which is provided by Blender.
	# Provides Brickschema functionality
	# For now lets bundle the latest nightly schema
	cd build/bonsai/bim/data/brick/ && wget --no-verbose https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl

	# Required for hipped roof generation
	cd build && . env/$(VENV_ACTIVATE) && $(PYTHON) -m pip wheel "git+https://github.com/prochitecture/bpypolyskel" --no-deps -w wheels/

	# folder for executable files
	mkdir -p build/bonsai/libs/bin

	# required for three-way git merging
ifeq ($(PLATFORM), win)
	cd build/bonsai/libs/bin && wget --no-verbose https://github.com/brunopostle/ifcmerge/releases/download/$(IFCMERGE_VERSION)/ifcmerge.exe
else
	cd build/bonsai/libs/bin && wget --no-verbose https://raw.githubusercontent.com/brunopostle/ifcmerge/$(IFCMERGE_VERSION)/ifcmerge && chmod +x ifcmerge
endif

	# Generate translations module for Bonsai build
	git clone https://github.com/IfcOpenShell/bonsai-translations.git build/working
	$(PYTHON) scripts/bonsai_translations.py -i "build/working" -o "build/bonsai"
	rm -rf build/working

	# Remove dependencies also bundled with Blender
	rm -rf build/wheels/numpy*

	cp pyproject.toml build/
ifeq ($(IS_STABLE), TRUE)
	$(SED) "s/0.0.0/$(VERSION_SEMVER)$(SEMVER_SUFFIX)/" build/bonsai/blender_manifest.toml
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_PYTHON)"/' build/pyproject.toml
else
	$(SED) "s/0.0.0/$(VERSION_SEMVER_DAILY)/" build/bonsai/blender_manifest.toml
	$(SED) "s/8888888/$(LAST_COMMIT_HASH)/" build/bonsai/__init__.py
	$(SED) "s/9999999/$(LAST_COMMIT_DATE)/" build/bonsai/__init__.py
	$(SED) "s/7777777/$(LAST_GIT_BRANCH)/" build/bonsai/__init__.py
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_DAILY)"/' build/pyproject.toml
endif

	$(SED) 's/^blender_version_min = "BLENDER_VERSION_MIN"/blender_version_min = "$(BLENDER_VERSION_MIN_$(PYVERSION))"/' build/bonsai/blender_manifest.toml
ifeq ($(PYVERSION), py311)
	$(SED) 's/^# blender_version_max = /blender_version_max = /' build/bonsai/blender_manifest.toml
endif

	$(SED) "s/os-arch/$(BLENDER_PLATFORM)/" build/bonsai/blender_manifest.toml

	# Provides bonsai Add-on functionality
	cd build && if command -v uv >/dev/null 2>&1; then \
		uv build --wheel; \
	else \
		. env/$(VENV_ACTIVATE) && $(PYTHON) -m build --wheel; \
	fi
	cp build/dist/*.whl build/wheels/

	# Safeguard for non-wheel dependencies slipping in.
	wheels=$$(find build/wheels/* ! -name "*.whl"); \
	if [ -n "$$wheels" ]; then \
		echo "Found non-wheel dependencies:"; \
		echo "$$wheels"; \
		echo "Error: non-wheel dependencies are not supported by Blender!"; \
		exit 1; \
	fi
	mv build/wheels/*.whl build/bonsai/wheels/

ifneq ($(PLATFORM), linux)
	# Safeguard: in case one of `pip download` will break,
	# it will produce a linux wheel for non-linux build (our github action machine is using linux).
	wheels=$$(find build/bonsai/wheels/*manylinux_*.whl); \
	if [ -n "$$wheels" ]; then \
		echo "Found linux wheel files in non-linux build:"; \
		echo "$$wheels"; \
		echo "Error: linux wheels are incompatible with build $(PLATFORM)!"; \
		exit 1; \
	fi
endif

	$(PYTHON) scripts/get_wheels.py build/bonsai/wheels build/bonsai/blender_manifest.toml
	rm -rf build/bonsai/bim/
	rm -rf build/bonsai/core/
	rm -rf build/bonsai/tool/
	rm -rf build/bonsai/libs/

ifeq ($(IS_STABLE), TRUE)
	cd build && zip -r bonsai_$(PYVERSION)-$(VERSION_SEMVER)$(SEMVER_SUFFIX)-$(BLENDER_PLATFORM).zip ./bonsai
else
	cd build && zip -r bonsai_$(PYVERSION)-$(VERSION_SEMVER_DAILY)-$(BLENDER_PLATFORM).zip ./bonsai
endif

	mv build/bonsai*.zip dist/

	rm -rf build

.PHONY: test
test:
	@echo "Running all tests..."
	@ERROR=0; \
	make test-core || ERROR=1; \
	make test-tool || ERROR=1; \
	make test-bim || ERROR=1; \
	if [ $$ERROR -ne 0 ]; then \
		echo "One or more tests failed"; \
		exit 1; \
	fi

.PHONY: test-core
test-core:
ifndef MODULE
	pytest -p no:pytest-blender test/core
else
	pytest -p no:pytest-blender test/core/test_${MODULE}.py
endif

.PHONY: test-bim
test-bim:
ifndef MODULE
	pytest test/bim
else
	pytest test/bim -m "$(MODULE)" ./ --maxfail=1
endif

.PHONY: test-tool
test-tool:
ifndef MODULE
	pytest test/tool
else
	pytest test/tool/test_$(MODULE).py --maxfail=1
endif

.PHONY: test-modal
test-modal:
	blender --window-geometry 0 0 1920 1080 --enable-event-simulate --python test/modal/test_modal.py

# Reregistering test is not added to the standard test suite because during unregister
# Blender removes all Bonsai dependencies breaking dev-environment symlinks.
.PHONY: test-reregister
test-reregister:
	blender --python scripts/reregister_bonsai.py

.PHONY: coverage
coverage:
	coverage run --source bonsai.core -m pytest -p no:pytest-blender test/core
	coverage html
	xdg-open htmlcov/index.html

.PHONY: license
license:
	copyright-header --license GPL3 --copyright-holder "Dion Moult <dion@thinkmoult.com>" --copyright-year "2022" --copyright-software "Bonsai" --copyright-software-description "OpenBIM Blender Add-on" -a ./ -o ./

.PHONY: clean
clean:
	rm -rf dist
	rm -rf htmlcov

.PHONY: dev
dev:
	blender -p setup_pytest.py
