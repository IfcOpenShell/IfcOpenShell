# import os
import bpy
# import uuid
# import hashlib
# import zipfile
# import tempfile
import ifcopenshell
from ifcopenshell import template
# import blenderbim.bim.handler
# from pathlib import Path

class SvIfcStore:
    path = ""
    file = None
    schema = None
    cache = None
    cache_path = None
    id_map = {}
    guid_map = {}
    deleted_ids = set()
    edited_objs = set()
    pset_template_path = ""
    pset_template_file = None
    library_path = ""
    library_file = None
    element_listeners = set()
    undo_redo_stack_objects = set()
    undo_redo_stack_object_names = {}
    current_transaction = ""
    last_transaction = ""
    history = []
    future = []
    schema_identifiers = ["IFC4", "IFC2X3"]

    @staticmethod
    def purge():
        SvIfcStore.path = ""
        SvIfcStore.file = None
        SvIfcStore.schema = None
        SvIfcStore.cache = None
        SvIfcStore.cache_path = None
        SvIfcStore.id_map = {}
        SvIfcStore.guid_map = {}
        SvIfcStore.deleted_ids = set()
        SvIfcStore.edited_objs = set()
        SvIfcStore.pset_template_path = ""
        SvIfcStore.pset_template_file = None
        SvIfcStore.library_path = ""
        SvIfcStore.library_file = None
        SvIfcStore.last_transaction = ""
        SvIfcStore.history = []
        SvIfcStore.future = []
        SvIfcStore.schema_identifiers = ["IFC4", "IFC2X3"]


    @staticmethod
    def create_boilerplate():

        file = template.create(
            filename="IfcSverchokDemoFile",
            organization=None,
            creator=None,
            project_name="IfcSverchokDemoProject",
            )
        if bpy.context.scene.unit_settings.system == 'IMPERIAL':
            #TODO change units to imperial
            pass
        model = ifcopenshell.api.run("context.add_context", file, context_type="Model")
        context = ifcopenshell.api.run(
            "context.add_context",
            file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        )
        site = ifcopenshell.api.run("root.create_entity", file, ifc_class="IfcSite", name="My Site")
        building = ifcopenshell.api.run(
            "root.create_entity", file, ifc_class="IfcBuilding", name="My Building"
        )
        building_storey = ifcopenshell.api.run(
            "root.create_entity", file, ifc_class="IfcBuildingStorey", name="My Storey"
        )

        ifcopenshell.api.run("aggregate.assign_object", file, product=site, relating_object=file.by_type("IfcProject")[0])
        ifcopenshell.api.run("aggregate.assign_object", file, product=building, relating_object=site)
        ifcopenshell.api.run("aggregate.assign_object", file, product=building_storey, relating_object=building)

        SvIfcStore.file = file
        return SvIfcStore.file
 


    @staticmethod
    def get_file():
        return SvIfcStore.file
