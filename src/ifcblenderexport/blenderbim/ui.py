import bpy
from bpy.types import Panel

class BIM_PT_object(Panel):
    bl_label = 'IFC Object'
    bl_idname = 'BIM_PT_object'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and hasattr(context.active_object, "BIMObjectProperties")

    def draw(self, context):

        if context.active_object is None:
            return
        layout = self.layout
        props = context.active_object.BIMObjectProperties

        layout.label(text="Software Identity:")
        row = layout.row()
        row.operator('bim.generate_global_id')

        layout.label(text="Attributes:")
        row = layout.row(align=True)
        row.prop(props, 'applicable_attributes', text='')
        row.operator('bim.add_attribute')

        for index, attribute in enumerate(props.attributes):
            row = layout.row(align=True)
            row.prop(attribute, 'name', text='')
            row.prop(attribute, 'string_value', text='')
            row.operator('bim.remove_attribute', icon='X', text='').attribute_index = index

        row = layout.row()
        row.prop(props, 'attributes')

        row = layout.row()
        row.prop(props, 'relating_type')
        row = layout.row()
        row.prop(props, 'relating_structure')

        layout.label(text="Property Sets:")
        row = layout.row()
        row.prop(context.scene.BIMProperties, "pset_name")
        row = layout.row()
        row.prop(context.scene.BIMProperties, "pset_file")
        row = layout.row()
        row.operator('bim.add_pset')

        for index, pset in enumerate(props.psets):
            row = layout.row(align=True)
            row.prop(pset, 'name', text='')
            row.prop(pset, 'file', text='')
            row.operator('bim.remove_pset', icon='X', text='').pset_index = index

        row = layout.row()
        row.prop(props, 'psets')

        row = layout.row(align=True)
        row.prop(props, 'override_pset_name', text='')
        row.operator('bim.add_override_pset')

        for index, pset in enumerate(props.override_psets):
            row = layout.row(align=True)
            row.prop(pset, 'name', text='')
            row.operator('bim.remove_override_pset', icon='X', text='').pset_index = index
            for prop in pset.properties:
                row = layout.row(align=True)
                row.prop(prop, 'name', text='')
                row.prop(prop, 'string_value', text='')

        layout.label(text="Quantities:")

        row = layout.row(align=True)
        row.prop(props, 'qto_name', text='')
        row.operator('bim.add_qto')

        for index, qto in enumerate(props.qtos):
            row = layout.row(align=True)
            row.prop(qto, 'name', text='')
            row.operator('bim.remove_qto', icon='X', text='').index = index
            for prop in qto.properties:
                row = layout.row(align=True)
                row.prop(prop, 'name', text='')
                row.prop(prop, 'string_value', text='')

        layout.label(text="Documents:")
        row = layout.row(align=True)
        row.prop(props, 'applicable_documents', text='')
        row.operator('bim.add_document')

        row = layout.row()
        row.operator('bim.fetch_object_passport')

        for index, document in enumerate(props.documents):
            row = layout.row(align=True)
            row.prop(document, 'file', text='')
            row.operator('bim.remove_document', icon='X', text='').document_index = index

        row = layout.row()
        row.prop(props, 'documents')

        layout.label(text="Classification:")

        for index, classification in enumerate(props.classifications):
            row = layout.row(align=True)
            row.prop(classification, 'identification', text='')
            row.prop(classification, 'name', text='')
            row.operator('bim.remove_classification', icon='X', text='').classification_index = index

        row = layout.row()
        row.prop(props, 'classifications')

        row = layout.row()
        row.prop(props, 'material_type')

        layout.label(text='Structural Boundary Condition:')

        row = layout.row()
        row.prop(props, 'has_boundary_condition')

        if bpy.context.active_object.BIMObjectProperties.has_boundary_condition:
            row = layout.row()
            row.prop(props.boundary_condition, 'name')
            for index, attribute in enumerate(props.boundary_condition.attributes):
                row = layout.row(align=True)
                row.prop(attribute, 'name', text='')
                row.prop(attribute, 'string_value', text='')

        row = layout.row()
        row.prop(props, 'structural_member_connection')


class BIM_PT_mesh(Panel):
    bl_label = 'IFC Representations'
    bl_idname = 'BIM_PT_mesh'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH" and \
               hasattr(context.active_object.data, "BIMMeshProperties")

    def draw(self, context):
        if not context.active_object.data:
            return
        layout = self.layout
        props = context.active_object.data.BIMMeshProperties

        row = layout.row(align=True)
        row.prop(bpy.context.scene.BIMProperties, 'available_contexts', text='')
        row.prop(bpy.context.scene.BIMProperties, 'available_subcontexts', text='')
        row.prop(bpy.context.scene.BIMProperties, 'available_target_views', text='')
        row = layout.row()
        row.operator('bim.assign_context')

        row = layout.row()
        row.prop(props, 'is_parametric')

        row = layout.row()
        row.prop(props, 'is_wireframe')
        row = layout.row()
        row.prop(props, 'is_swept_solid')

        row = layout.row()
        row.operator('bim.add_swept_solid')
        for index, swept_solid in enumerate(props.swept_solids):
            row = layout.row(align=True)
            row.prop(swept_solid, 'name', text='')
            row.operator('bim.remove_swept_solid', icon='X', text='').index = index
            row = layout.row()
            sub = row.row(align=True)
            sub.operator('bim.assign_swept_solid_outer_curve').index = index
            sub.operator('bim.select_swept_solid_outer_curve', icon='RESTRICT_SELECT_OFF', text='').index = index
            sub = row.row(align=True)
            sub.operator('bim.add_swept_solid_inner_curve').index = index
            sub.operator('bim.select_swept_solid_inner_curves', icon='RESTRICT_SELECT_OFF', text='').index = index
            row = layout.row(align=True)
            row.operator('bim.assign_swept_solid_extrusion').index = index
            row.operator('bim.select_swept_solid_extrusion', icon='RESTRICT_SELECT_OFF', text='').index = index
        row = layout.row()
        row.prop(props, 'swept_solids')


class BIM_PT_material(Panel):
    bl_label = 'IFC Materials'
    bl_idname = 'BIM_PT_material'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.active_material is not None

    def draw(self, context):
        if not bpy.context.active_object.active_material:
            return
        props = context.active_object.active_material.BIMMaterialProperties
        layout = self.layout
        row = layout.row()
        row.prop(props, 'is_external')
        row = layout.row(align=True)
        row.prop(props, 'location')
        row.operator('bim.select_external_material_dir', icon="FILE_FOLDER", text="")
        row = layout.row()
        row.prop(props, 'identification')
        row = layout.row()
        row.prop(props, 'name')

        row = layout.row()
        row.operator('bim.fetch_external_material')

        layout.label(text="Attributes:")
        row = layout.row(align=True)
        row.prop(props, 'applicable_attributes', text='')
        row.operator('bim.add_material_attribute')

        for index, attribute in enumerate(props.attributes):
            row = layout.row(align=True)
            row.prop(attribute, 'name', text='')
            row.prop(attribute, 'string_value', text='')
            row.operator('bim.remove_material_attribute', icon='X', text='').attribute_index = index

        row = layout.row()
        row.prop(props, 'attributes')

        layout.label(text="Property Sets:")
        row = layout.row(align=True)
        row.prop(props, 'available_material_psets', text='')
        row.operator('bim.add_material_pset')

        for index, pset in enumerate(props.psets):
            row = layout.row(align=True)
            row.prop(pset, 'name', text='')
            row.operator('bim.remove_material_pset', icon='X', text='').pset_index = index

        row = layout.row()
        row.prop(props, 'psets', text='')

        if context.active_object.BIMObjectProperties.material_type == 'IfcMaterialProfileSet':
            layout.label(text="Profile Definition:")
            row = layout.row()
            row.prop(props, 'profile_def')

            for index, attribute in enumerate(props.profile_attributes):
                row = layout.row(align=True)
                row.prop(attribute, 'name', text='')
                row.prop(attribute, 'string_value', text='')


class BIM_PT_gis(Panel):
    bl_label = 'IFC Georeferencing'
    bl_idname = "BIM_PT_gis"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        layout.row().prop(scene.BIMProperties, 'has_georeferencing')

        layout.label(text="Map Conversion:")
        layout.row().prop(scene.MapConversion, 'eastings')
        layout.row().prop(scene.MapConversion, 'northings')
        layout.row().prop(scene.MapConversion, 'orthogonal_height')
        layout.row().prop(scene.MapConversion, 'x_axis_abscissa')
        layout.row().prop(scene.MapConversion, 'x_axis_ordinate')
        layout.row().prop(scene.MapConversion, 'scale')

        layout.label(text="Target CRS:")
        layout.row().prop(scene.TargetCRS, 'name')
        layout.row().prop(scene.TargetCRS, 'description')
        layout.row().prop(scene.TargetCRS, 'geodetic_datum')
        layout.row().prop(scene.TargetCRS, 'vertical_datum')
        layout.row().prop(scene.TargetCRS, 'map_projection')
        layout.row().prop(scene.TargetCRS, 'map_zone')
        layout.row().prop(scene.TargetCRS, 'map_unit')


class BIM_PT_documentation(Panel):
    bl_label = "Diagrammatic Documentation"
    bl_idname = "BIM_PT_documentation"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = bpy.context.scene.DocProperties

        row = layout.row()
        row.operator('bim.set_view_preset_1')

        row = layout.row()
        row.prop(props, 'view_name')
        row.operator('bim.create_view', icon='ADD', text='')

        row = layout.row()
        row.prop(props, 'sheet_name')
        row.operator('bim.create_sheet', icon='ADD', text='')

        row = layout.row()
        row.prop(props, 'available_views')
        row.operator('bim.open_view', icon='URL', text='')
        row.operator('bim.activate_view', icon='SCENE', text='')

        row = layout.row()
        row.prop(props, 'available_sheets')
        row.operator('bim.open_sheet', icon='URL', text='')
        row.operator('bim.open_compiled_sheet', icon='OUTPUT', text='')

        row = layout.row()
        row.operator('bim.add_view_to_sheet')

        row = layout.row()
        row.operator('bim.create_sheets')

        row = layout.row()
        row.operator('bim.generate_digital_twin')


class BIM_PT_camera(Panel):
    bl_label = "Diagrams and Documentation"
    bl_idname = "BIM_PT_camera"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        engine = context.engine
        return context.camera and \
               hasattr(context.active_object.data, "BIMCameraProperties")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        dprops = bpy.context.scene.DocProperties
        props = context.active_object.data.BIMCameraProperties

        row = layout.row()
        row.prop(dprops, 'should_recut')

        row = layout.row()
        row.prop(props, 'is_nts')

        row = layout.row(align=True)
        row.prop(props, 'diagram_scale', text='')
        row.operator('bim.cut_section')


class BIM_PT_owner(Panel):
    bl_label = "Owner History"
    bl_idname = "BIM_PT_owner"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.BIMProperties

        row = layout.row()
        row.prop(props, 'person')

        row = layout.row()
        row.prop(props, 'organisation')

class BIM_PT_context(Panel):
    bl_label = "Geometric Representation Contexts"
    bl_idname = "BIM_PT_context"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        props = scene.BIMProperties

        for context in ['model', 'plan']:
            row = layout.row(align=True)
            row.prop(props, f'has_{context}_context')

            if not getattr(props, f'has_{context}_context'):
                continue

            layout.label(text="Geometric Representation Subcontexts:")
            row = layout.row(align=True)
            row.prop(props, 'available_subcontexts', text='')
            row.prop(props, 'available_target_views', text='')
            row.operator('bim.add_subcontext', icon='ADD', text='').context = context

            for subcontext_index, subcontext in enumerate(getattr(props, '{}_subcontexts'.format(context))):
                row = layout.row(align=True)
                row.prop(subcontext, 'name', text='')
                row.prop(subcontext, 'target_view', text='')
                row.operator('bim.remove_subcontext', icon='X', text='').indexes = '{}-{}'.format(context, subcontext_index)


class BIM_PT_bim(Panel):
    bl_label = "Building Information Modeling"
    bl_idname = "BIM_PT_bim"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bim_properties = scene.BIMProperties

        layout.label(text="System Setup:")

        row = layout.row()
        row.operator('bim.quick_project_setup')

        row = layout.row(align=True)
        row.prop(bim_properties, "schema_dir")
        row.operator("bim.select_schema_dir", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "data_dir")
        row.operator("bim.select_data_dir", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "ifc_file")
        row.operator("bim.select_ifc_file", icon="FILE_FOLDER", text="")

        layout.label(text="IFC Categorisation:")

        row = layout.row()
        row.prop(bim_properties, "ifc_product")
        row = layout.row()
        row.prop(bim_properties, "ifc_class")
        if bim_properties.ifc_predefined_type:
            row = layout.row()
            row.prop(bim_properties, "ifc_predefined_type")
        if bim_properties.ifc_predefined_type == 'USERDEFINED':
            row = layout.row()
            row.prop(bim_properties, "ifc_userdefined_type")
        row = layout.row()
        row.operator("bim.assign_class")

        row = layout.row(align=True)
        row.operator("bim.select_class")
        row.operator("bim.select_type")

        layout.label(text="Property Sets:")
        row = layout.row()
        row.prop(bim_properties, "pset_name")
        row = layout.row()
        row.prop(bim_properties, "pset_file")

        row = layout.row(align=True)
        row.operator("bim.assign_pset")
        row.operator("bim.unassign_pset")

        layout.label(text="Aggregates:")
        row = layout.row()
        row.prop(bim_properties, "aggregate_class")
        row = layout.row()
        row.prop(bim_properties, "aggregate_name")

        row = layout.row(align=True)
        row.operator("bim.create_aggregate")
        row.operator("bim.explode_aggregate")

        row = layout.row(align=True)
        row.operator("bim.edit_aggregate")
        row.operator("bim.save_aggregate")

        layout.label(text="Classifications:")
        row = layout.row()
        row.prop(bim_properties, "classification")
        row = layout.row()
        row.prop(bim_properties, "reference")

        row = layout.row(align=True)
        row.operator("bim.assign_classification")
        row.operator("bim.unassign_classification")


class BIM_PT_search(Panel):
    bl_label = "BIM Search"
    bl_idname = "BIM_PT_search"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        props = scene.BIMProperties

        row = layout.row()
        row.prop(props, 'search_regex')
        row = layout.row()
        row.prop(props, 'search_ignorecase')

        layout.label(text="Global ID:")
        row = layout.row(align=True)
        row.prop(props, 'global_id', text='')
        row.operator('bim.select_global_id', text='', icon='VIEWZOOM')

        layout.label(text="Attribute:")
        row = layout.row(align=True)
        row.prop(props, 'search_attribute_name', text='')
        row.prop(props, 'search_attribute_value', text='')
        row.operator('bim.select_attribute', text='', icon='VIEWZOOM')
        row.operator('bim.colour_by_attribute', text='', icon='BRUSH_DATA')

        layout.label(text="Pset:")
        row = layout.row(align=True)
        row.prop(props, 'search_pset_name', text='')
        row.prop(props, 'search_prop_name', text='')
        row.prop(props, 'search_pset_value', text='')
        row.operator('bim.select_pset', text='', icon='VIEWZOOM')
        row.operator('bim.colour_by_pset', text='', icon='BRUSH_DATA')


class BIM_PT_bcf(Panel):
    bl_label = "BIM Collaboration Format"
    bl_idname = "BIM_PT_bcf"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = bpy.context.scene.BCFProperties

        row = layout.row(align=True)
        row.prop(props, "bcf_file")
        row.operator("bim.select_bcf_file", icon="FILE_FOLDER", text="")

        row = layout.row()
        row.operator("bim.get_bcf_topics")

        props = bpy.context.scene.BCFProperties
        layout.template_list('BIM_UL_topics', '', props, 'topics', props, 'active_topic_index')

        row = layout.row()
        row.prop(props, 'topic_description', text='')

        row = layout.row()
        row.prop(props, 'viewpoints')
        row.operator('bim.activate_bcf_viewpoint', icon='SCENE', text='')

        row = layout.row()
        row.prop(props, 'topic_type', text='Type')
        row = layout.row()
        row.prop(props, 'topic_status', text='Status')
        row = layout.row()
        row.prop(props, 'topic_priority', text='Priority')
        row = layout.row()
        row.prop(props, 'topic_stage', text='Stage')
        row = layout.row()
        row.prop(props, 'topic_creation_date', text='Date')
        row = layout.row()
        row.prop(props, 'topic_creation_author', text='Author')
        row = layout.row()
        row.prop(props, 'topic_modified_date', text='Modified On')
        row = layout.row()
        row.prop(props, 'topic_modified_author', text='Modified By')
        row = layout.row()
        row.prop(props, 'topic_assigned_to', text='Assigned To')
        row = layout.row()
        row.prop(props, 'topic_due_date', text='Due Date')

        layout.label(text="Reference Links:")
        for index, label in enumerate(props.topic_links):
            row = layout.row()
            row.prop(label, 'name', text='Link {}'.format(index + 1))
            row.operator('bim.open_bcf_reference_link', icon='URL', text='').index = index

        layout.label(text="Labels:")
        for index, label in enumerate(props.topic_labels):
            row = layout.row(align=True)
            row.prop(label, 'name', text='')

        layout.label(text="BIM Snippet:")
        if props.topic_has_snippet:
            row = layout.row(align=True)
            row.prop(props, 'topic_snippet_type')
            if props.topic_snippet_schema:
                row.operator('bim.open_bcf_bim_snippet_schema', icon='URL', text='')

            row = layout.row(align=True)
            row.prop(props, 'topic_snippet_reference')
            if props.topic_snippet_is_external:
                row.operator('bim.open_bcf_bim_snippet_reference', icon='URL', text='')
            else:
                row.operator('bim.open_bcf_bim_snippet_reference', icon='FILE_FOLDER', text='').topic_guid = props.topic_guid

        layout.label(text="Document References:")
        for index, doc in enumerate(props.topic_document_references):
            row = layout.row(align=True)
            row.prop(doc, 'description', text=f'File {index+1} Description:')
            row = layout.row(align=True)
            row.prop(doc, 'name', text=f'File {index+1} URI')
            if doc.is_external:
                row.operator('bim.open_bcf_document_reference', icon='URL', text='').data = '{}/{}'.format(
                        props.topic_guid, index)
            else:
                row.operator('bim.open_bcf_document_reference', icon='FILE_FOLDER', text='').data = '{}/{}'.format(
                        props.topic_guid, index)

        layout.label(text="Related Topics:")
        for topic in props.topic_related_topics:
            row = layout.row(align=True)
            row.operator('bim.view_bcf_topic', text=topic.name).topic_guid = topic.guid


class BIM_PT_qa(Panel):
    bl_label = "BIMTester Quality Auditing"
    bl_idname = "BIM_PT_qa"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bim_properties = bpy.context.scene.BIMProperties

        layout.label(text="Gherkin Setup:")

        row = layout.row(align=True)
        row.prop(bim_properties, "features_dir")
        row.operator("bim.select_features_dir", icon="FILE_FOLDER", text="")

        if bim_properties.features_dir:
            row = layout.row(align=True)
            row.prop(bim_properties, "features_file")

            row = layout.row(align=True)
            row.prop(bim_properties, "scenario")

        layout.label(text="Quality Auditing:")

        row = layout.row()
        row.prop(bim_properties, "qa_reject_element_reason")
        row = layout.row()
        row.operator("bim.reject_element")

        row = layout.row(align=True)
        row.operator("bim.colour_by_class")
        row.operator("bim.reset_object_colours")

        row = layout.row()
        row.prop(bim_properties, "audit_ifc_class")

        row = layout.row(align=True)
        row.operator("bim.approve_class")
        row.operator("bim.reject_class")

        row = layout.row()
        row.operator("bim.select_audited")

class BIM_PT_library(Panel):
    bl_label = "BIM Server Library"
    bl_idname = "BIM_PT_library"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bim_properties = scene.BIMProperties

        layout.row().prop(scene.BIMProperties, 'has_library')

        layout.label(text="Project Library:")
        layout.row().prop(scene.BIMLibrary, 'location')
        layout.row().operator("bim.fetch_library_information")
        layout.row().prop(scene.BIMLibrary, 'name')
        layout.row().prop(scene.BIMLibrary, 'version')
        layout.row().prop(scene.BIMLibrary, 'version_date')
        layout.row().prop(scene.BIMLibrary, 'description')

class BIM_PT_diff(Panel):
    bl_label = "IFC Diff"
    bl_idname = "BIM_PT_diff"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bim_properties = scene.BIMProperties

        layout.label(text="IFC Diff Setup:")

        row = layout.row(align=True)
        row.prop(bim_properties, "diff_json_file")
        row.operator("bim.select_diff_json_file", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "diff_old_file")
        row.operator("bim.select_diff_old_file", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "diff_new_file")
        row.operator("bim.select_diff_new_file", icon="FILE_FOLDER", text="")

        row = layout.row()
        row.operator('bim.execute_ifc_diff')


class BIM_PT_mvd(Panel):
    bl_label = "Model View Definitions"
    bl_idname = "BIM_PT_mvd"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        bim_properties = scene.BIMProperties

        layout.label(text='Custom MVD:')

        row = layout.row()
        row.prop(bim_properties, 'export_has_representations')
        row = layout.row()
        row.prop(bim_properties, 'import_should_import_curves')
        row = layout.row()
        row.prop(bim_properties, 'import_should_import_opening_elements')
        row = layout.row()
        row.prop(bim_properties, 'import_should_import_spaces')

        layout.label(text='Experimental Modes:')

        row = layout.row()
        row.prop(bim_properties, 'import_should_use_legacy')
        row = layout.row()
        row.prop(bim_properties, 'import_should_use_cpu_multiprocessing')

        layout.label(text='Simplifications:')

        row = layout.row()
        row.prop(bim_properties, 'import_should_import_aggregates')
        row = layout.row()
        row.prop(bim_properties, 'import_should_merge_by_class')
        row = layout.row()
        row.prop(bim_properties, 'import_should_merge_by_material')
        row = layout.row()
        row.prop(bim_properties, 'import_should_clean_mesh')

        layout.label(text='Vendor Workarounds:')

        row = layout.row()
        row.prop(bim_properties, 'import_should_auto_set_workarounds')

        layout.label(text='Tekla Workarounds:')

        row = layout.row()
        row.prop(bim_properties, 'import_should_ignore_site_coordinates')

        layout.label(text='12D Workarounds:')

        row = layout.row()
        row.prop(bim_properties, 'import_should_reset_absolute_coordinates')

        layout.label(text='Revit Workarounds:')

        row = layout.row()
        row.prop(bim_properties, 'export_should_export_all_materials_as_styled_items')
        row = layout.row()
        row.prop(bim_properties, 'export_should_use_presentation_style_assignment')
        row = layout.row()
        row.prop(bim_properties, 'import_should_ignore_site_coordinates')
        row = layout.row()
        row.prop(bim_properties, 'import_should_ignore_building_coordinates')
        row = layout.row()
        row.prop(bim_properties, 'import_should_treat_styled_item_as_material')


class BIM_UL_topics(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.prop(item, 'name', text='', emboss=False)
        else:
            layout.label(text="", translate=False)


class BIM_ADDON_preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('bim.open_upstream', text='Visit Homepage').page = 'home'
        row.operator('bim.open_upstream', text='Visit Documentation').page = 'docs'
        row = layout.row()
        row.operator('bim.open_upstream', text='Visit Wiki').page = 'wiki'
        row.operator('bim.open_upstream', text='Visit Community').page = 'community'
        row = layout.row()
        row.operator('bim.uninstall')
