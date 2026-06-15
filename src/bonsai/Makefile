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

SHELL := sh
PYTHON:=python3
PIP:=pip3
PATCH:=patch
SED:=sed -i
VENV_ACTIVATE:=bin/activate

ifeq ($(OS),Windows_NT)
HOSTOS:=win
PYTHON:=python
VENV_ACTIVATE:=Scripts/activate
else
UNAME_S:=$(shell uname -s)
ifeq ($(UNAME_S),Linux)
HOSTOS:=linux
endif
ifeq ($(UNAME_S),Darwin)
HOSTOS:=macos
PYTHON:=python3
PATCH:=patch -d
SED:=sed -i '' -e
endif
endif

IS_STABLE:=FALSE
VERSION:=$(shell cat ../../VERSION)
VERSION_MAJOR:=$(shell cat '../../VERSION' | cut -d '.' -f 1)
VERSION_MINOR:=$(shell cat '../../VERSION' | cut -d '.' -f 2)
VERSION_PATCH:=$(shell cat '../../VERSION' | cut -d '.' -f 3)
VERSION_DATE:=$(shell date '+%y%m%d')
LAST_COMMIT_HASH:=$(shell git rev-parse HEAD)
LAST_COMMIT_DATE:=$(shell git show -s --format=%cI)
LAST_GIT_BRANCH:=$(shell git rev-parse --abbrev-ref HEAD)
PYPI_IMP:=cp

ifdef PYVERSION
SUPPORTED_PYVERSIONS := py311 py312 py313

ifeq ($(filter $(PYVERSION),$(SUPPORTED_PYVERSIONS)),)
$(error Unsupported PYVERSION=$(PYVERSION). Must be one of $(SUPPORTED_PYVERSIONS))
endif

PYMINOR:=$(subst py3,,$(PYVERSION))
PYLIBDIR:=python3.$(PYMINOR)
PYNUMBER:=3$(PYMINOR)
PYPI_VERSION:=3.$(PYMINOR)
endif # def PYVERSION

IFCMERGE_VERSION:=2026-04-07

ifdef PLATFORM
SUPPORTED_PLATFORMS := linux macos macosm1 win

ifeq ($(filter $(PLATFORM),$(SUPPORTED_PLATFORMS)),)
$(error Unsupported PLATFORM=$(PLATFORM). Must be one of $(SUPPORTED_PLATFORMS))
endif

ifeq ($(PLATFORM),macos)
ifeq ($(PYVERSION),py313)
$(error Blender 5.1 with Python 3.13 doesn't support intel macOS.)
endif
endif

ifeq ($(PLATFORM), linux)
PYPI_PLATFORM:=--platform manylinux_2_17_x86_64
BLENDER_PLATFORM:=linux-x64
endif

ifeq ($(PLATFORM), macos)
ifeq ($(PYVERSION), py311)
PYPI_PLATFORM:=--platform macosx_10_10_x86_64
else
PYPI_PLATFORM:=--platform macosx_10_13_x86_64
endif
BLENDER_PLATFORM:=macos-x64
endif

ifeq ($(PLATFORM), macosm1)
PYPI_PLATFORM:=--platform macosx_11_0_arm64
BLENDER_PLATFORM:=macos-arm64
endif

ifeq ($(PLATFORM), win)
PYPI_PLATFORM:=--platform win_amd64
BLENDER_PLATFORM:=windows-x64
endif

endif # def PLATFORM

# Current build commit hash.
OLD:=3e7b739
.PHONY: bump
bump:
ifndef NEW
	$(error ERROR: 'NEW' variable is not set (should be set with new commmit hash). Example use for 'bump' command: 'make bump NEW=0123456'.)
endif
	cd . && $(SED) -b "s/$(OLD)/$(NEW)/" Makefile
	cd ../ifcopenshell-python/ && $(SED) -b "s/$(OLD)/$(NEW)/" Makefile

.PHONY: dist
dist:
ifndef PLATFORM
	$(error PLATFORM is not set. Example values: $(SUPPORTED_PLATFORMS).)
endif
ifndef PYVERSION
	$(error PYVERSION is not set. Example values: $(SUPPORTED_PYVERSIONS). )
endif
	rm -rf build
	mkdir -p build
	mkdir -p dist
	cp -r bonsai build/

	# To scope any build-time dependencies
	cd build && $(PYTHON) -m venv env && . env/$(VENV_ACTIVATE) && $(PIP) install build
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) install wheel

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
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download GitPython --dest=./wheels
	# IfcOpenShell dependency - support for new typing features
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download typing_extensions --dest=./wheels
	# Required by IfcCSV
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download pandas $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
	# Pandas ships with very heavy tests
	# cd build/site-packages/pandas && rm -rf tests
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download openpyxl --dest=./wheels
	# odfpy doesn't come with its own wheel, so whee'l (get it?) create it ourselves!
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) wheel odfpy --wheel-dir=./wheels
	# Required by IFCCityJSON
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download "cjio >=0.8, <0.10" --dest=./wheels
	# Required in general for sorting all sorts of stuff in a nice way
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download natsort --dest=./wheels
	# Provides express rule validation for ifcopenshell.validate
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download pytest --dest=./wheels
	# Provides Brickschema functionality
	# Is not platform specific but has platform specific dependencies.
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download "brickschema[persistence]==0.7.6a2" $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
	# Required for SVG to DXF conversion
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download ezdxf $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
	# Required by bcf
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download xsdata --dest=./wheels
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download xmlschema --dest=./wheels
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download elementpath --dest=./wheels
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download six --dest=./wheels
	# Required by drawing module
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download lxml $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
	# Required by drawing module for markdown hyperlinks in annotations
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download markdown-it-py --dest=./wheels
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download mdurl --dest=./wheels
	# Required by qto and drawing module
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download shapely $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
	# Required by the BIM type manager thumbnail generator
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download pillow $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
	# Provides mustache templating in construction docs and web UI data
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download pystache --dest=./wheels
	# Provides SVG export in construction documentation
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download svgwrite --dest=./wheels
	# Provides fuzzy date parsing for construction sequencing
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download python-dateutil --dest=./wheels
	# Provides duration parsing for construction sequencing
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download isodate --dest=./wheels
	# Provides networkx graph analysis for project dependency calculations
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download networkx --dest=./wheels
	# Required by IFCDiff
	# Pinned <9.1: deepdiff 9.1.0 adds cachebox<6,>=5.2 which only ships macOS x86_64
	# wheels for macosx_10_12+ and is incompatible with our macos py311 --platform
	# macosx_10_10_x86_64 target. Revisit once the macos py311 platform tag is bumped
	# to 10_13 (matching py312/py313).
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download "deepdiff<9.1" --dest=./wheels
	# Required by IFCCSV and ifcopenshell.util.selector
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download lark --dest=./wheels
	# Required by IFC4D
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download PyP6Xer --dest=./wheels
	# Required by web module
	# Is not platform specific but has platform specific dependencies.
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download python-socketio[asyncio_client] $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download aiohttp $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
	# Required to access platform specific paths
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download platformdirs --dest=./wheels
	# Required by light module
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download pytz --dest=./wheels
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download tzfpy $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
	# pyradiance is using different platform versions than defaults in our makefile.
ifeq ($(PLATFORM), linux)
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download pyradiance --platform manylinux_2_28_x86_64 --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
else ifeq ($(PLATFORM), macos)
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download pyradiance --platform macosx_10_13_x86_64 --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
else
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download pyradiance $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels
endif
	# Required by ifctester web ui.
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) download flask $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=./wheels

	# jQuery is required for web UI functionality
	cd build/bonsai/bim/data/webui/static/js/ && wget https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js

	# Provides jsgantt-improved supports for web-based construction sequencing gantt charts
	cd build/bonsai/bim/data/gantt/ && wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js
	cd build/bonsai/bim/data/gantt/ && wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css

	# Provides IFCJSON functionality
	# TODO: Use official repo, once https://github.com/IFCJSON-Team/IFC2JSON_python/pull/8 is merged.
	cd build && . env/$(VENV_ACTIVATE) && $(PYTHON) -m pip wheel "git+https://github.com/Andrej730/IFC2JSON_python.git@pyproject_toml" --no-deps -w wheels/

	# Brickschema requires pkg_resources which is provided by Blender.
	# Provides Brickschema functionality
	# For now lets bundle the latest nightly schema
	cd build/bonsai/bim/data/brick/ && wget https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl

	# Required for hipped roof generation
	cd build && . env/$(VENV_ACTIVATE) && $(PYTHON) -m pip wheel "git+https://github.com/prochitecture/bpypolyskel" --no-deps -w wheels/

	# folder for executable files
	mkdir -p build/bonsai/libs/bin

	# required for three-way git merging
ifeq ($(PLATFORM), win)
	cd build/bonsai/libs/bin && wget https://github.com/brunopostle/ifcmerge/releases/download/$(IFCMERGE_VERSION)/ifcmerge.exe
else
	cd build/bonsai/libs/bin && wget https://raw.githubusercontent.com/brunopostle/ifcmerge/$(IFCMERGE_VERSION)/ifcmerge && chmod +x ifcmerge
endif

	# Generate translations module for Bonsai build
	git clone https://github.com/IfcOpenShell/bonsai-translations.git build/working
	$(PYTHON) scripts/bonsai_translations.py -i "build/working" -o "build/bonsai"
	rm -rf build/working

	# Remove dependencies also bundled with Blender
	rm -rf build/wheels/numpy*

	cp pyproject.toml build/
ifeq ($(IS_STABLE), TRUE)
	$(SED) "s/0.0.0/$(VERSION)/" build/bonsai/blender_manifest.toml
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' build/pyproject.toml
else
	$(SED) "s/0.0.0/$(VERSION)-alpha$(VERSION_DATE)/" build/bonsai/blender_manifest.toml
	$(SED) "s/8888888/$(LAST_COMMIT_HASH)/" build/bonsai/__init__.py
	$(SED) "s/9999999/$(LAST_COMMIT_DATE)/" build/bonsai/__init__.py
	$(SED) "s/7777777/$(LAST_GIT_BRANCH)/" build/bonsai/__init__.py
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)-alpha$(VERSION_DATE)"/' build/pyproject.toml
endif

# Blender 5.1+ requires Python 3.13.
ifeq ($(PYVERSION), py313)
	$(SED) 's/blender_version_min = "4\.2\.0"/blender_version_min = "5.1.0"/' build/bonsai/blender_manifest.toml
endif

	$(SED) "s/os-arch/$(BLENDER_PLATFORM)/" build/bonsai/blender_manifest.toml

	# Provides bonsai Add-on functionality
ifeq ($(IS_STABLE), TRUE)
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' build/pyproject.toml
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)a$(VERSION_DATE)"/' build/pyproject.toml
endif
	cd build && . env/$(VENV_ACTIVATE) && $(PYTHON) -m build
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
	cd build && zip -r bonsai_$(PYVERSION)-$(VERSION)-$(BLENDER_PLATFORM).zip ./bonsai
else
	cd build && zip -r bonsai_$(PYVERSION)-$(VERSION)-alpha$(VERSION_DATE)-$(BLENDER_PLATFORM).zip ./bonsai
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
	blender --enable-event-simulate --python test/modal/test_modal.py --window-maximized

# Reregistering test is not added to the standard test suite because during unregister
# Blender removes all Bonsai dependencies breaking dev-environment symlinks.
.PHONY: test-reregister
test-reregister:
	blender --python scripts/reregister_bonsai.py

.PHONY: qa
qa:
	black .
	pylint ./* --output-format=colorized --disable all --enable E --disable import-error

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
