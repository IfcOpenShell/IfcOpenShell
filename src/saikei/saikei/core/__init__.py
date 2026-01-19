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

"""Saikei Civil Core Module

This module contains pure Python business logic with NO Blender (bpy) dependencies.
All functions here must be testable outside of Blender.

Following Bonsai's architecture pattern:
- core/ = Pure Python logic, receives tool classes as parameters
- tool/ = Blender implementations with bpy
- civil/ = UI layer (operators, panels, properties)
"""
