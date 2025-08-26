# IfcPatch - IFC patching utility
# Copyright (C) 2024 Louis Trümpler <louis@lt.plus>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.unit
from logging import Logger


class Patcher:
    """
    Assigns fractions to material constituents based on their "width".

    In Reference View MVD, material layer information is exchanged through
    IfcMaterialConstituentSet and IfcPhysicalComplexQuantity instead of IfcMaterialLayerSet.
    The layer thicknesses are stored as IfcQuantityLength within IfcPhysicalComplexQuantity
    with a Discrimination of 'layer'.

    While the Fraction attribute in IfcMaterialConstituent is optional, it's valuable for
    downstream applications as it indicates the relative proportion of each constituent in
    the total material composition in a more straightforward way.
    However, authoring applications often export material constituents without setting this attribute.

    This patcher helps maintain proper material information in Reference View exports by:
    1. Finding width quantities from IfcPhysicalComplexQuantity with 'layer' discrimination
    2. Using these widths to calculate relative proportions
    3. Setting the optional but valuable Fraction attribute

    For example, if a wall has constituents with widths of 0.1m and 0.2m, their fractions
    would be set to 0.333 and 0.667 respectively.

    References:
    - IFC4 Reference View MVD: https://standards.buildingsmart.org/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML/
    - IfcMaterialConstituent: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/schema/ifcmaterialresource/lexical/ifcmaterialconstituent.htm
    """

    def __init__(self, file: ifcopenshell.file, logger: Logger, *args):
        self.file = file
        self.logger = logger

    def patch(self):
        """Execute the patch to assign fractions to material constituents."""
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)

        # Get length unit from project
        length_unit = ifcopenshell.util.unit.get_project_unit(self.file, "LENGTHUNIT")

        for constituent_set in self.file.by_type("IfcMaterialConstituentSet"):
            if not (constituents := constituent_set.MaterialConstituents):
                continue

            # Find elements associated with this constituent set
            if not (elements := set(ifcopenshell.util.element.get_elements_by_material(self.file, constituent_set))):
                continue

            # Sort elements by GlobalId to ensure consistent order
            elements_sorted = sorted(elements, key=lambda x: x.GlobalId)
            for element in elements_sorted:
                quantities = self.get_element_quantities(element)
                if quantities:
                    element_quantities = quantities
                    break

            if not element_quantities:
                continue

            # Calculate constituent widths and total width
            constituent_widths, total_width = self.calculate_constituent_widths(constituents, elements, unit_scale)

            if not constituent_widths:
                continue

            # Assign fractions based on widths
            for constituent, width in constituent_widths.items():
                fraction = width / total_width
                constituent.Fraction = fraction
                self.logger.info(
                    f"Constituent: {constituent.Name}, "
                    f"Width: {width:.4f} {length_unit}, "
                    f"Fraction: {fraction:.4f}"
                )

    def get_element_quantities(self, element: ifcopenshell.entity_instance) -> dict[str, float]:
        """Get width quantities for an element."""
        qtos = [
            v
            for k, v in ifcopenshell.util.element.get_psets(element, qtos_only=True).items()
            if k.endswith("BaseQuantities")
        ]
        if qtos:
            return {
                k: v["properties"]["Width"]
                for k, v in qtos[0].items()
                if isinstance(v, dict)
                and (v.get("Discrimination") or "").lower() == "layer"
                and v.get("properties", {}).get("Width", "") is not None
            }
        return {}

    def calculate_constituent_widths(
        self,
        constituents: list[ifcopenshell.entity_instance],
        elements: set[ifcopenshell.entity_instance],
        unit_scale: float,
    ) -> tuple[dict[ifcopenshell.entity_instance, float], float]:
        """Calculate the widths of constituents based on associated quantities."""
        if not elements:
            return {}, 0.0

        # Get quantities from all elements and use the first valid one
        element_quantities = {}
        for element in elements:
            quantities = self.get_element_quantities(element)
            if quantities:  # If we found valid quantities, use them
                element_quantities = quantities
                self.logger.debug(f"Using quantities from element: {element.GlobalId}")
                break

        if not element_quantities:
            self.logger.warning("No valid quantities found in any element")
            return {}, 0.0

        constituent_widths = {}
        total_width = 0.0

        for constituent in constituents:
            if not constituent.Name:  # Skip unnamed constituents as per RV MVD
                continue

            constituent_name = constituent.Name.strip()
            if width := element_quantities.get(constituent_name):
                constituent_widths[constituent] = width * unit_scale
                total_width += width * unit_scale
            else:
                self.logger.debug(f"No width found for constituent: {constituent_name}")

        return constituent_widths, total_width
