# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Bonsai Contributors
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy

from . import operator, ui

classes = (
    operator.CADSketcherWallTypeItem,
    operator.CADSketcherSlabTypeItem,
    operator.CADSketcherCoveringItem,
    operator.CADSketcherPlateItem,
    operator.CADSketcherOpeningItem,
    operator.CADSketcherWindowItem,
    operator.CADSketcherDoorItem,
    operator.CADSketcherBeamItem,
    operator.CADSketcherMemberItem,
    operator.CADSketcherFootingItem,
    operator.CADSketcherColumnItem,
    operator.CADSketcherPileItem,
    operator.FetchCADSketcher,
    ui.SetSketchRole,
    ui.BIM_PT_cadsketcher,
)


def register():
    pass


def unregister():
    pass
