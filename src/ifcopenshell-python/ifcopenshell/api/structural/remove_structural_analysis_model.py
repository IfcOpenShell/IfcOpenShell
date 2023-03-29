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
    def __init__(self, file, structural_analysis_model=None):
        """Removes an analysis model

        Note that the contents of an analysis model are currently preserved.

        :param structural_analysis_model: The IfcStructuralAnalysisModel to
            remove.
        :type structural_analysis_model: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None
        """
        self.file = file
        self.settings = {"structural_analysis_model": structural_analysis_model}

    def execute(self):
        for rel in self.settings["structural_analysis_model"].IsGroupedBy or []:
            self.file.remove(rel)
        self.file.remove(self.settings["structural_analysis_model"])
