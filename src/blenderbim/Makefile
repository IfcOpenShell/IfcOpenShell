# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020-2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

PYTHON:=python3.11
PIP:=pip3.11
PATCH:=patch
SED:=sed -i
ifeq ($(OS),Windows_NT)
HOSTOS:=win
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
PYVERSION:=py310
PYPI_IMP:=cp

ifeq ($(PYVERSION), py39)
PYLIBDIR:=python3.9
PYNUMBER:=39
PYPI_VERSION:=3.9
endif
ifeq ($(PYVERSION), py310)
PYLIBDIR:=python3.10
PYNUMBER:=310
PYPI_VERSION:=3.10
endif
ifeq ($(PYVERSION), py311)
PYLIBDIR:=python3.11
PYNUMBER:=311
PYPI_VERSION:=3.11
endif
ifeq ($(PYVERSION), py312)
PYLIBDIR:=python3.12
PYNUMBER:=312
PYPI_VERSION:=3.12
endif

ifeq ($(PLATFORM), linux)
PYPI_PLATFORM:=--platform manylinux_2_17_x86_64
endif

ifeq ($(PLATFORM), macos)
PYPI_PLATFORM:=--platform macosx_10_10_x86_64
endif

ifeq ($(PLATFORM), macosm1)
PYPI_PLATFORM:=--platform macosx_11_0_arm64
endif

ifeq ($(PLATFORM), win)
PYPI_PLATFORM:=--platform win_amd64
endif

# Current build commit hash.
OLD:=c18e4ea
.PHONY: bump
bump:
	cd . && $(SED) -b "s/$(OLD)/$(NEW)/" Makefile
	cd ../ifcopenshell-python/ && $(SED) -b "s/$(OLD)/$(NEW)/" Makefile
	cd ../ifcopenshell-python/docs/ifcconvert/ && $(SED) -b "s/$(OLD)/$(NEW)/" installation.rst

.PHONY: dist
dist:
ifndef PLATFORM
	$(error PLATFORM is not set)
endif
	rm -rf dist
	mkdir -p dist/working
	mkdir -p dist/blenderbim
	cp -r blenderbim/* dist/blenderbim/

	# Provides IfcOpenShell Python functionality
	cd ../ifcopenshell-python && make dist PLATFORM=$(PLATFORM)64 PYVERSION=$(PYVERSION) && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	rm -rf dist/working

	# Provides dependencies that are part of IfcOpenShell
	mkdir dist/working
	# Provides bcf functionality
	cd ../bcf && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides IFCClash functionality
	cd ../ifcclash && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides BIMTester functionality
	cd ../ifcbimtester && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides IFCTester functionality
	cd ../ifctester && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides IFCFM functionality
	cd ../ifcfm && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides bSDD functionality
	cd ../bsdd && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides IFCDiff functionality
	cd ../ifcdiff && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides IFCCSV functionality
	cd ../ifccsv && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides IFCPatch functionality
	cd ../ifcpatch && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides IFC4D functionality
	cd ../ifc4d && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides IFC5D functionality
	cd ../ifc5d && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides IFCCityJSON functionality
	cd ../ifccityjson && make dist && cp dist/*.whl ../blenderbim/dist/blenderbim/wheels/
	# Provides IfcGit functionality
	cd dist/working && . env/bin/activate && $(PIP) download GitPython --dest=../blenderbim/wheels
	rm -rf dist/working

	# Provides audio playback for costing
	# mkdir -p dist/working
	# git clone https://github.com/Andrej730/aud.git --branch master-reduced-size --depth 1 dist/working/aud
	# cd dist/working/aud && git checkout 529af208fbcb707c387bfb681d2605c0b6112de7
	# cp -r dist/working/aud/aud dist/blenderbim/libs/site/packages/
	# rm -rf dist/working

	# Provides jsgantt-improved supports for web-based construction sequencing gantt charts
	mkdir dist/working
	cd dist/working && wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js
	cd dist/working && wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css
	cp dist/working/jsgantt* dist/blenderbim/bim/data/gantt/
	rm -rf dist/working

	mkdir dist/working
	cd dist/working && $(PYTHON) -m venv env
	cd dist/working && mkdir site-packages
	# IfcOpenShell dependency - support for new typing features
	cd dist/working && . env/bin/activate && $(PIP) download typing_extensions --dest=../blenderbim/wheels
	# Required by IfcCSV
	cd dist/working && . env/bin/activate && $(PIP) download pandas $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=../blenderbim/wheels
	# Pandas ships with very heavy tests
	# cd dist/working/site-packages/pandas && rm -rf tests
	cd dist/working && . env/bin/activate && $(PIP) download openpyxl --dest=../blenderbim/wheels
	# odfpy doesn't come with its own wheel, so whee'l (get it?) create it ourselves!
	cd dist/working && . env/bin/activate && $(PIP) wheel odfpy --wheel-dir=./
	# Required by IFCCityJSON
	cd dist/working && . env/bin/activate && $(PIP) download cjio --dest=../blenderbim/wheels
	# Provides express rule validation for ifcopenshell.validate
	cd dist/working && . env/bin/activate && $(PIP) download pytest --dest=../blenderbim/wheels
	# Provides Brickschema functionality
	cd dist/working && . env/bin/activate && $(PIP) download "brickschema[persistence]==0.7.6a2" --dest=../blenderbim/wheels
	# Required for SVG to DXF conversion
	cd dist/working && . env/bin/activate && $(PIP) download ezdxf --dest=../blenderbim/wheels
	# Required by bcf
	cd dist/working && . env/bin/activate && $(PIP) download xsdata --dest=../blenderbim/wheels
	cd dist/working && . env/bin/activate && $(PIP) download xmlschema --dest=../blenderbim/wheels
	cd dist/working && . env/bin/activate && $(PIP) download elementpath --dest=../blenderbim/wheels
	cd dist/working && . env/bin/activate && $(PIP) download six --dest=../blenderbim/wheels
	# Required by drawing module
	cd dist/working && . env/bin/activate && $(PIP) download lxml $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=../blenderbim/wheels
	# Required by qto and drawing module
	cd dist/working && . env/bin/activate && $(PIP) download shapely $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=../blenderbim/wheels
	# Required by the BIM type manager thumbnail generator
	cd dist/working && . env/bin/activate && $(PIP) download pillow $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=../blenderbim/wheels
	# Provides mustache templating in construction docs and web UI data
	cd dist/working && . env/bin/activate && $(PIP) download pystache --dest=../blenderbim/wheels
	# Provides SVG export in construction documentation
	cd dist/working && . env/bin/activate && $(PIP) download svgwrite --dest=../blenderbim/wheels
	# Provides fuzzy date parsing for construction sequencing
	cd dist/working && . env/bin/activate && $(PIP) download python-dateutil --dest=../blenderbim/wheels
	# Provides duration parsing for construction sequencing
	cd dist/working && . env/bin/activate && $(PIP) download isodate --dest=../blenderbim/wheels
	# Provides networkx graph analysis for project dependency calculations
	cd dist/working && . env/bin/activate && $(PIP) download networkx --dest=../blenderbim/wheels
	# Required by IFCDiff
	cd dist/working && . env/bin/activate && $(PIP) download deepdiff --dest=../blenderbim/wheels
	# Required by IFCCSV and ifcopenshell.util.selector
	cd dist/working && . env/bin/activate && $(PIP) download lark --dest=../blenderbim/wheels
	# Required by IFC4D
	cd dist/working && . env/bin/activate && $(PIP) download PyP6Xer --dest=../blenderbim/wheels
	# Required by web module
	cd dist/working && . env/bin/activate && $(PIP) download python-socketio[asyncio_client] --dest=../blenderbim/wheels
	cd dist/working && . env/bin/activate && $(PIP) download aiohttp --dest=../blenderbim/wheels
	# Required by light module
	cd dist/working && . env/bin/activate && $(PIP) download pytz --dest=../blenderbim/wheels
	cd dist/working && . env/bin/activate && $(PIP) download tzfpy $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=../blenderbim/wheels
	# pyradiance is using different platform versions than defaults in our makefile.
ifeq ($(PLATFORM), linux)
	cd dist/working && . env/bin/activate && $(PIP) download pyradiance --platform manylinux_2_35_x86_64 --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=../blenderbim/wheels
else ifeq ($(PLATFORM), macos)
	cd dist/working && . env/bin/activate && $(PIP) download pyradiance --platform macosx_10_13_x86_64 --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=../blenderbim/wheels
else
	cd dist/working && . env/bin/activate && $(PIP) download pyradiance $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --dest=../blenderbim/wheels
endif
	rm -rf dist/working

	# Provides IFCJSON functionality
	mkdir dist/working
	cd dist/working && wget https://github.com/IFCJSON-Team/IFC2JSON_python/archive/master.zip
	cd dist/working && unzip master.zip
	# IFCJSON doesn't have pyrproject.toml, so we use python command.
	cd dist/working/IFC2JSON_python-master/file_converters/ifcjson && \
		$(PYTHON) -c "from setuptools import setup, find_packages; \
		setup( \
			name='ifcjson', \
			version='0.0.0', \
			author='Jan Brouwer', \
			author_email='jan@brewsky.nl', \
			packages=find_packages(include=['ifcjson*']), \
		)" bdist_wheel
	cp -r dist/working/IFC2JSON_python-master/file_converters/ifcjson/dist/*.whl dist/blenderbim/wheels/
	rm -rf dist/working

	# Brickschema requires pkg_resources which is provided by Blender.
	# Provides Brickschema functionality
	mkdir dist/working
	# For now lets bundle the latest nightly schema
	cd dist/working && wget https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl
	cd dist/working && cp Brick.ttl ../blenderbim/bim/schema/Brick.ttl
	rm -rf dist/working

	# Required for hipped roof generation
	mkdir dist/working
	cd dist/working && wget https://github.com/prochitecture/bpypolyskel/archive/refs/heads/master.zip
	cd dist/working && unzip master.zip
	cp -r dist/working/bpypolyskel-master/bpypolyskel dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required for Desktop icon and file association
	cp -r blenderbim/libs/desktop dist/blenderbim/libs/

	# Generate translations module for BBIM build
	git clone https://github.com/IfcOpenShell/blenderbim-translations.git dist/working
	$(PYTHON) scripts/bbim_translations.py -i "dist/working" -o "dist/blenderbim"
	rm -rf dist/working

	# Remove dependencies also bundled with Blender
	rm -rf dist/blenderbim/wheels/numpy*

ifeq ($(IS_STABLE), TRUE)
	cd dist/blenderbim && $(SED) "s/0, 0, 0/$(VERSION_MAJOR), $(VERSION_MINOR), $(VERSION_PATCH)/" __init__.py
	cd dist/blenderbim && $(SED) "s/0.0.0/$(VERSION)/" blender_manifest.toml
	cd dist && zip -r blenderbim-$(VERSION)-$(PYVERSION)-$(PLATFORM).zip ./*
else
	cd dist/blenderbim && $(SED) "s/0, 0, 0/$(VERSION_MAJOR), $(VERSION_MINOR), $(VERSION_PATCH), $(VERSION_DATE)/" __init__.py
	# Blender manifest version must be semver compatible.
	cd dist/blenderbim && $(SED) "s/0.0.0/$(VERSION)-$(VERSION_DATE)/" blender_manifest.toml
	cd dist/blenderbim && $(SED) "s/8888888/$(LAST_COMMIT_HASH)/" __init__.py
	cd dist && zip -r blenderbim-$(VERSION).$(VERSION_DATE)-$(PYVERSION)-$(PLATFORM).zip ./*
endif
	rm -rf dist/blenderbim

.PHONY: test
test:
	make test-core
	make test-tool
	make test-bim

.PHONY: test-core
test-core:
	pytest -p no:pytest-blender test/core

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
	pytest test/tool/test_$(MODULE).py
endif

.PHONY: qa
qa:
	black .
	pylint ./* --output-format=colorized --disable all --enable E --disable import-error

.PHONY: coverage
coverage:
	coverage run --source blenderbim.core -m pytest -p no:pytest-blender test/core
	coverage html
	xdg-open htmlcov/index.html

.PHONY: license
license:
	copyright-header --license GPL3 --copyright-holder "Dion Moult <dion@thinkmoult.com>" --copyright-year "2022" --copyright-software "BlenderBIM Add-on" --copyright-software-description "OpenBIM Blender Add-on" -a ./ -o ./

.PHONY: clean
clean:
	rm -rf dist
	rm -rf htmlcov

.PHONY: dev
dev:
	blender -p setup_pytest.py
