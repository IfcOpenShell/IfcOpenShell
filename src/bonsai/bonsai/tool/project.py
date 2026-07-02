# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import json
import os
import shutil
from collections import defaultdict
from math import radians
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    NamedTuple,
    NotRequired,
    Optional,
    TypedDict,
    Union,
)

import bpy
import ifcopenshell
import ifcopenshell.api.document
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
import numpy as np
import numpy.typing as npt
from ifcopenshell.api.project.append_asset import APPENDABLE_ASSET_TYPES
from mathutils import Matrix, Vector

import bonsai.bim.schema
import bonsai.core.aggregate
import bonsai.core.context
import bonsai.core.owner
import bonsai.core.root
import bonsai.core.tool
import bonsai.core.unit
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore

if TYPE_CHECKING:
    from bonsai.bim.module.project.prop import (
        BIMProjectProperties,
        Link,
        MeasureToolSettings,
    )

HiearchyDict = dict[ifcopenshell.entity_instance, "HiearchyDict"]


class Project(bonsai.core.tool.Project):
    @classmethod
    def get_project_props(cls) -> BIMProjectProperties:
        return bpy.context.scene.BIMProjectProperties

    @classmethod
    def get_measure_tool_settings(cls) -> MeasureToolSettings:
        assert (scene := bpy.context.scene)
        return scene.MeasureToolSettings  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_link_empty_handle(cls, link: Link) -> bpy.types.Object | None:
        if tool.Ifc.get():
            return tool.Ifc.get_object(tool.Ifc.get().by_id(link.ifc_definition_id))
        return link.empty_handle

    @classmethod
    def set_link_empty_handle(cls, link: Link, empty: bpy.types.Object) -> None:
        if tool.Ifc.get():
            tool.Ifc.link(tool.Ifc.get().by_id(link.ifc_definition_id), empty)
        else:
            link.empty_handle = empty

    @classmethod
    def calculate_link_matrix(cls, link: Link) -> Matrix:
        filepath = Path(tool.Ifc.resolve_uri(link.filepath))
        with open(filepath.with_suffix(".ifc.cache.json"), "r") as f:
            metadata = json.load(f)

        rot = ifcopenshell.util.shape_builder.np_rotation_matrix(
            radians(-float(metadata["model_project_north"])), 4, "Z"
        )
        global_matrix = rot @ np.eye(4)
        global_matrix[:, 3][:3] = [float(o) for o in metadata["model_origin_si"].split(",")]

        if tool.Ifc.get():
            transformation = tool.Ifc.get().by_id(link.ifc_definition_id)[1]  # Identification
        else:
            transformation = link.transformation

        if transformation:
            transformation = np.fromstring(transformation, sep=",", dtype=np.float64).reshape(4, 4)
            if not np.allclose(transformation, np.eye(4)):
                global_matrix = transformation @ global_matrix

        gprops = tool.Georeference.get_georeference_props()
        rot = ifcopenshell.util.shape_builder.np_rotation_matrix(radians(-float(gprops.model_project_north)), 4, "Z")
        local_matrix = rot @ np.eye(4)
        local_matrix[:, 3][:3] = [float(o) for o in gprops.model_origin_si.split(",")]
        return Matrix(np.linalg.inv(local_matrix) @ global_matrix)

    @classmethod
    def append_all_types_from_template(cls, template: str) -> None:
        # TODO refactor
        filepath = tool.Blender.get_data_dir_path(Path("templates") / "projects" / template)
        bpy.ops.bim.select_library_file(filepath=filepath.__str__())
        if IfcStore.library_file.schema != tool.Ifc.get().schema:
            return
        for element in IfcStore.library_file.by_type("IfcTypeProduct"):
            bpy.ops.bim.append_library_element(definition=element.id())

    @classmethod
    def create_empty(cls, name: str) -> bpy.types.Object:
        return bpy.data.objects.new(name, None)

    @classmethod
    def load_default_thumbnails(cls) -> None:
        if tool.Ifc.get().by_type("IfcElementType"):
            bpy.ops.bim.load_type_thumbnails()

    @classmethod
    def load_project_pset_templates(cls) -> None:
        props = tool.Blender.get_addon_preferences()
        pset_dir = tool.Ifc.resolve_uri(props.pset_dir)
        if os.path.isdir(pset_dir):
            for path in Path(pset_dir).glob("*.ifc"):
                bonsai.bim.schema.ifc.psetqto.templates.append(ifcopenshell.open(path))

    @classmethod
    def run_aggregate_assign_object(
        cls, relating_obj: Optional[bpy.types.Object] = None, related_obj: Optional[bpy.types.Object] = None
    ):
        return bonsai.core.aggregate.assign_object(
            tool.Ifc, tool.Aggregate, tool.Collector, relating_obj=relating_obj, related_obj=related_obj
        )

    @classmethod
    def run_context_add_context(
        cls,
        context_type: Optional[str] = None,
        context_identifier: Optional[str] = None,
        target_view: Optional[str] = None,
        parent: Optional[str] = None,
    ):
        return bonsai.core.context.add_context(
            tool.Ifc,
            context_type=context_type,
            context_identifier=context_identifier,
            target_view=target_view,
            parent=parent,
        )

    @classmethod
    def run_owner_add_organisation(cls):
        return bonsai.core.owner.add_organisation(tool.Ifc)

    @classmethod
    def run_owner_add_person(cls):
        return bonsai.core.owner.add_person(tool.Ifc)

    @classmethod
    def run_owner_add_person_and_organisation(
        cls, person: ifcopenshell.entity_instance, organisation: ifcopenshell.entity_instance
    ):
        return bonsai.core.owner.add_person_and_organisation(tool.Ifc, person=person, organisation=organisation)

    @classmethod
    def run_owner_set_user(cls, user: ifcopenshell.entity_instance):
        return bonsai.core.owner.set_user(tool.Owner, user=user)

    @classmethod
    def run_root_assign_class(
        cls,
        obj: bpy.types.Object,
        ifc_class: str,
        predefined_type: Optional[str] = None,
        should_add_representation: bool = True,
        context: Optional[ifcopenshell.entity_instance] = None,
        ifc_representation_class: Optional[str] = None,
    ):
        return bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            predefined_type=predefined_type,
            should_add_representation=should_add_representation,
            context=context,
            ifc_representation_class=ifc_representation_class,
        )

    @classmethod
    def run_unit_assign_scene_units(cls):
        return bonsai.core.unit.assign_scene_units(tool.Ifc, tool.Unit)

    @classmethod
    def set_context(cls, context: ifcopenshell.entity_instance) -> None:
        bonsai.bim.handler.refresh_ui_data()
        rprops = tool.Root.get_root_props()
        rprops.contexts = str(context.id())

    @classmethod
    def set_default_context(cls) -> None:
        context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        if context:
            rprops = tool.Root.get_root_props()
            rprops.contexts = str(context.id())

    @classmethod
    def set_default_modeling_dimensions(cls) -> None:
        props = tool.Model.get_model_props()
        props.extrusion_depth = 3
        props.length = 1
        props.rl1 = 0
        props.rl2 = 1
        props.x = 0.5
        props.y = 0.5
        props.z = 0.5

    @classmethod
    def get_recent_ifc_projects_path(cls) -> Path:
        return Path(bpy.utils.user_resource("CONFIG")) / "recent-ifc-projects.txt"

    _recent_ifc_projects_loaded: bool = False
    _recent_ifc_projects: list[Path] = []

    @classmethod
    def get_recent_ifc_projects(cls) -> list[Path]:
        if cls._recent_ifc_projects_loaded:
            return cls._recent_ifc_projects

        filepath = cls.get_recent_ifc_projects_path()
        if not filepath.exists():
            cls._recent_ifc_projects = []
            return []

        paths = []
        with open(filepath, "r") as fi:
            for line in fi:
                line = line.strip()
                if not line:
                    continue
                paths.append(Path(line))

        cls._recent_ifc_projects = paths
        return paths

    @classmethod
    def write_recent_ifc_projects(cls, filepaths: list[Path]) -> None:
        recent_projects_path = cls.get_recent_ifc_projects_path()
        try:
            recent_projects_path.parent.mkdir(parents=True, exist_ok=True)
            with open(recent_projects_path, "w") as fo:
                fo.write("\n".join(str(p) for p in filepaths))
            cls._recent_ifc_projects_loaded = False
        except PermissionError:
            msg = (
                f"WARNING. PermissionError trying to access '{str(recent_projects_path)}'. "
                "List of recently opened IFC projects won't be stored between Blender sessions."
            )
            print(msg)
            cls._recent_ifc_projects = filepaths

    @classmethod
    def add_recent_ifc_project(cls, filepath: Path) -> None:
        """Add `filepath` to the list of the recently opened IFC projects.

        If `filepath` was opened before, bump it in the list.
        """
        filepath = filepath.absolute()
        current_filepaths = cls.get_recent_ifc_projects()
        if filepath in current_filepaths:
            current_filepaths.remove(filepath)
        current_filepaths = [filepath] + current_filepaths
        # Limit it to 20 recent files.
        current_filepaths = current_filepaths[:20]
        cls.write_recent_ifc_projects(current_filepaths)

    @classmethod
    def clear_recent_ifc_projects(cls) -> None:
        cls.write_recent_ifc_projects([])

    @classmethod
    def get_appendable_asset_types(cls) -> tuple[str, ...]:
        return tuple(e for e in APPENDABLE_ASSET_TYPES if e != "IfcProduct")

    @classmethod
    def run_root_reload_grid_decorator(cls) -> None:
        tool.Root.reload_grid_decorator()

    @classmethod
    def get_linked_models_documents(cls) -> dict[str, ifcopenshell.entity_instance]:
        linked_docs = {}
        for doc in tool.Ifc.get().by_type("IfcDocumentInformation"):
            if doc.Scope == "LINKED_MODEL":
                for reference in tool.Drawing.get_document_references(doc):
                    linked_docs[Path(reference.Location).as_posix()] = doc
                    break
        return linked_docs

    @classmethod
    def load_linked_models_from_ifc(cls) -> None:
        links = tool.Project.get_project_props().links
        links.clear()
        for doc in tool.Ifc.get().by_type("IfcDocumentInformation"):
            if doc.Scope != "LINKED_MODEL":
                continue
            for reference in tool.Drawing.get_document_references(doc):
                filepath = reference.Location
                link = links.add()
                link.name = filepath
                link.filepath = filepath
                link.ifc_definition_id = reference.id()
                link.has_transformation = False
                if reference[1]:
                    m = np.fromstring(reference[1], sep=",", dtype=np.float64).reshape(4, 4)
                    link.has_transformation = not np.allclose(m, np.eye(4))
                # The selector query used at link time is persisted only in the
                # sidecar cache JSON; restore it so Reload/Load replay the filter.
                json_filepath = Path(tool.Ifc.resolve_uri(filepath)).with_suffix(".ifc.cache.json")
                if json_filepath.exists():
                    try:
                        link.query = json.loads(json_filepath.read_text()).get("query", "")
                    except (OSError, json.JSONDecodeError):
                        pass

    @classmethod
    def get_project_library_elements(
        cls, project_library: ifcopenshell.entity_instance
    ) -> set[ifcopenshell.entity_instance]:
        return set(element for rel in project_library.Declares for element in rel.RelatedDefinitions)

    @classmethod
    def get_project_library_rels(cls, ifc_file: ifcopenshell.file) -> set[ifcopenshell.entity_instance]:
        if tool.Ifc.get_schema() == "IFC2X3":
            return set()
        return set(rel for lib in ifc_file.by_type("IfcProjectLibrary") for rel in lib.Declares)

    @classmethod
    def is_element_assigned_to_project_library(
        cls,
        element: ifcopenshell.entity_instance,
        project_library_rels: set[ifcopenshell.entity_instance],
    ) -> bool:
        if not (has_context := getattr(element, "HasContext", ())):
            return False
        return any(rel in project_library_rels for rel in has_context)

    @classmethod
    def update_current_library_page(cls) -> None:
        props = cls.get_project_props()
        active_library_breadcrumb = props.get_active_library_breadcrumb()
        change_back = False
        if active_library_breadcrumb:
            name = active_library_breadcrumb.name
            breadcrumb_type = active_library_breadcrumb.breadcrumb_type
            library_id = active_library_breadcrumb.library_id
            change_back = True

        bpy.ops.bim.rewind_library()
        if change_back:
            bpy.ops.bim.change_library_element(
                element_name=name,
                breadcrumb_type=breadcrumb_type,
                library_id=library_id,
            )

    @classmethod
    def get_parent_library(
        cls, project_library: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        """Return the IfcContext that declares or nests ``project_library``.

        Returns ``None`` when ``project_library`` is itself the root of a
        library-only file (no IfcRelNests, no IfcRelDeclares).
        """
        if nests := project_library.Nests:
            return nests[0].RelatingObject
        if has_context := project_library.HasContext:
            return has_context[0].RelatingContext
        return None

    @classmethod
    def get_root_context(cls, ifc_file: ifcopenshell.file) -> ifcopenshell.entity_instance:
        """Return the file's root IfcContext.

        Prefers IfcProject if present, otherwise falls back to IfcProjectLibrary —
        library-only files are valid per IFC4+ and contain no IfcProject. Caller is
        responsible for the IFC2X3 guard; IfcContext does not exist in that schema.
        """
        if projects := ifc_file.by_type("IfcProject"):
            return projects[0]
        return ifc_file.by_type("IfcProjectLibrary")[0]

    @classmethod
    def get_project_hierarchy(cls, ifc_file: ifcopenshell.file) -> HiearchyDict:
        """Get project hierarchy in the following form:

        {
            IfcProject: { IfcProjectLibrary A: { ... }, },
            IfcProjectLibrary A: { IfcProjectLibrary B: { ... } },
            IfcProjectLibrary B: { ... },
        }

        Use IfcProject to get hierarchy root.

        """
        hierarchy: HiearchyDict = defaultdict(dict)
        if tool.Ifc.get_schema() == "IFC2X3":
            return hierarchy
        for project_library in ifc_file.by_type("IfcProjectLibrary"):
            parent_library = cls.get_parent_library(project_library)
            if parent_library is None:
                continue
            hierarchy[parent_library][project_library] = hierarchy[project_library]
        return hierarchy

    @classmethod
    def load_project_libraries_to_ui(
        cls, parent_library: ifcopenshell.entity_instance, hierarchy: HiearchyDict
    ) -> None:
        libraries = hierarchy[parent_library]
        props = cls.get_project_props()
        for project_library in libraries:
            library_elements = tool.Project.get_project_library_elements(project_library)
            subhierarchy = libraries[project_library]
            for sublibrary in subhierarchy:
                sublibrary_elements = tool.Project.get_project_library_elements(sublibrary)
                library_elements.update(sublibrary_elements)
            props.add_library_project_library(
                project_library.Name or "Unnamed", len(library_elements), project_library.id(), bool(subhierarchy)
            )

    @classmethod
    def get_library_element_attr_name(cls, library_element: ifcopenshell.entity_instance) -> str:
        if library_element.is_a("IfcProfileDef"):
            return "ProfileName"
        return "Name"

    # TODO: Move to ifcopenshell.api and add tests.
    @classmethod
    def remove_project_library(cls, project_library: ifcopenshell.entity_instance) -> None:
        ifc_file = project_library.file
        roots_to_remove = {project_library}
        rels_to_clean_up: set[ifcopenshell.entity_instance] = set()
        queue = [project_library]
        while queue:
            current = queue.pop()
            inverses = ifc_file.get_inverse(current)
            rels_to_clean_up.update(i for i in inverses if i.is_a() in ("IfcRelNests", "IfcRelDeclares"))

            children = ifcopenshell.util.element.get_components(current)
            queue.extend(children)
            roots_to_remove.update(children)

        def remove_root(root: ifcopenshell.entity_instance) -> None:
            history = root.OwnerHistory
            ifc_file.remove(root)
            if history:
                ifcopenshell.util.element.remove_deep2(ifc_file, history)

        for root in roots_to_remove:
            remove_root(root)

        # Clean up invalidated rels.
        for rel in rels_to_clean_up:
            if rel.is_a("IfcRelDeclares"):
                # Project library was either assigned to Project or some types were assigned to it.
                if not rel.RelatingContext or not rel.RelatedDefinitions:
                    remove_root(rel)
            elif rel.is_a("IfcRelNests"):
                # Project library was either parent or child to other project libraries.
                if not rel.RelatingObject or not rel.RelatedObjects:
                    remove_root(rel)
            else:
                assert False, f"Shouldn't be here, {rel}"

    class HeaderData(NamedTuple):
        mvd: str
        author_name: str
        author_email: str
        organisation_name: str
        organisation_email: str
        authorisation: str

    @classmethod
    def get_header_data(cls) -> HeaderData:
        assert (ifc_file := tool.Ifc.get())

        # MVD.
        if isinstance(ifc_file, ifcopenshell.sqlite):
            mvd = ifc_file.mvd_str
        else:
            mvd = "".join(ifc_file.header.file_description.description)
        if f"[" in mvd:
            mvd = mvd.split("[")[1][0:-1]

        # Author.
        author = ifc_file.header.file_name.author
        author_name, author_email = "", ""
        if author:
            author_name = author[0]
            if len(author) > 1:
                author_email = author[1]

        # Organization.
        organization_name, organization_email = "", ""
        organization = ifc_file.header.file_name.organization
        if organization:
            organization_name = organization[0]
            if len(organization) > 1:
                organization_email = organization[1]

        authorization = ifc_file.header.file_name.authorization or ""
        return cls.HeaderData(
            mvd=mvd,
            author_name=author_name,
            author_email=author_email,
            organisation_name=organization_name,
            organisation_email=organization_email,
            authorisation=authorization,
        )

    @classmethod
    def get_clipping_planes_normals(cls) -> list[tuple[Vector, Vector]]:
        normals: list[tuple[Vector, Vector]] = []
        for clipping_plane in tool.Project.get_project_props().clipping_planes:
            plane = clipping_plane.obj
            if not plane or not plane.data:
                continue

            if plane.mode == "EDIT":
                continue  # A profile decorator or something else is used here.

            assert isinstance(plane.data, bpy.types.Mesh)
            v1 = plane.matrix_world @ plane.data.vertices[0].co
            v2 = plane.matrix_world @ plane.data.vertices[1].co
            v3 = plane.matrix_world @ plane.data.vertices[2].co
            d1 = v1 - v2
            d2 = v3 - v2
            normals.append((v1, d1.cross(d2).normalized()))
        return normals

    TEMP_PROJECT_PATH = Path.cwd() / "test/files/temp/test_project.ifc"

    @classmethod
    def save_test_project(cls) -> None:
        tmp = cls.TEMP_PROJECT_PATH.parent
        # Clean up previous test project to avoid conflicts with non-updated assets.
        if tmp.exists():
            shutil.rmtree(tmp)
        bpy.ops.bim.save_project(filepath=cls.TEMP_PROJECT_PATH.__str__(), should_save_as=True)

    @classmethod
    def get_metadata_document_information(cls) -> Optional[ifcopenshell.entity_instance]:
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            return None
        for doc in ifc_file.by_type("IfcDocumentInformation"):
            if getattr(doc, "Scope", None) == "BLEND_METADATA":
                return doc
        return None

    @classmethod
    def create_metadata_document_information(cls, metadata_filename: str) -> ifcopenshell.entity_instance:
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            raise Exception("No IFC file loaded")

        doc = ifcopenshell.api.document.add_information(ifc_file, parent=None)

        if ifc_file.schema == "IFC2X3":
            ifcopenshell.api.document.edit_information(
                ifc_file,
                information=doc,
                attributes={
                    "DocumentId": "BLEND_METADATA",
                    "Name": "Blend Metadata",
                    "Scope": "BLEND_METADATA",
                    "Description": "References to blend metadata file for this IFC project",
                    "Location": metadata_filename,
                },
            )
        else:
            ifcopenshell.api.document.edit_information(
                ifc_file,
                information=doc,
                attributes={
                    "Identification": "BLEND_METADATA",
                    "Name": "Blend Metadata",
                    "Scope": "BLEND_METADATA",
                    "Description": "References to blend metadata file for this IFC project",
                    "Location": metadata_filename,
                },
            )

        return doc

    @classmethod
    def update_metadata_document_information(cls, metadata_filename: str) -> None:
        doc = cls.get_metadata_document_information()
        if not doc:
            return

        ifc_file = tool.Ifc.get()
        ifcopenshell.api.document.edit_information(
            ifc_file, information=doc, attributes={"Location": metadata_filename}
        )

    @classmethod
    def remove_metadata_document_information(cls) -> None:
        doc = cls.get_metadata_document_information()
        if not doc:
            return

        ifc_file = tool.Ifc.get()
        ifcopenshell.api.document.remove_information(ifc_file, information=doc)

    class Link:
        """Tools for working with linked models."""

        class LinkedObjectChunk(TypedDict):
            """There's actually no dictionary with those keys,
            just using this class to document what keys we do assign to the objects
            that represent chunks of the linked models.
            """

            guids: list[str]
            """List of guids present in the object."""

            guid_ids: list[int]
            """Number of faces that belong to each guid.

            E.g. if chunk consists of two 12 tris cubes:
            ```
                guids = ["aaa", "bbb"]
                # Meaning object has 24 polygons
                # [0;11] is part of "aaa", [12:23] is part of "bbb".
                guid_ids = [12, 24]
            ```
            """

            db: str
            """Absolute filepath to .ifc.cache.sqlite."""

            ifc_filepath: str
            """Absolute filepath to .ifc."""

            # Only added when object is queried.
            selected_vertices: NotRequired[list[tuple[int, int, int]]]
            selected_edges: NotRequired[list[tuple[int, int]]]
            selected_tris: NotRequired[list[tuple[int, int, int]]]

            hidden_indices: NotRequired[list[int]]
            """List of hidden indices in "guids".
            Note that entire object also can be hidden by ``hide_viewport`` and then "hidden_indices" won't be set.

            ```
                guids = ["aaa", "bbb", "ccc"]
                # guid "bbb" is hidden.
                hidden_indices = [1]
            ```
            """

        @classmethod
        def is_linked_element(cls, obj: bpy.types.Object) -> bool:
            return "guids" in obj

        @classmethod
        def get_obj_by_guid(cls, link: Link, guid: str) -> bpy.types.Object | None:
            assert link.is_loaded

            handle = tool.Project.get_link_empty_handle(link)
            assert handle
            col = handle.instance_collection
            assert col

            guid_obj = None
            for obj in col.objects:
                obj_guids: list[str] = obj["guids"]
                if guid in obj_guids:
                    guid_obj = obj
                    break

            return guid_obj

        @classmethod
        def get_linked_element_guid_ids(cls, obj: bpy.types.Object, *, skip_hidden: bool) -> npt.NDArray[np.int64]:
            obj_guid_ids: npt.NDArray[np.int64] = np.array(obj["guid_ids"])

            if not skip_hidden:
                return obj_guid_ids

            # 'hidden_indices' is needed, because otherwise we can't make sense of 'guid_ids',
            # since part of the geometry is hidden.
            obj_hidden_indices: list[int] = list(obj.get("hidden_indices") or [])

            if not obj_hidden_indices:
                return obj_guid_ids

            # Skip hidden geometry indices.
            hidden_indices_mask = np.zeros(len(obj_guid_ids), dtype=bool)
            hidden_indices_mask[obj_hidden_indices] = True
            deltas = np.diff(obj_guid_ids, prepend=0)
            deltas[~hidden_indices_mask] = 0
            obj_guid_ids -= np.cumsum(deltas)
            return obj_guid_ids

        @classmethod
        def get_guid_by_face_index(cls, obj: bpy.types.Object, face_index: int) -> str | None:
            guids: list[str] = obj["guids"]
            guid_ids = cls.get_linked_element_guid_ids(obj, skip_hidden=True)
            for guid, guid_end_index in zip(guids, guid_ids):
                if face_index < guid_end_index:
                    return guid

        @classmethod
        def get_linked_element_geom_slice(cls, obj: bpy.types.Object, guid: str) -> slice[int, int]:
            """
            Get slice for ``obj.data.polygons`` for the provided ``guid``.
            """
            obj_guids: list[str] = obj["guids"]

            # Just to be safe.
            obj_hidden_indices: list[int] = obj.get("hidden_indices") or []
            index = obj_guids.index(guid)
            if index in obj_hidden_indices:
                assert False, "Unexpected. Why would you need the geometry for the hidden element?"
            obj_guid_ids = cls.get_linked_element_guid_ids(obj, skip_hidden=False)
            guid_end_index = obj_guid_ids[index]
            guid_start_index = index and obj_guid_ids[index - 1]
            return slice(guid_start_index, guid_end_index)

        @classmethod
        def setup_hide_modifier(
            cls,
            obj: bpy.types.Object,
            hide_type: Literal["hide_selected", "hide_unselected"],
        ) -> bpy.types.VertexGroup:
            # `MeshPolygon.hide` works only in EDIT mode,
            # so we use vertex groups + Mask modifier.
            # But since for hiding we're modifying object in a linked model,
            # then those changes are ephemeral and not fully supported by Blender
            # e.g. they're not tracked by UNDO system.

            MODIFIER_VG_NAME = "BBIM_HIDE_LINKED_GEOMETRY"

            vertex_groups = obj.vertex_groups
            vertex_group = vertex_groups.get(MODIFIER_VG_NAME)
            if vertex_group is None:
                vertex_group = vertex_groups.new(name=MODIFIER_VG_NAME)

            modifiers = obj.modifiers
            modifier = modifiers.get(MODIFIER_VG_NAME)
            if modifier is None:
                modifier = modifiers.new(MODIFIER_VG_NAME, "MASK")
            assert isinstance(modifier, bpy.types.MaskModifier)
            modifier.vertex_group = MODIFIER_VG_NAME
            # Mask modifier by default shows only geometry from the provided vertex group.
            modifier.invert_vertex_group = hide_type == "hide_selected"
            return vertex_group

        @classmethod
        def hide_linked_element(cls, obj: bpy.types.Object, guid: str) -> None:
            verts = tool.Project.Link.get_linked_element_verts(obj, guid)

            vertex_group = cls.setup_hide_modifier(obj, "hide_selected")
            vertex_group.add(verts, 1.0, "REPLACE")

            hidden_indices: list[int] = list(obj.get("hidden_indices") or [])
            guid_ids: list[str] = obj["guids"]
            index = guid_ids.index(guid)
            hidden_indices.append(index)
            obj["hidden_indices"] = hidden_indices

        @classmethod
        def unhide_all_elements(cls, link: Link) -> None:
            obj = tool.Project.get_link_empty_handle(link)
            assert obj
            col = obj.instance_collection
            assert col

            for obj_ in col.objects:
                obj_.hide_viewport = False

                if "hidden_indices" not in obj_:
                    continue
                obj_.vertex_groups.clear()
                obj_.modifiers.clear()
                del obj_["hidden_indices"]

        @classmethod
        def hide_all_elements_except(cls, link: Link, queried_obj: bpy.types.Object, queried_guid: str) -> None:
            handle = tool.Project.get_link_empty_handle(link)
            assert handle
            col = handle.instance_collection
            assert col

            for obj_ in col.objects:
                if "guids" not in obj_:
                    continue
                if obj_ != queried_obj:
                    # Just hide the entire chunk, if queried guid is not part of it.
                    obj_.hide_viewport = True
                    continue

                guids: list[str] = obj_["guids"]
                queried_guid_index = guids.index(queried_guid)

                # Get vertices for the queried element before modifying hidden_indices.
                queried_verts = cls.get_linked_element_verts(obj_, queried_guid)
                vertex_group = cls.setup_hide_modifier(obj_, "hide_unselected")

                assert isinstance(mesh := obj_.data, bpy.types.Mesh)
                # Clean up possible previously hidden elements.
                vertex_group.remove(range(len(mesh.vertices)))

                vertex_group.add(queried_verts, 1.0, "REPLACE")

                # Mark all guids as hidden except the queried one.
                obj_["hidden_indices"] = [i for i in range(len(guids)) if i != queried_guid_index]

        @classmethod
        def select_linked_element_geom(cls, obj: bpy.types.Object, guid: str) -> None:
            slice_ = cls.get_linked_element_geom_slice(obj, guid)

            mesh = obj.data
            assert isinstance(mesh, bpy.types.Mesh)
            guid_polygons = mesh.polygons[slice_]

            selected_tris: list[tuple[int, ...]] = []
            selected_edges: list[tuple[int, ...]] = []

            # Restart verts indices for our polygons.
            guid_vertices_set: set[int] = set()
            for polygon in guid_polygons:
                guid_vertices_set.update(polygon.vertices)
            vert_map = {k: v for v, k in enumerate(guid_vertices_set)}

            selected_vertices = [obj.matrix_world @ mesh.vertices[vi].co for vi in vert_map]
            for polygon in guid_polygons:
                selected_tris.append(tuple(vert_map[vi] for vi in polygon.vertices))
                selected_edges.extend(tuple([vert_map[vi] for vi in e]) for e in polygon.edge_keys)

            obj["selected_vertices"] = selected_vertices
            obj["selected_edges"] = selected_edges
            obj["selected_tris"] = selected_tris

        @classmethod
        def get_linked_element_verts(cls, obj: bpy.types.Object, guid: str) -> set[int]:
            slice_ = cls.get_linked_element_geom_slice(obj, guid)

            mesh = obj.data
            assert isinstance(mesh, bpy.types.Mesh)
            guid_polygons = mesh.polygons[slice_]

            guid_vertices_set: set[int] = set()
            for polygon in guid_polygons:
                guid_vertices_set.update(polygon.vertices)
            return guid_vertices_set

        @classmethod
        def select_linked_element(
            cls,
            context: bpy.types.Context,
            obj: bpy.types.Object,
            guid: str,
            instance_matrix: Matrix | None = None,
        ) -> None:
            import sqlite3

            from ifcpatch.recipes.ExtractPropertiesToSQLite import (
                ElementRow,
                PropertyRow,
                RelationshipRow,
            )

            from bonsai.bim.module.project.data import LinksData
            from bonsai.bim.module.project.decorator import ProjectDecorator

            # Not sure if there's a difference between `instance_matrix` coming from `ray_cast`
            # and usual `matrix_world`, maybe we can just get it from object always.
            if instance_matrix is None:
                instance_matrix = obj.matrix_world

            cls.deselect_queried_linked_element()
            cls.set_queried_linked_element(obj, guid, instance_matrix)
            cls.select_linked_element_geom(obj, guid)
            db = sqlite3.connect(obj["db"])
            c = db.cursor()

            c.execute(f"SELECT * FROM elements WHERE global_id = '{guid}' LIMIT 1")
            element = ElementRow(*c.fetchone())

            attributes: dict[str, Any] = {}
            for i, attr in enumerate(["GlobalId", "IFC Class", "Predefined Type", "Name", "Description"]):
                if element[i + 1] is not None:
                    attributes[attr] = element[i + 1]

            c.execute("SELECT * FROM properties WHERE element_id = ?", (element[0],))
            rows = [PropertyRow(*row) for row in c.fetchall()]

            properties: defaultdict[str, dict[str, str]] = defaultdict(dict)
            for row in rows:
                properties[row.pset_name][row.name] = row.value

            c.execute("SELECT * FROM relationships WHERE from_id = ?", (element[0],))
            relationships = [RelationshipRow(*row) for row in c.fetchall()]

            relating_type_id = None

            for relationship in relationships:
                if relationship[1] == "IfcRelDefinesByType":
                    relating_type_id = relationship[2]

            type_properties: defaultdict[str, dict[str, str]] = defaultdict(dict)
            if relating_type_id is not None:
                c.execute("SELECT * FROM properties WHERE element_id = ?", (relating_type_id,))
                rows = [PropertyRow(*row) for row in c.fetchall()]
                for row in rows:
                    type_properties[row.pset_name][row.name] = row.value

            LinksData.linked_data = {
                "attributes": attributes,
                "properties": [(k, properties[k]) for k in sorted(properties.keys())],
                "type_properties": [(k, type_properties[k]) for k in sorted(type_properties.keys())],
            }
            db.close()

            assert context.screen
            for area in context.screen.areas:
                if area.type == "PROPERTIES":
                    for region in area.regions:
                        if region.type == "WINDOW":
                            region.tag_redraw()
                elif area.type == "VIEW_3D":
                    area.tag_redraw()

            ProjectDecorator.install(context)

        @classmethod
        def set_queried_linked_element(cls, obj: bpy.types.Object, guid: str, instance_matrix: Matrix) -> None:
            props = tool.Project.get_project_props()
            props.queried_obj = obj
            props.queried_obj_root = cls.find_obj_root(obj, instance_matrix)
            props.queried_guid = guid

        @classmethod
        def deselect_queried_linked_element(cls) -> None:
            props = tool.Project.get_project_props()
            obj = props.queried_obj
            props.property_unset("queried_obj")
            props.property_unset("queried_obj_root")
            props.property_unset("queried_guid")

            if obj is not None:
                for field in cls.SelectedGeometry._fields:
                    del obj[field]

        @classmethod
        def find_obj_root(cls, obj: bpy.types.Object, matrix: Matrix) -> bpy.types.Object | None:
            collections = set(obj.users_collection)
            for o in bpy.data.objects:
                if (
                    o.type != "EMPTY"
                    or o.instance_type != "COLLECTION"
                    or o.instance_collection not in collections
                    or not np.allclose(matrix, o.matrix_world, atol=1e-4)
                ):
                    continue
                return o

        class SelectedGeometry(NamedTuple):
            selected_vertices: list[tuple[float, float, float]]
            selected_edges: list[tuple[int, int]]
            selected_tris: list[tuple[int, int, int]]

        @classmethod
        def get_selected_geometry(cls, obj: bpy.types.Object) -> SelectedGeometry:
            return cls.SelectedGeometry(
                obj["selected_vertices"],
                obj["selected_edges"],
                obj["selected_tris"],
            )
