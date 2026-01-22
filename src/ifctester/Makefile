# IfcTester - IDS based model auditing
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcTester.
#
# IfcTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcTester.  If not, see <http://www.gnu.org/licenses/>.

PACKAGE_NAME:=ifctester
include ../common.mk

NODE_ENV ?= production
WEBAPP_DIR := webapp
WEBAPP_BUILD_DIR := $(WEBAPP_DIR)/dist
PYODIDE_DIR := $(WEBAPP_DIR)/public/pyodide
PYODIDE_VERSION := 0.28.0
PYODIDE_URL := https://github.com/pyodide/pyodide/releases/download/$(PYODIDE_VERSION)/pyodide-$(PYODIDE_VERSION).tar.bz2
IFCTESTER_WHEEL_BUILD_DIR ?= build_ifctester_wheel
IFCTESTER_WHEEL_PUBLIC_DIR ?= /worker/bin
IFCTESTER_WHEEL_URL ?=
IFCTESTER_WHEEL_DIR := $(WEBAPP_DIR)/public$(IFCTESTER_WHEEL_PUBLIC_DIR)

define RUN_WEBAPP
	@WHEEL_URL="$(IFCTESTER_WHEEL_URL)"; \
	if [ -n "$$WHEEL_URL" ]; then \
		cd $(WEBAPP_DIR) && VITE_IFCTESTER_WHEEL_URL=$$WHEEL_URL npm run $(1); \
	else \
		cd $(WEBAPP_DIR) && npm run $(1); \
	fi
endef

.PHONY: webapp-dev
webapp-dev:
	$(call RUN_WEBAPP,dev)

.PHONY: pyodide-download
pyodide-download:
	echo "Use Python ${PYTHON} and pip ${PIP} to build the package"
	@if [ -d "$(PYODIDE_DIR)" ]; then \
		echo "Pyodide directory already exists at $(PYODIDE_DIR), skipping download"; \
	else \
		echo "Downloading and preparing Pyodide $(PYODIDE_VERSION)..."; \
		mkdir -p $(PYODIDE_DIR)/tmp; \
		curl -L -o $(PYODIDE_DIR)/tmp/pyodide-$(PYODIDE_VERSION).tar.bz2 $(PYODIDE_URL); \
		cd $(PYODIDE_DIR)/tmp && tar -xjf pyodide-$(PYODIDE_VERSION).tar.bz2 && cd -; \
		cp $(PYODIDE_DIR)/tmp/pyodide/pyodide.asm.js $(PYODIDE_DIR)/; \
		cp $(PYODIDE_DIR)/tmp/pyodide/pyodide.asm.wasm $(PYODIDE_DIR)/; \
		cp $(PYODIDE_DIR)/tmp/pyodide/pyodide.mjs $(PYODIDE_DIR)/; \
		cp $(PYODIDE_DIR)/tmp/pyodide/pyodide.mjs.map $(PYODIDE_DIR)/; \
		cp $(PYODIDE_DIR)/tmp/pyodide/python_stdlib.zip $(PYODIDE_DIR)/; \
		cp $(PYODIDE_DIR)/tmp/pyodide/pyodide-lock.json $(PYODIDE_DIR)/; \
		cp $(PYODIDE_DIR)/tmp/pyodide/certifi-*-py3-none-any.whl $(PYODIDE_DIR)/ 2>/dev/null || true; \
		cp $(PYODIDE_DIR)/tmp/pyodide/charset_normalizer-*-py3-none-any.whl $(PYODIDE_DIR)/ 2>/dev/null || true; \
		cp $(PYODIDE_DIR)/tmp/pyodide/idna-*-py3-none-any.whl $(PYODIDE_DIR)/ 2>/dev/null || true; \
		cp $(PYODIDE_DIR)/tmp/pyodide/micropip-*-py3-none-any.whl $(PYODIDE_DIR)/ 2>/dev/null || true; \
		cp $(PYODIDE_DIR)/tmp/pyodide/numpy-*-cp313-cp313-pyodide_2025_0_wasm32.whl $(PYODIDE_DIR)/ 2>/dev/null || true; \
		cp $(PYODIDE_DIR)/tmp/pyodide/python_dateutil-*-py2.py3-none-any.whl $(PYODIDE_DIR)/ 2>/dev/null || true; \
		cp $(PYODIDE_DIR)/tmp/pyodide/requests-*-py3-none-any.whl $(PYODIDE_DIR)/ 2>/dev/null || true; \
		cp $(PYODIDE_DIR)/tmp/pyodide/shapely-*-cp313-cp313-pyodide_2025_0_wasm32.whl $(PYODIDE_DIR)/ 2>/dev/null || true; \
		cp $(PYODIDE_DIR)/tmp/pyodide/six-*-py2.py3-none-any.whl $(PYODIDE_DIR)/ 2>/dev/null || true; \
		cp $(PYODIDE_DIR)/tmp/pyodide/typing_extensions-*-py3-none-any.whl $(PYODIDE_DIR)/ 2>/dev/null || true; \
		cp $(PYODIDE_DIR)/tmp/pyodide/urllib3-*-py3-none-any.whl $(PYODIDE_DIR)/ 2>/dev/null || true; \
		rm -rf $(PYODIDE_DIR)/tmp/pyodide; \
		rm -f $(PYODIDE_DIR)/tmp/pyodide-$(PYODIDE_VERSION).tar.bz2; \
		echo "Pyodide $(PYODIDE_VERSION) prepared in $(PYODIDE_DIR)"; \
	fi

.PHONY: webapp-build
webapp-build: pyodide-download
	cd $(WEBAPP_DIR) && npm install
	$(call RUN_WEBAPP,build)

.PHONY: ifctester-wheel
ifctester-wheel:
	rm -rf $(IFCTESTER_WHEEL_BUILD_DIR)
	mkdir -p $(IFCTESTER_WHEEL_BUILD_DIR)
	cp -r $(PACKAGE_NAME) $(IFCTESTER_WHEEL_BUILD_DIR)/
	cp pyproject.toml $(IFCTESTER_WHEEL_BUILD_DIR)/
	cp README.md $(IFCTESTER_WHEEL_BUILD_DIR)/
	rm -rf $(IFCTESTER_WHEEL_BUILD_DIR)/$(PACKAGE_NAME)/webapp
ifeq ($(IS_STABLE), TRUE)
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' $(IFCTESTER_WHEEL_BUILD_DIR)/pyproject.toml
ifdef IS_MODULE
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' $(IFCTESTER_WHEEL_BUILD_DIR)/$(PACKAGE_NAME)
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' $(IFCTESTER_WHEEL_BUILD_DIR)/$(PACKAGE_NAME)/__init__.py
endif
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)a$(VERSION_DATE)"/' $(IFCTESTER_WHEEL_BUILD_DIR)/pyproject.toml
ifdef IS_MODULE
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)-alpha$(VERSION_DATE)"/' $(IFCTESTER_WHEEL_BUILD_DIR)/$(PACKAGE_NAME)
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)-alpha$(VERSION_DATE)"/' $(IFCTESTER_WHEEL_BUILD_DIR)/$(PACKAGE_NAME)/__init__.py
endif
endif
	cd $(IFCTESTER_WHEEL_BUILD_DIR) && $(PYTHON) -m venv env && . env/$(VENV_ACTIVATE) && $(PIP) install build
	cd $(IFCTESTER_WHEEL_BUILD_DIR) && . env/$(VENV_ACTIVATE) && $(PYTHON) -m build
	mkdir -p $(IFCTESTER_WHEEL_DIR)
	@WHEEL_FILE=$$(ls $(IFCTESTER_WHEEL_BUILD_DIR)/dist/ifctester-*.whl | head -n 1); \
		if [ -z "$$WHEEL_FILE" ]; then echo "No ifctester wheel produced"; exit 1; fi; \
		WHEEL_BASENAME=$$(basename $$WHEEL_FILE); \
		cp $$WHEEL_FILE $(IFCTESTER_WHEEL_DIR)/$$WHEEL_BASENAME; \
		echo "Copied $$WHEEL_FILE to $(IFCTESTER_WHEEL_DIR)/$$WHEEL_BASENAME";
	rm -rf $(IFCTESTER_WHEEL_BUILD_DIR)

.PHONY: webapp-serve
webapp-serve: webapp-build
	cd $(WEBAPP_DIR) && $(PYTHON) serve.py

.PHONY: clean
clean:
	rm -rf $(WEBAPP_BUILD_DIR)
	rm -rf $(WEBAPP_DIR)/node_modules
	rm -rf $(PYODIDE_DIR)
	rm -rf $(PACKAGE_NAME)/webapp
	rm -rf dist

.PHONY: dist
dist: webapp-prepare
# For some reason OS is not initalized when we call common.mk dist, which matters on Windows.
# So we pass it explicitly.
	$(MAKE) -f ../common.mk dist PACKAGE_NAME=$(PACKAGE_NAME) OS=$(OS)

.PHONY: webapp-prepare
webapp-prepare: webapp-build
	rm -rf $(PACKAGE_NAME)/webapp/www/*
	mkdir -p $(PACKAGE_NAME)/webapp/www
	cp -r $(WEBAPP_BUILD_DIR)/* $(PACKAGE_NAME)/webapp/www/
	cp $(WEBAPP_DIR)/__init__.py $(PACKAGE_NAME)/webapp/__init__.py
	cp $(WEBAPP_DIR)/serve.py $(PACKAGE_NAME)/webapp/serve.py

.PHONY: test
test:
	pytest -p no:pytest-blender test
