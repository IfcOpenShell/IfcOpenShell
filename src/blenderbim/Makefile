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

ifeq ($(PLATFORM), linux)
PYPI_PLATFORM:=--platform manylinux_2_17_x86_64
ifeq ($(PYVERSION), py39)
HPPFCL_URL:=https://anaconda.org/conda-forge/hpp-fcl/2.3.4/download/linux-64/hpp-fcl-2.3.4-py39h40a70d0_0.conda
EIGENPY_URL:=https://anaconda.org/conda-forge/eigenpy/3.1.0/download/linux-64/eigenpy-3.1.0-py39hdfdd6bb_0.conda
BOOST_URL:=https://anaconda.org/conda-forge/boost/1.78.0/download/linux-64/boost-1.78.0-py39h7c9e3ff_4.tar.bz2
QHULL_URL:=https://anaconda.org/conda-forge/qhull/2020.2/download/linux-64/qhull-2020.2-h4bd325d_2.tar.bz2
LXML_URL:=https://files.pythonhosted.org/packages/19/d9/a69c6aff5673554df48120565a14a50eaa41d29ae03b02faa0b023666318/lxml-4.6.3-cp39-cp39-manylinux2014_x86_64.whl
SHAPELY_URL:=https://files.pythonhosted.org/packages/2d/f2/8ec281d357e8bb7d08dc8d727f0e4c8ef3dae7d3fa75c69c8e452bb82d50/shapely-2.0.1-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
PILLOW_URL:=https://files.pythonhosted.org/packages/01/61/3ff85fb4bb596ce3d223c8fcf93c8df5c12bc8899dfb4fb3cb1c5b20dd5f/Pillow-9.2.0-cp39-cp39-manylinux_2_28_x86_64.whl
endif
ifeq ($(PYVERSION), py310)
HPPFCL_URL:=https://anaconda.org/conda-forge/hpp-fcl/2.3.4/download/linux-64/hpp-fcl-2.3.4-py310h995690b_0.conda
EIGENPY_URL:=https://anaconda.org/conda-forge/eigenpy/3.1.0/download/linux-64/eigenpy-3.1.0-py310hf02b7e0_0.conda
BOOST_URL:=https://anaconda.org/conda-forge/boost/1.78.0/download/linux-64/boost-1.78.0-py310hc4a4660_4.tar.bz2
QHULL_URL:=https://anaconda.org/conda-forge/qhull/2020.2/download/linux-64/qhull-2020.2-h4bd325d_2.tar.bz2
LXML_URL:=https://files.pythonhosted.org/packages/25/1e/19b46d8e8881fe0df2e20945d51919eeb1817836d62a90efa8506530e45c/lxml-4.8.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_24_x86_64.whl
SHAPELY_URL:=https://files.pythonhosted.org/packages/a8/a5/403728b5614b28083f6424dfdefec5fcf58068495fb03bb08532671c642f/shapely-2.0.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
PILLOW_URL:=https://files.pythonhosted.org/packages/f6/51/320986ebd6d46a0e95c2240468ced73153b691ce07617078bcdf30c609ec/Pillow-9.2.0-cp310-cp310-manylinux_2_28_x86_64.whl
endif
ASSIMP_URL:=https://anaconda.org/conda-forge/assimp/5.0.1/download/linux-64/assimp-5.0.1-hedfc422_6.tar.bz2
OCTOMAP_URL:=https://anaconda.org/conda-forge/octomap/1.9.8/download/linux-64/octomap-1.9.8-h924138e_0.tar.bz2
BOOSTCPP_URL:=https://anaconda.org/conda-forge/boost-cpp/1.78.0/download/linux-64/boost-cpp-1.78.0-h6582d0a_3.conda
ZLIB_URL:=https://anaconda.org/conda-forge/zlib/1.2.11/download/linux-64/zlib-1.2.11-h516909a_1010.tar.bz2
endif

ifeq ($(PLATFORM), macos)
PYPI_PLATFORM:=--platform macosx_10_9_x86_64
ifeq ($(PYVERSION), py39)
HPPFCL_URL:=https://anaconda.org/conda-forge/hpp-fcl/2.3.4/download/osx-64/hpp-fcl-2.3.4-py39hd85b194_0.conda
EIGENPY_URL:=https://anaconda.org/conda-forge/eigenpy/3.1.0/download/osx-64/eigenpy-3.1.0-py39hc4d6e28_0.conda
BOOST_URL:=https://anaconda.org/conda-forge/boost/1.78.0/download/osx-64/boost-1.78.0-py39h953a6b8_4.tar.bz2
QHULL_URL:=https://anaconda.org/conda-forge/qhull/2020.2/download/osx-64/qhull-2020.2-h940c156_2.tar.bz2
LXML_URL:=https://files.pythonhosted.org/packages/b8/74/a71f7ad72e8db54ce899efab84507b801660750cbbfa6a39e6717557d36a/lxml-4.6.3-cp39-cp39-macosx_10_9_x86_64.whl
SHAPELY_URL:=https://files.pythonhosted.org/packages/36/a4/7e542a209f862f967d7cb8e939eff155f4294a27d17e16441fb8bdd51a2c/shapely-2.0.1-cp39-cp39-macosx_10_9_x86_64.whl
PILLOW_URL:=https://files.pythonhosted.org/packages/88/7a/ddfe28b485b623361457d4783007c1f9ba83a87f93e7fec32f64793efb6c/Pillow-9.2.0-cp39-cp39-macosx_10_10_x86_64.whl
endif
ifeq ($(PYVERSION), py310)
HPPFCL_URL:=https://anaconda.org/conda-forge/hpp-fcl/2.3.4/download/osx-64/hpp-fcl-2.3.4-py310h1db6f5f_0.conda
EIGENPY_URL:=https://anaconda.org/conda-forge/eigenpy/3.1.0/download/osx-64/eigenpy-3.1.0-py310h43da829_0.conda
BOOST_URL:=https://anaconda.org/conda-forge/boost/1.78.0/download/osx-64/boost-1.78.0-py310h3e792ce_4.tar.bz2
QHULL_URL:=https://anaconda.org/conda-forge/qhull/2020.2/download/osx-64/qhull-2020.2-h940c156_2.tar.bz2
LXML_URL:=https://files.pythonhosted.org/packages/a1/44/17b7dac7a18807d30e2fe10c3328c152808f5464565e230bfd0e77f178c6/lxml-4.8.0-cp310-cp310-macosx_10_15_x86_64.whl
SHAPELY_URL:=https://files.pythonhosted.org/packages/1f/2a/dc3353c2431cf53e8d04bb8fba27e584410ca3435c9c85f76d71bf0c0e80/shapely-2.0.1-cp310-cp310-macosx_10_9_x86_64.whl
PILLOW_URL:=https://files.pythonhosted.org/packages/d8/60/b13c00d403f34110e96c1b5c0afa73ce461efe3fe960c3a7e3e7fe190d82/Pillow-9.2.0-cp310-cp310-macosx_10_10_x86_64.whl
endif
ASSIMP_URL:=https://anaconda.org/conda-forge/assimp/5.0.1/download/osx-64/assimp-5.0.1-h1224e73_6.tar.bz2
OCTOMAP_URL:=https://anaconda.org/conda-forge/octomap/1.9.8/download/osx-64/octomap-1.9.8-hb8565cd_0.tar.bz2
BOOSTCPP_URL:=https://anaconda.org/conda-forge/boost-cpp/1.78.0/download/osx-64/boost-cpp-1.78.0-hf5ba120_3.conda
ZLIB_URL:=https://anaconda.org/conda-forge/zlib/1.2.11/download/osx-64/zlib-1.2.11-h7795811_1010.tar.bz2
endif

ifeq ($(PLATFORM), macosm1)
PYPI_PLATFORM:=--platform macosx_11_0_arm64
ifeq ($(PYVERSION), py39)
HPPFCL_URL:=https://anaconda.org/conda-forge/hpp-fcl/2.3.4/download/osx-arm64/hpp-fcl-2.3.4-py39hc34188a_0.conda
EIGENPY_URL:=https://anaconda.org/conda-forge/eigenpy/3.1.0/download/osx-arm64/eigenpy-3.1.0-py39h13cfc01_0.conda
BOOST_URL:=https://anaconda.org/conda-forge/boost/1.78.0/download/osx-arm64/boost-1.78.0-py39h99de9ae_4.tar.bz2
QHULL_URL:=https://anaconda.org/conda-forge/qhull/2020.2/download/osx-arm64/qhull-2020.2-hc021e02_2.tar.bz2
LXML_URL:=https://anaconda.org/conda-forge/lxml/4.9.1/download/osx-arm64/lxml-4.9.1-py39h9eb174b_0.tar.bz2
SHAPELY_URL:=https://files.pythonhosted.org/packages/ea/aa/45fbd031edf3149cb767d8b9f9db45d5faf0324d743c6b8fb0298cc022d0/shapely-2.0.1-cp39-cp39-macosx_11_0_arm64.whl
PILLOW_URL:=https://files.pythonhosted.org/packages/aa/bc/21097cd891dd2fa02f2b3d767e02e883e026482e59d29975d1bc30024aa3/Pillow-9.2.0-cp39-cp39-macosx_11_0_arm64.whl
endif
ifeq ($(PYVERSION), py310)
HPPFCL_URL:=https://anaconda.org/conda-forge/hpp-fcl/2.3.4/download/osx-arm64/hpp-fcl-2.3.4-py310h46fc4cd_0.conda
EIGENPY_URL:=https://anaconda.org/conda-forge/eigenpy/3.1.0/download/osx-arm64/eigenpy-3.1.0-py310ha2643af_0.conda
BOOST_URL:=https://anaconda.org/conda-forge/boost/1.78.0/download/osx-arm64/boost-1.78.0-py310h629746b_4.tar.bz2
QHULL_URL:=https://anaconda.org/conda-forge/qhull/2020.2/download/osx-arm64/qhull-2020.2-hc021e02_2.tar.bz2
LXML_URL:=https://anaconda.org/conda-forge/lxml/4.9.1/download/osx-arm64/lxml-4.9.1-py310h02f21da_0.tar.bz2
SHAPELY_URL:=https://files.pythonhosted.org/packages/ec/41/d59208743e737184e1b403e95a937aebb022b8459e99efbcd5208fc8be46/shapely-2.0.1-cp310-cp310-macosx_11_0_arm64.whl
PILLOW_URL:=https://files.pythonhosted.org/packages/0c/5f/117b653cad585f3aedfe0de996c292e67d4b020ed77f652e5a6c8c24f908/Pillow-9.2.0-cp310-cp310-macosx_11_0_arm64.whl
endif
ASSIMP_URL:=https://anaconda.org/conda-forge/assimp/5.0.1/download/osx-arm64/assimp-5.0.1-h0f81e16_7.tar.bz2
OCTOMAP_URL:=https://anaconda.org/conda-forge/octomap/1.9.8/download/osx-arm64/octomap-1.9.8-hffc8910_0.tar.bz2
BOOSTCPP_URL:=https://anaconda.org/conda-forge/boost-cpp/1.78.0/download/osx-arm64/boost-cpp-1.78.0-h9ed8d21_3.conda
ZLIB_URL:=https://anaconda.org/conda-forge/zlib/1.2.11/download/osx-arm64/zlib-1.2.11-h90dfc92_1014.tar.bz2
endif

ifeq ($(PLATFORM), win)
PYPI_PLATFORM:=--platform win_amd64
ifeq ($(PYVERSION), py39)
HPPFCL_URL:=https://anaconda.org/conda-forge/hpp-fcl/2.3.4/download/win-64/hpp-fcl-2.3.4-py39h39b25cb_0.conda
EIGENPY_URL:=https://anaconda.org/conda-forge/eigenpy/3.1.0/download/win-64/eigenpy-3.1.0-py39hb6c915b_0.conda
BOOST_URL:=https://anaconda.org/conda-forge/boost/1.78.0/download/win-64/boost-1.78.0-py39hea4d8d1_4.tar.bz2
LXML_URL:=https://files.pythonhosted.org/packages/72/d4/426ecb8849c47c3e370c87aa0ac05d85768df917ffea27fcd6686a5e6495/lxml-4.6.3-cp39-cp39-win_amd64.whl
SHAPELY_URL:=https://files.pythonhosted.org/packages/a7/ae/eab645c4075093584b7a65ab71cb8ff4563a015bd935c9b55dba14b2c1eb/shapely-2.0.1-cp39-cp39-win_amd64.whl
PILLOW_URL:=https://files.pythonhosted.org/packages/19/3f/b4d4bcf05dbcbe07f2e9613a8f4180c297395e73a91d8ad22c32c6624f8c/Pillow-9.2.0-cp39-cp39-win_amd64.whl
endif
ifeq ($(PYVERSION), py310)
HPPFCL_URL:=https://anaconda.org/conda-forge/hpp-fcl/2.3.4/download/win-64/hpp-fcl-2.3.4-py310heb59267_0.conda
EIGENPY_URL:=https://anaconda.org/conda-forge/eigenpy/3.1.0/download/win-64/eigenpy-3.1.0-py310hd146abe_0.conda
BOOST_URL:=https://anaconda.org/conda-forge/boost/1.78.0/download/win-64/boost-1.78.0-py310h220cb41_4.tar.bz2
LXML_URL:=https://files.pythonhosted.org/packages/f6/71/65c80a4caa1617a4c6e8fe1500cebb179db96232e2f623bfe6a1f4294e39/lxml-4.8.0-cp310-cp310-win_amd64.whl
SHAPELY_URL:=https://files.pythonhosted.org/packages/81/8a/7ac076a86b2632f1872284c5e60ed5f2fc26094875a85b35d9fa17b52504/shapely-2.0.1-cp310-cp310-win_amd64.whl
PILLOW_URL:=https://files.pythonhosted.org/packages/02/55/67a3c17b9e7d972ed8c246f104da99ca4f3ea42fba566697e479011b84b6/Pillow-9.2.0-cp310-cp310-win_amd64.whl
endif
ASSIMP_URL:=https://anaconda.org/conda-forge/assimp/5.0.1/download/win-64/assimp-5.0.1-hc2aa0de_6.tar.bz2
OCTOMAP_URL:=https://anaconda.org/conda-forge/octomap/1.9.8/download/win-64/octomap-1.9.8-h91493d7_0.tar.bz2
BOOSTCPP_URL:=https://anaconda.org/conda-forge/boost-cpp/1.78.0/download/win-64/boost-cpp-1.78.0-h9f4b32c_3.conda
ZLIB_URL:=https://anaconda.org/conda-forge/zlib/1.2.11/download/win-64/zlib-1.2.11-h62dcd97_1010.tar.bz2
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
	cd dist/working && wget https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-$(PYNUMBER)-v0.7.0-fdb8ea1-$(PLATFORM)64.zip
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
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifcopenshell-python/ifcopenshell/util/* dist/blenderbim/libs/site/packages/ifcopenshell/util/
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifcopenshell-python/ifcopenshell/api/* dist/blenderbim/libs/site/packages/ifcopenshell/api/
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
	# Provides IFCCOBie functionality
	cp -r dist/working/IfcOpenShell-0.7.0/src/ifccobie/* dist/blenderbim/libs/site/packages/
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
	cd dist/working && . env/bin/activate && $(PIP) install openpyxl --target=./site-packages
	cd dist/working && . env/bin/activate && $(PIP) install odfpy --target=./site-packages
	# Required by IFCCityJSON
	cd dist/working && . env/bin/activate && $(PIP) install cjio --target=./site-packages
	# Provides express rule validation for ifcopenshell.validate
	cd dist/working && . env/bin/activate && $(PIP) install pytest --target=./site-packages
	# Provides Brickschema functionality
	cd dist/working && . env/bin/activate && $(PIP) install brickschema[persistence] --target=./site-packages
	cp -r dist/working/site-packages/* dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by IFCClash
	mkdir dist/working
	cd dist/working && wget $(HPPFCL_URL)
	cd dist/working && unzip hpp-fcl*
	cd dist/working && tar -I zstd -xvf pkg*
ifeq ($(PLATFORM), linux)
	cp -r dist/working/lib/$(PYLIBDIR)/site-packages/hppfcl dist/blenderbim/libs/site/packages/
	cp -r dist/working/lib/*.so* dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macos)
	cp -r dist/working/lib/$(PYLIBDIR)/site-packages/hppfcl dist/blenderbim/libs/site/packages/
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macosm1)
	cp -r dist/working/lib/$(PYLIBDIR)/site-packages/hppfcl dist/blenderbim/libs/site/packages/
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), win)
	cp -r dist/working/Lib/site-packages/hppfcl dist/blenderbim/libs/site/packages/
	cp -r dist/working/Library/bin/*.dll dist/blenderbim/libs/site/packages/hppfcl/
endif
	rm -rf dist/working

	# Required by hpp-fcl
	mkdir dist/working
	cd dist/working && wget $(ASSIMP_URL)
	cd dist/working && tar -xf assimp*
ifeq ($(PLATFORM), linux)
	cp -r dist/working/lib/*.so* dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macos)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macosm1)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), win)
	cp -r dist/working/Library/bin/*.dll dist/blenderbim/libs/site/packages/hppfcl/
endif
	rm -rf dist/working

	# Required by hpp-fcl except on Windows
ifneq ($(PLATFORM), win)
	mkdir dist/working
	cd dist/working && wget $(QHULL_URL)
	cd dist/working && tar -xf qhull*
ifeq ($(PLATFORM), linux)
	cp -r dist/working/lib/*.so* dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macos)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macosm1)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
	rm -rf dist/working
endif

	# Required by hpp-fcl
	mkdir dist/working
	cd dist/working && wget $(EIGENPY_URL)
	cd dist/working && unzip eigenpy*
	cd dist/working && tar -I zstd -xvf pkg*
ifeq ($(PLATFORM), linux)
	cp -r dist/working/lib/*.so* dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macos)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macosm1)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), win)
	cp -r dist/working/Library/bin/*.dll dist/blenderbim/libs/site/packages/hppfcl/
endif
	rm -rf dist/working

	# Required by hpp-fcl
	mkdir dist/working
	cd dist/working && wget $(OCTOMAP_URL)
	cd dist/working && tar -xf octomap*
ifeq ($(PLATFORM), linux)
	cp -r dist/working/lib/*.so* dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macos)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macosm1)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), win)
	# Uh, do nothing, apparently? No DLLs are shipped.
endif
	rm -rf dist/working

	# Required by hpp-fcl
	mkdir dist/working
	cd dist/working && wget $(BOOST_URL)
	cd dist/working && tar -xf boost*
ifeq ($(PLATFORM), linux)
	cp -r dist/working/lib/*.so* dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macos)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macosm1)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), win)
	cp -r dist/working/Library/bin/*.dll dist/blenderbim/libs/site/packages/hppfcl/
endif
	rm -rf dist/working

	# Required by hpp-fcl
	mkdir dist/working
	cd dist/working && wget $(BOOSTCPP_URL)
	cd dist/working && unzip boost-cpp*
	cd dist/working && tar -I zstd -xvf pkg*
ifeq ($(PLATFORM), linux)
	cp -r dist/working/lib/libboost_serialization.so* dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macos)
	cp -r dist/working/lib/libboost_serialization.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macosm1)
	cp -r dist/working/lib/libboost_serialization.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), win)
	cp -r dist/working/Library/bin/boost_serialization.dll dist/blenderbim/libs/site/packages/hppfcl/
endif
	rm -rf dist/working

	# Required by hpp-fcl
	mkdir dist/working
	cd dist/working && wget $(ZLIB_URL)
	cd dist/working && tar -xf zlib*
ifeq ($(PLATFORM), linux)
	cp -r dist/working/lib/*.so* dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macos)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), macosm1)
	cp -r dist/working/lib/*.dylib dist/blenderbim/libs/
endif
ifeq ($(PLATFORM), win)
	cp -r dist/working/Library/bin/*.dll dist/blenderbim/libs/site/packages/hppfcl/
endif
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

	# Required by IFCCOBie for XLSX support
	# TODO: see if we can replace this with openpyxl which does both read/write
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/0c/bc/82d6783f83f65f56d8b77d052773c4a2f952fa86385f0cd54e1e006658d7/XlsxWriter-1.2.9.tar.gz
	cd dist/working && tar -xzvf XlsxWriter*
	cd dist/working/XlsxWriter-1.2.9/ && cp -r xlsxwriter ../../blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by augin
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/76/b4/b7baffbda025efd5dc8fcd8d2e953e3aa939c236a484084fa8f4c3588ee9/boto3-1.17.17.tar.gz
	cd dist/working && tar -xzvf boto3*
	cd dist/working/boto3-1.17.17/ && cp -r boto3 ../../blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by boto3
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/7f/2e/e02fdfd0f0377c4e44e61de27b05d5cfe93575770661ef9ded80ed90fa88/botocore-1.20.17.tar.gz
	cd dist/working && tar -xzvf botocore*
	cd dist/working/botocore-1.20.17/ && cp -r botocore ../../blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by boto3
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/3c/56/3f325b1eef9791759784aa5046a8f6a1aff8f7c898a2e34506771d3b99d8/jmespath-0.10.0.tar.gz
	cd dist/working && tar -xzvf jmespath*
	cd dist/working/jmespath-0.10.0/ && cp -r jmespath ../../blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by boto3
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/08/e1/3ee2096ebaeeb8c186d20ed16c8faf4a503913e5c9a0e14cd6b8ffc405a3/s3transfer-0.3.4.tar.gz
	cd dist/working && tar -xzvf s3transfer*
	cd dist/working/s3transfer-0.3.4/ && cp -r s3transfer ../../blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides IFCJSON functionality
	mkdir dist/working
	cd dist/working && wget https://github.com/IFCJSON-Team/IFC2JSON_python/archive/master.zip
	cd dist/working && unzip master.zip
	cp -r dist/working/IFC2JSON_python-master/file_converters/ifcjson dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides OpenLCA functionality
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/85/33/f91b96e9e8608ff65a003b692e8a9cdd60f2178f60617e5b1d21334c009c/olca-ipc-0.0.10.tar.gz
	cd dist/working && tar -xzvf olca-ipc*
	cd dist/working/olca-ipc-0.0.10/ && cp -r olca ../../blenderbim/libs/site/packages/
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
	cd dist/working && wget https://blenderbim.org/builds/pkg_resources.tar.gz
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

	# Remove dependencies also bundled with Blender
	rm -rf dist/blenderbim/libs/site/packages/numpy
	rm -rf dist/blenderbim/libs/site/packages/numpy.libs

	cd dist/blenderbim && $(SED) "s/999999/$(VERSION)/" __init__.py
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
