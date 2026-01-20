# ==============================================================================
# Saikei Civil - Civil Engineering Tools for Blender
# Copyright (c) 2025 Michael Yoder / Desert Springs Civil Engineering PLLC
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Primary Author: Michael Yoder
# Company: Desert Springs Civil Engineering PLLC
# ==============================================================================


"""
Saikei Civil - Civil engineering design tools for Blender

This addon extends Bonsai (BlenderBIM) with civil engineering capabilities,
focusing on IFC4x3 alignment modeling for roads, railways, and infrastructure.

Requires:
    - Bonsai addon installed and enabled
    - IFC4X3 schema for alignment features
"""

bl_info = {
    "name": "Saikei Civil",
    "author": "IfcOpenShell Contributors",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Saikei Civil",
    "description": "Civil engineering design tools for IFC4x3 alignments",
    "doc_url": "https://docs.ifcopenshell.org/",
    "category": "Import-Export",
}

import sys

IN_BLENDER = sys.modules.get("bpy", None) is not None

if IN_BLENDER:
    from . import civil

    def register():
        civil.register()

    def unregister():
        civil.unregister()
