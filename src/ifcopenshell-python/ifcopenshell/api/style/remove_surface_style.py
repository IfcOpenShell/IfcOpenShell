# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, style=None):
        """Removes a presentation item from a presentation style

        :param style: The IfcPresentationItem to remove.
        :type style: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Create a new surface style
            style = ifcopenshell.api.run("style.add_style", model)

            # Create a simple shading colour and transparency.
            shading = ifcopenshell.api.run("style.add_surface_style", model,
                style=style, ifc_class="IfcSurfaceStyleShading", attributes={
                    "SurfaceColour": { "Name": None, "Red": 1.0, "Green": 0.8, "Blue": 0.8 },
                    "Transparency": 0., # 0 is opaque, 1 is transparent
                })

            # Remove the shading item
            ifcopenshell.api.run("style.remove_surface_style", model, style=shading)
        """
        self.file = file
        self.settings = {"style": style}

    def execute(self):
        to_delete = set()
        if self.settings["style"].is_a("IfcSurfaceStyleWithTextures"):
            for texture in self.settings["style"].Textures or []:
                if texture.IsMappedBy:
                    for coordinate in texture.IsMappedBy:
                        to_delete.add(coordinate)
                else:
                    to_delete.add(texture)

        for attribute in self.settings["style"]:
            if isinstance(attribute, ifcopenshell.entity_instance) and attribute.id():
                to_delete.add(attribute)

        self.file.remove(self.settings["style"])

        for element in to_delete:
            ifcopenshell.util.element.remove_deep2(self.file, element)
