IS_STABLE:=FALSE
VERSION:=$(shell cat ../../VERSION)
VERSION_DATE:=$(shell date '+%y%m%d')
PYVERSION:=py311
PLATFORM:=linux64

PYTHON:=python3.11
PIP:=pip3.11
SED:=sed -i
VENV_ACTIVATE:=bin/activate

ifeq ($(OS),Windows_NT)
HOSTOS:=win
PYTHON:=python
VENV_ACTIVATE:=Scripts/activate
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

# We actually do support glibc 2.28-2.30 (see #5636)
# but those are old and there's no demand for it.
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

IOS_URL:=https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-$(PYNUMBER)-v0.8.1-a2538fd-$(PLATFORM).zip
IFCCONVERT_URL:=https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.8.1-a2538fd-$(PLATFORM).zip

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

.PHONY: zip-ifcconvert
zip-ifcconvert:
ifndef PLATFORM
	$(error PLATFORM is not set)
endif
	mkdir -p dist
	cd dist && wget $(IFCCONVERT_URL)
	cd dist && mv *.zip ifcconvert-$(VERSION)-$(PLATFORM).zip

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
	rm -rf build
	mkdir -p build
	mkdir -p dist
	cp -r ifcopenshell build/

	mkdir build/botbuild
	cd build/botbuild && wget $(IOS_URL) && unzip ifcopenshell-python*
	cp -r build/botbuild/ifcopenshell/*ifcopenshell_wrapper* build/ifcopenshell/
	cp ../../README.md build/
	cp pyproject.toml build/
ifeq ($(IS_STABLE), TRUE)
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' build/pyproject.toml
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' build/ifcopenshell/__init__.py
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)a$(VERSION_DATE)"/' build/pyproject.toml
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)-alpha$(VERSION_DATE)"/' build/ifcopenshell/__init__.py
endif

	cd build && $(PYTHON) -m venv env && . env/$(VENV_ACTIVATE) && $(PIP) install build
	cd build && . env/$(VENV_ACTIVATE) && $(PYTHON) -m build

ifeq ($(IS_STABLE), TRUE)
	mv build/dist/ifcopenshell-*.whl dist/ifcopenshell-$(VERSION)-$(PYVERSION)-none-$(PLATFORMTAG).whl
else
	cp build/dist/ifcopenshell-*.whl dist/ifcopenshell-$(VERSION)a$(VERSION_DATE)-$(PYVERSION)-none-$(PLATFORMTAG).whl
endif
	rm -rf build
