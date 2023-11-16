# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
    def __init__(self, file, material=None, style=None, context=None):
        """Unassigns a style to a material

        This does the inverse of assign_material_style.

        :param material: The IfcMaterial which you want to unassign the style from.
        :type material: ifcopenshell.entity_instance.entity_instance
        :param style: The IfcPresentationStyle (typically IfcSurfaceStyle) that
            you want to unassign from material. This will then be applied to all
            objects that have that material.
        :type style: ifcopenshell.entity_instance.entity_instance
        :param context: The IfcGeometricRepresentationSubContext at which this
            style should be unassigned. Typically this is the Model BODY context.
        :type context: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            ifcopenshell.api.run("style.unassign_material_style", model, material=concrete, style=style, context=body)
        """
        self.file = file
        self.settings = {
            "material": material,
            "style": style,
            "context": context,
        }

    def execute(self):
        to_delete = set()
        for definition in self.settings["material"].HasRepresentation:
            for representation in definition.Representations:
                if not representation.is_a("IfcStyledRepresentation"):
                    continue
                if representation.ContextOfItems != self.settings["context"]:
                    continue
                for item in representation.Items:
                    if not item.is_a("IfcStyledItem"):
                        continue
                    styles = [s for s in item.Styles if s != self.settings["style"]]
                    if not styles:
                        self.file.remove(item)
                    elif len(styles) != len(item.Styles):
                        item.Styles = styles
                if not representation.Items:
                    self.file.remove(representation)
            if not definition.Representations:
                self.file.remove(definition)
