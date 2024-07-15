# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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

"""Geometry processing and analysis

IFC may define geometry explicitly (such as meshes) or implicitly (such as
parametric extrusions). This module provides methods to extract geometric
definitions in IFC into explicitly tessellated triangles or OpenCASCADE Breps
for further processing.

This is typically needed when writing software to visualise or analyse
geometry. See also :mod:`ifcopenshell.util.shape` for deriving quantities.
"""


def _has_occ():
    # NOTE: All pythonocc versions since 7.4.0 are using OCC.Core.
    # Previous versions (pythonocc<=0.17.3) are using just OCC.

    try:
        import OCC.Core.BRepTools

        return True
    except ImportError:
        pass

    try:
        import OCC.BRepTools

        return True
    except ImportError:
        pass

    return False


has_occ = _has_occ()

if has_occ:
    from . import occ_utils as utils

from .main import *
