VERSION:=`date '+%y%m%d'`
PYVERSION:=py310
PLATFORM:=linux

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

ifeq ($(PYVERSION), py39)
PYNUMBER:=39
endif
ifeq ($(PYVERSION), py310)
PYNUMBER:=310
endif
ifeq ($(PYVERSION), py311)
PYNUMBER:=311
endif
ifeq ($(PYVERSION), py312)
PYNUMBER:=312
endif

ifeq ($(PLATFORM), linux)
PLATFORMTAG:=manylinux_2_31_x86_64
endif
ifeq ($(PLATFORM), macos)
PLATFORMTAG:=macosx_10_15_x86_64
endif
ifeq ($(PLATFORM), macosm1)
PLATFORMTAG:=macosx_11_0_arm64
endif
ifeq ($(PLATFORM), win)
PLATFORMTAG:=win_amd64
endif

.PHONY: test
test:
	pytest -p no:pytest-blender test

# safe version of tests without mathutils dependency
# for tests to work for github workflow with python <3.10 #3895
.PHONY: test-safe
test-safe:
	pytest -p no:pytest-blender test --ignore=test/util/test_shape_builder.py

.PHONY: build-ids-docs
build-ids-docs:
	mkdir -p test/build
	cd test && python ids_doc_generator.py

.PHONY: qa
qa:
	black .
	pylint ./* --output-format=colorized --disable all --enable E

.PHONY: license
license:
	#copyright-header --license LGPL3 --copyright-holder "Thomas Krijnen <thomas@aecgeeks.com>" --copyright-year "2022" --copyright-software "IfcOpenShell" --copyright-software-description "IFC toolkit and geometry engine" -a ./ -o ./
	copyright-header --license LGPL3 --copyright-holder "Dion Moult <dion@thinkmoult.com>" --copyright-year "2022" --copyright-software "IfcOpenShell" --copyright-software-description "IFC toolkit and geometry engine" -a ./ -o ./

.PHONY: coverage
coverage:
	coverage run --source ifcopenshell -m pytest -p no:pytest-blender test
	coverage html
	xdg-open htmlcov/index.html

.PHONY: clean
clean:
	rm -rf htmlcov

.PHONY: dist
dist:
ifndef PLATFORM
	$(error PLATFORM is not set)
endif
	rm -rf dist
	mkdir -p dist/working
	mkdir -p dist/ifcopenshell
	cp -r ifcopenshell/* dist/ifcopenshell/

	cd dist/working && wget https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-$(PYNUMBER)-v0.7.0-c7830e9-$(PLATFORM)64.zip
	cd dist/working && unzip ifcopenshell-python*
	cp -r dist/working/ifcopenshell/ifcopenshell_wrapper.py dist/ifcopenshell/
ifeq ($(PLATFORM), win)
	cp -r dist/working/ifcopenshell/_ifcopenshell_wrapper.pyd dist/ifcopenshell/
else
	cp -r dist/working/ifcopenshell/_ifcopenshell_wrapper.so dist/ifcopenshell/
endif
	rm -rf dist/working
	# distutils cannot access anything outside the cwd, so hackishly swap out the README.md
	cp README.md ../README.bak
	cp ../../README.md README.md
	$(SED) "s/999999/$(VERSION)/" pyproject.toml
	python -m build
	$(SED) "s/$(VERSION)/999999/" pyproject.toml
	mv ../README.bak README.md
	cd dist && mv ifcopenshell-0.7.0.$(VERSION)-py3-none-any.whl ifcopenshell-0.7.0.$(VERSION)-$(PYVERSION)-none-$(PLATFORMTAG).whl
	rm -rf dist/ifcopenshell
	rm -rf dist/ifcopenshell.egg-info
	rm -rf dist/ifcopenshell-0.7.0.$(VERSION).tar.gz
