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

PYTHON:=python3.11
PIP:=pip3.11
SED:=sed -i
ifeq ($(UNAME_S),Darwin)
PYTHON:=python3
SED:=sed -i '' -e
endif
VERSION:=$(shell cat ../../VERSION)

.PHONY: license
license:
	copyright-header --license LGPL3 --copyright-holder "Dion Moult <dion@thinkmoult.com>" --copyright-year "2022" --copyright-software "BIMTester" --copyright-software-description "OpenBIM Auditing Tool" -a ./ -o ./

.PHONY: qa
qa:
	black .

.PHONY: dist
dist:
	rm -rf dist
	cp pyproject.toml pyproject.toml.bak
	cp bimtester/__init__.py __init__.py.bak
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' pyproject.toml
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' bimtester/__init__.py
	mkdir -p dist/working
	cd dist/working && $(PYTHON) -m venv env
	cd dist/working && . env/bin/activate && $(PIP) install pybabel
	cd dist/working && . env/bin/activate && $(PIP) install babel
	cd dist/working/ && . env/bin/activate && ./env/bin/pybabel compile -d ../../bimtester/locale/
	python -m build
	mv pyproject.toml.bak pyproject.toml
	mv __init__.py.bak bimtester/__init__.py
	rm -rf dist/working
