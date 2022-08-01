# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.


class Data:
    is_loaded = False
    products = {}
    groups = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.products = {}
        cls.groups = {}

    @classmethod
    def load(cls, file):
        cls.products = {}
        cls.groups = {}
        for group in file.by_type("IfcGroup", include_subtypes=False):
            if group.IsGroupedBy:
                for rel in group.IsGroupedBy:
                    for product in rel.RelatedObjects:
                        cls.products.setdefault(product.id(), []).append(group.id())
            data = group.get_info()
            data["HasAssignments"] = group.HasAssignments
            data["IsGroupedBy"] = group.IsGroupedBy
            del data["OwnerHistory"]
            cls.groups[group.id()] = data
        cls.is_loaded = True
