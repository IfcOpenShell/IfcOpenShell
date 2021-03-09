VERSION:=`date '+%y%m%d'`
PYVERSION:=py37

ifeq ($(PLATFORM), win)
ifeq ($(PYVERSION), py37)
PYTHONOCC_URL:=https://anaconda.org/DLR-SC/pythonocc-core/0.17.3/download/win-64/pythonocc-core-0.17.3-py37he980bc4_10.tar.bz2
OCE_URL:=https://anaconda.org/DLR-SC/oce/0.17.2/download/win-64/oce-0.17.2-he980bc4_14.tar.bz2
TBB_URL:=https://anaconda.org/DLR-SC/tbb/2019.5/download/win-64/tbb-2019.5-he980bc4_0.tar.bz2
endif
ifeq ($(PYVERSION), py39)
PYTHONOCC_URL:=https://anaconda.org/conda-forge/pythonocc-core/7.4.1/download/win-64/pythonocc-core-7.4.1-py39h3d1c7c5_0.tar.bz2
OCE_URL:=https://anaconda.org/conda-forge/occt/7.4.0/download/win-64/occt-7.4.0-h823b557_3.tar.bz2
TBB_URL:=https://anaconda.org/conda-forge/tbb/2020.2/download/win-64/tbb-2020.2-h2d74725_4.tar.bz2
endif
endif

ifeq ($(PLATFORM), macos)
ifeq ($(PYVERSION), py37)
PYTHONOCC_URL:=https://anaconda.org/DLR-SC/pythonocc-core/0.17.3/download/osx-64/pythonocc-core-0.17.3-py37h04f5b5a_10.tar.bz2
OCE_URL:=https://anaconda.org/DLR-SC/oce/0.17.2/download/osx-64/oce-0.17.2-h04f5b5a_12.tar.bz2
TBB_URL:=https://anaconda.org/DLR-SC/tbb/4.3.6/download/osx-64/tbb-4.3.6-0.tar.bz2
endif
ifeq ($(PYVERSION), py39)
PYTHONOCC_URL:=https://anaconda.org/conda-forge/pythonocc-core/7.4.1/download/osx-64/pythonocc-core-7.4.1-py39h4d29fe3_0.tar.bz2
OCE_URL:=https://anaconda.org/conda-forge/occt/7.4.0/download/osx-64/occt-7.4.0-hb9b6dc7_3.tar.bz2
TBB_URL:=https://anaconda.org/conda-forge/tbb/2020.2/download/osx-64/tbb-2020.2-h940c156_4.tar.bz2
endif
endif

ifeq ($(PLATFORM), linux)
ifeq ($(PYVERSION), py37)
PYTHONOCC_URL:=https://anaconda.org/DLR-SC/pythonocc-core/0.17.3/download/linux-64/pythonocc-core-0.17.3-py37h6bb024c_10.tar.bz2
OCE_URL:=https://anaconda.org/DLR-SC/oce/0.17.2/download/linux-64/oce-0.17.2-h6bb024c_14.tar.bz2
TBB_URL:=https://anaconda.org/DLR-SC/tbb/4.3.6/download/linux-64/tbb-4.3.6-0.tar.bz2
endif
ifeq ($(PYVERSION), py39)
PYTHONOCC_URL:=https://anaconda.org/conda-forge/pythonocc-core/7.4.1/download/linux-64/pythonocc-core-7.4.1-py39h465cb30_0.tar.bz2
OCE_URL:=https://anaconda.org/conda-forge/occt/7.4.0/download/linux-64/occt-7.4.0-h9121d39_3.tar.bz2
TBB_URL:=https://anaconda.org/conda-forge/tbb/2020.2/download/linux-64/tbb-2020.2-h4bd325d_4.tar.bz2
endif
endif

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
ifeq ($(PYVERSION), py37)
	cd dist/working && wget https://s3.amazonaws.com/ifcopenshell-builds/ifcblender-python-37-v0.6.0-517b819-$(PLATFORM)64.zip
endif
ifeq ($(PYVERSION), py39)
	cd dist/working && wget https://s3.amazonaws.com/ifcopenshell-builds/ifcblender-python-39-v0.6.0-517b819-$(PLATFORM)64.zip
endif
	cd dist/working && unzip ifcblender*
	cp -r dist/working/io_import_scene_ifc/ifcopenshell dist/blenderbim/libs/site/packages/

	# See bug #812
	cd dist/working && wget https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.6.0/src/ifcblenderexport/occ_utils.py
	cd dist/working && mv occ_utils.py ../blenderbim/libs/site/packages/ifcopenshell/geom/occ_utils.py
	rm -rf dist/working

	# Provides IfcConvert for construction documentation
	mkdir dist/working
	cd dist/working && wget https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.6.0-517b819-$(PLATFORM)64.zip
	cd dist/working && unzip IfcConvert*
ifeq ($(PLATFORM), win)
	cp -r dist/working/IfcConvert.exe dist/blenderbim/libs/
else
	cp -r dist/working/IfcConvert dist/blenderbim/libs/
endif
	rm -rf dist/working

	# Provides Python OCC functionality for cutting IFC geometry for construction documentation
	mkdir dist/working
	cd dist/working && wget $(PYTHONOCC_URL)
	cd dist/working && tar -xjvf pythonocc-core*
ifeq ($(PLATFORM), win)
	cd dist/working && cp -r Lib/site-packages/OCC ../blenderbim/libs/site/packages/
else
ifeq ($(PYVERSION), py37)
	cd dist/working && cp -r lib/python3.7/site-packages/OCC ../blenderbim/libs/site/packages/
endif
ifeq ($(PYVERSION), py39)
	cd dist/working && cp -r lib/python3.9/site-packages/OCC ../blenderbim/libs/site/packages/
endif
endif
	rm -rf dist/working

	# Required by Python OCC
	mkdir dist/working
	cd dist/working && wget $(OCE_URL)
	cd dist/working && tar -xjvf oc*
ifeq ($(PLATFORM), win)
ifeq ($(PYVERSION), py37)
	cd dist/working && cp -r Library/bin/* ../blenderbim/libs/site/packages/OCC/
endif
ifeq ($(PYVERSION), py39)
	cd dist/working && cp -r Library/bin/* ../blenderbim/libs/site/packages/OCC/Core/
endif
else
	# Unix Conda builds of PythonOCC expect OCE libs to have a RPATH of ../../../
	cd dist/working && cp -r lib/* ../blenderbim/libs/
endif
ifeq ($(PLATFORM), linux)
	rm -rf dist/blenderbim/libs/oce-0.17
endif
	rm -rf dist/working

	# Required by OpenCascade
	mkdir dist/working
	cd dist/working && wget $(TBB_URL)
	cd dist/working && tar -xjvf tbb*
ifeq ($(PLATFORM), win)
ifeq ($(PYVERSION), py37)
	cd dist/working && cp -r Library/bin/* ../blenderbim/libs/site/packages/OCC/
endif
ifeq ($(PYVERSION), py39)
	cd dist/working && cp -r Library/bin/* ../blenderbim/libs/site/packages/OCC/Core/
endif
else
	cd dist/working && cp -r lib/* ../blenderbim/libs/
endif
	rm -rf dist/working

ifeq ($(PLATFORM), macos)
	mkdir dist/working
	cd dist/working && wget https://blenderbim.org/builds/patch-blender28-bim-macos.zip
	cd dist/working && unzip patch*
	cd dist/working && cp -r *.dylib ../blenderbim/libs/
	rm -rf dist/working
endif

	# Provides dependencies that are part of IfcOpenShell
	mkdir dist/working
	cd dist/working && wget https://github.com/IfcOpenShell/IfcOpenShell/archive/v0.6.0.zip
	cd dist/working && unzip v0.6.0.zip
	# IfcOpenBot sometimes lags behind, so we hotfix the Python utilities
	cp -r dist/working/IfcOpenShell-0.6.0/src/ifcopenshell-python/ifcopenshell/util/* dist/blenderbim/libs/site/packages/ifcopenshell/util/
	# Provides bcf functionality
	cp -r dist/working/IfcOpenShell-0.6.0/src/bcf/bcf dist/blenderbim/libs/site/packages/
	# Provides IFCClash functionality
	cp -r dist/working/IfcOpenShell-0.6.0/src/ifcclash/* dist/blenderbim/libs/site/packages/
	# Provides BIMTester functionality
	cp -r dist/working/IfcOpenShell-0.6.0/src/ifcbimtester/bimtester dist/blenderbim/libs/site/packages/
	# Provides IFCCOBie functionality
	cp -r dist/working/IfcOpenShell-0.6.0/src/ifccobie/* dist/blenderbim/libs/site/packages/
	# Provides IFCDiff functionality
	cp -r dist/working/IfcOpenShell-0.6.0/src/ifcdiff/* dist/blenderbim/libs/site/packages/
	# Provides IFCCSV functionality
	cp -r dist/working/IfcOpenShell-0.6.0/src/ifccsv/* dist/blenderbim/libs/site/packages/
	# Provides IFCPatch functionality
	cp -r dist/working/IfcOpenShell-0.6.0/src/ifcpatch/ifcpatch dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides Mustache templating in construction documentation
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/d6/fd/eb8c212053addd941cc90baac307c00ac246ac3fce7166b86434c6eae963/pystache-0.5.4.tar.gz
	cd dist/working && tar -xzvf pystache*
	cd dist/working/pystache-0.5.4/ && python setup.py build && cp -r build/lib/pystache ../../blenderbim/libs/site/packages/
	rm -rf dist/working

	# Provides SVG export in construction documentation
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/79/e8/7eb2ba188eda14a4b47e33b51f3b4978985f4116655c699bcd18c79279b5/svgwrite-1.3.1.zip
	cd dist/working && unzip svgwrite*
	cp -r dist/working/svgwrite-1.3.1/svgwrite dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by IFCDiff
	mkdir dist/working
	cd dist/working && wget https://github.com/Moult/deepdiff/archive/master.zip
	cd dist/working && unzip master.zip
	cp -r dist/working/deepdiff-master/deepdiff dist/blenderbim/libs/site/packages/
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
	cd dist/working && wget https://files.pythonhosted.org/packages/bb/41/ad9ce53bb978b68af8ae415293cafc89b165b8ad55a593725299dca76729/xmlschema-1.1.1.tar.gz
	cd dist/working && tar -xzvf xmlschema*
	cp -r dist/working/xmlschema-1.1.1/xmlschema dist/blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by bcf
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/12/f9/f9960222d5274944b01391749e55e4dcdf28d8f0c108b64ac931ceff6fdb/elementpath-1.4.3.tar.gz
	cd dist/working && tar -xzvf elementpath*
	cp -r dist/working/elementpath-1.4.3/elementpath dist/blenderbim/libs/site/packages/
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

	# Required by IFCClash
ifeq ($(PLATFORM), linux)
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/0c/fa/00d85f893b02289e2942849d97f8818dde8e2111182e825fb3a735677791/python_fcl-0.0.12-cp37-cp37m-manylinux1_x86_64.whl
	cd dist/working && unzip python_fcl*
	cp -r dist/working/fcl dist/blenderbim/libs/site/packages/
	rm -rf dist/working
endif
ifeq ($(PLATFORM), win)
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/19/e6/6e9f33fb59e8f27c0e1592bd26e644bc92b85c942b072b2d3854105d5887/python_fcl_win32-0.0.12.post3-py3-none-win_amd64.whl
	cd dist/working && unzip python_fcl*
	cp -r dist/working/fcl dist/blenderbim/libs/site/packages/
	rm -rf dist/working
endif

	# Required by BIMTester
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/c8/4b/d0a8c23b6c8985e5544ea96d27105a273ea22051317f850c2cdbf2029fe4/behave-1.2.6.tar.gz
	cd dist/working && tar -xzvf behave*
	cd dist/working/behave-1.2.6/ && cp -r behave ../../blenderbim/libs/site/packages/
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

	# Required by IFCCOBie for XLSX support
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/0c/bc/82d6783f83f65f56d8b77d052773c4a2f952fa86385f0cd54e1e006658d7/XlsxWriter-1.2.9.tar.gz
	cd dist/working && tar -xzvf XlsxWriter*
	cd dist/working/XlsxWriter-1.2.9/ && cp -r xlsxwriter ../../blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by IFCCOBie for ODS support
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/97/73/8ade73f6749177003f7ce3304f524774adda96e6aaab30ea79fd8fda7934/odfpy-1.4.1.tar.gz
	cd dist/working && tar -xzvf odfpy*
	cd dist/working/odfpy-1.4.1/ && cp -r odf ../../blenderbim/libs/site/packages/
	rm -rf dist/working

	# Required by odfpy
	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/a4/5f/f8aa58ca0cf01cbcee728abc9d88bfeb74e95e6cb4334cfd5bed5673ea77/defusedxml-0.6.0.tar.gz
	cd dist/working && tar -xzvf defusedxml*
	cd dist/working/defusedxml-0.6.0/ && cp -r defusedxml ../../blenderbim/libs/site/packages/
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

	cd dist/blenderbim && sed -i "s/999999/$(VERSION)/" __init__.py
	cd dist && zip -r blender28-bim-$(VERSION)-$(PYVERSION)-$(PLATFORM).zip ./*
	rm -rf dist/blenderbim

.PHONY: clean
clean:
	rm -rf dist
