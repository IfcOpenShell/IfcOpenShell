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
import ifcopenshell.util.element
import ifcopenshell.util.pset
from typing import Optional, Any, Union


def edit_pset(
    file: ifcopenshell.file,
    pset: ifcopenshell.entity_instance,
    name: Optional[str] = None,
    properties: Optional[dict[str, Any]] = None,
    pset_template: Optional[ifcopenshell.entity_instance] = None,
    should_purge: bool = True,
) -> None:
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
    :type pset: ifcopenshell.entity_instance
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
        directly. Note that provided `properties` might be mutated in the process.
    :type properties: dict
    :param pset_template: If a property set template is provided, this will
        be used to determine data types. If no user-defined template is
        provided, the built-in buildingSMART templates will be loaded.
    :type pset_template: ifcopenshell.entity_instance, optional
    :param should_purge: If set as False, properties set to None will be
        left as None but not removed. If set to true, properties set to None
        will actually be removed. The default of true is the same behaviour as
        :func:`ifcopenshell.api.pset.edit_qto`.
    :type should_purge: bool, optional
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Let's imagine we have a new wall type.
        wall_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWallType")

        # This is a standard buildingSMART property set.
        pset = ifcopenshell.api.pset.add_pset(model, product=wall_type, name="Pset_WallCommon")

        # In this scenario, we don't specify any pset_template because it is
        # part of the built-in buildingSMART templates, and so the
        # FireRating will automatically be an IfcLabel, and the thermal
        # transmittance value will automatically be an
        # IfcThermalTransmittanceMeasure. Neither of these properties exist
        # yet, so they will be created.
        ifcopenshell.api.pset.edit_pset(model,
            pset=pset, properties={"FireRating": "2HR", "ThermalTransmittance": 42.3})

        # We can edit existing properties. In this case, "FireRating" is
        # edited from "2HR" to "1HR". Combustible is new, and will be added.
        # The existing "ThermalTransmittance" property will be left
        # unchanged.
        ifcopenshell.api.pset.edit_pset(model,
            pset=pset, properties={"FireRating": "1HR", "Combustible": False})

        # Setting to None will change the value but not delete the property.
        ifcopenshell.api.pset.edit_pset(model, pset=pset, properties={"Combustible": None})

        # If you actually want to delete the property, enable purging.
        ifcopenshell.api.pset.edit_pset(model, pset=pset,
            properties={"Combustible": None}, should_purge=True)

        # What if we wanted to manage our own properties? Let's create our
        # own "Company Standard" property set templates. Notice how we
        # prefix our property set with "Foo_", if our company name was "Foo"
        # this would make sense.
        template = ifcopenshell.api.pset_template.add_pset_template(model, name="Foo_bar")

        # Let's imagine we want all model authors to specify two properties,
        # one being a length measurement and another being a boolean.
        prop1 = ifcopenshell.api.pset_template.add_prop_template(model,
            pset_template=template, name="DemoA", primary_measure_type="IfcLengthMeasure")
        prop2 = ifcopenshell.api.pset_template.add_prop_template(model,
            pset_template=template, name="DemoB", primary_measure_type="IfcBoolean")

        # Now we can use our property set template to add our properties,
        # and the data types will always match our template.
        pset = ifcopenshell.api.pset.add_pset(model, product=wall_type, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(model,
            pset=pset, properties={"DemoA": 42.3, "DemoB": True}, pset_template=template)

        # Here's a third scenario where we want to add arbitrary properties
        # that are not standardised by anything, not even our own custom
        # templates.
        pset = ifcopenshell.api.pset.add_pset(model, product=wall_type, name="Custom_Pset")
        ifcopenshell.api.pset.edit_pset(model,
            pset=pset, properties={
                # Basic Python data types are mapped to a sensible default
                "SomeLabel": "Foo",
                "SomeNumber": 12.3,
                # But we can always specify exactly what we're after too
                "ExplicitLength": model.createIfcLengthMeasure(42.3)
            })

        # Editing existing properties will retain their current data types
        # if possible. So this will still be a length measure.
        ifcopenshell.api.pset.edit_pset(model, pset=pset, properties={"ExplicitLength": 12.3})
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "pset": pset,
        "name": name,
        "properties": properties or {},
        "pset_template": pset_template,
        "should_purge": should_purge,
    }
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

    def execute(self) -> None:
        self.update_pset_name()
        self.load_pset_template()
        existing_props = self.update_existing_properties()
        new_props = self.add_new_properties()
        self.assign_new_properties(existing_props + new_props)

    def update_pset_name(self) -> None:
        if self.settings["name"]:
            self.settings["pset"].Name = self.settings["name"]

    def load_pset_template(self) -> None:
        if self.settings["pset_template"]:
            self.pset_template = self.settings["pset_template"]
        else:
            self.psetqto = ifcopenshell.util.pset.get_template(self.file.schema_identifier)
            self.pset_template = self.psetqto.get_by_name(self.settings["pset"].Name)

    def _should_update_prop(self, prop: ifcopenshell.entity_instance) -> bool:
        """
        Checks if the given property should be changed
        """
        return prop.Name in self.settings["properties"]

    def _try_purge(self, prop: ifcopenshell.entity_instance) -> bool:
        """
        Tries to remove the property
        if successful, returns True, otherwise False
        NOTE: Assumes the prop exists
        """
        if not self.settings["should_purge"]:
            return False

        del self.settings["properties"][prop.Name]
        self.file.remove(prop)
        return True

    # TODO - Add support for changing property types?
    #   For example - IfcPropertyEnumeratedValue to
    # IfcPropertySingleValue.  Or maybe the user should
    # just delete the property first? - vulevukusej
    def update_existing_properties(self) -> list[ifcopenshell.entity_instance]:
        existing_props = []
        for prop in self.get_properties():
            if not self._should_update_prop(prop):
                existing_props.append(prop)
                continue

            if self.file.get_total_inverses(prop) > 1:
                continue  # Treat as a new property to avoid affecting other psets.

            if prop.is_a("IfcPropertyEnumeratedValue"):
                prop = self.update_existing_prop_enum(prop)
                if prop:
                    existing_props.append(prop)
            elif prop.is_a("IfcPropertySingleValue"):
                prop = self.update_existing_prop_single_value(prop)
                if prop:
                    existing_props.append(prop)
            else:
                raise NotImplementedError(f"Updating '{prop.is_a()}' properties is not supported yet")
        return existing_props

    def update_existing_prop_enum(
        self, prop: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        """
        NOTE: Assumes the prop exists
        """
        value = self.settings["properties"][prop.Name]
        unit, value = self.unpack_unit_value(value)

        if isinstance(value, (tuple, list)):
            sel_vals = []
            if not value:
                if self._try_purge(prop):
                    return
            # Only need the first enum type since all enums are of the same type.
            if reference := prop.EnumerationReference:
                primary_measure_type = reference.EnumerationValues[0].is_a()
            elif enum_values := prop.EnumerationValues:
                primary_measure_type = enum_values[0].is_a()
            else:
                primary_measure_type = self.get_primary_measure_type(prop.Name, new_value=value[0])
                assert primary_measure_type, f"Couldn't find primary measure type for the prop value: '{value[0]}'."
            for val in value:
                ifc_val = self.file.create_entity(primary_measure_type, val)
                sel_vals.append(ifc_val)
            prop.EnumerationValues = tuple(sel_vals) or None

        elif isinstance(value, ifcopenshell.entity_instance) and value.is_a("IfcPropertyEnumeratedValue"):
            # Copy enum value.
            if (value_enum_values := value.EnumerationValues) is None:
                if self._try_purge(prop):
                    return
            prop.EnumerationValues = value_enum_values

            # Copy values from / recreate value EnumerationReference in prop.
            value_reference = value.EnumerationReference
            prop_reference = prop.EnumerationReference
            if value_reference is None:
                if prop_reference:
                    ifcopenshell.util.element.remove_deep2(self.file, prop_reference)
                prop.EnumerationReference = None
            else:
                if prop_reference is None:
                    prop_reference = ifcopenshell.util.element.copy_deep(self.file, value_reference)
                    prop.EnumerationReference = prop_reference
                else:
                    prop_reference.Name = value_reference.Name
                    prop_reference.EnumerationValues = value_reference.EnumerationValues
                    prop_reference.Unit = value_reference.Unit

        else:
            raise ValueError(
                f'Value "{self.settings["properties"][prop.Name]}" is not a valid value for enum property {prop.Name}.'
            )

        if unit:
            prop.Unit = unit
        del self.settings["properties"][prop.Name]
        return prop

    def update_existing_prop_single_value(
        self, prop: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        """
        NOTE: Assumes the prop exists
        """
        value = self.settings["properties"][prop.Name]
        unit, value = self.unpack_unit_value(value)
        if value is None:
            if self._try_purge(prop):
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
        if unit:
            prop.Unit = unit
        del self.settings["properties"][prop.Name]
        return prop

    def add_new_properties(self) -> list[ifcopenshell.entity_instance]:
        properties = []
        for name, value in self.settings["properties"].items():
            if value is None and self.settings["should_purge"]:
                continue
            unit, value = self.unpack_unit_value(value)

            if isinstance(value, ifcopenshell.entity_instance):
                if value.is_a("IfcProperty"):
                    properties.append(value)

                # If it's not an entity, then it's a primitive data type
                elif not value.is_entity():
                    kwargs = {"Name": name, "NominalValue": value}
                    if unit:
                        kwargs["Unit"] = unit
                    properties.append(self.file.create_entity("IfcPropertySingleValue", **kwargs))

                else:
                    raise ValueError(f"{value.is_a()} cannot be assigned to the property set '{name}'")

            elif isinstance(value, (tuple, list)):
                if not value:
                    continue
                for pset_template in self.pset_template.HasPropertyTemplates:
                    if pset_template.Name != name:
                        continue

                    if pset_template.TemplateType == "P_LISTVALUE":
                        ifc_class = getattr(pset_template, "PrimaryMeasureType", None)
                        if ifc_class is None:
                            raise ValueError(f"pset template '{pset_template.Name}' is missing PrimaryMeasureType")

                        properties.append(
                            self.file.create_entity(
                                "IfcPropertyListValue",
                                Name=name,
                                ListValues=[self.file.create_entity(ifc_class, v) for v in value],
                                Unit=unit,
                            )
                        )
                        break

                    elif pset_template.TemplateType == "P_ENUMERATEDVALUE":
                        prop_enum = self.file.create_entity(
                            "IFCPROPERTYENUMERATION",
                            Name=name,
                            EnumerationValues=pset_template.Enumerators.EnumerationValues,
                            **({"Unit": unit} if unit else {}),
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
                        break

                    raise NotImplementedError(f"Template type '{pset_template.TemplateType}' is not supported yet")

                else:
                    raise NotImplementedError(f"No template found for property '{name}'")

            else:
                primary_measure_type = self.get_primary_measure_type(name, new_value=value)
                if value is None:
                    nominal_value = value
                else:
                    value = self.cast_value_to_primary_measure_type(value, primary_measure_type)
                    nominal_value = self.file.create_entity(primary_measure_type, value)
                args = {"Name": name, "NominalValue": nominal_value}
                if unit:
                    args["Unit"] = unit

                properties.append(self.file.create_entity("IfcPropertySingleValue", **args))
        return properties

    def assign_new_properties(self, props: list[ifcopenshell.entity_instance]) -> None:
        if hasattr(self.settings["pset"], "HasProperties"):
            self.settings["pset"].HasProperties = props

        # Material / Profile properties
        elif hasattr(self.settings["pset"], "Properties"):
            self.settings["pset"].Properties = props

        # IFC2X3 IfcMaterialProperties
        elif self.settings["pset"].is_a("IfcMaterialProperties"):
            self.settings["pset"].ExtendedProperties = props

    def get_properties(self) -> list[ifcopenshell.entity_instance]:
        """
        Returns list of existing properties
        """
        if (props := getattr(self.settings["pset"], "HasProperties", ...)) is not ...:
            return props or []

        # Material / Profile properties
        elif (props := getattr(self.settings["pset"], "Properties", ...)) is not ...:
            return props or []

        # IFC2X3 IfcMaterialProperties
        elif (props := getattr(self.settings["pset"], "ExtendedProperties", ...)) is not ...:
            return props or []

        raise TypeError(f"'{self.settings['pset']}' is not a valid pset")

    def get_primary_measure_type(
        self,
        name: str,
        old_value: Optional[ifcopenshell.entity_instance] = None,
        new_value: Optional[Union[ifcopenshell.entity_instance, str, float, bool, int]] = None,
    ) -> Union[str, None]:
        if old_value:
            return old_value.is_a()
        if self.pset_template:
            for prop_template in self.pset_template.HasPropertyTemplates:
                if prop_template.Name != name:
                    continue
                return prop_template.PrimaryMeasureType or "IfcLabel"
        if isinstance(new_value, ifcopenshell.entity_instance):
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

    @staticmethod
    def unpack_unit_value(value_candidate):
        """
        Returns tuple of the format: (Unit, NominalValue)
        NOTE: Unit fallbacks to None
        """
        if value_candidate is None:
            return (None, None)

        if isinstance(value_candidate, dict):  # Custom IfcUnits can be passed in a dict along with the pset value
            return (value_candidate["Unit"], value_candidate["NominalValue"])

        return (None, value_candidate)
