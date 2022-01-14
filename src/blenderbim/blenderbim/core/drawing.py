# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.


def enable_editing_text(drawing, obj=None):
    drawing.enable_editing_text(obj)
    drawing.import_text_attributes(obj)


def disable_editing_text(drawing, obj=None):
    drawing.disable_editing_text(obj)


def edit_text(ifc, drawing, obj=None):
    ifc.run(
        "drawing.edit_text_literal",
        text_literal=drawing.get_text_literal(obj),
        attributes=drawing.export_text_literal_attributes(obj),
    )
    drawing.update_text_value(obj)
    drawing.disable_editing_text(obj)


def enable_editing_text_product(drawing, obj=None):
    drawing.enable_editing_text_product(obj)
    drawing.import_text_product(obj)


def disable_editing_text_product(drawing, obj=None):
    drawing.disable_editing_text_product(obj)


def edit_text_product(ifc, drawing, obj=None, product=None):
    element = ifc.get_entity(obj)
    existing_product = drawing.get_text_product(element)
    if existing_product == product:
        return
    if existing_product:
        ifc.run("drawing.unassign_product", relating_product=existing_product, related_object=element)
    if product:
        ifc.run("drawing.assign_product", relating_product=product, related_object=element)
    drawing.update_text_value(obj)
    drawing.disable_editing_text_product(obj)
