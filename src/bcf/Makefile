# BCF - BCF Python library
# Copyright (C) 2021 Prabhat Singh <singh01prabhat@gmail.com>
#
# This file is part of BCF.
#
# BCF is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BCF is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BCF.  If not, see <http://www.gnu.org/licenses/>.

VERSION:=$(shell cat ../../VERSION)
SED:=sed -i
ifeq ($(UNAME_S),Darwin)
SED:=sed -i '' -e
endif

.PHONY: ci
ci:
	tox

.PHONY: license
license:
	copyright-header --license LGPL3 --copyright-holder "Andrea Ghensi <andrea.ghensi@gmail.com>" --copyright-year "2022" --copyright-software "IfcOpenShell" --copyright-software-description "BCF XML file handling" -a ./ -o ./

# TODO: make this based on xsd file presence
.PHONY: models
models:
	cd src && xsdata generate -p bcf.v2.model --unnest-classes --kw-only --slots -ds Google bcf/v2/xsd
	cd src && xsdata generate -p bcf.v3.model --unnest-classes --kw-only --slots -ds Google bcf/v3/xsd

.PHONY: dist
dist:
	rm -rf dist
	cp pyproject.toml pyproject.toml.bak
	cp src/bcf/__init__.py __init__.py.bak
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' pyproject.toml
	$(SED) 's/version = "0.0.0"/version = "$(VERSION)"/' src/bcf/__init__.py
	python -m build
	mv pyproject.toml.bak pyproject.toml
	mv __init__.py.bak src/bcf/__init__.py

# .PHONY
# api:
#     openapi-python-client generate --url https://api.swaggerhub.com/apis/buildingSMART/BCF/3.0
