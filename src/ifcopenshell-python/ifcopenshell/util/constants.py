#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from typing import Literal

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "IFC_APPLICATION",
    "IFC_GRID_AXIS",
    "IFC_PRODUCT",
    "IFC_PROJECT",
    "IFC_PROPERTY_SINGLE_VALUE",
    "IFC_QUANTITY_AREA",
    "IFC_QUANTITY_COUNT",
    "IFC_QUANTITY_LENGTH",
    "IFC_QUANTITY_TIME",
    "IFC_QUANTITY_VOLUME",
    "IFC_QUANTITY_WEIGHT",
    "IFC_SI_UNIT",
    "IFC_TYPES",
    "IFC_UNIT_ASSIGNMENT",
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

# TODO: complete this
IFC_APPLICATION = "IfcApplication"
IFC_GRID_AXIS = "IfcGridAxis"
IFC_PRODUCT = "IfcProduct"
IFC_PROJECT = "IfcProject"
IFC_PROPERTY_SINGLE_VALUE = "IfcPropertySingleValue"
IFC_QUANTITY_AREA = "IfcQuantityArea"
IFC_QUANTITY_COUNT = "IfcQuantityCount"
IFC_QUANTITY_LENGTH = "IfcQuantityLength"
IFC_QUANTITY_TIME = "IfcQuantityTime"
IFC_QUANTITY_VOLUME = "IfcQuantityVolume"
IFC_QUANTITY_WEIGHT = "IfcQuantityWeight"
IFC_SI_UNIT = "IfcSIUnit"
IFC_UNIT_ASSIGNMENT = "IfcUnitAssignment"

# TODO: complete this
IFC_TYPES = Literal[
    "IfcApplication",
    "IfcGridAxis",
    "IfcProduct",
    "IfcProject",
    "IfcPropertySingleValue",
    "IfcQuantityArea",
    "IfcQuantityCount",
    "IfcQuantityLength",
    "IfcQuantityTime",
    "IfcQuantityVolume",
    "IfcQuantityWeight",
    "IfcSIUnit",
    "IfcUnitAssignment",
]
