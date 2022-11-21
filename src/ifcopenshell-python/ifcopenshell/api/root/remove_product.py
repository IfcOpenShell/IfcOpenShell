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

import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        representations = []
        if self.settings["product"].is_a("IfcProduct"):
            if self.settings["product"].Representation:
                representations = self.settings["product"].Representation.Representations or []
            else:
                representations = []
        elif self.settings["product"].is_a("IfcTypeProduct"):
            representations = [rm.MappedRepresentation for rm in self.settings["product"].RepresentationMaps or []]
        for representation in representations:
            ifcopenshell.api.run(
                "geometry.unassign_representation",
                self.file,
                **{"product": self.settings["product"], "representation": representation}
            )
            ifcopenshell.api.run("geometry.remove_representation", self.file, **{"representation": representation})
        for opening in getattr(self.settings["product"], "HasOpenings", []) or []:
            ifcopenshell.api.run("void.remove_opening", self.file, opening=opening.RelatedOpeningElement)

        if self.settings["product"].is_a("IfcGrid"):
            for axis in (
                self.settings["product"].UAxes + self.settings["product"].VAxes + (self.settings["product"].WAxes or ())
            ):
                ifcopenshell.api.run("grid.remove_grid_axis", self.file, axis=axis)

        # TODO: remove object placement and other relationships
        for inverse in self.file.get_inverse(self.settings["product"]):
            if inverse.is_a("IfcRelDefinesByProperties"):
                ifcopenshell.api.run(
                    "pset.remove_pset",
                    self.file,
                    product=self.settings["product"],
                    pset=inverse.RelatingPropertyDefinition,
                )
            elif inverse.is_a("IfcRelAssociatesMaterial"):
                ifcopenshell.api.run("material.unassign_material", self.file, product=self.settings["product"])
            elif inverse.is_a("IfcRelDefinesByType"):
                if inverse.RelatingType == self.settings["product"]:
                    for related_object in inverse.RelatedObjects:
                        ifcopenshell.api.run("type.unassign_type", self.file, related_object=related_object)
                else:
                    ifcopenshell.api.run("type.unassign_type", self.file, related_object=self.settings["product"])
            elif inverse.is_a("IfcRelSpaceBoundary"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelFillsElement"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelVoidsElement"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelNests"):
                if inverse.RelatingObject == self.settings["product"]:
                    for subelement in inverse.RelatedObjects:
                        if subelement.is_a("IfcDistributionPort"):
                            ifcopenshell.api.run("root.remove_product", self.file, product=subelement)
                    if not inverse.RelatedObjects:
                        self.file.remove(inverse)
            elif inverse.is_a("IfcRelAggregates"):
                if inverse.RelatingObject == self.settings["product"] or len(inverse.RelatedObjects) == 1:
                    self.file.remove(inverse)
            elif inverse.is_a("IfcRelContainedInSpatialStructure"):
                if inverse.RelatingStructure == self.settings["product"] or len(inverse.RelatedElements) == 1:
                    self.file.remove(inverse)
            elif inverse.is_a("IfcRelConnectsPathElements"):
                self.file.remove(inverse)
        self.file.remove(self.settings["product"])
