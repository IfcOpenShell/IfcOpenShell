VERSION:=$(shell cat ../../VERSION)
PYVERSION:=py311
PLATFORM:=linux64

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

ifeq ($(PLATFORM), linux64)
PLATFORMTAG:=manylinux_2_31_x86_64
endif
ifeq ($(PLATFORM), macos64)
PLATFORMTAG:=macosx_10_15_x86_64
endif
ifeq ($(PLATFORM), macosm164)
PLATFORMTAG:=macosx_11_0_arm64
endif
ifeq ($(PLATFORM), win64)
PLATFORMTAG:=win_amd64
endif

IOS_URL:=https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-$(PYNUMBER)-v0.7.9-c18e4ea-$(PLATFORM).zip

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

.PHONY: zip
zip:
ifndef PLATFORM
	$(error PLATFORM is not set)
endif
	rm -rf dist
	mkdir -p dist/working
	mkdir -p dist/ifcopenshell
	cp -r ifcopenshell/* dist/ifcopenshell/

	cd dist/working && wget $(IOS_URL)
	cd dist/working && unzip ifcopenshell-python*
	cp -r dist/working/ifcopenshell/*ifcopenshell_wrapper* dist/ifcopenshell/
	rm -rf dist/working
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' dist/ifcopenshell/__init__.py
	cd dist && zip -r ifcopenshell-python-$(VERSION)-$(PYVERSION)-$(PLATFORM).zip ifcopenshell
	rm -rf dist/ifcopenshell

.PHONY: dist
dist:
ifndef PLATFORM
	$(error PLATFORM is not set)
endif
	rm -rf dist
	mkdir -p dist/working
	mkdir -p dist/ifcopenshell
	cp -r ifcopenshell/* dist/ifcopenshell/

	cd dist/working && wget $(IOS_URL)
	cd dist/working && unzip ifcopenshell-python*
	cp -r dist/working/ifcopenshell/*ifcopenshell_wrapper* dist/ifcopenshell/
	rm -rf dist/working
	# distutils cannot access anything outside the cwd, so hackishly swap out the README.md
	cp README.md ../README.bak
	cp ../../README.md README.md
	cp pyproject.toml pyproject.toml.bak
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' pyproject.toml
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' dist/ifcopenshell/__init__.py
	python -m build
	mv pyproject.toml.bak pyproject.toml
	mv ../README.bak README.md
	cd dist && mv ifcopenshell-$(VERSION)-py3-none-any.whl ifcopenshell-$(VERSION)-$(PYVERSION)-none-$(PLATFORMTAG).whl
	rm -rf dist/ifcopenshell
	rm -rf dist/ifcopenshell.egg-info
	rm -rf dist/ifcopenshell-$(VERSION).tar.gz
