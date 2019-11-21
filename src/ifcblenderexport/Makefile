.PHONY: dist
dist:
ifndef PLATFORM
	$(error PLATFORM is not set)
endif
	rm -rf dist
	mkdir -p dist
	cd dist && wget https://s3.amazonaws.com/ifcopenshell-builds/ifcblender-python-37-v0.6.0-b4ce5be-$(PLATFORM)64.zip
	cd dist && unzip ifcblender*
	cp -r blenderbim dist/
	cp -r dist/io_import_scene_ifc/ifcopenshell dist/blenderbim/
	rm -rf dist/io_import_scene_ifc
	cd dist/blenderbim && export VERSION=`date '+%y%m%d'` && sed -i "s/999999/$(VERSION)/" __init__.py
	cd dist && zip -r blender28-bim-`date '+%y%m%d'`-$(PLATFORM).zip blenderbim
	cd dist && rm -rf io_* && rm -rf blenderbim && rm ifcblender-python-37-v0.6.0-b4ce5be-$(PLATFORM)64.zip

.PHONY: clean
clean:
	rm -rf dist
