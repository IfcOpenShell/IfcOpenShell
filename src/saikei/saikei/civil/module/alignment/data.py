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


"""Data caching layer for the alignment module

This module provides cached access to alignment data for UI display,
following Bonsai's data loading pattern.
"""


def get_ifc_file():
    """Get the current IFC file from Bonsai"""
    try:
        import bonsai.tool as tool

        return tool.Ifc.get()
    except (ImportError, AttributeError):
        return None


class AlignmentData:
    """Cached alignment data for UI display"""

    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        """Load alignment data from IFC file"""
        cls.data = {
            "alignments": [],
            "active_alignment": None,
            "segments": [],
        }

        ifc = get_ifc_file()
        if ifc is None:
            cls.is_loaded = True
            return

        # Load all alignments
        alignments = ifc.by_type("IfcAlignment")
        cls.data["alignments"] = [
            {
                "id": a.id(),
                "name": a.Name or f"Alignment {a.id()}",
                "global_id": a.GlobalId,
            }
            for a in alignments
        ]

        cls.is_loaded = True

    @classmethod
    def refresh(cls):
        """Force refresh of alignment data"""
        cls.is_loaded = False
        cls.load()
