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
    def __init__(self, file, Name=None):
        """Adds a new layer

        An IFC layer is like a CAD layer. Portions of an object's geometry
        (typically portions of its 2D linework) can be assigned to layers, which
        can provide stylistic information such as line weights, colours, or
        simply be used for filtering.

        Layers have historically been used to organise CAD data and included in
        ISO standards such as ISO 13567 or by the AIA. This alllows IFC data to
        be compatible with older, 2D-oriented, layer-based workflows.

        Some software that are still based on layers, such as Tekla or ArchiCAD
        may also use this layer information for filtering.

        :param Name: The name of the layer. Defaults to "Unnamed".
        :type Name: str, optional
        :return: The newly created IfcPresentationLayerAssignment element
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

            ifcopenshell.api.run("layer.add_layer", model, Name="AI-WALL-FULL-DIMS-N")
        """
        self.file = file
        self.settings = {"Name": Name or "Unnamed"}

    def execute(self):
        return self.file.create_entity("IfcPresentationLayerAssignment", Name=self.settings["Name"])
