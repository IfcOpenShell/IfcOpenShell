# bSDD - Python bSDD library
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of bSDD.
#
# bSDD is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bSDD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with bSDD.  If not, see <http://www.gnu.org/licenses/>.

VERSION:=`date '+%y%m%d'`
SED:=sed -i
ifeq ($(UNAME_S),Darwin)
SED:=sed -i '' -e
endif

.PHONY: test
test:
	pytest -p no:pytest-blender test

.PHONY: dist
dist:
	rm -rf dist
	$(SED) "s/999999/$(VERSION)/" pyproject.toml
	python -m build
	$(SED) "s/$(VERSION)/999999/" pyproject.toml
