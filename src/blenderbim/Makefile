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

PYTHON:=python3.10
PIP:=pip3.10
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

VERSION:=`date '+%y%m%d'`
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

.PHONY: bump
bump:
	cd . && $(SED) "s/$(OLD)/$(NEW)/" Makefile
	cd ../ifcopenshell-python/ && $(SED) "s/$(OLD)/$(NEW)/" Makefile
	cd ../ifcopenshell-python/docs/ifcconvert/ && $(SED) "s/$(OLD)/$(NEW)/" installation.rst
	cd ../ifcopenshell-python/docs/ifcopenshell-python/ && $(SED) "s/$(OLD)/$(NEW)/" installation.rst

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
	cd dist/working && wget https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-$(PYNUMBER)-v0.7.0-c7830e9-$(PLATFORM)64.zip
	cd dist/working && unzip ifcopenshell-python*
	cp -r dist/working/ifcopenshell dist/blenderbim/libs/site/packages/

	# See bug #812
	cd dist/working && wget https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.7.0/src/blenderbim/occ_utils.py
	cd dist/working && mv occ_utils.py ../blenderbim/libs/site/packages/ifcopenshell/geom/occ_utils.py
	rm -rf dist/working

	# Provides dependencies that are part of IfcOpenShell
	mkdir dist/working
	cd dist/working && wget https://github.com/IfcOpenShell/IfcOpenShell/archive/v0.7.0.zip
	cd dist/working && unzip v0.7.0.zip
	# IfcOpenBot sometimes lags behind, so we hotfix the Python utilities
	rm -rf dist/blenderbim/libs/site/packages/ifcopenshell/util/
	rm -rf dist/blenderbim/libs/site/packages/ifcopenshell/api/
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifcopenshell-python/ifcopenshell/util dist/blenderbim/libs/site/packages/ifcopenshell/
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifcopenshell-python/ifcopenshell/api dist/blenderbim/libs/site/packages/ifcopenshell/
	cp dist/working/IfcOpenShell-0.7.0/src/ifcopenshell-python/ifcopenshell/*.py dist/blenderbim/libs/site/packages/ifcopenshell/
	cp dist/working/IfcOpenShell-0.7.0/src/ifcopenshell-python/ifcopenshell/express/rule_executor.py dist/blenderbim/libs/site/packages/ifcopenshell/express/
	# Provides bcf functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/bcf/src/bcf dist/blenderbim/libs/site/packages/
	# Provides IFCClash functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifcclash/ifcclash dist/blenderbim/libs/site/packages/
	# Provides BIMTester functionality
	cd dist/working && $(PYTHON) -m venv env
	cd dist/working && . env/bin/activate && $(PIP) install pybabel
	cd dist/working && . env/bin/activate && $(PIP) install babel
	cd dist/working && . env/bin/activate && ./env/bin/pybabel compile -d ./IfcOpenShell-0.7.0/src/ifcbimtester/bimtester/locale/
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifcbimtester/bimtester dist/blenderbim/libs/site/packages/
	# Provides IFCTester functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifctester/ifctester dist/blenderbim/libs/site/packages/
	# Provides IFCFM functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifcfm/ifcfm dist/blenderbim/libs/site/packages/
	# Provides bSDD functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/bsdd/* dist/blenderbim/libs/site/packages/
	# Provides IFCDiff functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifcdiff/* dist/blenderbim/libs/site/packages/
	# Provides IFCCSV functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifccsv/* dist/blenderbim/libs/site/packages/
	# Provides IFCPatch functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifcpatch/ifcpatch dist/blenderbim/libs/site/packages/
	# Provides IFC4D functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifc4d/ifc4d dist/blenderbim/libs/site/packages/
	# Provides IFC5D functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifc5d/ifc5d dist/blenderbim/libs/site/packages/
	# Provides IFCCityJSON functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifccityjson dist/blenderbim/libs/site/packages/
	# Provides IfcGit functionality
	cd dist/working && . env/bin/activate && $(PIP) install GitPython --target=./site-packages
	cp -r dist/working/site-packages/smmap dist/blenderbim/libs/site/packages/
	cp -r dist/working/site-packages/gitdb dist/blenderbim/libs/site/packages/
	cp -r dist/working/site-packages/git dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides audio playback for costing
	mkdir -p dist/working
	git clone https://github.com/Andrej730/aud.git --branch master-reduced-size --depth 1 dist/working/aud
	cd dist/working/aud && git checkout 529af208fbcb707c387bfb681d2605c0b6112de7
	cp -r dist/working/aud/aud dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides jsgantt-improved supports for web-based construction sequencing gantt charts
	mkdir dist/working
	cd dist/working && wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js
	cd dist/working && wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css
	cp dist/working/jsgantt* dist/blenderbim/bim/data/gantt/
	rm -rf dist/working

	mkdir dist/working
	cd dist/working && $(PYTHON) -m venv env
	cd dist/working && mkdir site-packages
	# Required by IfcCSV
	cd dist/working && . env/bin/activate && $(PIP) install pandas $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --target=./site-packages
	# Pandas ships with very heavy tests
	cd dist/working/site-packages/pandas && rm -rf tests
	cd dist/working && . env/bin/activate && $(PIP) install openpyxl --target=./site-packages
	cd dist/working && . env/bin/activate && $(PIP) install odfpy --target=./site-packages
	# Required by IFCCityJSON
	cd dist/working && . env/bin/activate && $(PIP) install cjio --target=./site-packages
	# Provides express rule validation for ifcopenshell.validate
	cd dist/working && . env/bin/activate && $(PIP) install pytest --target=./site-packages
	# Provides Brickschema functionality
	cd dist/working && . env/bin/activate && $(PIP) install "brickschema[persistence]==0.7.6a2" --target=./site-packages
	# Required for SVG to DXF conversion
	cd dist/working && . env/bin/activate && $(PIP) install ezdxf --target=./site-packages
	# Required by bcf
	cd dist/working && . env/bin/activate && $(PIP) install xsdata --target=./site-packages
	cd dist/working && . env/bin/activate && $(PIP) install xmlschema --target=./site-packages
	cd dist/working && . env/bin/activate && $(PIP) install elementpath --target=./site-packages
	cd dist/working && . env/bin/activate && $(PIP) install six --target=./site-packages
	# Required by drawing module
	cd dist/working && . env/bin/activate && $(PIP) install lxml $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --target=./site-packages
	# Required by qto and drawing module
	cd dist/working && . env/bin/activate && $(PIP) install shapely $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --target=./site-packages
	# Required by the BIM type manager thumbnail generator
	cd dist/working && . env/bin/activate && $(PIP) install pillow $(PYPI_PLATFORM) --python-version $(PYPI_VERSION) --implementation $(PYPI_IMP) --only-binary=:all: --target=./site-packages
	# Provides mustache templating in construction docs and web UI data
	cd dist/working && . env/bin/activate && $(PIP) install pystache --target=./site-packages
	# Provides SVG export in construction documentation
	cd dist/working && . env/bin/activate && $(PIP) install svgwrite --target=./site-packages
	# Provides fuzzy date parsing for construction sequencing
	cd dist/working && . env/bin/activate && $(PIP) install python-dateutil --target=./site-packages
	# Provides duration parsing for construction sequencing
	cd dist/working && . env/bin/activate && $(PIP) install isodate --target=./site-packages
	# Provides networkx graph analysis for project dependency calculations
	cd dist/working && . env/bin/activate && $(PIP) install networkx --target=./site-packages
	# Required by IFCDiff
	cd dist/working && . env/bin/activate && $(PIP) install deepdiff --target=./site-packages
	# Required by IFCCSV and ifcopenshell.util.selector
	cd dist/working && . env/bin/activate && $(PIP) install lark --target=./site-packages
	# Required by IFC4D
	cd dist/working && . env/bin/activate && $(PIP) install PyP6Xer --target=./site-packages
	cp -r dist/working/site-packages/* dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by BIMTester
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/c8/4b/d0a8c23b6c8985e5544ea96d27105a273ea22051317f850c2cdbf2029fe4/behave-1.2.6.tar.gz
	cd dist/working && tar -xzvf behave*
	cd dist/working/behave-1.2.6/ && cp -r behave ../../blenderbim/libs/site/packages/
	# See bug #1294
	cd dist/working/ && wget https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.7.0/src/ifcbimtester/patch/model_core.patch
	cd dist/working/ && wget https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.7.0/src/ifcbimtester/patch/runner_util.patch
	cd dist/working/ && $(PATCH) ../blenderbim/libs/site/packages/behave/model_core.py < model_core.patch
	cd dist/working/ && $(PATCH) ../blenderbim/libs/site/packages/behave/runner_util.py < runner_util.patch
	# See bug #2159
	cd dist/working/ && wget https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.7.0/src/ifcbimtester/patch/junit.patch
	cd dist/working/ && $(PATCH) ../blenderbim/libs/site/packages/behave/reporter/junit.py < junit.patch
	rm -rf dist/working

	# Required by behave
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/f4/65/220bb4075fddb09d5b3ea2c1c1fa66c1c72be9361ec187aab50fa161e576/parse-1.15.0.tar.gz
	cd dist/working && tar -xzvf parse*
	cd dist/working/parse-1.15.0/ && cp parse.py ../../blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by behave
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/2e/79/81bebd1b0446d46733db99d74543b4bb80646ef4c988584bae0862e706bc/parse_type-0.5.2.tar.gz
	cd dist/working && tar -xzvf parse_type*
	cd dist/working/parse_type-0.5.2/ && cp -r parse_type ../../blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides IFCJSON functionality
	mkdir dist/working
	cd dist/working && wget https://github.com/IFCJSON-Team/IFC2JSON_python/archive/master.zip
	cd dist/working && unzip master.zip
	cp -r dist/working/IFC2JSON_python-master/file_converters/ifcjson dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides Brickschema functionality
	mkdir dist/working
	# For now lets bundle the latest nightly schema
	cd dist/working && wget https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl
	cd dist/working && cp Brick.ttl ../blenderbim/bim/schema/Brick.ttl
	rm -rf dist/working

	# Required by brickschema
	# This is a bit of a dodgy one, it should be provided by setuptools which Blender doesn't ship.
	mkdir dist/working
	cd dist/working && wget https://github.com/IfcOpenShell/IfcOpenShell/raw/v0.7.0/src/blenderbim/scripts/pkg_resources.tar.gz
	cd dist/working && tar -xzvf pkg_resources*
	cd dist/working/ && cp -r pkg_resources ../blenderbim/libs/site/packages/
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
	rm -rf dist/blenderbim/libs/site/packages/numpy
	rm -rf dist/blenderbim/libs/site/packages/numpy.libs

	cd dist/blenderbim && $(SED) "s/999999/$(VERSION)/" __init__.py
	cd dist/blenderbim && $(SED) "s/999999/$(VERSION)/" blender_manifest.toml
	cd dist/blenderbim/bim && $(SED) "s/8888888/$(LAST_COMMIT_HASH)/" __init__.py
	cd dist && zip -r blenderbim-$(VERSION)-$(PYVERSION)-$(PLATFORM).zip ./*
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
