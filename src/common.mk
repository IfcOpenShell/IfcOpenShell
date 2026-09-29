SHELL := sh
IS_STABLE:=FALSE
PYTHON:=python3
PIP:=pip3
VERSION:=$(shell cat ../../VERSION)
VERSION_BASE:=$(shell sed -E 's/[[:alpha:]]+[0-9]+$$//' ../../VERSION)
VERSION_PYTHON:=$(shell sed 's/alpha/a/' ../../VERSION)
VERSION_DATE:=$(shell date '+%y%m%d')
VERSION_DAILY:=$(VERSION_BASE)a$(VERSION_DATE)
SED:=sed -i
VENV_BIN:=bin

ifeq ($(OS),Windows_NT)
PYTHON:=python
PIP:=pip
VENV_BIN:=Scripts
else
UNAME_S:=$(shell uname -s)
ifeq ($(UNAME_S),Darwin)
SED:=sed -i '' -e
PYTHON:=python3
endif
endif

VENV_ACTIVATE:=$(VENV_BIN)/activate

.PHONY: dist
dist:
	rm -rf build
	mkdir -p build
	mkdir -p dist
	cp -r $(PACKAGE_NAME) build/
	cp pyproject.toml build/
	if [ -f README.md ]; then cp README.md build/; fi
ifeq ($(IS_STABLE), TRUE)
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_PYTHON)"/' build/pyproject.toml
ifdef IS_MODULE
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_PYTHON)"/' build/$(PACKAGE_NAME)
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_PYTHON)"/' build/$(PACKAGE_NAME)/__init__.py
endif
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_DAILY)"/' build/pyproject.toml
ifdef IS_MODULE
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_DAILY)"/' build/$(PACKAGE_NAME)
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION_DAILY)"/' build/$(PACKAGE_NAME)/__init__.py
endif
endif
	cd build && $(PYTHON) -m venv env && . env/$(VENV_ACTIVATE) && $(PIP) install build
	cd build && . env/$(VENV_ACTIVATE) && $(PYTHON) -m build
	cp build/dist/*.whl dist/
	rm -rf build
