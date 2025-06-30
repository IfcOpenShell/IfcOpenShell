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
import ifcopenshell.api.pset
import ifcopenshell.util.pset
from typing import Optional, Any, Union
from typing_extensions import assert_never

FLOAT_TYPE_KEYWORDS = (
    ("Area", ("area",)),
    ("Volume", ("volume",)),
    ("Weight", ("weight", "mass")),
    ("Length", ("length", "width", "height", "depth", "distance")),
    ("Time", ("time", "duration")),
)

PROP_VALUE_TYPE = Union[ifcopenshell.entity_instance, float, int, dict[str, "PROP_VALUE_TYPE"]]


def edit_qto(
    file: ifcopenshell.file,
    qto: ifcopenshell.entity_instance,
    name: Optional[str] = None,
    properties: Optional[dict[str, PROP_VALUE_TYPE]] = None,
    pset_template: Optional[ifcopenshell.entity_instance] = None,
) -> None:
    """Edits a quantity set and its quantities

    At its simplest usage, this may be used to edit the name of a quantity
    set. It may also be used to add, edit, or remove quantities.

    See ifcopenshell.api.pset.edit_pset for documentation on how this is
    intended to be used.

    One major difference is that quantities set to None are always purged.
    It is not allowed to have None quantities in IFC.

    :param qto: The IfcElementQuantity or IfcPhysicalComplexQuantity to edit.
    :param name: A new name for the quantity set. If no name is specified,
        the quantity set name is not changed.
    :param properties: A dictionary of properties. The keys must be a string
        of the name of the quantity. The data type of the value will be
        determined by the quantity set template. If no quantity set
        template is found, the data types of the Python values and
        properties names will influence the IFC data type of the quantity.

        - For `float` values - see `FLOAT_TYPE_KEYWORDS` for the keywords in property name
        used to detect the quantity type. If no keyword matches,
        the default quantity type will be IfcQuantityLength.

        - `int` values will map to IfcQuantityCount.

        - dictionary values will be used to create IfcPhysicalComplexQuantity with
        properties from the dictionary.

        If more control is desired, you may explicitly specify IFC data objects directly.
    :param pset_template: If a quantity set template is provided, this will
        be used to determine data types. If no user-defined template is
        provided, the built-in buildingSMART templates will be loaded.
    :return: None

    Example:

    .. code:: python

        # Let's imagine we have a new wall type.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # This is a standard buildingSMART property set.
        qto = ifcopenshell.api.pset.add_qto(model, product=wall, name="Qto_WallBaseQuantities")

        # In this scenario, we don't specify any pset_template because it is
        # part of the built-in buildingSMART templates, and so the Length
        # will automatically be an IfcLengthMeasure, and the NetVolume will
        # automatically be an IfcVolumeMeasure. Neither of these properties
        # exist yet, so they will be created.
        ifcopenshell.api.pset.edit_qto(model, qto=qto, properties={"Length": 12, "NetVolume": 7.2})

        # Setting to None will delete the quantity.
        ifcopenshell.api.pset.edit_qto(model, qto=qto, properties={"Length": None})

        # What if we wanted to manage our own properties? Let's create our
        # own "Company Standard" property set templates. Notice how we
        # prefix our property set with "Foo_", if our company name was "Foo"
        # this would make sense. In this example, we say that our template
        # only applies to walls and is for quantities.
        template = ifcopenshell.api.pset_template.add_pset_template(model,
            name="Foo_Wall", template_type="QTO_OCCURRENCEDRIVEN", applicable_entity="IfcWall")

        # Let's imagine we want all model authors to specify a length
        # measurement for the portion of a wall that is overhanging.
        prop = ifcopenshell.api.pset_template.add_prop_template(model, pset_template=template,
            name="OverhangLength", template_type="Q_LENGTH", primary_measure_type="IfcLengthMeasure")

        # Now we can use our property set template to add our properties,
        # and the data types will always match our template.
        qto = ifcopenshell.api.pset.add_qto(model, product=wall, name="Foo_Wall")
        ifcopenshell.api.pset.edit_qto(model,
            qto=qto, properties={"OverhangLength": 42.3}, pset_template=template)

        # Here's a third scenario where we want to add arbitrary quantities
        # that are not standardised by anything, not even our own custom
        # templates.
        qto = ifcopenshell.api.pset.add_qto(model, product=wall, name="Custom_Qto")
        ifcopenshell.api.pset.edit_qto(model,
            qto=qto, properties={
                "SomeLength": model.createIfcLengthMeasure(42.3),
                "SomeArea": model.createIfcAreaMeasure(21.0)
            })

        # Editing existing quantities will retain their current data types
        # if possible. So this will still be a length measure.
        ifcopenshell.api.pset.edit_qto(model, qto=qto, properties={"SomeLength": 12.3})
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"qto": qto, "name": name, "properties": properties or {}, "pset_template": pset_template}
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

    def execute(self):
        self.qto_idx = 5
        if self.settings["qto"].is_a("IfcPhysicalComplexQuantity"):
            self.qto_idx = 2

        self.update_qto_name()
        self.load_qto_template()
        self.update_existing_properties()
        new_properties = self.add_new_properties()
        self.extend_qto_with_new_properties(new_properties)

    def update_qto_name(self) -> None:
        if self.settings["name"]:
            self.settings["qto"].Name = self.settings["name"]

    def load_qto_template(self) -> None:
        if self.settings["pset_template"]:
            self.pset_template = self.settings["pset_template"]
        else:
            self.psetqto = ifcopenshell.util.pset.get_template(self.file.schema_identifier)
            self.qto_template = self.psetqto.get_by_name(self.settings["qto"].Name)

    def update_existing_properties(self) -> None:
        for prop in self.settings["qto"][self.qto_idx] or []:
            self.update_existing_property(prop)

    def update_existing_property(self, prop: ifcopenshell.entity_instance) -> None:
        if prop.Name not in self.settings["properties"]:
            return
        value = self.settings["properties"][prop.Name]
        name = prop.Name
        if value is None:
            self.file.remove(prop)
        elif prop.is_a("IfcPhysicalComplexQuantity") and isinstance(value, dict):
            prop.Discrimination = value.get("Discrimination", prop.Discrimination)
            ifcopenshell.api.pset.edit_qto(self.file, qto=prop, properties=value["HasQuantities"])
        elif prop.is_a("IfcPhysicalSimpleQuantity"):
            value = value.wrappedValue if isinstance(value, ifcopenshell.entity_instance) else value
            # 3 IfcPhysicalSimpleQuantity.XXXValue
            if self.file.schema == "IFC4X3" and prop.is_a("IfcQuantityCount"):
                prop[3] = int(value)
            else:
                prop[3] = float(value)
        del self.settings["properties"][name]

    def add_new_properties(self) -> list[ifcopenshell.entity_instance]:
        properties = []
        for name, value in self.settings["properties"].items():
            if value is None:
                continue
            if isinstance(value, dict):
                complex_qto = self.file.create_entity(
                    "IfcPhysicalComplexQuantity", Name=name, Discrimination=value["Discrimination"]
                )
                properties.append(complex_qto)
                ifcopenshell.api.pset.edit_qto(self.file, qto=complex_qto, properties=value["HasQuantities"])
            else:
                property_type = self.get_canonical_property_type(name, value)
                value = value.wrappedValue if isinstance(value, ifcopenshell.entity_instance) else value
                properties.append(
                    self.file.create_entity(
                        "IfcQuantity{}".format(property_type),
                        **{"Name": name, "{}Value".format(property_type): value},
                    )
                )
        return properties

    def extend_qto_with_new_properties(self, new_properties: list[ifcopenshell.entity_instance]) -> None:
        props = list(self.settings["qto"][self.qto_idx]) if self.settings["qto"][self.qto_idx] else []
        props.extend(new_properties)
        self.settings["qto"][self.qto_idx] = props

    def get_canonical_property_type(self, name: str, value: Union[ifcopenshell.entity_instance, float, int]) -> str:
        if isinstance(value, ifcopenshell.entity_instance):
            result = value.is_a().replace("Ifc", "").replace("Measure", "")
            # Sigh, IFC inconsistencies
            if result == "Numeric":
                result = "Number"
            elif result == "Mass":
                result = "Weight"
            return result
        if self.qto_template:
            for prop_template in self.qto_template.HasPropertyTemplates:
                if prop_template.Name != name:
                    continue
                return prop_template.TemplateType[2:].lower().capitalize()
        return infer_property_type(name, value)


def infer_property_type(name: str, value: Union[float, int]) -> str:
    name_lower = name.lower()
    # Only undetected type is IfcQuantityNumber (IFC4X3),
    # not sure when it's appropriate.
    if isinstance(value, float):
        for category, keywords in FLOAT_TYPE_KEYWORDS:
            if any(keyword in name_lower for keyword in keywords):
                return category
        return "Length"
    elif isinstance(value, int):
        return "Count"
    else:
        assert_never(value)
