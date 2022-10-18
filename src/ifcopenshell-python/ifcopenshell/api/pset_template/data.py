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
    pset_templates = {}
    prop_templates = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.pset_templates = {}
        cls.prop_templates = {}

    @classmethod
    def load(cls, file):
        cls._file = file

        cls.pset_templates = {}
        cls.prop_templates = {}

        for pset_template in cls._file.by_type("IfcPropertySetTemplate"):
            data = pset_template.get_info()
            data["HasPropertyTemplates"] = [e.id() for e in pset_template.HasPropertyTemplates or []]
            if "OwnerHistory" in data:
                del data["OwnerHistory"]
            cls.pset_templates[pset_template.id()] = data

        for prop_template in cls._file.by_type("IfcSimplePropertyTemplate"):
            data = prop_template.get_info()
            cls.prop_templates[prop_template.id()] = {
                "GlobalId": data["GlobalId"],
                "Name": data["Name"],
                "Description": data["Description"],
                "PrimaryMeasureType": data["PrimaryMeasureType"],
                "TemplateType": data["TemplateType"],
                "Enumerators": data["Enumerators"]
            }
        cls.is_loaded = True
