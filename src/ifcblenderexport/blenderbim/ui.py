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

        layout.label(text="Property Sets:")
        row = layout.row()
        row.operator('bim.add_pset')

        for index, pset in enumerate(props.psets):
            row = layout.row(align=True)
            row.prop(pset, 'name', text='')
            row.prop(pset, 'file', text='')
            row.operator('bim.remove_pset', icon='X', text='').pset_index = index

        row = layout.row()
        row.prop(props, 'psets')

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
        props = bpy.context.scene.DocProperties

        row = layout.row()
        row.operator('bim.cut_section')

class BIM_PT_context(Panel):
    bl_label = "Geometric Representation Contexts"
    bl_idname = "BIM_PT_context"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        props = scene.BIMProperties

        for context in ['model', 'plan']:
            row = layout.row(align=True)
            row.prop(props, 'has_{}_context'.format(context))
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

        col = layout.column()
        row = col.row(align=True)
        row.prop(bim_properties, "schema_dir")
        row.operator("bim.select_schema_dir", icon="FILE_FOLDER", text="")

        col = layout.column()
        row = col.row(align=True)
        row.prop(bim_properties, "data_dir")
        row.operator("bim.select_data_dir", icon="FILE_FOLDER", text="")

        layout.label(text="Software Identity:")

        row = layout.row()
        row.prop(bim_properties, 'global_id')
        row = layout.row()
        row.operator('bim.select_global_id')

        layout.label(text="IFC Categorisation:")

        row = layout.row()
        row.prop(bim_properties, "ifc_class")
        row = layout.row()
        row.prop(bim_properties, "ifc_predefined_type")
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
        row = layout.row()
        row.operator("bim.create_aggregate")

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

        layout.label(text="Custom MVD:")

        row = layout.row()
        row.prop(bim_properties, "export_has_representations")
        row = layout.row()
        row.prop(bim_properties, "export_should_export_all_materials_as_styled_items")
        row = layout.row()
        row.prop(bim_properties, "export_should_use_presentation_style_assignment")

        row = layout.row()
        row.prop(bim_properties, "import_should_ignore_site_coordinates")
        row = layout.row()
        row.prop(bim_properties, "import_should_import_curves")
