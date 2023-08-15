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
    def __init__(self, file, product=None):
        """Removes a product

        This is effectively a smart delete function that not only removes a
        product, but also all of its relationships. It is always recommended to
        use this function to prevent orphaned data in your IFC model.

        This is intended to be used for removing:

        - IfcAnnotation
        - IfcElement
        - IfcElementType
        - IfcSpatialElement
        - IfcSpatialElementType

        For example, geometric representations are removed. Placement
        coordinates are also removed. Properties are removed. Material, type,
        containment, aggregation, and nesting relationships are removed (but
        naturally, the materials, types, containers, etc themselves remain).

        :param product: The element to remove.
        :type product: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # We have a wall.
            wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

            # No we don't.
            ifcopenshell.api.run("root.remove_product", model, product=wall)
        """
        self.file = file
        self.settings = {"product": product}

    def execute(self):
        representations = []
        if self.settings["product"].is_a("IfcProduct"):
            if self.settings["product"].Representation:
                representations = self.settings["product"].Representation.Representations or []
            else:
                representations = []

            # remove object placements
            object_placement = self.settings["product"].ObjectPlacement
            if object_placement:
                if self.file.get_total_inverses(object_placement) == 1:
                    self.settings["product"].ObjectPlacement = None  # remove the inverse for remove_deep2 to work
                    ifcopenshell.util.element.remove_deep2(self.file, object_placement)

        elif self.settings["product"].is_a("IfcTypeProduct"):
            representations = [rm.MappedRepresentation for rm in self.settings["product"].RepresentationMaps or []]

            # remove psets
            psets = self.settings["product"].HasPropertySets or []
            for pset in psets:
                if self.file.get_total_inverses(pset) != 1:
                    continue
                ifcopenshell.api.run(
                    "pset.remove_pset",
                    self.file,
                    product=self.settings["product"],
                    pset=pset,
                )

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
        for inverse_id in [i.id() for i in self.file.get_inverse(self.settings["product"])]:
            try:
                inverse = self.file.by_id(inverse_id)
            except:
                continue
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
                ifcopenshell.api.run("boundary.remove_boundary", self.file, boundary=inverse)
            elif inverse.is_a("IfcRelFillsElement"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelVoidsElement"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelServicesBuildings"):
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
            elif inverse.is_a("IfcRelConnectsElements"):
                if inverse.is_a("IfcRelConnectsWithRealizingElements"):
                    if self.settings["product"] not in (inverse.RelatingElement, inverse.RelatedElement) and any(
                        el for el in inverse.RealizingElements if el != self.settings["product"]
                    ):
                        continue
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelConnectsPorts"):
                if self.settings["product"] not in (inverse.RelatingPort, inverse.RelatedPort):
                    # if it's not RelatingPort/RelatedPort then it's optional RealizingElement
                    # so we keep the relationship
                    continue
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssignsToGroup"):
                if len(inverse.RelatedObjects) == 1:
                    self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssignsToProduct"):
                if inverse.RelatingProduct == self.settings["product"]:
                    self.file.remove(inverse)
                elif len(inverse.RelatedObjects) == 1:
                    self.file.remove(inverse)
        self.file.remove(self.settings["product"])
