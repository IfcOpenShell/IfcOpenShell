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


def load_sheets(drawing):
    drawing.import_sheets()
    drawing.enable_editing_sheets()


def disable_editing_sheets(drawing):
    drawing.disable_editing_sheets()


def add_sheet(ifc, drawing, titleblock=None):
    sheet = ifc.run("document.add_information")
    identification = drawing.generate_sheet_identification()
    identification = drawing.ensure_unique_identification(identification)
    attributes = {"Identification": identification, "Name": "UNTITLED", "Scope": "DOCUMENTATION"}
    if ifc.get_schema() == "IFC2X3":
        attributes["DocumentId"] = attributes["Identification"]
        del attributes["Identification"]
    ifc.run("document.edit_information", information=sheet, attributes=attributes)
    drawing.create_svg_sheet(sheet, titleblock)
    drawing.import_sheets()


def open_sheet(drawing, sheet=None):
    drawing.open_svg(drawing.get_sheet_filename(sheet))


def remove_sheet(ifc, drawing, sheet=None):
    ifc.run("document.remove_document", document=sheet)
    drawing.import_sheets()


def load_drawings(drawing):
    drawing.import_drawings()
    drawing.enable_editing_drawings()


def disable_editing_drawings(drawing):
    drawing.disable_editing_drawings()


def add_drawing(ifc, collector, drawing, target_view=None, location_hint=None):
    drawing_name = drawing.ensure_unique_drawing_name(drawing.generate_drawing_name(target_view, location_hint))
    drawing_matrix = drawing.generate_drawing_matrix(target_view, location_hint)
    camera = drawing.create_camera(drawing_name, drawing_matrix)
    element = drawing.run_root_assign_class(
        obj=camera,
        ifc_class="IfcAnnotation",
        predefined_type="DRAWING",
        should_add_representation=True,
        context=drawing.get_body_context(),
        ifc_representation_class=None,
    )
    group = ifc.run("group.add_group")
    ifc.run("group.edit_group", group=group, attributes={"Name": drawing_name, "ObjectType": "DRAWING"})
    ifc.run("group.assign_group", group=group, product=element)
    collector.assign(camera)
    pset = ifc.run("pset.add_pset", product=element, name="EPset_Drawing")
    ifc.run("pset.edit_pset", pset=pset, properties={"TargetView": target_view, "Scale": "1/100"})
    drawing.import_drawings()


def remove_drawing(ifc, drawing_tool, drawing=None):
    collection = drawing_tool.get_drawing_collection(drawing)
    group = drawing_tool.get_drawing_group(drawing)
    if group:
        drawing_tool.delete_drawing_elements(drawing_tool.get_group_elements(group))
        ifc.run("group.remove_group", group=group)
    drawing_tool.delete_collection(collection)
    ifc.run("root.remove_product", product=drawing)
    drawing_tool.import_drawings()


def update_drawing_name(ifc, drawing_tool, drawing=None, name=None):
    if drawing_tool.get_name(drawing) != name:
        ifc.run("attribute.edit_attributes", product=drawing, attributes={"Name": name})
    group = drawing_tool.get_drawing_group(drawing)
    if drawing_tool.get_name(group) != name:
        ifc.run("attribute.edit_attributes", product=group, attributes={"Name": name})
    drawing_tool.set_drawing_collection_name(group, drawing_tool.get_drawing_collection(drawing))


def add_annotation(ifc, collector, drawing_tool, drawing=None, object_type=None):
    context = drawing_tool.get_annotation_context(drawing_tool.get_drawing_target_view(drawing))
    if not context:
        return
    drawing_tool.show_decorations()
    obj = drawing_tool.create_annotation_object(object_type)
    element = ifc.get_entity(obj)
    if not element:
        element = drawing_tool.run_root_assign_class(
            obj=obj,
            ifc_class="IfcAnnotation",
            predefined_type=object_type,
            should_add_representation=True,
            context=context,
            ifc_representation_class=drawing_tool.get_ifc_representation_class(object_type),
        )
        ifc.run("group.assign_group", group=drawing_tool.get_drawing_group(drawing), product=element)
    collector.assign(obj)
    drawing_tool.enable_editing(obj)
