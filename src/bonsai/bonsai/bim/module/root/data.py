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

from collections import defaultdict
import bpy
import ifcopenshell.util.element
import ifcopenshell.util.schema
from ifcopenshell.util.doc import get_entity_doc, get_predefined_type_doc, get_class_suggestions
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from typing import Union


def refresh():
    IfcClassData.is_loaded = False


class IfcClassData:
    element: Union[ifcopenshell.entity_instance, None] = None
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["ifc_products"] = cls.ifc_products()
        cls.data["ifc_classes"] = cls.ifc_classes()
        cls.data["ifc_classes_suggestions"] = cls.ifc_classes_suggestions()  # Call AFTER cls.ifc_classes()
        cls.data["representation_template"] = cls.representation_template()
        cls.data["contexts"] = cls.contexts()

        cls.data["has_entity"] = cls.has_entity()
        cls.data["name"] = cls.name()
        cls.data["has_inherited_predefined_type"] = cls.has_inherited_predefined_type()
        cls.data["ifc_class"] = cls.ifc_class()
        cls.data["ifc_predefined_types"] = cls.ifc_predefined_types()
        cls.data["can_reassign_class"] = cls.can_reassign_class()
        cls.data["profile"] = cls.profile()

    @classmethod
    def ifc_products(cls):
        products = [
            "IfcElementType",
            "IfcElement",
            "IfcSpatialElement",
            "IfcSpatialElementType",
            "IfcStructuralItem",
            "IfcAnnotation",
            "IfcRelSpaceBoundary",
        ]
        version = tool.Ifc.get_schema()
        if version == "IFC2X3":
            products = [
                "IfcElementType",
                "IfcElement",
                "IfcSpatialStructureElement",
                "IfcStructuralItem",
                "IfcAnnotation",
                "IfcRelSpaceBoundary",
            ]
        return [(e, e, (get_entity_doc(version, e) or {}).get("description", "")) for e in products]

    @classmethod
    def ifc_classes(cls):
        ifc_product = bpy.context.scene.BIMRootProperties.ifc_product
        declaration = tool.Ifc.schema().declaration_by_name(ifc_product)
        declarations = ifcopenshell.util.schema.get_subtypes(declaration)
        names = [d.name() for d in declarations]
        if ifc_product == "IfcElementType":
            names.append("IfcTypeProduct")
            if tool.Ifc.get_schema() in ("IFC2X3", "IFC4"):
                names.extend(("IfcDoorStyle", "IfcWindowStyle"))
        if ifc_product == "IfcElement":
            names.remove("IfcOpeningElement")
            if tool.Ifc.get_schema() == "IFC4":
                # Yeah, weird isn't it.
                names.remove("IfcOpeningStandardCase")
        version = tool.Ifc.get_schema()
        return [(c, c, (get_entity_doc(version, c) or {}).get("description", "")) for c in sorted(names)]

    @classmethod
    def ifc_predefined_types(cls):
        types_enum = []
        ifc_class = bpy.context.scene.BIMRootProperties.ifc_class
        declaration = tool.Ifc.schema().declaration_by_name(ifc_class)
        version = tool.Ifc.get_schema()
        for attribute in declaration.attributes():
            if attribute.name() == "PredefinedType":
                types_enum.extend(
                    [
                        (e, e, get_predefined_type_doc(version, ifc_class, e) or "")
                        for e in attribute.type_of_attribute().declared_type().enumeration_items()
                    ]
                )
                break
        return types_enum

    @classmethod
    def ifc_classes_suggestions(cls):
        # suggestions : dict[class_name: list[dict[predefined_type, name(optional)]]]
        suggestions = defaultdict(list)
        version = tool.Ifc.get_schema()
        for ifc_class, _, _ in cls.data["ifc_classes"]:
            class_doc = get_entity_doc(version, ifc_class) or {}
            predefined_types = class_doc.get("predefined_types", {})
            for predefined_type in predefined_types.keys():
                suggestions[ifc_class].append({"predefined_type": predefined_type})

            class_suggestions = get_class_suggestions(version, ifc_class)
            if not class_suggestions:
                continue
            for suggestion_dict in class_suggestions:
                suggestions[ifc_class].append(suggestion_dict)
        return suggestions

    @classmethod
    def representation_template(cls):
        ifc_class = bpy.context.scene.BIMRootProperties.ifc_class
        templates = [
            ("EMPTY", "No Geometry", "Start with an empty object"),
            None,
        ]
        templates.extend(
            [
                (
                    "OBJ",
                    "Tessellation From Object",
                    "Use an object as a template to create a new tessellation",
                ),
                (
                    "MESH",
                    "Custom Tessellation",
                    "Create a basic tessellated or faceted cube",
                ),
                (
                    "EXTRUSION",
                    "Custom Extruded Solid",
                    "An extrusion from an arbitrary profile",
                ),
            ]
        )
        if ifc_class.endswith("Type") or ifc_class.endswith("Style"):
            templates.extend(
                [
                    None,
                    (
                        "LAYERSET_AXIS2",
                        "Vertical Layers",
                        "For objects similar to walls, will automatically add IfcMaterialLayerSet",
                    ),
                    (
                        "LAYERSET_AXIS3",
                        "Horizontal Layers",
                        "For objects similar to slabs, will automatically add IfcMaterialLayerSet",
                    ),
                    (
                        "PROFILESET",
                        "Extruded Profile",
                        "Create profile type object, automatically defines IfcMaterialProfileSet with the first profile from library",
                    ),
                ]
            )
        if ifc_class in ("IfcWindowType", "IfcWindowStyle", "IfcWindow"):
            templates.extend([None, ("WINDOW", "Window", "Parametric window")])
        elif ifc_class in ("IfcDoorType", "IfcDoorStyle", "IfcDoor"):
            templates.extend([None, ("DOOR", "Door", "Parametric door")])
        elif ifc_class in ("IfcStairType", "IfcStairFlightType", "IfcStair", "IfcStairFlight"):
            templates.extend([None, ("STAIR", "Stair", "Parametric stair")])
        elif ifc_class in ("IfcRailingType", "IfcRailing"):
            templates.extend([None, ("RAILING", "Railing", "Parametric railing")])
        elif ifc_class in ("IfcRoofType", "IfcRoof"):
            templates.extend([None, ("ROOF", "Roof", "Parametric roof with a constant pitch")])
        elif ifc_class and "Segment" in ifc_class:
            templates.extend(
                (
                    None,
                    (
                        "FLOW_SEGMENT_RECTANGULAR",
                        "Rectangular Distribution Segment",
                        "Works similarly to Profile, has distribution ports",
                    ),
                    (
                        "FLOW_SEGMENT_CIRCULAR",
                        "Circular Distribution Segment",
                        "Works similarly to Profile, has distribution ports",
                    ),
                    (
                        "FLOW_SEGMENT_CIRCULAR_HOLLOW",
                        "Circular Hollow Distribution Segment",
                        "Works similarly to Profile, has distribution ports",
                    ),
                )
            )

        return templates

    @classmethod
    def contexts(cls):
        results = []
        for element in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            results.append((str(element.id()), element.ContextType or "Unnamed", ""))
        for element in tool.Ifc.get().by_type("IfcGeometricRepresentationSubContext", include_subtypes=False):
            results.append(
                (
                    str(element.id()),
                    "{}/{}/{}".format(
                        element.ContextType or "Unnamed",
                        element.ContextIdentifier or "Unnamed",
                        element.TargetView or "Unnamed",
                    ),
                    "",
                )
            )
        return results

    @classmethod
    def has_entity(cls) -> Union[ifcopenshell.entity_instance, None]:
        obj = tool.Blender.get_active_object()
        cls.element = None
        if not obj:
            return

        element = tool.Ifc.get_entity(obj)
        if not element:
            return

        # Double check
        linked_obj = tool.Ifc.get_object(element)
        if linked_obj != obj:
            return

        cls.element = element
        return cls.element

    @classmethod
    def name(cls) -> Union[str, None]:
        element = cls.element
        if not element:
            return
        name = element.is_a()
        predefined_type = ifcopenshell.util.element.get_predefined_type(element)
        if predefined_type:
            name += f"[{predefined_type}]"
        return name

    @classmethod
    def has_inherited_predefined_type(cls) -> bool:
        element = cls.element
        if not element:
            return False
        if element_type := ifcopenshell.util.element.get_type(element):
            # Allow for None due to https://github.com/buildingSMART/IFC4.3.x-development/issues/818
            return ifcopenshell.util.element.get_predefined_type(element_type) not in ("NOTDEFINED", None)
        return False

    @classmethod
    def ifc_class(cls) -> Union[str, None]:
        element = cls.element
        if element:
            return element.is_a()

    @classmethod
    def can_reassign_class(cls) -> bool:
        element = cls.element
        if element:
            if element.is_a("IfcOpeningElement") or element.is_a("IfcOpeningStandardCase"):
                return False
            if element.is_a() in (
                "IfcWindowStyle",
                "IfcDoorStyle",
            ):  # see https://github.com/IfcOpenShell/IfcOpenShell/issues/4622#issuecomment-2095676368
                return True
            for product in cls.ifc_products():
                if element.is_a(product[0]):
                    return True
        return False

    @classmethod
    def profile(cls) -> list[tuple[str, str, str]]:
        items = [("-", "-", "")]
        ifc_file = tool.Ifc.get()
        for profile in ifc_file.by_type("IfcProfileDef"):
            if not (profile_name := profile.ProfileName):
                continue
            items.append((str(profile.id()), profile_name, profile.is_a()))
        return items
