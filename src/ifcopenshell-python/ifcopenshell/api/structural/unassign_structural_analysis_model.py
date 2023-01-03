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
import ifcopenshell.api


class Usecase:
    def __init__(self, file, product=None, structural_analysis_model=None):
        """Removes a relationship between a structural element and the analysis model

        :param product: The structural element that is part of the analysis.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param structural_analysis_model: The IfcStructuralAnalysisModel that
            the structural element is related to.
        :type structural_analysis_model: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None
        """
        self.file = file
        self.settings = {
            "product": product,
            "structural_analysis_model": structural_analysis_model,
        }

    def execute(self):
        if not self.settings["structural_analysis_model"].IsGroupedBy:
            return
        rel = self.settings["structural_analysis_model"].IsGroupedBy[0]
        related_objects = set(rel.RelatedObjects) or set()
        related_objects.remove(self.settings["product"])
        if len(related_objects):
            rel.RelatedObjects = list(related_objects)
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
        else:
            self.file.remove(rel)
