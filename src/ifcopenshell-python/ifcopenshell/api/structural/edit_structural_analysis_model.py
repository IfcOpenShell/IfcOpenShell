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
    def __init__(self, file, structural_analysis_model=None, attributes=None):
        """Edits the attributes of an IfcStructuralAnalysisModel

        For more information about the attributes and data types of an
        IfcStructuralAnalysisModel, consult the IFC documentation.

        :param structural_analysis_model: The IfcStructuralAnalysisModel entity you want to edit
        :type structural_analysis_model: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None
        """
        self.file = file
        self.settings = {"structural_analysis_model": structural_analysis_model, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["structural_analysis_model"], name, value)
        return self.settings["structural_analysis_model"]
