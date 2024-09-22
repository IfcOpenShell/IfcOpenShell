# IfcPatch - IFC patching utility
# AssignConstituentFractions Recipe
# This recipe assigns fractions to material constituents in an IFC file based on their widths.

import ifcopenshell
from ifcopenshell.util.unit import calculate_unit_scale
from logging import Logger
from collections import defaultdict
from typing import List


class Patcher:
    """
    Assigns fractions to material constituents in an IFC file based on their widths.

    This patcher calculates the widths of material constituents based on associated quantities
    and assigns fraction values accordingly.
    """

    def __init__(self, src: str, file: ifcopenshell.file, logger: Logger, *args):
        self.src = src
        self.file = file
        self.logger = logger

    def patch(self):
        """
        Execute the patch to assign fractions to material constituents.
        """
        unit_scale_to_mm = calculate_unit_scale(self.file) * 1000.0

        for constituent_set in self.file.by_type('IfcMaterialConstituentSet'):
            constituents = constituent_set.MaterialConstituents or []
            if not constituents:
                continue  # Skip if no constituents found

            # Find elements associated with this constituent set via IfcRelAssociatesMaterial
            associated_elements = self.get_associated_elements(constituent_set)
            if not associated_elements:
                continue  # Skip if no associated elements found

            # Collect quantities associated with the elements
            quantities = self.get_quantities_from_elements(associated_elements)

            # Build a mapping of quantity names to quantities
            quantity_name_map = self.build_quantity_name_map(quantities)

            # Calculate widths for constituents
            constituent_widths, total_width_mm = self.calculate_constituent_widths(
                constituents, quantity_name_map, unit_scale_to_mm
            )

            if total_width_mm == 0.0:
                constituent_set_name = constituent_set.Name or "Unnamed Constituent Set"
                self.logger.warning(f"No widths found for constituents in set '{constituent_set_name}'. Skipping.")
                continue  # Skip if total width is zero to avoid division by zero

            # Assign fractions based on widths
            for constituent, width_mm in constituent_widths.items():
                fraction = width_mm / total_width_mm
                constituent.Fraction = fraction
                self.logger.info(f"Constituent: {constituent.Name}, Width: {width_mm:.2f} mm, Fraction: {fraction:.4f}")

    def get_associated_elements(self, constituent_set) -> List[ifcopenshell.entity_instance]:
        """
        Retrieve elements associated with a given material constituent set.

        :param constituent_set: The material constituent set.
        :return: A list of associated elements.
        """
        associated_elements = []
        for rel in self.file.get_inverse(constituent_set):
            if rel.is_a('IfcRelAssociatesMaterial') and rel.RelatedObjects:
                associated_elements.extend(rel.RelatedObjects)
        return associated_elements

    def get_element_quantities(self, element) -> List[ifcopenshell.entity_instance]:
        """
        Retrieve quantities associated with an element.

        :param element: The IFC element.
        :return: A list of quantities.
        """
        quantities = []
        for rel in getattr(element, 'IsDefinedBy', []):
            if rel.is_a('IfcRelDefinesByProperties'):
                prop_def = rel.RelatingPropertyDefinition
                if prop_def.is_a('IfcElementQuantity'):
                    quantities.extend(prop_def.Quantities)
        return quantities

    def get_quantities_from_elements(self, elements) -> List[ifcopenshell.entity_instance]:
        """
        Collect quantities from a list of elements.

        :param elements: A list of IFC elements.
        :return: A list of quantities.
        """
        quantities = []
        for element in elements:
            quantities.extend(self.get_element_quantities(element))
        return quantities

    def build_quantity_name_map(self, quantities) -> defaultdict:
        """
        Build a mapping from quantity names to quantities.

        :param quantities: A list of quantities.
        :return: A defaultdict mapping names to quantities.
        """
        quantity_name_map = defaultdict(list)
        for q in quantities:
            if q.is_a('IfcPhysicalComplexQuantity'):
                q_name = (q.Name or '').strip().lower()
                quantity_name_map[q_name].append(q)
        return quantity_name_map

    def extract_width_from_quantity(self, quantity, unit_scale_to_mm: float) -> float:
        """
        Extract the width from a quantity.

        :param quantity: The complex quantity.
        :param unit_scale_to_mm: The unit scale to millimeters.
        :return: The width in millimeters.
        """
        for sub_q in getattr(quantity, 'HasQuantities', []):
            if sub_q.is_a('IfcQuantityLength') and (sub_q.Name or '').strip().lower() == 'width':
                raw_length_value = sub_q.LengthValue or 0.0
                width_mm = raw_length_value * unit_scale_to_mm
                return width_mm
        return 0.0

    def calculate_constituent_widths(self, constituents, quantity_name_map, unit_scale_to_mm: float):
        """
        Calculate the widths of constituents based on associated quantities.

        :param constituents: A list of material constituents.
        :param quantity_name_map: A mapping from quantity names to quantities.
        :param unit_scale_to_mm: The unit scale to millimeters.
        :return: A tuple containing the constituent widths and total width.
        """
        constituents_by_name = defaultdict(list)
        for constituent in constituents:
            constituent_name = (constituent.Name or "Unnamed Constituent").strip().lower()
            constituents_by_name[constituent_name].append(constituent)

        constituent_widths = {}
        total_width_mm = 0.0

        for constituent_name, constituents_list in constituents_by_name.items():
            quantities_list = quantity_name_map.get(constituent_name, [])
            for i, constituent in enumerate(constituents_list):
                width_mm = 0.0
                if i < len(quantities_list):
                    matched_quantity = quantities_list[i]
                    width_mm = self.extract_width_from_quantity(matched_quantity, unit_scale_to_mm)
                constituent_widths[constituent] = width_mm
                total_width_mm += width_mm

        return constituent_widths, total_width_mm
