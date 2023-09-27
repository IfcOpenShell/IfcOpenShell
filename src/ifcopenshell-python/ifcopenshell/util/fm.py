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
import ifcopenshell.util.attribute

# COBie actually uses an exclusion list, but this inclusion list is equivalent.
cobie_type_classes = [
    "IfcDoorStyle",
    "IfcBuildingElementProxyType",
    "IfcChimneyType",
    "IfcCoveringType",
    "IfcDoorType",
    "IfcFootingType",
    "IfcPileType",
    "IfcRoofType",
    "IfcShadingDeviceType",
    "IfcWindowType",
    "IfcDistributionControlElementType",
    "IfcDistributionChamberElementType",
    "IfcEnergyConversionDeviceType",
    "IfcFlowControllerType",
    "IfcFlowMovingDeviceType",
    "IfcFlowStorageDeviceType",
    "IfcFlowTerminalType",
    "IfcFlowTreatmentDeviceType",
    "IfcElementAssemblyType",
    "IfcBuildingElementPartType",
    "IfcDiscreteAccessoryType",
    "IfcMechanicalFastenerType",
    "IfcReinforcingElementType",
    "IfcVibrationIsolatorType",
    "IfcFurnishingElementType",
    "IfcGeographicElementType",
    "IfcTransportElementType",
    "IfcSpatialZoneType",
    "IfcWindowStyle",
]

cobie_component_classes = [
    "IfcBuildingElementProxy",
    "IfcChimney",
    "IfcCovering",
    "IfcDoor",
    "IfcShadingDevice",
    "IfcWindow",
    "IfcDistributionControlElement",
    "IfcDistributionChamberElement",
    "IfcEnergyConversionDevice",
    "IfcFlowController",
    "IfcFlowMovingDevice",
    "IfcFlowStorageDevice",
    "IfcFlowTerminal",
    "IfcFlowTreatmentDevice",
    "IfcDiscreteAccessory",
    "IfcTendon",
    "IfcTendonAnchor",
    "IfcVibrationIsolator",
    "IfcFurnishingElement",
    "IfcGeographicElement",
    "IfcTransportElement",
]

fmhem_classes_ifc4 = [
    "IfcDoorType",
    "IfcWindowType",
    "IfcShadingDeviceType",
    "IfcDistributionControlElementType",
    "IfcEnergyConversionDeviceType",
    "IfcFlowControllerType",
    "IfcFlowMovingDeviceType",
    "IfcFlowStorageDeviceType",
    "IfcFlowTerminalType",
    "IfcFlowTreatmentDeviceType",
    "IfcFurnishingElementType",
    "IfcTransportElementType",
]

fmhem_classes_ifc2x3 = [
    "IfcDoorStyle",
    "IfcWindowStyle",
    "IfcShadingDeviceType",
    "IfcDistributionControlElementType",
    "IfcEnergyConversionDeviceType",
    "IfcFlowControllerType",
    "IfcFlowMovingDeviceType",
    "IfcFlowStorageDeviceType",
    "IfcFlowTerminalType",
    "IfcFlowTreatmentDeviceType",
    "IfcFurnishingElementType",
    "IfcTransportElementType",
]

fmhem_excluded_classes = [
    "IfcCooledBeamType",
    "IfcBurnerType",
    "IfcCoilType",
    "IfcLampType",
]


def get_cobie_types(ifc_file):
    elements = []
    for ifc_class in cobie_type_classes:
        try:
            elements += ifc_file.by_type(ifc_class)
        except:
            pass
    return elements


def get_cobie_components(ifc_file):
    elements = []
    for ifc_class in cobie_component_classes:
        try:
            elements += ifc_file.by_type(ifc_class)
        except:
            pass
    return elements


def get_fmhem_types(ifc_file):
    elements = []
    if ifc_file.schema == "IFC2X3":
        fmhem_classes = fmhem_classes_ifc2x3
    else:
        fmhem_classes = fmhem_classes_ifc4
    for ifc_class in fmhem_classes:
        try:
            elements += [e for e in ifc_file.by_type(ifc_class) if e.is_a() not in fmhem_excluded_classes]
        except:
            pass
    return elements


def get_fmhem_classes(schema="IFC4"):
    results = {}

    def get_fmhem_class(declaration):
        if declaration.name() in fmhem_excluded_classes:
            pass
        elif declaration.is_abstract():
            pass
        else:
            types = []
            for attribute in declaration.all_attributes():
                if attribute.name() == "PredefinedType":
                    types = list(ifcopenshell.util.attribute.get_enum_items(attribute))
                    if "NOTDEFINED" in types:
                        types.remove("NOTDEFINED")
            results[declaration.name()] = types

        for subtype in declaration.subtypes():
            get_fmhem_class(subtype)

    if schema == "IFC4":
        classes = fmhem_classes_ifc4
    elif schema == "IFC2X3":
        classes = fmhem_classes_ifc2x3
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema)
    for ifc_class in classes:
        declaration = schema.declaration_by_name(ifc_class)
        get_fmhem_class(declaration)
    return results
