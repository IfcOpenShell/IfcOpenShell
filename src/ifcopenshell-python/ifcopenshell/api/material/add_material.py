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


class Usecase:
    def __init__(self, file, name=None, category=None):
        """Adds a new material

        A material in IFC represents a physical material, such as timber, steel,
        concrete, aluminium, etc. It may also contain physical properties used
        for structural or lighting simulation. Note that unlike the computer
        graphics industry, a material by itself does not define any colour or
        lighting information. Colours in IFC are known as "styles", and an IFC
        material may or may not have any style information associated with it.
        See ifcopenshell.api.style for more information.

        A material is typically given a code name which is used by architects in
        elevations and details when tagging finishes. Materials are also useful
        to structural engineers in specifying the exact types of concrete and
        steel to be used in structural simulations.

        In addition, materials can belong to a category. Specifying this
        category is critical to allow model recipients to make simple queries
        like "show me all concrete / steel" elements in the model. Without
        standardised category naming of all materials, this type of query
        becomes a bespoke and inefficient task. A list of categories are:
        'concrete', 'steel', 'aluminium', 'block', 'brick', 'stone', 'wood',
        'glass', 'gypsum', 'plastic', and 'earth'. The user is allowed to
        specify their own category instead if none of these categories are
        appropriate.

        Note that categories are not available in IFC2X3. This shortcoming is
        one of the big reasons projects should upgrade to IFC4.

        :param name: The name of the material, typically tagged in a finishes
            drawing or schedule.
        :type name: str
        :param category: The category of the material.
        :type category: str, optional
        :return: The newly created IfcMaterial
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Let's create two materials with their respective categories
            concrete = ifcopenshell.api.run("material.add_material", model, name="CON01", category="concrete")
            steel = ifcopenshell.api.run("material.add_material", model, name="ST01", category="steel")

            # Let's imagine an urban concrete bench which is purely made out of concrete
            concrete_bench = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcFurnitureType")

            # Assign the concrete material to that bench. Note that no colour
            # "Style" has been specified.
            ifcopenshell.api.run("material.assign_material", model, product=concrete_bench, material=concrete)
        """
        self.file = file
        self.settings = {"name": name or "Unnamed", "category": category}

    def execute(self):
        material = self.file.create_entity("IfcMaterial", **{"Name": self.settings["name"] or "Unnamed"})
        if self.settings["category"]:
            material.Category = self.settings["category"]
        return material
