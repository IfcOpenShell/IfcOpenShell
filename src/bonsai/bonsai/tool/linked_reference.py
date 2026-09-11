# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Union

import bpy
import ifcopenshell
import ifcopenshell.api.document
from mathutils import Matrix

import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.linked_reference.prop import BIMLinkedReferenceProperties, LinkedReferenceLink

REFERENCES_COLLECTION_NAME = "LinkedReferences"
DOCUMENT_SCOPE = "LINKED_REFERENCE"
SUPPORTED_SUFFIXES = (".svg", ".dxf")

_timer_callback: Union[Callable[[], Union[float, None]], None] = None


class LinkedReferenceError(Exception):
    """User facing failure while loading or refreshing a linked reference."""


class LinkedReference:
    @classmethod
    def get_props(cls) -> BIMLinkedReferenceProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMLinkedReferenceProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_collection(cls, create: bool = False) -> Union[bpy.types.Collection, None]:
        assert (scene := bpy.context.scene)
        for child in scene.collection.children:
            if child.name == REFERENCES_COLLECTION_NAME:
                return child
        if not create:
            return None
        collection = bpy.data.collections.new(REFERENCES_COLLECTION_NAME)
        scene.collection.children.link(collection)
        return collection

    @classmethod
    def matrix_to_string(cls, matrix: Matrix) -> str:
        return ",".join(str(value) for row in matrix for value in row)

    @classmethod
    def string_to_matrix(cls, string: str) -> Matrix:
        values = [float(value) for value in string.split(",")]
        return Matrix((values[0:4], values[4:8], values[8:12], values[12:16]))

    @classmethod
    def resolve_path(cls, filepath: str) -> Path:
        return Path(tool.Ifc.resolve_uri(filepath))

    @classmethod
    def get_file_mtime(cls, filepath: Path) -> str:
        return str(filepath.stat().st_mtime_ns)

    @classmethod
    def get_anchor(cls, link: LinkedReferenceLink) -> Union[bpy.types.Object, None]:
        try:
            anchor = link.anchor
        except ReferenceError:
            return None
        if anchor is None or anchor.name not in bpy.data.objects:
            return None
        return anchor

    @classmethod
    def load_link(cls, link: LinkedReferenceLink) -> bpy.types.Object:
        filepath = cls.resolve_path(link.filepath)
        if not filepath.is_file():
            raise LinkedReferenceError(f"File not found: '{filepath}'.")
        collection = cls.get_collection(create=True)
        assert collection
        anchor = bpy.data.objects.new(f"LinkedReference/{Path(link.filepath).name}", None)
        anchor.empty_display_type = "ARROWS"
        collection.objects.link(anchor)
        if link.transformation:
            anchor.matrix_world = cls.string_to_matrix(link.transformation)
        try:
            objects = cls.import_file(filepath, collection)
        except LinkedReferenceError:
            bpy.data.objects.remove(anchor)
            raise
        for obj in objects:
            obj.parent = anchor
        link.anchor = anchor
        link.is_loaded = True
        link.file_mtime = cls.get_file_mtime(filepath)
        return anchor

    @classmethod
    def refresh_link(cls, link: LinkedReferenceLink) -> None:
        anchor = cls.get_anchor(link)
        if anchor is None:
            raise LinkedReferenceError("Linked reference is not loaded.")
        filepath = cls.resolve_path(link.filepath)
        if not filepath.is_file():
            raise LinkedReferenceError(f"File not found: '{filepath}'.")
        collection = cls.get_collection(create=True)
        assert collection
        old_children = list(anchor.children)
        # Import before removing so a failed import keeps the previous geometry.
        objects = cls.import_file(filepath, collection)
        for obj in objects:
            obj.parent = anchor
        cls.remove_objects(old_children)
        link.file_mtime = cls.get_file_mtime(filepath)

    @classmethod
    def unload_link(cls, link: LinkedReferenceLink) -> None:
        cls.store_placement(link)
        if anchor := cls.get_anchor(link):
            cls.remove_objects(list(anchor.children))
            bpy.data.objects.remove(anchor)
        link.anchor = None
        link.is_loaded = False

    @classmethod
    def remove_objects(cls, objects: Iterable[bpy.types.Object]) -> None:
        data = set()
        for obj in objects:
            if obj.data:
                data.add(obj.data)
            bpy.data.objects.remove(obj)
        for datablock in data:
            if datablock.users == 0:
                if isinstance(datablock, bpy.types.Mesh):
                    bpy.data.meshes.remove(datablock)
                elif isinstance(datablock, bpy.types.Curve):
                    bpy.data.curves.remove(datablock)

    @classmethod
    def store_placement(cls, link: LinkedReferenceLink) -> None:
        anchor = cls.get_anchor(link)
        if anchor is None:
            return
        link.transformation = cls.matrix_to_string(anchor.matrix_world)
        if link.ifc_definition_id and tool.Ifc.get():
            try:
                reference = tool.Ifc.get().by_id(link.ifc_definition_id)
            except RuntimeError:
                return
            reference[1] = link.transformation

    @classmethod
    def sync_placements_to_ifc(cls) -> None:
        try:
            props = cls.get_props()
        except (AssertionError, AttributeError):
            return
        for link in props.references:
            if link.is_loaded:
                cls.store_placement(link)

    @classmethod
    def get_linked_reference_documents(cls) -> dict[str, ifcopenshell.entity_instance]:
        documents = {}
        for document in tool.Ifc.get().by_type("IfcDocumentInformation"):
            if document.Scope == DOCUMENT_SCOPE:
                for reference in tool.Document.get_document_references(document):
                    documents[Path(reference.Location).as_posix()] = document
                    break
        return documents

    @classmethod
    def add_document_reference(cls, filepath: str) -> ifcopenshell.entity_instance:
        ifc_file = tool.Ifc.get()
        if not (document := cls.get_linked_reference_documents().get(filepath)):
            document = ifcopenshell.api.document.add_information(ifc_file)
            document.Name = Path(filepath).name
            document.Scope = DOCUMENT_SCOPE
        reference = ifcopenshell.api.document.add_reference(ifc_file, information=document)
        reference[1] = cls.matrix_to_string(Matrix.Identity(4))
        reference.Location = filepath.replace("\\", "/")
        return reference

    @classmethod
    def remove_document_reference(cls, link: LinkedReferenceLink) -> None:
        if not link.ifc_definition_id or not tool.Ifc.get():
            return
        try:
            reference = tool.Ifc.get().by_id(link.ifc_definition_id)
        except RuntimeError:
            return
        document = tool.Document.get_reference_document(reference)
        ifcopenshell.api.document.remove_reference(tool.Ifc.get(), reference)
        if document and not tool.Document.get_document_references(document):
            ifcopenshell.api.document.remove_information(tool.Ifc.get(), document)

    @classmethod
    def load_from_ifc(cls) -> None:
        references = cls.get_props().references
        references.clear()
        for document in tool.Ifc.get().by_type("IfcDocumentInformation"):
            if document.Scope != DOCUMENT_SCOPE:
                continue
            for reference in tool.Document.get_document_references(document):
                link = references.add()
                link.name = Path(reference.Location).name
                link.filepath = reference.Location
                link.ifc_definition_id = reference.id()
                link.transformation = reference[1] or ""

    @classmethod
    def import_file(cls, filepath: Path, collection: bpy.types.Collection) -> list[bpy.types.Object]:
        suffix = filepath.suffix.lower()
        if suffix == ".svg":
            return cls.import_svg(filepath, collection)
        elif suffix == ".dxf":
            return cls.import_dxf(filepath, collection)
        raise LinkedReferenceError(f"Unsupported file format '{suffix}', expected .svg or .dxf.")

    @classmethod
    def import_svg(cls, filepath: Path, collection: bpy.types.Collection) -> list[bpy.types.Object]:
        previous_objects = set(bpy.data.objects)
        previous_collections = set(bpy.data.collections)
        try:
            result = bpy.ops.import_curve.svg(filepath=str(filepath))
        except (AttributeError, RuntimeError):
            result = cls._retry_svg_with_addon(filepath)
        if "FINISHED" not in result:
            raise LinkedReferenceError(f"SVG import failed for '{filepath}'.")
        objects = [obj for obj in bpy.data.objects if obj not in previous_objects]
        if not objects:
            raise LinkedReferenceError(f"No importable geometry found in '{filepath.name}'.")
        for obj in objects:
            for users_collection in obj.users_collection:
                users_collection.objects.unlink(obj)
            collection.objects.link(obj)
        for orphan in [c for c in bpy.data.collections if c not in previous_collections and not c.objects]:
            bpy.data.collections.remove(orphan)
        return objects

    @classmethod
    def _retry_svg_with_addon(cls, filepath: Path) -> set[str]:
        import addon_utils

        try:
            addon_utils.enable("io_curve_svg", default_set=True)
            return bpy.ops.import_curve.svg(filepath=str(filepath))
        except Exception as e:
            raise LinkedReferenceError(
                "Blender's bundled SVG importer (io_curve_svg) is not available. "
                f"Enable the 'Import-Export: Scalable Vector Graphics' add-on and retry. Error: {e}"
            )

    @classmethod
    def import_dxf(cls, filepath: Path, collection: bpy.types.Collection) -> list[bpy.types.Object]:
        try:
            import ezdxf
            import ezdxf.entities
            import ezdxf.path
            import ezdxf.units
        except ImportError as e:
            raise LinkedReferenceError(f"The bundled ezdxf library is required for DXF references: {e}")

        try:
            doc = ezdxf.readfile(str(filepath))
        except Exception as e:
            raise LinkedReferenceError(f"Failed to read DXF file '{filepath}': {e}")

        insunits = doc.header.get("$INSUNITS", 0)
        try:
            scale = ezdxf.units.conversion_factor(insunits, ezdxf.units.M) if insunits else 1.0
        except ValueError:
            scale = 1.0

        verts: list[tuple[float, float, float]] = []
        edges: list[tuple[int, int]] = []
        # Curve flattening tolerance of 5mm, expressed in drawing units.
        distance = 0.005 / scale

        def walk(entities: Iterable[ezdxf.entities.DXFEntity], depth: int = 0) -> Iterator[ezdxf.entities.DXFEntity]:
            for entity in entities:
                if entity.dxftype() == "INSERT":
                    if depth < 8:
                        try:
                            yield from walk(entity.virtual_entities(), depth + 1)
                        except Exception:
                            pass
                else:
                    yield entity

        skipped = 0
        for entity in walk(doc.modelspace()):
            if entity.dxftype() == "POINT":
                point = entity.dxf.location
                verts.append((point.x * scale, point.y * scale, point.z * scale))
                continue
            try:
                points = list(ezdxf.path.make_path(entity).flattening(distance))
            except (TypeError, ValueError, AttributeError):
                skipped += 1
                continue
            if len(points) < 2:
                continue
            start = len(verts)
            verts.extend((point.x * scale, point.y * scale, point.z * scale) for point in points)
            edges.extend((start + i, start + i + 1) for i in range(len(points) - 1))

        if not verts:
            raise LinkedReferenceError(
                f"No importable geometry found in '{filepath.name}' ({skipped} unsupported entities skipped)."
            )

        mesh = bpy.data.meshes.new(filepath.name)
        mesh.from_pydata(verts, edges, [])
        obj = bpy.data.objects.new(filepath.name, mesh)
        collection.objects.link(obj)
        return [obj]

    @classmethod
    def cancel_timer(cls) -> None:
        global _timer_callback
        if _timer_callback is not None and bpy.app.timers.is_registered(_timer_callback):
            bpy.app.timers.unregister(_timer_callback)
        _timer_callback = None

    @classmethod
    def reset_timer(cls) -> None:
        cls.cancel_timer()
        try:
            props = cls.get_props()
        except (AssertionError, AttributeError):
            return
        if not props.auto_refresh:
            return

        def on_timer() -> Union[float, None]:
            try:
                cls.refresh_outdated_links()
            except Exception as error:
                print(f"Bonsai: linked reference auto refresh failed: {error}")
            # Reschedule by returning the next interval, see Autosave.reset_timer.
            try:
                props = cls.get_props()
                return float(props.auto_refresh_interval) if props.auto_refresh else None
            except (AssertionError, AttributeError):
                return None

        global _timer_callback
        _timer_callback = on_timer
        bpy.app.timers.register(on_timer, first_interval=float(props.auto_refresh_interval))

    @classmethod
    def refresh_outdated_links(cls) -> None:
        for link in cls.get_props().references:
            if not link.is_loaded or cls.get_anchor(link) is None:
                continue
            filepath = cls.resolve_path(link.filepath)
            if not filepath.is_file():
                continue
            if cls.get_file_mtime(filepath) != link.file_mtime:
                cls.refresh_link(link)
