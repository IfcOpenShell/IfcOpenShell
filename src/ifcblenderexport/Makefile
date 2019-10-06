.PHONY: dist
dist:
ifndef PLATFORM
	$(error PLATFORM is not set)
endif
	rm -rf dist
	mkdir -p dist
	cd dist && wget https://s3.amazonaws.com/ifcopenshell-builds/ifcblender-python-37-v0.6.0-b4ce5be-$(PLATFORM)64.zip
	cd dist && unzip ifcblender*
	cp -r io_export_ifc dist/
	cp -r dist/io_import_scene_ifc/ifcopenshell dist/io_export_ifc/
	cd dist && zip -r blender28-bim-$(date '+%y%m%d')-$(PLATFORM).zip io_export_ifc io_import_scene_ifc
	cd dist && rm -rf io_* && rm ifcblender-python-37-v0.6.0-b4ce5be-$(PLATFORM)64.zip

.PHONY: clean
clean:
	rm -rf dist
