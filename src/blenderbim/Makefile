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

ifeq ($(PLATFORM), linux)
PYPI_PLATFORM:=--platform manylinux_2_17_x86_64
LXML_ARCH:=manylinux_2_28_x86_64
SHAPELY_ARCH:=manylinux_2_17_x86_64.manylinux2014_x86_64
PILLOW_ARCH:=manylinux_2_28_x86_64
endif

ifeq ($(PLATFORM), macos)
PYPI_PLATFORM:=--platform macosx_10_9_x86_64
SHAPELY_ARCH:=macosx_10_9_x86_64
PILLOW_ARCH:=macosx_10_10_x86_64
ifeq ($(PYVERSION), py39)
LXML_ARCH:=macosx_11_0_x86_64
endif
ifeq ($(PYVERSION), py310)
LXML_ARCH:=macosx_11_0_x86_64
endif
ifeq ($(PYVERSION), py311)
LXML_ARCH:=macosx_11_0_universal2
endif
endif

ifeq ($(PLATFORM), macosm1)
PYPI_PLATFORM:=--platform macosx_11_0_arm64
LXML_ARCH:=macosx_11_0_universal2
SHAPELY_ARCH:=macosx_11_0_arm64
PILLOW_ARCH:=macosx_11_0_arm64
endif

ifeq ($(PLATFORM), win)
PYPI_PLATFORM:=--platform win_amd64
LXML_ARCH:=win_amd64
SHAPELY_ARCH:=win_amd64
PILLOW_ARCH:=win_amd64
endif

LXML_NAME:=lxml
LXML_VER:=4.9.4
SHAPELY_NAME:=shapely
SHAPELY_VER:=2.0.2
PILLOW_NAME:=pillow
PILLOW_PKG_NAME:=Pillow
PILLOW_VER:=9.5.0
SHAPELY_URL:=https://files.pythonhosted.org/packages/cp$(PYNUMBER)/s/$(SHAPELY_NAME)/$(SHAPELY_NAME)-$(SHAPELY_VER)-cp$(PYNUMBER)-cp$(PYNUMBER)-$(SHAPELY_ARCH).whl
PILLOW_URL:=https://files.pythonhosted.org/packages/cp$(PYNUMBER)/p/$(PILLOW_NAME)/$(PILLOW_PKG_NAME)-$(PILLOW_VER)-cp$(PYNUMBER)-cp$(PYNUMBER)-$(PILLOW_ARCH).whl

ifeq ($(PLATFORM), macosm1)
ifeq ($(PYVERSION), py39)
LXML_URL:=https://anaconda.org/conda-forge/lxml/4.9.1/download/osx-arm64/lxml-4.9.1-py39h0520ce3_1.tar.bz2
endif
ifeq ($(PYVERSION), py310)
LXML_URL:=https://anaconda.org/conda-forge/lxml/4.9.1/download/osx-arm64/lxml-4.9.1-py310h02f21da_0.tar.bz2
endif
ifeq ($(PYVERSION), py311)
LXML_URL:=https://anaconda.org/conda-forge/lxml/4.9.1/download/osx-arm64/lxml-4.9.1-py311h246f609_1.tar.bz2
endif
else
LXML_URL:=https://files.pythonhosted.org/packages/cp$(PYNUMBER)/l/$(LXML_NAME)/$(LXML_NAME)-$(LXML_VER)-cp$(PYNUMBER)-cp$(PYNUMBER)-$(LXML_ARCH).whl
endif
$(info $$LXML_URL is [${LXML_URL}])
$(info $$SHAPELY_URL is [${SHAPELY_URL}])
$(info $$PILLOW_URL is [${PILLOW_URL}])

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
	cd dist/working && wget https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-$(PYNUMBER)-v0.7.0-f7c03db-$(PLATFORM)64.zip
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

	# Provides Mustache templating in construction documentation
	# TODO: remove this dependency, it seems overkill and we seem to get by with str replaces
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/3f/e7/8750ba6c6101d6aa5ceeb20c013adf2c6f3554a12c71d75654b468404bfa/pystache-0.6.0.tar.gz
	cd dist/working && tar -xzvf pystache*
	cd dist/working/pystache-0.6.0/ && $(PYTHON) setup.py build && cp -r build/lib/pystache ../../blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides SVG export in construction documentation
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/79/e8/7eb2ba188eda14a4b47e33b51f3b4978985f4116655c699bcd18c79279b5/svgwrite-1.3.1.zip
	cd dist/working && unzip svgwrite*
	cp -r dist/working/svgwrite-1.3.1/svgwrite dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides fuzzy date parsing for construction sequencing
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/be/ed/5bbc91f03fa4c839c4c7360375da77f9659af5f7086b7a7bdda65771c8e0/python-dateutil-2.8.1.tar.gz
	cd dist/working && tar -xzvf python-dateutil*
	cp -r dist/working/python-dateutil-2.8.1/dateutil dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides duration parsing for construction sequencing
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/b1/80/fb8c13a4cd38eb5021dc3741a9e588e4d1de88d895c1910c6fc8a08b7a70/isodate-0.6.0.tar.gz
	cd dist/working && tar -xzvf isodate*
	cp -r dist/working/isodate-0.6.0/src/isodate dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides networkx graph analysis for project dependency calculations
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/b0/21/adfbf6168631e28577e4af9eb9f26d75fe72b2bb1d33762a5f2c425e6c2a/networkx-2.5.1.tar.gz
	cd dist/working && tar -xzvf networkx*
	cp -r dist/working/networkx-2.5.1/networkx dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by networkx
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/4f/51/15a4f6b8154d292e130e5e566c730d8ec6c9802563d58760666f1818ba58/decorator-5.0.9.tar.gz
	cd dist/working && tar -xzvf decorator*
	cp -r dist/working/decorator-5.0.9/src/decorator.py dist/blenderbim/libs/site/packages/
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

	# Required by IFCDiff
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/0f/ca/caead2949fbb824c7142e3774fa841aa853bb4d4331b440da8c8514dfc6f/deepdiff-5.8.1.tar.gz
	cd dist/working && tar -xzvf deepdiff*
	cp -r dist/working/deepdiff-5.8.1/deepdiff dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by deepdiff
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/00/55/ce2cbc6d64034b30cad81a29ba61bdba456f190f5e83c09831304bf68d6b/jsonpickle-1.2.tar.gz
	cd dist/working && tar -xzvf jsonpickle*
	cp -r dist/working/jsonpickle-1.2/jsonpickle dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by deepdiff
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/a3/b7/d4d69641cbe707a45c23b190f2d717466ba5accc4c70b5f7a8a450387895/ordered-set-3.1.1.tar.gz
	cd dist/working && tar -xzvf ordered-set*
	cp -r dist/working/ordered-set-3.1.1/ordered_set.py dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by lark
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/00/32/8076fa13e832bb4dcff379f18f228e5a53412be0631808b9ca2610c0f566/pyparsing-2.4.5.tar.gz
	cd dist/working && tar -xzvf pyparsing*
	cp -r dist/working/pyparsing-2.4.5/pyparsing.py dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by bcf
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/5b/ef/f97c3e1a7efa00e989a793fe15297214fc95ad7d9e3810586bd08ce9f0f3/xmlschema-2.0.2.tar.gz
	cd dist/working && tar -xzvf xmlschema*
	cp -r dist/working/xmlschema-2.0.2/xmlschema dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by bcf
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/ad/c7/17c9d16320d8e2cfdb27d2fd298b5e8f7a3f211025b0c1bc7a39a85bd690/xsdata-22.11.tar.gz
	cd dist/working && tar -xzvf xsdata*
	cp -r dist/working/xsdata-22.11/xsdata dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by bcf
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/11/bc/5afb61dd5d863e5cf77cd952445c50c17e65953405986f19e97e4389692a/elementpath-3.0.2.tar.gz
	cd dist/working && tar -xzvf elementpath*
	cp -r dist/working/elementpath-3.0.2/elementpath dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by bcf
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/21/9f/b251f7f8a76dec1d6651be194dfba8fb8d7781d10ab3987190de8391d08e/six-1.14.0.tar.gz
	cd dist/working && tar -xzvf six*
	cp -r dist/working/six-1.14.0/six.py dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by IFCCSV and ifcopenshell.util.selector
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/18/4d/8d522136c37d9e1ea74062b41b8d5e1318ebf45063ae46ce72ed60af223b/lark-parser-0.8.5.tar.gz
	cd dist/working && tar -xzvf lark-parser*
	cp -r dist/working/lark-parser-0.8.5/lark dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by IFC4D
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/b0/bb/9c4dddd3ca173cb56241cfb2eddfae24690dc676d357ac4cab17d0a36d9d/PyP6Xer-1.13.0.tar.gz
	cd dist/working && tar -xzvf PyP6Xer*
	cp -r dist/working/PyP6Xer-1.13.0/xerparser dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by QTOCalculator
	mkdir dist/working
	cd dist/working && wget $(SHAPELY_URL)
	cd dist/working && cp *.whl shapely.zip && unzip shapely.zip
	cp -r dist/working/shapely dist/blenderbim/libs/site/packages/
ifeq ($(PLATFORM), win)
	cp -r dist/working/shapely.libs dist/blenderbim/libs/site/packages/
endif
ifeq ($(PLATFORM), linux)
	cp -r dist/working/shapely.libs dist/blenderbim/libs/site/packages/
endif
	rm -rf dist/working

	# Required by the BIM tool thumbnail generator
	mkdir dist/working
	cd dist/working && wget $(PILLOW_URL)
	cd dist/working && cp *.whl pillow.zip && unzip pillow.zip
	cp -r dist/working/PIL dist/blenderbim/libs/site/packages/
ifeq ($(PLATFORM), linux)
	cp -r dist/working/Pillow.libs dist/blenderbim/libs/site/packages/
endif
	rm -rf dist/working

	# Required by xerparser and IFC4D
	# TODO: remove this dependency. It's only used to show a progress bar.
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/9f/7b/76c4e5ef1a1b528fcaada4133f972e77d33c252831676cf414119ca6093d/tqdm-4.50.0.tar.gz
	cd dist/working && tar -xzvf tqdm*
	cp -r dist/working/tqdm-4.50.0/tqdm dist/blenderbim/libs/site/packages/
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
	cd dist/working && . env/bin/activate && $(PIP) install "ezdxf" --target=./site-packages
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

	# Required by ids - uh, not any more, but I'm trying it out in the drawing module
ifeq ($(PLATFORM), macosm1)
	# No wheels available for MacOS M1, but turns out this Anaconda build works
	mkdir dist/working
	cd dist/working && wget $(LXML_URL)
	cd dist/working && tar -xf lxml*
	cp -r dist/working/lib/$(PYLIBDIR)/site-packages/lxml dist/blenderbim/libs/site/packages/
	rm -rf dist/working
else
	# Wheels are preferred for other OSes. A first attempt at using Anaconda
	# builds for everything shows it breaks on windows. See #2422.
	mkdir dist/working
	cd dist/working && wget $(LXML_URL)
	cd dist/working && cp *.whl lxml.zip && unzip lxml.zip
	cp -r dist/working/lxml dist/blenderbim/libs/site/packages/
	rm -rf dist/working
endif

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
