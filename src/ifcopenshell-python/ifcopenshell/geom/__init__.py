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

"""Geometry processing and analysis"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def _has_occ():
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
