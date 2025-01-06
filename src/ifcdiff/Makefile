# IfcDiff - Compare IFCs
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcDiff.
#
# IfcDiff is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcDiff is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcDiff.  If not, see <http://www.gnu.org/licenses/>.

PACKAGE_NAME:=ifcdiff.py
IS_MODULE:=true
include ../common.mk

.PHONY: test
test:
	pytest -p no:pytest-blender test.py

.PHONY: qa
qa:
	black .
