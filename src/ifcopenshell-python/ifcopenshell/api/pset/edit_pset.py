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

import ifcopenshell
import ifcopenshell.util.pset


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"pset": None, "name": None, "properties": {}, "pset_template": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.update_pset_name()
        self.load_pset_template()
        self.update_existing_properties()
        new_properties = self.add_new_properties()
        self.extend_pset_with_new_properties(new_properties)

    def update_pset_name(self):
        if self.settings["name"]:
            self.settings["pset"].Name = self.settings["name"]

    def load_pset_template(self):
        if self.settings["pset_template"]:
            self.pset_template = self.settings["pset_template"]
        else:
            # TODO: add IFC2X3 PsetQto template support
            self.psetqto = ifcopenshell.util.pset.get_template("IFC4")
            self.pset_template = self.psetqto.get_by_name(self.settings["pset"].Name)

    #TODO - Add support for changing property types?
    #   For example - IfcPropertyEnumeratedValue to 
    # IfcPropertySingleValue.  Or maybe the user should
    # just delete the property first? - vulevukusej
    def update_existing_properties(self):
        for prop in self.get_properties():
            if prop.is_a("IfcPropertyEnumeratedValue"):
                self.update_existing_enum(prop)
            else:
                self.update_existing_property(prop)
    
    def update_existing_enum(self, prop):
        if prop.Name not in self.settings["properties"]:
            return
        value = self.settings["properties"][prop.Name]
        if isinstance(value, list):
            sel_vals = []
            for val in value:
                primary_measure_type = prop.EnumerationReference.EnumerationValues[0].is_a() #Only need the first enum type since all enums are of the same type
                ifc_val = self.file.create_entity(primary_measure_type, val)
                sel_vals.append(ifc_val)
            prop.EnumerationValues = tuple(sel_vals)

        else:
            if value.EnumerationReference.EnumerationValues == ():
                prop.EnumerationReference.EnumerationValues = ()
                prop.EnumerationValues = ()
                
            elif isinstance(value, ifcopenshell.entity_instance):
                prop.EnumerationReference.EnumerationValues = value.EnumerationReference.EnumerationValues
                prop.EnumerationValues = value.EnumerationValues
        del self.settings["properties"][prop.Name]
    
    def update_existing_property(self, prop): 
        if prop.Name not in self.settings["properties"]:
            return
        value = self.settings["properties"][prop.Name]
        if value is None:
            prop.NominalValue = None
        elif isinstance(value, ifcopenshell.entity_instance):
            prop.NominalValue = value
        else:
            primary_measure_type = self.get_primary_measure_type(
                prop.Name, old_value=prop.NominalValue, new_value=value
            )
            value = self.cast_value_to_primary_measure_type(value, primary_measure_type)
            prop.NominalValue = self.file.create_entity(primary_measure_type, value)
        del self.settings["properties"][prop.Name]

    def add_new_properties(self):
        properties = []
        for name, value in self.settings["properties"].items():
            if value is None:
                continue
            if isinstance(value, ifcopenshell.entity_instance):
                if value.is_a(True) == "IFC4.IfcPropertyEnumeratedValue":
                    properties.append(value)
                    continue               
                else:
                    properties.append(
                        self.file.create_entity(
                            "IfcPropertySingleValue",
                            **{"Name": name, "NominalValue": value},
                        )
                    )
            #TODO-The following "elif" is temporary code, will need to refactor at some point - vulevukusej
            elif isinstance(value, list):
                for pset_template in self.settings["pset_template"].HasPropertyTemplates:
                    if pset_template.Name == name:
                        prop_enum = self.file.create_entity(
                            "IFCPROPERTYENUMERATION",
                            Name=name,
                            EnumerationValues=pset_template.Enumerators.EnumerationValues
                        )
                        prop_enum_value = self.file.create_entity(
                            "IFCPROPERTYENUMERATEDVALUE",
                            Name=name,
                            EnumerationValues=tuple(self.file.create_entity(
                            pset_template.PrimaryMeasureType, v) for v in value),
                            EnumerationReference=prop_enum
                        )
                        properties.append(prop_enum_value)
                        continue
            else:
                primary_measure_type = self.get_primary_measure_type(name, new_value=value)
                value = self.cast_value_to_primary_measure_type(value, primary_measure_type)
                nominal_value = self.file.create_entity(primary_measure_type, value)
            
                properties.append(
                    self.file.create_entity(
                        "IfcPropertySingleValue",
                        **{"Name": name, "NominalValue": nominal_value},
                    )
                )
        return properties

    def extend_pset_with_new_properties(self, new_properties):
        props = list(self.get_properties())
        props.extend(new_properties)
        if hasattr(self.settings["pset"], "HasProperties"):
            self.settings["pset"].HasProperties = props
        elif hasattr(self.settings["pset"], "Properties"):
            self.settings["pset"].Properties = props

    def get_properties(self):
        if hasattr(self.settings["pset"], "HasProperties"):
            return self.settings["pset"].HasProperties or []
        elif hasattr(self.settings["pset"], "Properties"):  # For IfcMaterialProperties
            return self.settings["pset"].Properties or []

    def get_primary_measure_type(self, name, old_value=None, new_value=None):
        if self.pset_template:
            for prop_template in self.pset_template.HasPropertyTemplates:
                if prop_template.Name != name:
                    continue
                return prop_template.PrimaryMeasureType or "IfcLabel"
        if old_value:
            return old_value.is_a()
        elif new_value and hasattr(new_value, "is_a"):
            return new_value.is_a()
        elif new_value is not None:
            if isinstance(new_value, str):
                return "IfcLabel"
            elif isinstance(new_value, float):
                return "IfcReal"
            elif isinstance(new_value, bool):
                return "IfcBoolean"
            elif isinstance(new_value, int):
                return "IfcInteger"

    def cast_value_to_primary_measure_type(self, value, primary_measure_type):
        type_str = self.file.create_entity(primary_measure_type).attribute_type(0)
        type_fn = {
            "AGGREGATE OF DOUBLE": list,
            "AGGREGATE OF INT": list,
            "AGGREGATE OF ENTITY INSTANCE": list,
            "BINARY": bytes,
            "LOGICAL": str,
            "BOOL": bool,
            "INT": int,
            "DOUBLE": float,
            "STRING": str,
        }[type_str]
        if type_str == "AGGREGATE OF DOUBLE":
            return [float(i) for i in value]
        elif type_str == "AGGREGATE OF INT":
            return [int(i) for i in value]
        return type_fn(value)
