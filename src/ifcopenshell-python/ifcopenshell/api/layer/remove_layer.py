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
    def __init__(self, file, layer=None):
        """Removes a layer

        All representation items assigned to the layer will remain, but the
        relationship to the layer will be removed.

        :param layer: The IfcPresentationLayerAssignment entity to remove
        :type layer: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            layer = ifcopenshell.api.run("layer.add_layer", model, Name="AI-WALL")
            ifcopenshell.api.run("layer.remove_layer", model, layer=layer)
        """
        self.file = file
        self.settings = {"layer": layer}

    def execute(self):
        self.file.remove(self.settings["layer"])
