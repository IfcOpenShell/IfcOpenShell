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

PACKAGE_NAME:=bcf
include ../common.mk

.PHONY: ci
ci:
	tox

.PHONY: license
license:
	copyright-header --license LGPL3 --copyright-holder "Andrea Ghensi <andrea.ghensi@gmail.com>" --copyright-year "2022" --copyright-software "IfcOpenShell" --copyright-software-description "BCF XML file handling" -a ./ -o ./

# TODO: make this based on xsd file presence
.PHONY: models
models:
	xsdata generate -p bcf.v2.model --unnest-classes --kw-only --slots -ds Google bcf/v2/xsd
	xsdata generate -p bcf.v3.model --unnest-classes --kw-only --slots -ds Google bcf/v3/xsd

.PHONY: test
test:
	pytest -p no:pytest-blender tests

# .PHONY
# api:
#     openapi-python-client generate --url https://api.swaggerhub.com/apis/buildingSMART/BCF/3.0
