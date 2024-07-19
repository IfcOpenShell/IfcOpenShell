# IfcBIMTester - BIM Gherkin testing.
# Copyright (C) 2020-2024 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcBIMTester.
#
# IfcBIMTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcBIMTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcBIMTester.  If not, see <http://www.gnu.org/licenses/>.

PACKAGE_NAME:=bimtester
include ../common.mk

.PHONY: license
license:
	copyright-header --license LGPL3 --copyright-holder "Dion Moult <dion@thinkmoult.com>" --copyright-year "2022" --copyright-software "BIMTester" --copyright-software-description "OpenBIM Auditing Tool" -a ./ -o ./

.PHONY: qa
qa:
	black .

.PHONY: dist
dist:
	rm -rf build
	mkdir -p build
	mkdir -p dist
	cp -r $(PACKAGE_NAME) build/
	cp pyproject.toml build/
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' build/pyproject.toml
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' build/$(PACKAGE_NAME)/__init__.py
	cd build && $(PYTHON) -m venv env && . env/$(VENV_ACTIVATE) && $(PIP) install build
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) install pybabel
	cd build && . env/$(VENV_ACTIVATE) && $(PIP) install babel
	cd build && . env/$(VENV_ACTIVATE) && ./env/$(VENV_BIN)/pybabel compile -d ./bimtester/locale/
	cd build && . env/$(VENV_ACTIVATE) && $(PYTHON) -m build
	cp build/dist/*.whl dist/
	rm -rf build
