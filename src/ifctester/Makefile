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
WORKER_BIN_DIR := $(WEBAPP_DIR)/public/worker/bin
IFCOPENSHELL_WASM_WHEEL := ifcopenshell-0.8.5+a51b2c5-cp313-cp313-pyodide_2025_0_wasm32.whl
IFCOPENSHELL_WASM_WHEEL_URL := https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-0.8.5%2Ba51b2c5-cp313-cp313-pyodide_2025_0_wasm32.whl
IFCOPENSHELL_WASM_WHEEL_PATH := $(WORKER_BIN_DIR)/$(IFCOPENSHELL_WASM_WHEEL)
WEBAPP_GENERATED_DIR := $(WEBAPP_DIR)/public/worker/generated
WEBAPP_IFCTESTER_MANIFEST := $(WEBAPP_GENERATED_DIR)/ifctester.json
WEBAPP_IFCTESTER_BUILD_DIR := build-webapp-wheel
PACKAGE_WEBAPP_DIR := $(PACKAGE_NAME)/webapp
PACKAGE_WEBAPP_WWW_DIR := $(PACKAGE_WEBAPP_DIR)/www

.PHONY: webapp-dev
webapp-dev: pyodide-download ifcopenshell-wasm-download webapp-stage-ifctester-wheel
	cd $(WEBAPP_DIR) && npm install
	cd $(WEBAPP_DIR) && npm run dev

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

.PHONY: ifcopenshell-wasm-download
ifcopenshell-wasm-download:
	@if [ -f "$(IFCOPENSHELL_WASM_WHEEL_PATH)" ]; then \
		echo "IfcOpenShell wasm wheel already exists at $(IFCOPENSHELL_WASM_WHEEL_PATH), skipping download"; \
	else \
		echo "Downloading IfcOpenShell wasm wheel..."; \
		mkdir -p $(WORKER_BIN_DIR); \
		rm -f $(WORKER_BIN_DIR)/ifcopenshell-*.whl; \
		curl -fL -o "$(IFCOPENSHELL_WASM_WHEEL_PATH)" "$(IFCOPENSHELL_WASM_WHEEL_URL)"; \
		echo "IfcOpenShell wasm wheel prepared at $(IFCOPENSHELL_WASM_WHEEL_PATH)"; \
	fi

.PHONY: webapp-stage-ifctester-wheel
webapp-stage-ifctester-wheel:
	rm -rf $(WEBAPP_GENERATED_DIR)
	rm -rf $(WEBAPP_IFCTESTER_BUILD_DIR)
	mkdir -p $(WEBAPP_IFCTESTER_BUILD_DIR)
	cp -r $(PACKAGE_NAME) $(WEBAPP_IFCTESTER_BUILD_DIR)/
	rm -rf $(WEBAPP_IFCTESTER_BUILD_DIR)/$(PACKAGE_NAME)/webapp
	cp pyproject.toml $(WEBAPP_IFCTESTER_BUILD_DIR)/
	cp README.md $(WEBAPP_IFCTESTER_BUILD_DIR)/
ifeq ($(IS_STABLE), TRUE)
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' $(WEBAPP_IFCTESTER_BUILD_DIR)/pyproject.toml
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' $(WEBAPP_IFCTESTER_BUILD_DIR)/$(PACKAGE_NAME)/__init__.py
else
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)a$(VERSION_DATE)"/' $(WEBAPP_IFCTESTER_BUILD_DIR)/pyproject.toml
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)-alpha$(VERSION_DATE)"/' $(WEBAPP_IFCTESTER_BUILD_DIR)/$(PACKAGE_NAME)/__init__.py
endif
	cd $(WEBAPP_IFCTESTER_BUILD_DIR) && $(PYTHON) -m venv env --system-site-packages && . env/$(VENV_ACTIVATE) && python -m pip install build && python -m build --wheel --no-isolation
	mkdir -p $(WEBAPP_GENERATED_DIR)
	wheel=$$(basename $(WEBAPP_IFCTESTER_BUILD_DIR)/dist/$(PACKAGE_NAME)-*.whl); \
	cp "$(WEBAPP_IFCTESTER_BUILD_DIR)/dist/$$wheel" "$(WEBAPP_GENERATED_DIR)/$$wheel"; \
	printf '{\n    "wheel_url": "/worker/generated/%s"\n}\n' "$$wheel" > "$(WEBAPP_IFCTESTER_MANIFEST)"
	rm -rf $(WEBAPP_IFCTESTER_BUILD_DIR)

.PHONY: webapp-build
webapp-build: pyodide-download ifcopenshell-wasm-download webapp-stage-ifctester-wheel
	cd $(WEBAPP_DIR) && npm install
	cd $(WEBAPP_DIR) && npm run build

.PHONY: webapp-serve
webapp-serve: webapp-build
	cd $(WEBAPP_DIR) && $(PYTHON) serve.py

.PHONY: clean
clean:
	rm -rf $(WEBAPP_BUILD_DIR)
	rm -rf $(WEBAPP_DIR)/node_modules
	rm -rf $(PYODIDE_DIR)
	rm -f $(WORKER_BIN_DIR)/ifcopenshell-*.whl
	rm -rf $(WEBAPP_GENERATED_DIR)
	rm -rf $(WEBAPP_IFCTESTER_BUILD_DIR)
	rm -rf $(PACKAGE_NAME)/webapp
	rm -rf dist

.PHONY: python-dist
python-dist:
	rm -rf dist
# For some reason OS is not initalized when we call common.mk dist, which matters on Windows.
# So we pass it explicitly.
	$(MAKE) -f ../common.mk dist PACKAGE_NAME=$(PACKAGE_NAME) OS=$(OS) IS_STABLE=$(IS_STABLE)

.PHONY: dist
dist: webapp-prepare
	$(MAKE) python-dist OS=$(OS) IS_STABLE=$(IS_STABLE)

.PHONY: webapp-prepare
webapp-prepare: webapp-build
	rm -rf $(PACKAGE_WEBAPP_WWW_DIR)
	mkdir -p $(PACKAGE_WEBAPP_WWW_DIR)
	cp -r $(WEBAPP_BUILD_DIR)/* $(PACKAGE_WEBAPP_WWW_DIR)/
	cp $(WEBAPP_DIR)/__init__.py $(PACKAGE_WEBAPP_DIR)/__init__.py
	cp $(WEBAPP_DIR)/serve.py $(PACKAGE_WEBAPP_DIR)/serve.py

.PHONY: test
test:
	pytest -p no:pytest-blender test

.PHONY: build-ids-docs
build-ids-docs:
	mkdir -p test/build
	cd test && python ids_doc_generator.py
