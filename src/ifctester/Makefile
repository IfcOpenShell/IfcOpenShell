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
WEBAPP_DIR := webapp-next
WEBAPP_BUILD_DIR := $(WEBAPP_DIR)/dist

.PHONY: webapp-dev
webapp-dev:
	cd $(WEBAPP_DIR) && npm run dev

.PHONY: webapp-build
webapp-build:
	cd $(WEBAPP_DIR) && npm install
	cd $(WEBAPP_DIR) && npm run build

.PHONY: webapp-serve
webapp-serve: webapp-build
	cd $(WEBAPP_DIR) && $(PYTHON) serve.py

.PHONY: webapp-clean
webapp-clean:
	rm -rf $(WEBAPP_BUILD_DIR)
	rm -rf $(WEBAPP_DIR)/node_modules

.PHONY: dist
dist: webapp-prepare
	$(MAKE) -f ../common.mk dist PACKAGE_NAME=$(PACKAGE_NAME)

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
