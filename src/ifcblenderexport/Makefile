VERSION:=`date '+%y%m%d'`
ifeq ($(PLATFORM), win)
PYTHONOCC_URL:=https://anaconda.org/DLR-SC/pythonocc-core/0.17.3/download/win-64/pythonocc-core-0.17.3-py37he980bc4_10.tar.bz2
OCE_URL:=https://anaconda.org/DLR-SC/oce/0.17.2/download/win-64/oce-0.17.2-he980bc4_14.tar.bz2
TBB_URL:=https://anaconda.org/DLR-SC/tbb/2019.5/download/win-64/tbb-2019.5-he980bc4_0.tar.bz2
endif
ifeq ($(PLATFORM), macos)
PYTHONOCC_URL:=https://anaconda.org/DLR-SC/pythonocc-core/0.17.3/download/osx-64/pythonocc-core-0.17.3-py37h04f5b5a_10.tar.bz2
OCE_URL:=https://anaconda.org/DLR-SC/oce/0.17.2/download/osx-64/oce-0.17.2-h04f5b5a_12.tar.bz2
TBB_URL:=https://anaconda.org/DLR-SC/tbb/4.3.6/download/osx-64/tbb-4.3.6-0.tar.bz2
endif
ifeq ($(PLATFORM), linux)
PYTHONOCC_URL:=https://anaconda.org/DLR-SC/pythonocc-core/0.17.3/download/linux-64/pythonocc-core-0.17.3-py37h6bb024c_10.tar.bz2
OCE_URL:=https://anaconda.org/DLR-SC/oce/0.17.2/download/linux-64/oce-0.17.2-h6bb024c_14.tar.bz2
TBB_URL:=https://anaconda.org/DLR-SC/tbb/4.3.6/download/linux-64/tbb-4.3.6-0.tar.bz2
endif

.PHONY: dist
dist:
ifndef PLATFORM
	$(error PLATFORM is not set)
endif
	rm -rf dist
	mkdir -p dist/working
	mkdir -p dist/blenderbim
ifneq ($(PLATFORM), win)
	mkdir -p dist/lib
endif
	cp -r blenderbim/* dist/blenderbim/

	cd dist/working && wget https://s3.amazonaws.com/ifcopenshell-builds/ifcblender-python-37-v0.6.0-e44221c-$(PLATFORM)64.zip
	cd dist/working && unzip ifcblender*
	cp -r dist/working/io_import_scene_ifc/ifcopenshell dist/
	# See bug #812
	cd dist/working && wget https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.6.0/src/ifcblenderexport/occ_utils.py
	cd dist/working && mv occ_utils.py ../ifcopenshell/geom/occ_utils.py
	rm -rf dist/working

	mkdir dist/working
	cd dist/working && wget $(PYTHONOCC_URL)
	cd dist/working && tar -xjvf pythonocc-core*
ifeq ($(PLATFORM), win)
	cd dist/working && cp -r Lib/site-packages/OCC ../
else
	cd dist/working && cp -r lib/python3.7/site-packages/OCC ../
endif
	rm -rf dist/working

	mkdir dist/working
	cd dist/working && wget $(OCE_URL)
	cd dist/working && tar -xjvf oce*
ifeq ($(PLATFORM), win)
	cd dist/working && cp -r Library/bin/* ../OCC/
else
	cd dist/working && cp -r lib/* ../lib/
endif
	rm -rf dist/working

	mkdir dist/working
	cd dist/working && wget $(TBB_URL)
	cd dist/working && tar -xjvf tbb*
ifeq ($(PLATFORM), win)
	cd dist/working && cp -r Library/bin/* ../OCC/
else
	cd dist/working && cp -r lib/* ../lib/
endif
	rm -rf dist/working

ifeq ($(PLATFORM), macos)
	mkdir dist/working
	cd dist/working && wget https://blenderbim.org/builds/patch-blender28-bim-macos.zip
	cd dist/working && unzip patch*
	cd dist/working && cp -r *.dylib ../lib/
	rm -rf dist/working
endif

	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/d6/fd/eb8c212053addd941cc90baac307c00ac246ac3fce7166b86434c6eae963/pystache-0.5.4.tar.gz
	cd dist/working && tar -xzvf pystache*
	cd dist/working/pystache-0.5.4/ && python setup.py build && cp -r build/lib/pystache ../../
	rm -rf dist/working

	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/79/e8/7eb2ba188eda14a4b47e33b51f3b4978985f4116655c699bcd18c79279b5/svgwrite-1.3.1.zip
	cd dist/working && unzip svgwrite*
	cp -r dist/working/svgwrite-1.3.1/svgwrite dist/
	rm -rf dist/working

	mkdir dist/working
	cd dist/working && wget https://github.com/Moult/deepdiff/archive/master.zip
	cd dist/working && unzip master.zip
	cp -r dist/working/deepdiff-master/deepdiff dist/
	rm -rf dist/working

	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/00/55/ce2cbc6d64034b30cad81a29ba61bdba456f190f5e83c09831304bf68d6b/jsonpickle-1.2.tar.gz
	cd dist/working && tar -xzvf jsonpickle*
	cp -r dist/working/jsonpickle-1.2/jsonpickle dist/
	rm -rf dist/working

	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/a3/b7/d4d69641cbe707a45c23b190f2d717466ba5accc4c70b5f7a8a450387895/ordered-set-3.1.1.tar.gz
	cd dist/working && tar -xzvf ordered-set*
	cp -r dist/working/ordered-set-3.1.1/ordered_set.py dist/
	rm -rf dist/working

	mkdir dist/working
	cd dist/working && wget https://files.pythonhosted.org/packages/00/32/8076fa13e832bb4dcff379f18f228e5a53412be0631808b9ca2610c0f566/pyparsing-2.4.5.tar.gz
	cd dist/working && tar -xzvf pyparsing*
	cp -r dist/working/pyparsing-2.4.5/pyparsing.py dist/
	rm -rf dist/working

	cd dist/ && wget https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.6.0/src/ifcdiff/ifcdiff.py

	cd dist/blenderbim && sed -i "s/999999/$(VERSION)/" __init__.py
	cd dist && zip -r blender28-bim-$(VERSION)-$(PLATFORM).zip ./*
	rm -rf dist/blenderbim
	rm -rf dist/ifcopenshell
	rm -rf dist/OCC
	rm -rf dist/pystache
	rm -rf dist/svgwrite
	rm -rf dist/deepdiff
	rm -rf dist/jsonpickle
	rm -rf dist/ordered_set.py
	rm -rf dist/pyparsing.py
	rm -rf dist/ifcdiff.py
ifneq ($(PLATFORM), win)
	rm -rf dist/lib
endif

.PHONY: clean
clean:
	rm -rf dist
