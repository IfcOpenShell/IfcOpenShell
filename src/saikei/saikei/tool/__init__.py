# Saikei Civil - Civil Engineering Tools for IfcOpenShell
# Copyright (C) 2025 IfcOpenShell Contributors
#
# This file is part of Saikei Civil.
#
# Saikei Civil is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Saikei Civil is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Saikei Civil.  If not, see <http://www.gnu.org/licenses/>.

"""Saikei Civil Tool Module

This module contains Blender-specific implementations that bridge the
core business logic to the Blender environment.

Following Bonsai's architecture pattern:
- core/ = Pure Python logic
- tool/ = Blender implementations with bpy (this module)
- civil/ = UI layer (operators, panels, properties)

Usage:
    from .... import tool  # relative import from within saikei package
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Ifc.get()
"""

from .alignment import Alignment

# Lazy import wrappers for Bonsai's tools
# We use lazy imports to avoid circular import issues with Bonsai's tool module
_bonsai_ifc = None
_bonsai_collector = None


class _LazyIfc:
    """Lazy wrapper for bonsai.tool.Ifc to avoid circular imports."""

    @staticmethod
    def _get_real():
        global _bonsai_ifc
        if _bonsai_ifc is None:
            try:
                from bonsai.tool import Ifc as _Ifc

                _bonsai_ifc = _Ifc
            except ImportError:
                _bonsai_ifc = None
        return _bonsai_ifc

    def __getattr__(self, name):
        real = self._get_real()
        if real is None:
            raise ImportError("Bonsai is not available")
        return getattr(real, name)

    @classmethod
    def get(cls):
        real = cls._get_real()
        if real is None:
            return None
        return real.get()

    @classmethod
    def get_object(cls, element):
        real = cls._get_real()
        if real is None:
            return None
        return real.get_object(element)

    @classmethod
    def link(cls, element, obj):
        real = cls._get_real()
        if real is None:
            return None
        return real.link(element, obj)

    @classmethod
    def unlink(cls, obj=None, element=None):
        real = cls._get_real()
        if real is None:
            return None
        return real.unlink(obj=obj, element=element)


class _LazyCollector:
    """Lazy wrapper for bonsai.tool.Collector to avoid circular imports."""

    @staticmethod
    def _get_real():
        global _bonsai_collector
        if _bonsai_collector is None:
            try:
                from bonsai.tool import Collector as _Collector

                _bonsai_collector = _Collector
            except ImportError:
                _bonsai_collector = None
        return _bonsai_collector

    def __getattr__(self, name):
        real = self._get_real()
        if real is None:
            raise ImportError("Bonsai is not available")
        return getattr(real, name)

    @classmethod
    def assign(cls, obj):
        real = cls._get_real()
        if real is None:
            return None
        return real.assign(obj)


# Export lazy wrappers as if they were the real tools
Ifc = _LazyIfc()
Collector = _LazyCollector()
