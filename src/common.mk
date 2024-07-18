PYTHON:=python3.11
PIP:=pip3.11
VERSION:=$(shell cat ../../VERSION)
SED:=sed -i
ifeq ($(OS),Windows_NT)
PYTHON:=python
PIP:=pip
endif
ifeq ($(UNAME_S),Darwin)
SED:=sed -i '' -e
PYTHON:=python3
endif

.PHONY: dist
dist:
	rm -rf build
	mkdir -p build
	mkdir -p dist
	cp -r $(PACKAGE_NAME) build/
	cp pyproject.toml build/
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' build/pyproject.toml
ifdef IS_MODULE
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' build/$(PACKAGE_NAME)
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' build/$(PACKAGE_NAME)/__init__.py
endif
	cd build && $(PYTHON) -m venv env && . env/bin/activate && $(PIP) install build
	cd build && . env/bin/activate && $(PYTHON) -m build
	cp build/dist/*.whl dist/
	rm -rf build
