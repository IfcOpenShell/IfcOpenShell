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

from pathlib import Path
import ifcopenshell


def enable_editing_text(drawing, obj=None):
    drawing.enable_editing_text(obj)
    drawing.import_text_attributes(obj)


def disable_editing_text(drawing, obj=None):
    drawing.disable_editing_text(obj)


def edit_text(drawing, obj=None):
    drawing.synchronise_ifc_and_text_attributes(obj)
    drawing.update_text_size_pset(obj)
    drawing.update_text_value(obj)
    drawing.disable_editing_text(obj)


def enable_editing_assigned_product(drawing, obj=None):
    drawing.enable_editing_assigned_product(obj)
    drawing.import_assigned_product(obj)


def disable_editing_assigned_product(drawing, obj=None):
    drawing.disable_editing_assigned_product(obj)


def edit_assigned_product(ifc, drawing, obj=None, product=None):
    element = ifc.get_entity(obj)
    existing_product = drawing.get_assigned_product(element)
    if existing_product != product:
        if existing_product:
            ifc.run("drawing.unassign_product", relating_product=existing_product, related_object=element)
        if product:
            ifc.run("drawing.assign_product", relating_product=product, related_object=element)
        drawing.update_text_value(obj)

    drawing.disable_editing_assigned_product(obj)


def load_sheets(drawing):
    drawing.import_sheets()
    drawing.enable_editing_sheets()


def disable_editing_sheets(drawing):
    drawing.disable_editing_sheets()


def add_sheet(ifc, drawing, titleblock: ifcopenshell.entity_instance):
    sheet = ifc.run("document.add_information")
    layout = ifc.run("document.add_reference", information=sheet)
    titleblock_reference = ifc.run("document.add_reference", information=sheet)
    identification = drawing.generate_sheet_identification()
    identification = drawing.ensure_unique_identification(identification)
    if ifc.get_schema() == "IFC2X3":
        attributes = {"DocumentId": identification, "Name": "UNTITLED", "Scope": "SHEET"}
    else:
        attributes = {"Identification": identification, "Name": "UNTITLED", "Scope": "SHEET"}
    ifc.run("document.edit_information", information=sheet, attributes=attributes)

    attributes = drawing.generate_reference_attributes(
        layout, Location=drawing.get_default_layout_path(identification, "UNTITLED"), Description="LAYOUT"
    )
    ifc.run("document.edit_reference", reference=layout, attributes=attributes)

    attributes = drawing.generate_reference_attributes(
        layout, Location=drawing.get_default_titleblock_path(titleblock), Description="TITLEBLOCK"
    )
    ifc.run("document.edit_reference", reference=titleblock_reference, attributes=attributes)

    drawing.create_svg_sheet(sheet, titleblock)
    drawing.import_sheets()


def regenerate_sheet(drawing, sheet=None):
    titleblock_uri = drawing.get_document_uri(sheet, "TITLEBLOCK")
    drawing.create_svg_sheet(sheet, drawing.sanitise_filename(Path(titleblock_uri).stem))
    try:
        drawing.add_drawings(sheet)
    except FileNotFoundError:
        path_layout = drawing.get_document_uri(sheet, "LAYOUT")
        if drawing.does_file_exist(path_layout):
            drawing.delete_file(path_layout)


def open_sheet(drawing, sheet=None):
    drawing.open_layout_svg(drawing.get_document_uri(sheet, "LAYOUT"))


def remove_sheet(ifc, drawing, sheet=None):
    for reference in drawing.get_document_references(sheet):
        if drawing.get_reference_description(reference) in ("LAYOUT", "SHEET", "REVISION", "RASTER"):
            uri = ifc.resolve_uri(drawing.get_document_uri(reference))
            if drawing.does_file_exist(uri):
                drawing.delete_file(uri)
    ifc.run("document.remove_information", information=sheet)
    drawing.import_sheets()


def rename_sheet(ifc, drawing, sheet: ifcopenshell.entity_instance, identification: str, name: str) -> None:
    if ifc.get_schema() == "IFC2X3":
        attributes = {"DocumentId": identification, "Name": name}
    else:
        attributes = {"Identification": identification, "Name": name}
    ifc.run("document.edit_information", information=sheet, attributes=attributes)
    for reference in drawing.get_document_references(sheet):
        description = drawing.get_reference_description(reference)
        if description == "SHEET":
            old_location = drawing.get_reference_location(reference)
            new_location = drawing.get_default_sheet_path(identification, name)
            if old_location != new_location:
                ifc.run("document.edit_reference", reference=reference, attributes={"Location": new_location})
                old_location = ifc.resolve_uri(old_location)
                if drawing.does_file_exist(old_location):
                    drawing.move_file(old_location, ifc.resolve_uri(new_location))
        elif description == "LAYOUT":
            old_location = drawing.get_reference_location(reference)
            new_location = drawing.get_default_layout_path(identification, name)
            if old_location != new_location:
                ifc.run("document.edit_reference", reference=reference, attributes={"Location": new_location})
                old_location = ifc.resolve_uri(old_location)
                if drawing.does_file_exist(old_location):
                    drawing.move_file(old_location, ifc.resolve_uri(new_location))


def rename_reference(ifc, drawing, reference=None, identification=None):
    attributes = drawing.generate_reference_attributes(reference, Identifiaction=identification)
    ifc.run("document.edit_reference", reference=reference, attributes=attributes)


def load_schedules(drawing):
    drawing.import_documents("SCHEDULE")
    drawing.enable_editing_schedules()


def load_references(drawing):
    drawing.import_documents("REFERENCE")
    drawing.enable_editing_references()


def disable_editing_schedules(drawing):
    drawing.disable_editing_schedules()


def disable_editing_references(drawing):
    drawing.disable_editing_references()


def add_document(ifc, drawing, document_type, uri=None):
    document = ifc.run("document.add_information")
    reference = ifc.run("document.add_reference", information=document)
    name = drawing.get_path_filename(uri)
    if ifc.get_schema() == "IFC2X3":
        attributes = {"DocumentId": "X", "Name": name, "Scope": document_type}
    else:
        attributes = {"Identification": "X", "Name": name, "Scope": document_type}
    ifc.run("document.edit_information", information=document, attributes=attributes)
    ifc.run("document.edit_reference", reference=reference, attributes={"Location": uri})
    drawing.import_documents(document_type)


def remove_document(ifc, drawing, document_type, document=None):
    ifc.run("document.remove_information", information=document)
    drawing.import_documents(document_type)


def open_schedule(drawing, schedule=None):
    drawing.open_spreadsheet(drawing.get_document_uri(schedule))


def open_reference(drawing, reference=None):
    drawing.open_svg(drawing.get_document_uri(reference))


def update_document_name(ifc, drawing, document=None, name=None):
    if drawing.get_name(document) != name:
        ifc.run("document.edit_information", information=document, attributes={"Name": name})


def load_drawings(drawing):
    drawing.import_drawings()
    drawing.enable_editing_drawings()


def disable_editing_drawings(drawing):
    drawing.disable_editing_drawings()


def add_drawing(ifc, collector, drawing, target_view=None, location_hint=None):
    drawing_name = drawing.ensure_unique_drawing_name(drawing.generate_drawing_name(target_view, location_hint))
    drawing_matrix = drawing.generate_drawing_matrix(target_view, location_hint)
    camera = drawing.create_camera(drawing_name, drawing_matrix, location_hint)
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
    ifc.run("group.assign_group", group=group, products=[element])
    collector.assign(camera)
    pset = ifc.run("pset.add_pset", product=element, name="EPset_Drawing")
    if drawing.get_unit_system() == "METRIC":
        scale = "1/100"
        human_scale = "1:100"
    else:
        scale = "1/96"
        human_scale = '1/8"=1\'-0"'

    shading_styles_path = drawing.get_default_drawing_resource_path("ShadingStyles")
    ifc.run(
        "pset.edit_pset",
        pset=pset,
        properties={
            "TargetView": target_view,
            "Scale": scale,
            "HumanScale": human_scale,
            "HasUnderlay": False,
            "HasLinework": True,
            "HasAnnotation": True,
            "GlobalReferencing": True,
            "Stylesheet": drawing.get_default_drawing_resource_path("Stylesheet"),
            "Markers": drawing.get_default_drawing_resource_path("Markers"),
            "Symbols": drawing.get_default_drawing_resource_path("Symbols"),
            "Patterns": drawing.get_default_drawing_resource_path("Patterns"),
            "ShadingStyles": (shading_styles_path := drawing.get_default_drawing_resource_path("ShadingStyles")),
            "CurrentShadingStyle": drawing.get_default_shading_style(),
        },
    )
    drawing.setup_shading_styles_path(shading_styles_path)
    information = ifc.run("document.add_information")
    uri = drawing.get_default_drawing_path(drawing_name)
    reference = ifc.run("document.add_reference", information=information)
    if ifc.get_schema() == "IFC2X3":
        attributes = {"DocumentId": "X", "Name": drawing_name, "Scope": "DRAWING"}
    else:
        attributes = {"Identification": "X", "Name": drawing_name, "Scope": "DRAWING"}
    ifc.run("document.edit_information", information=information, attributes=attributes)
    ifc.run("document.edit_reference", reference=reference, attributes={"Location": uri})
    ifc.run("document.assign_document", products=[element], document=reference)
    drawing.import_drawings()


def duplicate_drawing(ifc, drawing_tool, drawing=None, should_duplicate_annotations=False):
    drawing_name = drawing_tool.ensure_unique_drawing_name(drawing_tool.get_name(drawing))
    new_drawing = ifc.run("root.copy_class", product=drawing)
    drawing_tool.copy_representation(drawing, new_drawing)
    drawing_tool.set_name(new_drawing, drawing_name)
    group = drawing_tool.get_drawing_group(new_drawing)
    ifc.run("group.unassign_group", group=group, products=[new_drawing])
    new_group = ifc.run("group.add_group")
    ifc.run("group.edit_group", group=new_group, attributes={"Name": drawing_name, "ObjectType": "DRAWING"})
    ifc.run("group.assign_group", group=new_group, products=[new_drawing])
    if should_duplicate_annotations:
        for annotation in drawing_tool.get_group_elements(group):
            if annotation == drawing:
                continue
            new_annotation = ifc.run("root.copy_class", product=annotation)
            drawing_tool.copy_representation(annotation, new_annotation)
            ifc.run("group.unassign_group", group=group, products=[new_annotation])
            ifc.run("group.assign_group", group=new_group, products=[new_annotation])

    old_reference = drawing_tool.get_drawing_document(new_drawing)
    ifc.run("document.unassign_document", products=[new_drawing], document=old_reference)

    information = ifc.run("document.add_information")
    uri = drawing_tool.get_default_drawing_path(drawing_name)
    reference = ifc.run("document.add_reference", information=information)
    if ifc.get_schema() == "IFC2X3":
        attributes = {"DocumentId": "X", "Name": drawing_name, "Scope": "DRAWING"}
    else:
        attributes = {"Identification": "X", "Name": drawing_name, "Scope": "DRAWING"}
    ifc.run("document.edit_information", information=information, attributes=attributes)
    ifc.run("document.edit_reference", reference=reference, attributes={"Location": uri})
    ifc.run("document.assign_document", products=[new_drawing], document=reference)

    drawing_tool.import_drawings()
    return new_drawing


def remove_drawing(ifc, drawing_tool, drawing=None):
    if drawing_tool.is_active_drawing(drawing):
        drawing_tool.run_drawing_activate_model()

    collection = drawing_tool.get_drawing_collection(drawing)
    if collection:
        drawing_tool.delete_collection(collection)

    for reference in drawing_tool.get_drawing_references(drawing):
        reference_obj = ifc.get_object(reference)
        if reference_obj:
            drawing_tool.delete_object(reference_obj)
        ifc.run("root.remove_product", product=reference)

    information = drawing_tool.get_reference_document(drawing_tool.get_drawing_document(drawing))
    uri = ifc.resolve_uri(drawing_tool.get_document_uri(information))
    if drawing_tool.does_file_exist(uri):
        drawing_tool.delete_file(uri)
    ifc.run("document.remove_information", information=information)

    group = drawing_tool.get_drawing_group(drawing)
    if group:
        drawing_tool.delete_drawing_elements(drawing_tool.get_group_elements(group))
        ifc.run("group.remove_group", group=group)

    drawing_tool.import_drawings()


def update_drawing_name(ifc, drawing_tool, drawing=None, name=None):
    if drawing_tool.get_name(drawing) != name:
        ifc.run("attribute.edit_attributes", product=drawing, attributes={"Name": name})
    group = drawing_tool.get_drawing_group(drawing)
    if drawing_tool.get_name(group) != name:
        ifc.run("attribute.edit_attributes", product=group, attributes={"Name": name})
    collection = drawing_tool.get_drawing_collection(drawing)
    if collection:
        drawing_tool.set_drawing_collection_name(drawing, collection)

    reference = drawing_tool.get_drawing_document(drawing)
    information = drawing_tool.get_reference_document(reference)
    ifc.run("document.edit_information", information=information, attributes={"Name": name})
    old_location = drawing_tool.get_reference_location(reference)
    new_location = drawing_tool.get_default_drawing_path(name)
    if old_location != new_location:
        ifc.run("document.edit_reference", reference=reference, attributes={"Location": new_location})
        resolved_old_location = ifc.resolve_uri(old_location)
        resolved_new_location = ifc.resolve_uri(new_location)
        if drawing_tool.does_file_exist(resolved_old_location):
            drawing_tool.move_file(resolved_old_location, resolved_new_location)

        for reference in drawing_tool.get_references_with_location(old_location):
            ifc.run("document.edit_reference", reference=reference, attributes={"Location": new_location})
            sheet = drawing_tool.get_reference_document(reference)
            if sheet:
                uri = ifc.resolve_uri(drawing_tool.get_document_uri(sheet, "LAYOUT"))
                if drawing_tool.does_file_exist(uri):
                    drawing_tool.update_embedded_svg_location(uri, reference, resolved_new_location)

        if drawing_tool.is_editing_sheets():
            drawing_tool.import_sheets()


def add_annotation(ifc, collector, drawing_tool, drawing=None, object_type=None):
    target_view = drawing_tool.get_drawing_target_view(drawing)
    context = drawing_tool.get_annotation_context(target_view, object_type)
    if not context:
        context = drawing_tool.create_annotation_context(target_view, object_type)

    drawing_tool.show_decorations()
    obj = drawing_tool.create_annotation_object(drawing, object_type)
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
        ifc.run("group.assign_group", group=drawing_tool.get_drawing_group(drawing), products=[element])
    collector.assign(obj)
    drawing_tool.enable_editing(obj)


def build_schedule(drawing, schedule=None):
    drawing.create_svg_schedule(schedule)
    drawing.open_svg(drawing.get_path_with_ext(drawing.get_document_uri(schedule), "svg"))


def sync_references(ifc, collector, drawing_tool, drawing=None):
    if not drawing_tool.has_annotation(drawing):
        return

    context = drawing_tool.get_annotation_context(drawing_tool.get_drawing_target_view(drawing))
    if not context:
        return

    group = drawing_tool.get_drawing_group(drawing)
    for reference_element in drawing_tool.get_potential_reference_elements(drawing):
        reference_obj = ifc.get_object(reference_element)
        annotation = drawing_tool.get_drawing_reference_annotation(drawing, reference_element)

        should_delete_existing_annotation = False
        should_create_annotation = False

        # remove annotation only if the reference object was changed
        # otherwise we rely on the existing annotation
        if annotation:
            if reference_obj and (ifc.is_moved(reference_obj) or ifc.is_edited(reference_obj)):
                should_delete_existing_annotation = True

        if should_delete_existing_annotation or not annotation:
            should_create_annotation = True

        if should_delete_existing_annotation:
            annotation_obj = ifc.get_object(annotation)
            if annotation_obj:
                drawing_tool.delete_object(annotation_obj)
            ifc.run("root.remove_product", product=annotation)

        if should_create_annotation:
            annotation = drawing_tool.generate_reference_annotation(drawing, reference_element, context)
            if annotation:
                ifc.run("drawing.assign_product", relating_product=reference_element, related_object=annotation)
                ifc.run("group.assign_group", group=group, products=[annotation])
                collector.assign(ifc.get_object(annotation))

        if reference_obj and ifc.is_moved(reference_obj):
            drawing_tool.sync_object_placement(reference_obj)

        if reference_obj and ifc.is_edited(reference_obj):
            drawing_tool.sync_object_representation(reference_obj)


def select_assigned_product(drawing, context):
    drawing.select_assigned_product(context)


def activate_drawing_view(ifc, drawing_tool, drawing):
    camera = ifc.get_object(drawing)
    if not camera:
        camera = drawing_tool.import_drawing(drawing)
        drawing_tool.import_annotations_in_group(drawing_tool.get_drawing_group(drawing))
    drawing_tool.activate_drawing(camera)
