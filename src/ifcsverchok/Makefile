# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2020-2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcSverchok.
#
# IfcSverchok is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcSverchok is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IfcSverchok.  If not, see <http://www.gnu.org/licenses/>.

VERSION:=`date '+%y%m%d'`
IS_STABLE:=FALSE
VERSION:=$(shell cat ../../VERSION)
VERSION_MAJOR:=$(shell cat '../../VERSION' | cut -d '.' -f 1)
VERSION_MINOR:=$(shell cat '../../VERSION' | cut -d '.' -f 2)
VERSION_PATCH:=$(shell cat '../../VERSION' | cut -d '.' -f 3)
VERSION_DATE:=$(shell date '+%y%m%d')

SED:=sed -i
ifeq ($(UNAME_S),Darwin)
SED:=sed -i '' -e
endif

.PHONY: dist
dist:
	rm -rf dist
	mkdir -p dist/ifcsverchok
	cp -r ./*.py dist/ifcsverchok/
	cp -r ./nodes dist/ifcsverchok/
ifeq ($(IS_STABLE), TRUE)
	cd dist/ifcsverchok && $(SED) "s/0, 0, 0/$(VERSION_MAJOR), $(VERSION_MINOR), $(VERSION_PATCH)/" __init__.py
	cd dist && zip -r ifcsverchok-$(VERSION).zip ./*
else
	cd dist/ifcsverchok && $(SED) "s/0, 0, 0/$(VERSION_MAJOR), $(VERSION_MINOR), $(VERSION_PATCH), $(VERSION_DATE)/" __init__.py
	cd dist && zip -r ifcsverchok-$(VERSION).$(VERSION_DATE).zip ./*
endif
	rm -rf dist/ifcsverchok

.PHONY: clean
clean:
	rm -rf dist
