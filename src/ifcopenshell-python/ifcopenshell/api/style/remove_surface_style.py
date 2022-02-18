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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"style": None}
        for key, value in settings.items():
            self.settings[key] = value

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
