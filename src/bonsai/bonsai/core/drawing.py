# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import ifcopenshell.util.representation

    import bonsai.tool as tool


def enable_editing_text(drawing: type[tool.Drawing], obj: bpy.types.Object) -> None:
    drawing.enable_editing_text(obj)
    drawing.import_text_attributes(obj)


def disable_editing_text(drawing: type[tool.Drawing], obj: bpy.types.Object) -> None:
    drawing.disable_editing_text(obj)


def edit_text(drawing: type[tool.Drawing], obj: bpy.types.Object) -> None:
    literal_attributes = drawing.export_text_literal_attributes(obj)
    drawing.edit_text_font_size(obj, drawing.export_font_size(obj))
    drawing.edit_text_wrap_length(obj, drawing.export_wrap_length(obj))
    drawing.edit_text_symbol(obj, drawing.export_symbol(obj))
    drawing.edit_text_literals(obj, literal_attributes)
    drawing.disable_editing_text(obj)


def copy_text_to_selection(
    drawing: type[tool.Drawing],
    attribute: Literal["FONT_SIZE", "ALIGNMENT", "WRAP_LENGTH", "SYMBOL", "LITERALS"],
    attribute_obj: bpy.types.Object,
    apply_objs: list[bpy.types.Object],
) -> None:
    if attribute == "FONT_SIZE":
        data = drawing.export_font_size(attribute_obj)
    elif attribute == "ALIGNMENT":
        data = drawing.export_alignment(attribute_obj)
    elif attribute == "WRAP_LENGTH":
        data = drawing.export_wrap_length(attribute_obj)
    elif attribute == "SYMBOL":
        data = drawing.export_symbol(attribute_obj)
    elif attribute == "LITERALS":
        data = drawing.export_text_literal_attributes(attribute_obj)
    for obj in apply_objs:
        if attribute == "FONT_SIZE":
            drawing.edit_text_font_size(obj, data)
        elif attribute == "ALIGNMENT":
            drawing.edit_text_alignment(obj, data)
        elif attribute == "WRAP_LENGTH":
            drawing.edit_text_wrap_length(obj, data)
        elif attribute == "SYMBOL":
            drawing.edit_text_symbol(obj, data)
        elif attribute == "LITERALS":
            drawing.edit_text_literals(obj, data)
        drawing.disable_editing_text(obj)


def enable_editing_assigned_product(drawing: type[tool.Drawing], obj: bpy.types.Object) -> None:
    drawing.enable_editing_assigned_product(obj)
    drawing.import_assigned_product(obj)


def disable_editing_assigned_product(drawing: type[tool.Drawing], obj: bpy.types.Object) -> None:
    drawing.disable_editing_assigned_product(obj)


def edit_assigned_product(
    ifc: type[tool.Ifc],
    drawing: type[tool.Drawing],
    obj: bpy.types.Object,
    product: Optional[ifcopenshell.entity_instance] = None,
) -> None:
    element = ifc.get_entity(obj)
    assert element

    # Temporarily accomodate existing bug and check for multiple products.
    existing_products = drawing.get_assigned_product_workaround(element)
    if existing_products != [product]:

        if product in existing_products:
            assert product is not None
            existing_products.remove(product)

        for existing_product in existing_products:
            ifc.run("drawing.unassign_product", relating_product=existing_product, related_object=element)

        if product:
            ifc.run("drawing.assign_product", relating_product=product, related_object=element)

    drawing.disable_editing_assigned_product(obj)


def load_sheets(drawing: type[tool.Drawing]) -> None:
    drawing.import_sheets()
    drawing.enable_editing_sheets()


def disable_editing_sheets(drawing: type[tool.Drawing]) -> None:
    drawing.disable_editing_sheets()


def add_sheet(ifc: type[tool.Ifc], drawing: type[tool.Drawing], titleblock: ifcopenshell.entity_instance) -> None:
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


def regenerate_sheet(
    drawing: type[tool.Drawing], sheet: ifcopenshell.entity_instance
) -> Union[list[tool.Drawing.SheetWarningType], None]:
    titleblock_uri = drawing.get_document_uri(sheet, "TITLEBLOCK")
    assert titleblock_uri

    drawing.create_svg_sheet(sheet, drawing.sanitise_filename(Path(titleblock_uri).stem))
    try:
        drawing.add_drawings(sheet)
    except FileNotFoundError:
        path_layout = drawing.get_document_uri(sheet, "LAYOUT")
        assert path_layout
        if drawing.does_file_exist(path_layout):
            drawing.delete_file(path_layout)


def open_layout(drawing: type[tool.Drawing], sheet: ifcopenshell.entity_instance) -> None:
    drawing.open_layout_svg(drawing.get_document_uri(sheet, "LAYOUT"))


def remove_sheet(ifc: type[tool.Ifc], drawing: type[tool.Drawing], sheet: ifcopenshell.entity_instance) -> None:
    for reference in drawing.get_document_references(sheet):
        if drawing.get_reference_description(reference) in ("LAYOUT", "SHEET", "REVISION", "RASTER"):
            uri = ifc.resolve_uri(drawing.get_document_uri(reference))
            if drawing.does_file_exist(uri):
                drawing.delete_file(uri)
    ifc.run("document.remove_information", information=sheet)
    drawing.import_sheets()


def rename_sheet(
    ifc: type[tool.Ifc],
    drawing: type[tool.Drawing],
    sheet: ifcopenshell.entity_instance,
    identification: str,
    name: str,
) -> None:
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


def rename_reference(
    ifc: type[tool.Ifc], drawing: type[tool.Drawing], reference: ifcopenshell.entity_instance, identification: str
) -> None:
    attributes = drawing.generate_reference_attributes(reference, Identification=identification)
    ifc.run("document.edit_reference", reference=reference, attributes=attributes)


def load_schedules(drawing: type[tool.Drawing]) -> None:
    drawing.import_documents("SCHEDULE")
    drawing.enable_editing_schedules()


def load_references(drawing: type[tool.Drawing]) -> None:
    drawing.import_documents("REFERENCE")
    drawing.enable_editing_references()


def disable_editing_schedules(drawing: type[tool.Drawing]) -> None:
    drawing.disable_editing_schedules()


def disable_editing_references(drawing: type[tool.Drawing]) -> None:
    drawing.disable_editing_references()


def add_document(
    ifc: type[tool.Ifc], drawing: type[tool.Drawing], document_type: tool.Drawing.DOCUMENT_TYPE, uri: str
) -> None:
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


def remove_document(
    ifc: type[tool.Ifc],
    drawing: type[tool.Drawing],
    document_type: tool.Drawing.DOCUMENT_TYPE,
    document: ifcopenshell.entity_instance,
) -> None:
    ifc.run("document.remove_information", information=document)
    drawing.import_documents(document_type)


def open_schedule(drawing: type[tool.Drawing], schedule: ifcopenshell.entity_instance) -> None:
    drawing.open_spreadsheet(drawing.get_document_uri(schedule))


def open_reference(drawing: type[tool.Drawing], reference: ifcopenshell.entity_instance) -> None:
    drawing.open_svg(drawing.get_document_uri(reference))


def update_document_name(
    ifc: type[tool.Ifc], drawing: type[tool.Drawing], document: ifcopenshell.entity_instance, name=None
) -> None:
    if drawing.get_name(document) != name:
        ifc.run("document.edit_information", information=document, attributes={"Name": name})


def load_drawings(drawing: type[tool.Drawing]) -> None:
    drawing.import_drawings()
    drawing.enable_editing_drawings()


def disable_editing_drawings(drawing: type[tool.Drawing]) -> None:
    drawing.disable_editing_drawings()


def add_drawing(
    ifc: type[tool.Ifc],
    collector: type[tool.Collector],
    drawing: type[tool.Drawing],
    target_view: ifcopenshell.util.representation.TARGET_VIEW,
    location_hint: Union[tool.Drawing.LocationHintLiteral, int],
) -> None:
    assert location_hint is not None
    drawing_name = drawing.ensure_unique_drawing_name(drawing.generate_drawing_name(target_view, location_hint))
    drawing_matrix = drawing.generate_drawing_matrix(target_view, location_hint)
    camera = drawing.create_camera(drawing_name, drawing_matrix, location_hint, target_view)
    element = drawing.run_root_assign_class(
        obj=camera,
        ifc_class="IfcAnnotation",
        predefined_type="DRAWING",
        should_add_representation=True,
        context=drawing.get_body_context(),
        ifc_representation_class=None,
    )

    drawings_parent_group = drawing.ensure_drawings_parent_group()

    group = ifc.run("group.add_group")
    ifc.run("group.edit_group", group=group, attributes={"Name": drawing_name, "ObjectType": "DRAWING"})
    ifc.run("group.assign_group", group=group, products=[element])

    ifc.run("group.assign_group", group=drawings_parent_group, products=[group])

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

    drawings_parent_document = drawing.ensure_drawings_parent_document()

    information = ifc.run("document.add_information", parent=drawings_parent_document)
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


def duplicate_drawing(
    ifc: type[tool.Ifc],
    blender: type[tool.Blender],
    drawing_tool: type[tool.Drawing],
    geometry: type[tool.Geometry],
    drawing: ifcopenshell.entity_instance,
    should_duplicate_annotations: bool = False,
) -> ifcopenshell.entity_instance:
    drawing_name = drawing_tool.ensure_unique_drawing_name(drawing_tool.get_name(drawing))
    new_drawing = ifc.run("root.copy_class", product=drawing)
    drawing_tool.clear_annotation_relationships(new_drawing)
    drawing_tool.copy_representation(drawing, new_drawing)
    drawing_tool.set_name(new_drawing, drawing_name)
    group = drawing_tool.get_drawing_group(new_drawing)
    ifc.run("group.unassign_group", group=group, products=[new_drawing])

    drawings_parent_group = drawing_tool.ensure_drawings_parent_group()

    new_group = ifc.run("group.add_group")
    ifc.run("group.edit_group", group=new_group, attributes={"Name": drawing_name, "ObjectType": "DRAWING"})
    ifc.run("group.assign_group", group=new_group, products=[new_drawing])
    ifc.run("group.assign_group", group=drawings_parent_group, products=[new_group])
    if should_duplicate_annotations:
        new_annotations: list[ifcopenshell.entity_instance] = []
        annotation_objs = [ifc.get_object(a) for a in drawing_tool.get_group_elements(group) if a != drawing]
        old_to_new, _ = geometry.duplicate_ifc_objects(annotation_objs)
        for new_elements in old_to_new.values():
            # Remove the Blender object, since we haven't actually activated the duplicated drawing
            for new_element in new_elements:
                blender.remove_object(ifc.get_object(new_element))
            new_annotations.extend(new_elements)
        ifc.run("group.unassign_group", group=group, products=new_annotations)
        ifc.run("group.assign_group", group=new_group, products=new_annotations)

    old_reference = drawing_tool.get_drawing_document(new_drawing)
    ifc.run("document.unassign_document", products=[new_drawing], document=old_reference)

    drawings_parent_document = drawing_tool.ensure_drawings_parent_document()

    information = ifc.run("document.add_information", parent=drawings_parent_document)
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


def remove_drawing(
    ifc: type[tool.Ifc], drawing_tool: type[tool.Drawing], drawing: ifcopenshell.entity_instance
) -> None:
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


def update_drawing_name(
    ifc: type[tool.Ifc], drawing_tool: type[tool.Drawing], drawing: ifcopenshell.entity_instance, name: str
) -> None:
    if drawing_tool.get_name(drawing) != name:
        ifc.run("attribute.edit_attributes", product=drawing, attributes={"Name": name})

    drawing_tool.set_camera_name(drawing, name)

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


def add_annotation(
    ifc: type[tool.Ifc],
    collector: type[tool.Collector],
    drawing_tool: type[tool.Drawing],
    drawing: ifcopenshell.entity_instance,
    object_type: str,
    relating_type: ifcopenshell.entity_instance,
    enable_editing: bool = False,
) -> bpy.types.Object:
    target_view = drawing_tool.get_drawing_target_view(drawing)
    context = drawing_tool.get_annotation_context(target_view, object_type)
    if not context:
        context = drawing_tool.create_annotation_context(target_view, object_type)

    drawing_tool.show_decorations()
    obj = drawing_tool.create_annotation_object(drawing, object_type)
    element = ifc.get_entity(obj)
    if not element:  # Brand new annotation
        relating_type_rep = drawing_tool.get_annotation_representation(relating_type) if relating_type else None
        element = drawing_tool.run_root_assign_class(
            obj=obj,
            ifc_class="IfcAnnotation",
            predefined_type=object_type,
            should_add_representation=not relating_type_rep,
            context=context,
            ifc_representation_class=drawing_tool.get_ifc_representation_class(object_type),
        )
        if relating_type:
            drawing_tool.run_type_assign_type(element=element, relating_type=relating_type)
        ifc.run("group.assign_group", group=drawing_tool.get_drawing_group(drawing), products=[element])
    if representation := drawing_tool.get_representation(element, context):
        drawing_tool.reload_representation(obj=obj, representation=representation)
    collector.assign(obj, should_clean_users_collection=True)
    if not relating_type_rep and object_type != "IMAGE" and enable_editing:
        drawing_tool.enable_editing(obj)
    return obj


def build_schedule(drawing: type[tool.Drawing], schedule: ifcopenshell.entity_instance) -> None:
    drawing.create_svg_schedule(schedule)
    drawing.open_svg(drawing.get_path_with_ext(drawing.get_document_uri(schedule), "svg"))


def sync_references(
    ifc: type[tool.Ifc],
    collector: type[tool.Collector],
    drawing_tool: type[tool.Drawing],
    drawing: ifcopenshell.entity_instance,
) -> None:
    if not drawing_tool.has_annotation(drawing):
        return

    if not (context := drawing_tool.get_annotation_context(drawing_tool.get_drawing_target_view(drawing))):
        return

    group = drawing_tool.get_drawing_group(drawing)
    potential_reference_elements = drawing_tool.get_potential_reference_elements(drawing)

    for element in potential_reference_elements:
        # Skip spatial elements - their IFC placement is the source of truth
        if element.is_a("IfcSpatialElement"):
            continue

        # Skip grids - their IFC placement is the source of truth
        if element.is_a("IfcGrid") or element.is_a("IfcGridAxis"):
            continue

        if (obj := ifc.get_object(element)) and ifc.is_moved(obj):
            drawing_tool.sync_object_placement(obj)

    for element in drawing_tool.get_group_elements(group):
        if not drawing_tool.is_auto_annotation(element):
            continue

        # Skip spatial elements - should never sync their placement
        if element.is_a("IfcSpatialElement"):
            continue

        # Skip grids
        if element.is_a("IfcGrid") or element.is_a("IfcGridAxis"):
            continue

        if (obj := ifc.get_object(element)) and ifc.is_moved(obj):
            drawing_tool.sync_object_placement(obj)
        if not (reference_element := drawing_tool.get_assigned_product(element)):
            if obj := ifc.get_object(element):
                drawing_tool.delete_object(obj)
            ifc.run("root.remove_product", product=element)
            continue
        reference_obj = ifc.get_object(reference_element)
        if reference_element not in potential_reference_elements:
            # It was auto created, so it makes sense to auto delete
            if obj := ifc.get_object(element):
                drawing_tool.delete_object(obj)
            ifc.run("root.remove_product", product=element)
        elif not drawing_tool.regenerate_reference_annotation(drawing, element, reference_element, context):
            if obj := ifc.get_object(element):
                drawing_tool.delete_object(obj)
            ifc.run("root.remove_product", product=element)

    for reference_element in potential_reference_elements:
        if not drawing_tool.get_drawing_reference_annotation(drawing, reference_element):
            if annotation := drawing_tool.generate_reference_annotation(drawing, reference_element, context):
                ifc.run("drawing.assign_product", relating_product=reference_element, related_object=annotation)
                ifc.run("group.assign_group", group=group, products=[annotation])
                collector.assign(ifc.get_object(annotation))


def select_assigned_product(drawing: type[tool.Drawing], context: bpy.types.Context) -> None:
    drawing.select_assigned_product(context)


def activate_drawing_view(
    ifc: type[tool.Ifc],
    blender: type[tool.Blender],
    drawing_tool: type[tool.Drawing],
    drawing: ifcopenshell.entity_instance,
) -> None:
    camera = ifc.get_object(drawing)
    if not camera:
        camera = drawing_tool.import_drawing(drawing)
        drawing_tool.import_annotations_in_group(drawing_tool.get_drawing_group(drawing))
    blender.activate_camera(camera)
    drawing_tool.isolate_camera_collection(camera)
    drawing_tool.activate_drawing(camera)
