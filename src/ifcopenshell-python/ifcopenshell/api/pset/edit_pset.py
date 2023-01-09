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
    def __init__(self, file, pset=None, name=None, properties=None, pset_template=None, should_purge=False):
        """Edits a property set and its properties

        At its simplest usage, this may be used to edit the name of a property
        set. It may also be used to add, edit, or remove properties, either
        arbitrarily or using a property set template.

        A list of properties are provided as a dictionary, where the keys are
        property names, and values are property values. Keys that don't already
        exist are interpreted as properties to be added. Keys that already exist
        are interpreted as properties to be edited. A "None" value may specify a
        property to be deleted.

        Properties must have a data type. There are lots of data types in IFCs,
        not just simple unitless data types like integers, booleans, text, but
        also distinguishing between types of text, like labels versus
        descriptive text. There are also lots of unit-based data types like
        areas, volumes, lengths, power, density, flow rates, pressure, etc.

        To ensure the appropriate data type is used for properties, a property
        set template may be used. These can be seen as "property
        specifications". A default selection is provided by buildingSMART, so
        that all buildingSMART defined standard properties have exactly the same
        data types and exactly the right property names without fear of invalid
        data or typos. The built-in buildingSMART templates are always loaded.
        However, you may also specify your own templates. If you try to add a
        non-standard property that does not exist in either your own template or
        in the built-in buildingSMART template, then you have the responsibility
        to ensure that data types are always consistent and correct.

        :param pset: The IfcPropertySet to edit.
        :type pset: ifcopenshell.entity_instance.entity_instance
        :param name: A new name for the property set. If no name is specified,
            the property set name is not changed.
        :type name: str, optional
        :param properties: A dictionary of properties. The keys must be a string
            of the name of the property. The data type of the value will be
            determined by the property set template. If no property set
            template is found, the data types of the Python values will
            influence the IFC data type of the property. String values will
            become IfcLabel, float values will become IfcReal, booleans will
            become IfcBoolean, and integers will become IfcInteger. If more
            control is desired, you may explicitly specify IFC data objects
            directly.
        :type properties: dict
        :param pset_template: If a property set template is provided, this will
            be used to determine data types. If no user-defined template is
            provided, the built-in buildingSMART templates will be loaded.
        :type pset_template: ifcopenshell.entity_instance.entity_instance
        :param should_purge: If left as False, properties set to None will be
            left as None but not removed. If set to true, properties set to None
            will actually be removed.
        :type should_purge: bool, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Let's imagine we have a new wall type.
            wall_type = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWallType")

            # This is a standard buildingSMART property set.
            pset = ifcopenshell.api.run("pset.add_pset", model, product=wall_type, name="Pset_WallCommon")

            # In this scenario, we don't specify any pset_template because it is
            # part of the built-in buildingSMART templates, and so the
            # FireRating will automatically be an IfcLabel, and the thermal
            # transmittance value will automatically be an
            # IfcThermalTransmittanceMeasure. Neither of these properties exist
            # yet, so they will be created.
            ifcopenshell.api.run("pset.edit_pset", model,
                pset=pset, properties={"FireRating": "2HR", "ThermalTransmittance": 42.3})

            # We can edit existing properties. In this case, "FireRating" is
            # edited from "2HR" to "1HR". Combustible is new, and will be added.
            # The existing "ThermalTransmittance" property will be left
            # unchanged.
            ifcopenshell.api.run("pset.edit_pset", model,
                pset=pset, properties={"FireRating": "1HR", "Combustible": False})

            # Setting to None will change the value but not delete the property.
            ifcopenshell.api.run("pset.edit_pset", model, pset=pset, properties={"Combustible": None})

            # If you actually want to delete the property, enable purging.
            ifcopenshell.api.run("pset.edit_pset", model, pset=pset,
                properties={"Combustible": None}, should_purge=True)

            # What if we wanted to manage our own properties? Let's create our
            # own "Company Standard" property set templates. Notice how we
            # prefix our property set with "Foo_", if our company name was "Foo"
            # this would make sense.
            template = ifcopenshell.api.run("pset_template.add_pset_template", model, name="Foo_bar")

            # Let's imagine we want all model authors to specify two properties,
            # one being a length measurement and another being a boolean.
            prop1 = ifcopenshell.api.run("pset_template.add_prop_template", model,
                pset_template=template, name="DemoA", primary_measure_type="IfcLengthMeasure")
            prop2 = ifcopenshell.api.run("pset_template.add_prop_template", model,
                pset_template=template, name="DemoB", primary_measure_type="IfcBoolean")

            # Now we can use our property set template to add our properties,
            # and the data types will always match our template.
            pset = ifcopenshell.api.run("pset.add_pset", model, product=wall_type, name="Foo_Bar")
            ifcopenshell.api.run("pset.edit_pset", model,
                pset=pset, properties={"DemoA": 42.3, "DemoB": True}, pset_template=template)

            # Here's a third scenario where we want to add arbitrary properties
            # that are not standardised by anything, not even our own custom
            # templates.
            pset = ifcopenshell.api.run("pset.add_pset", model, product=wall_type, name="Custom_Pset")
            ifcopenshell.api.run("pset.edit_pset", model,
                pset=pset, properties={
                    # Basic Python data types are mapped to a sensible default
                    "SomeLabel": "Foo",
                    "SomeNumber": 12.3,
                    # But we can always specify exactly what we're after too
                    "ExplicitLength": model.createIfcLengthMeasure(42.3)
                })

            # Editing existing properties will retain their current data types
            # if possible. So this will still be a length measure.
            ifcopenshell.api.run("pset.edit_pset", model, pset=pset, properties={"ExplicitLength": 12.3})
        """
        self.file = file
        self.settings = {
            "pset": pset,
            "name": name,
            "properties": properties or {},
            "pset_template": pset_template,
            "should_purge": should_purge,
        }

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

    # TODO - Add support for changing property types?
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
                primary_measure_type = prop.EnumerationReference.EnumerationValues[
                    0
                ].is_a()  # Only need the first enum type since all enums are of the same type
                ifc_val = self.file.create_entity(primary_measure_type, val)
                sel_vals.append(ifc_val)
            prop.EnumerationValues = tuple(sel_vals)

        else:
            if value.EnumerationReference.EnumerationValues == ():
                if self.settings["should_purge"]:
                    del self.settings["properties"][prop.Name]
                    self.file.remove(prop)
                    return
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
            if self.settings["should_purge"]:
                del self.settings["properties"][prop.Name]
                self.file.remove(prop)
                return
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
            # TODO-The following "elif" is temporary code, will need to refactor at some point - vulevukusej
            elif isinstance(value, list):
                for pset_template in self.settings["pset_template"].HasPropertyTemplates:
                    if pset_template.Name == name:
                        prop_enum = self.file.create_entity(
                            "IFCPROPERTYENUMERATION",
                            Name=name,
                            EnumerationValues=pset_template.Enumerators.EnumerationValues,
                        )
                        prop_enum_value = self.file.create_entity(
                            "IFCPROPERTYENUMERATEDVALUE",
                            Name=name,
                            EnumerationValues=tuple(
                                self.file.create_entity(pset_template.PrimaryMeasureType, v) for v in value
                            ),
                            EnumerationReference=prop_enum,
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
