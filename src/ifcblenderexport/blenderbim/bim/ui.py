import bpy
from bpy.types import Panel
from bpy.props import StringProperty


class BIM_PT_object(Panel):
    bl_label = "IFC Object"
    bl_idname = "BIM_PT_object"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and hasattr(context.active_object, "BIMObjectProperties")

    def draw(self, context):
        if context.active_object is None:
            return
        layout = self.layout
        props = context.active_object.BIMObjectProperties
        bim_properties = context.scene.BIMProperties

        if props.is_reassigning_class or "/" not in context.active_object.name:
            row = layout.row()
            row.prop(bim_properties, "ifc_product")
            row = layout.row()
            row.prop(bim_properties, "ifc_class")
            if bim_properties.ifc_predefined_type:
                row = layout.row()
                row.prop(bim_properties, "ifc_predefined_type")
            if bim_properties.ifc_predefined_type == "USERDEFINED":
                row = layout.row()
                row.prop(bim_properties, "ifc_userdefined_type")
            row = layout.row(align=True)
            if "Ifc" not in context.active_object.name:
                op = row.operator("bim.assign_class")
            else:
                op = row.operator("bim.assign_class")
            op.object_name = context.active_object.name
            op = row.operator("bim.unassign_class", icon="X", text="")
            op.object_name = context.active_object.name
        else:
            row = layout.row()
            row.operator("bim.reassign_class", text="Reassign IFC Class")

        if "Ifc" not in context.active_object.name:
            return

        layout.label(text="Attributes:")
        row = layout.row(align=True)
        row.prop(props, "applicable_attributes", text="")
        row.operator("bim.add_attribute")

        for index, attribute in enumerate(props.attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.prop(attribute, "string_value", text="")
            if attribute.name == "GlobalId":
                row.operator("bim.generate_global_id", icon="FILE_REFRESH", text="")
            op = row.operator("bim.copy_attribute_to_selection", icon="COPYDOWN", text="")
            op.attribute_name = attribute.name
            op.attribute_value = attribute.string_value
            row.operator("bim.remove_attribute", icon="X", text="").attribute_index = index

        row = layout.row()
        row.prop(props, "attributes")

        if "IfcSite/" in context.active_object.name or "IfcBuilding/" in context.active_object.name:
            self.draw_addresses_ui()

        row = layout.row(align=True)
        row.prop(props, "relating_type")
        row.operator("bim.select_similar_type", icon="RESTRICT_SELECT_OFF", text="")
        row = layout.row()
        row.prop(props, "relating_structure")

    def draw_addresses_ui(self):
        layout = self.layout
        layout.label(text="Address:")
        address = bpy.context.active_object.BIMObjectProperties.address
        row = layout.row()
        row.prop(address, "purpose")
        if address.purpose == "USERDEFINED":
            row = layout.row()
            row.prop(address, "user_defined_purpose")
        row = layout.row()
        row.prop(address, "description")

        row = layout.row()
        row.prop(address, "internal_location")
        row = layout.row()
        row.prop(address, "address_lines")
        row = layout.row()
        row.prop(address, "postal_box")
        row = layout.row()
        row.prop(address, "town")
        row = layout.row()
        row.prop(address, "region")
        row = layout.row()
        row.prop(address, "postal_code")
        row = layout.row()
        row.prop(address, "country")


class BIM_PT_object_material(Panel):
    bl_label = "IFC Object Material"
    bl_idname = "BIM_PT_object_material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and hasattr(context.active_object, "BIMObjectProperties")

    def draw(self, context):
        if context.active_object is None:
            return
        layout = self.layout
        props = context.active_object.BIMObjectProperties
        row = layout.row()
        row.prop(props, "material_type")

        if props.material_type == "None" and props.relating_type:
            props = props.relating_type.BIMObjectProperties
            if props.material_type == "None":
                pass
            elif props.material_type == "IfcMaterial" and props.material:
                layout.label(text="Inherited Material:")
            elif props.material_set:
                layout.label(text="Inherited Material Set:")

        if props.material_type == "None":
            pass
        elif props.material_type == "IfcMaterial":
            row = layout.row()
            row.prop(props, "material")
        else:
            set_props = props.material_set
            row = layout.row()
            row.prop(set_props, "name", text="Name")
            row = layout.row()
            row.prop(set_props, "description", text="Description")
            row = layout.row()

        if props.material_type == "IfcMaterialLayerSet":
            row.template_list(
                "MATERIAL_UL_matslots", "", set_props, "material_layers", set_props, "active_material_layer_index"
            )
            col = row.column(align=True)
            col.operator("bim.add_material_layer", icon="ADD", text="")
            col.operator(
                "bim.remove_material_layer", icon="REMOVE", text=""
            ).index = set_props.active_material_layer_index
            col.operator("bim.move_material_layer", icon="TRIA_UP", text="").direction = "UP"
            col.operator("bim.move_material_layer", icon="TRIA_DOWN", text="").direction = "DOWN"

            if set_props.active_material_layer_index < len(set_props.material_layers):
                material = set_props.material_layers[set_props.active_material_layer_index]
                row = layout.row()
                row.prop(material, "material")
                row = layout.row()
                row.prop(material, "name")
                row = layout.row()
                row.prop(material, "description")
                row = layout.row()
                row.prop(material, "category")
                if material.category == "Custom":
                    row = layout.row()
                    row.prop(material, "custom_category")
                row = layout.row()
                row.prop(material, "layer_thickness")
                row = layout.row()
                row.prop(material, "is_ventilated")
                row = layout.row()
                row.prop(material, "priority")
        elif props.material_type == "IfcMaterialConstituentSet":
            row.template_list(
                "MATERIAL_UL_matslots",
                "",
                set_props,
                "material_constituents",
                set_props,
                "active_material_constituent_index",
            )
            col = row.column(align=True)
            col.operator("bim.add_material_constituent", icon="ADD", text="")
            col.operator(
                "bim.remove_material_constituent", icon="REMOVE", text=""
            ).index = set_props.active_material_constituent_index
            col.operator("bim.move_material_constituent", icon="TRIA_UP", text="").direction = "UP"
            col.operator("bim.move_material_constituent", icon="TRIA_DOWN", text="").direction = "DOWN"

            if set_props.active_material_constituent_index < len(set_props.material_constituents):
                material = set_props.material_constituents[set_props.active_material_constituent_index]
                row = layout.row()
                row.prop(material, "material")
                row = layout.row()
                row.prop(material, "name")
                row = layout.row()
                row.prop(material, "description")
                row = layout.row()
                row.prop(material, "fraction")
                row = layout.row()
                row.prop(material, "category")
        elif props.material_type == "IfcMaterialProfileSet":
            row.template_list(
                "MATERIAL_UL_matslots",
                "",
                set_props,
                "material_profiles",
                set_props,
                "active_material_profile_index",
            )
            col = row.column(align=True)
            col.operator("bim.add_material_profile", icon="ADD", text="")
            col.operator(
                "bim.remove_material_profile", icon="REMOVE", text=""
            ).index = set_props.active_material_profile_index
            col.operator("bim.move_material_profile", icon="TRIA_UP", text="").direction = "UP"
            col.operator("bim.move_material_profile", icon="TRIA_DOWN", text="").direction = "DOWN"

            if set_props.active_material_profile_index < len(set_props.material_profiles):
                material = set_props.material_profiles[set_props.active_material_profile_index]
                row = layout.row()
                row.prop(material, "material")
                row = layout.row()
                row.prop(material, "name")
                row = layout.row()
                row.prop(material, "description")
                row = layout.row()
                row.prop(material, "priority")
                row = layout.row()
                row.prop(material, "category")
                row = layout.row()
                row.prop(material, "profile")
                for index, attribute in enumerate(material.profile_attributes):
                    row = layout.row(align=True)
                    row.prop(attribute, "name", text="")
                    row.prop(attribute, "string_value", text="")


class BIM_PT_object_psets(Panel):
    bl_label = "IFC Object Property Sets"
    bl_idname = "BIM_PT_object_psets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and hasattr(context.active_object, "BIMObjectProperties")

    def draw(self, context):
        if context.active_object is None:
            return
        layout = self.layout
        props = context.active_object.BIMObjectProperties
        row = layout.row(align=True)
        row.prop(props, "pset_name", text="")
        row.operator("bim.add_pset")

        self.draw_psets_ui(props)

        if props.relating_type and props.relating_type.BIMObjectProperties.psets:
            layout.label(text="Inherited Psets:")
            self.draw_psets_ui(props.relating_type.BIMObjectProperties, enabled=False)

    def draw_psets_ui(self, props, enabled=True):
        for index, pset in enumerate(props.psets):
            box = self.layout.box()
            row = box.row(align=True)
            row.prop(
                pset,
                "is_expanded",
                icon="TRIA_DOWN" if pset.is_expanded else "TRIA_RIGHT",
                icon_only=True,
                emboss=False,
            )
            row2 = row.row(align=True)
            row2.enabled = enabled
            row2.prop(pset, "name", text="", icon="COPY_ID", emboss=pset.is_editable)

            if enabled:
                row.prop(pset, "is_editable", icon="CHECKMARK" if pset.is_editable else "GREASEPENCIL", icon_only=True)
                row.operator("bim.remove_pset", icon="X", text="").pset_index = index
            if not pset.is_expanded:
                continue
            if pset.is_editable:
                for prop in pset.properties:
                    row = box.row(align=True)
                    row.enabled = enabled
                    row.prop(prop, "name", text="")
                    row.prop(prop, "string_value", text="")
                    if not enabled:
                        continue
                    op = row.operator("bim.copy_property_to_selection", icon="COPYDOWN", text="")
                    op.pset_name = pset.name
                    op.prop_name = prop.name
                    op.prop_value = prop.string_value
            else:
                col = box.column(align=True)
                for prop in pset.properties:
                    if not prop.string_value:
                        continue
                    col.enabled = enabled
                    col.prop(prop, "string_value", text=prop.name)


class BIM_PT_object_qto(Panel):
    bl_label = "IFC Object Quantity Sets"
    bl_idname = "BIM_PT_object_qto"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and hasattr(context.active_object, "BIMObjectProperties")

    def draw(self, context):
        if context.active_object is None:
            return
        layout = self.layout
        props = context.active_object.BIMObjectProperties
        row = layout.row(align=True)
        row.prop(props, "qto_name", text="")
        row.operator("bim.add_qto")

        for index, qto in enumerate(props.qtos):
            box = self.layout.box()
            row = box.row(align=True)

            row.prop(
                qto, "is_expanded", icon="TRIA_DOWN" if qto.is_expanded else "TRIA_RIGHT", icon_only=True, emboss=False
            )
            row.prop(qto, "name", text="", icon="COPY_ID")
            row.operator("bim.remove_qto", icon="X", text="").index = index
            if not qto.is_expanded:
                continue
            for index2, prop in enumerate(qto.properties):
                row = box.row(align=True)
                row.prop(prop, "name", text="")
                row.prop(prop, "string_value", text="")
                if (
                    "length" in prop.name.lower()
                    or "width" in prop.name.lower()
                    or "height" in prop.name.lower()
                    or "depth" in prop.name.lower()
                    or "perimeter" in prop.name.lower()
                ):
                    op = row.operator("bim.guess_quantity", icon="IPO_EASE_IN_OUT", text="")
                    op.qto_index = index
                    op.prop_index = index2
                elif "area" in prop.name.lower():
                    op = row.operator("bim.guess_quantity", icon="MESH_CIRCLE", text="")
                    op.qto_index = index
                    op.prop_index = index2
                elif "volume" in prop.name.lower():
                    op = row.operator("bim.guess_quantity", icon="SPHERE", text="")
                    op.qto_index = index
                    op.prop_index = index2


class BIM_PT_object_structural(Panel):
    bl_label = "IFC Structural Relationships"
    bl_idname = "BIM_PT_object_structural"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and hasattr(context.active_object, "BIMObjectProperties")

    def draw(self, context):
        if context.active_object is None:
            return
        layout = self.layout
        props = context.active_object.BIMObjectProperties
        row = layout.row()
        row.prop(props, "has_boundary_condition")

        if bpy.context.active_object.BIMObjectProperties.has_boundary_condition:
            row = layout.row()
            row.prop(props.boundary_condition, "name")
            for index, attribute in enumerate(props.boundary_condition.attributes):
                row = layout.row(align=True)
                row.prop(attribute, "name", text="")
                row.prop(attribute, "string_value", text="")

        row = layout.row()
        row.prop(props, "structural_member_connection")


class BIM_PT_document_information(Panel):
    bl_label = "IFC Documents"
    bl_idname = "BIM_PT_document_information"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.scene.BIMProperties

        row = layout.row()
        row.operator("bim.add_document_information")

        if props.document_information:
            layout.template_list(
                "BIM_UL_document_information",
                "",
                props,
                "document_information",
                props,
                "active_document_information_index",
            )

            if props.active_document_information_index < len(props.document_information):
                information = props.document_information[props.active_document_information_index]
                row = layout.row(align=True)
                row.prop(information, "name")
                row.operator(
                    "bim.remove_document_information", icon="X", text=""
                ).index = props.active_document_information_index
                row = layout.row()
                row.prop(information, "human_name")
                row = layout.row()
                row.prop(information, "description")
                row = layout.row()
                row.prop(information, "location")
                row = layout.row()
                row.prop(information, "purpose")
                row = layout.row()
                row.prop(information, "intended_use")
                row = layout.row()
                row.prop(information, "scope")
                row = layout.row()
                row.prop(information, "revision")
                row = layout.row()
                row.prop(information, "creation_time")
                row = layout.row()
                row.prop(information, "last_revision_time")
                row = layout.row()
                row.prop(information, "electronic_format")
                row = layout.row()
                row.prop(information, "valid_from")
                row = layout.row()
                row.prop(information, "valid_until")
                row = layout.row()
                row.prop(information, "confidentiality")
                row = layout.row()
                row.prop(information, "status")

        row = layout.row()
        row.operator("bim.add_document_reference")

        if props.document_references:
            layout.template_list(
                "BIM_UL_document_references", "", props, "document_references", props, "active_document_reference_index"
            )

            if props.active_document_reference_index < len(props.document_references):
                reference = props.document_references[props.active_document_reference_index]
                row = layout.row(align=True)
                row.prop(reference, "name")
                row.operator(
                    "bim.remove_document_reference", icon="X", text=""
                ).index = props.active_document_reference_index
                row = layout.row()
                row.prop(reference, "human_name")
                row = layout.row()
                row.prop(reference, "location")
                row = layout.row()
                row.prop(reference, "description")
                row = layout.row(align=True)
                row.prop(reference, "referenced_document")
                row.operator(
                    "bim.assign_document_information", icon="LINKED", text=""
                ).index = props.active_document_reference_index

            row = layout.row(align=True)
            row.operator("bim.assign_document_reference", text="Assign Reference")
            row.operator("bim.unassign_document_reference", text="Unassign Reference")


class BIM_PT_constraints(Panel):
    bl_label = "IFC Constraints"
    bl_idname = "BIM_PT_constraints"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.scene.BIMProperties

        row = layout.row()
        row.operator("bim.add_constraint")

        if props.constraints:
            layout.template_list("BIM_UL_constraints", "", props, "constraints", props, "active_constraint_index")

            if props.active_constraint_index < len(props.constraints):
                constraint = props.constraints[props.active_constraint_index]
                row = layout.row(align=True)
                row.prop(constraint, "name")
                row.operator("bim.remove_constraint", icon="X", text="").index = props.active_constraint_index
                row = layout.row()
                row.prop(constraint, "description")
                row = layout.row()
                row.prop(constraint, "constraint_grade")
                if constraint.constraint_grade == "USERDEFINED":
                    row = layout.row()
                    row.prop(constraint, "user_defined_grade")
                row = layout.row()
                row.prop(constraint, "constraint_source")
                row = layout.row()
                row.prop(constraint, "objective_qualifier")
                if constraint.objective_qualifier == "USERDEFINED":
                    row = layout.row()
                    row.prop(constraint, "user_defined_qualifier")

            row = layout.row(align=True)
            row.operator("bim.assign_constraint", text="Assign Constraint")
            row.operator("bim.unassign_constraint", text="Unassign Constraint")


class BIM_PT_documents(Panel):
    bl_label = "IFC Documents"
    bl_idname = "BIM_PT_documents"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.active_object.BIMObjectProperties

        if not props.document_references:
            layout.label(text="No documents found")

        row = layout.row()
        row.operator("bim.fetch_object_passport")

        if props.document_references:
            layout.template_list(
                "BIM_UL_document_references", "", props, "document_references", props, "active_document_reference_index"
            )

            if props.active_document_reference_index < len(props.document_references):
                reference = props.document_references[props.active_document_reference_index]
                row = layout.row(align=True)
                row.prop(reference, "name")
                if reference.name in bpy.context.scene.BIMProperties.document_references:
                    reference = bpy.context.scene.BIMProperties.document_references[reference.name]
                    row.operator(
                        "bim.remove_object_document_reference", icon="X", text=""
                    ).index = props.active_document_reference_index
                    row = layout.row()
                    row.prop(reference, "human_name")
                    row = layout.row()
                    row.prop(reference, "location")
                    row = layout.row()
                    row.prop(reference, "description")
                    row = layout.row()
                    row.prop(reference, "referenced_document")
                else:
                    layout.label(text="Reference is invalid")


class BIM_PT_constraint_relations(Panel):
    bl_label = "IFC Constraints"
    bl_idname = "BIM_PT_constraint_relations"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.active_object.BIMObjectProperties

        if not props.constraints:
            layout.label(text="No constraints found")

        if props.constraints:
            layout.template_list("BIM_UL_constraints", "", props, "constraints", props, "active_constraint_index")

            if props.active_constraint_index < len(props.constraints):
                constraint = props.constraints[props.active_constraint_index]
                row = layout.row(align=True)
                row.prop(constraint, "name")
                if constraint.name in bpy.context.scene.BIMProperties.constraints:
                    constraint = bpy.context.scene.BIMProperties.constraints[constraint.name]
                    row.operator(
                        "bim.remove_object_constraint", icon="X", text=""
                    ).index = props.active_constraint_index
                    row = layout.row()
                    row.prop(constraint, "description")
                    row = layout.row()
                    row.prop(constraint, "constraint_grade")
                    if constraint.constraint_grade == "USERDEFINED":
                        row = layout.row()
                        row.prop(constraint, "user_defined_grade")
                    row = layout.row()
                    row.prop(constraint, "constraint_source")
                    row = layout.row()
                    row.prop(constraint, "objective_qualifier")
                    if constraint.objective_qualifier == "USERDEFINED":
                        row = layout.row()
                        row.prop(constraint, "user_defined_qualifier")
                else:
                    layout.label(text="Constraint is invalid")


class BIM_PT_representations(Panel):
    bl_label = "IFC Representations"
    bl_idname = "BIM_PT_representations"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        props = context.active_object.BIMObjectProperties

        if not props.representation_contexts:
            layout.label(text="No representations found")

        row = layout.row(align=True)
        row.prop(bpy.context.scene.BIMProperties, "available_contexts", text="")
        row.prop(bpy.context.scene.BIMProperties, "available_subcontexts", text="")
        row.prop(bpy.context.scene.BIMProperties, "available_target_views", text="")
        op = row.operator("bim.switch_context", icon="ADD", text="")
        op.has_target_context = False

        for index, subcontext in enumerate(props.representation_contexts):
            row = layout.row(align=True)
            row.prop(subcontext, "context", text="")
            row.prop(subcontext, "name", text="")
            row.prop(subcontext, "target_view", text="")
            op = row.operator("bim.switch_context", icon="OUTLINER_DATA_MESH", text="")
            op.has_target_context = True
            op.context_name = subcontext.context
            op.subcontext_name = subcontext.name
            op.target_view_name = subcontext.target_view
            row.operator("bim.remove_context", icon="X", text="").index = index


class BIM_PT_classification_references(Panel):
    bl_label = "IFC Classification References"
    bl_idname = "BIM_PT_classification_references"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.active_object.BIMObjectProperties

        if not props.classifications:
            layout.label(text="No classifications found")

        for index, classification in enumerate(props.classifications):
            row = layout.row(align=True)
            row.prop(classification, "name")
            row.operator("bim.remove_classification_reference", icon="X", text="").classification_index = index
            row = layout.row(align=True)
            row.prop(classification, "human_name")
            row = layout.row(align=True)
            row.prop(classification, "location")
            row = layout.row(align=True)
            row.prop(classification, "description")
            row = layout.row(align=True)
            row.prop(classification, "referenced_source")


class BIM_PT_psets(Panel):
    bl_label = "IFC Property Sets"
    bl_idname = "BIM_PT_psets"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMProperties

        row = layout.row(align=True)
        row.prop(props, "pset_template_files", text="")

        row = layout.row(align=True)
        row.prop(props, "property_set_templates", text="")
        row.operator("bim.add_property_set_template", text="", icon="ADD")
        row.operator("bim.remove_property_set_template", text="", icon="PANEL_CLOSE")
        row.operator("bim.edit_property_set_template", text="", icon="IMPORT")
        row.operator("bim.save_property_set_template", text="", icon="EXPORT")

        row = layout.row(align=True)
        row.prop(props.active_property_set_template, "name")
        row = layout.row(align=True)
        row.prop(props.active_property_set_template, "description")
        row = layout.row(align=True)
        row.prop(props.active_property_set_template, "template_type")
        row = layout.row(align=True)
        row.prop(props.active_property_set_template, "applicable_entity")

        layout.label(text="Property Templates:")

        row = layout.row(align=True)
        row.operator("bim.add_property_template")

        for index, template in enumerate(props.property_templates):
            row = layout.row(align=True)
            row.prop(template, "name", text="")
            row.prop(template, "description", text="")
            row.prop(template, "primary_measure_type", text="")
            row.operator("bim.remove_property_template", icon="X", text="").index = index


class BIM_PT_classifications(Panel):
    bl_label = "IFC Classifications"
    bl_idname = "BIM_PT_classifications"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMProperties

        row = layout.row(align=True)
        row.prop(props, "classification", text="")
        row.operator("bim.add_classification", text="", icon="ADD")

        if context.scene.BIMProperties.classification_references.raw_data:
            context.scene.BIMProperties.classification_references.draw_stub(context, layout)
            row = layout.row(align=True)
            row.operator("bim.assign_classification")
            row.operator("bim.unassign_classification")
        else:
            row = layout.row(align=True)
            row.operator("bim.load_classification").is_file = True

        if not props.classifications:
            return

        layout.label(text="Classifications:")

        for index, classification in enumerate(props.classifications):
            row = layout.row(align=True)
            row.prop(classification, "name")
            row.operator("bim.load_classification", icon="IMPORT", text="").classification_index = index
            row.operator("bim.remove_classification", icon="X", text="").classification_index = index
            row = layout.row(align=True)
            row.prop(classification, "source")
            row = layout.row(align=True)
            row.prop(classification, "edition")
            row = layout.row(align=True)
            row.prop(classification, "edition_date")
            row = layout.row(align=True)
            row.prop(classification, "description")
            row = layout.row(align=True)
            row.prop(classification, "location")
            row = layout.row(align=True)
            row.prop(classification, "reference_tokens")

        row = layout.row()
        row.prop(props, "classifications")


class BIM_PT_mesh(Panel):
    bl_label = "IFC Representations"
    bl_idname = "BIM_PT_mesh"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and hasattr(context.active_object.data, "BIMMeshProperties")
        )

    def draw(self, context):
        if not context.active_object.data:
            return
        layout = self.layout
        props = context.active_object.data.BIMMeshProperties

        row = layout.row(align=True)
        row.operator("bim.push_representation")

        row = layout.row()
        row.prop(props, "geometry_type")
        layout.label(text="IFC Parameters:")
        row = layout.row()
        row.operator("bim.get_representation_ifc_parameters")
        row = layout.row()
        row.operator("bim.bake_parametric_geometry")
        for index, ifc_parameter in enumerate(props.ifc_parameters):
            row = layout.row(align=True)
            row.prop(ifc_parameter, "name", text="")
            row.prop(ifc_parameter, "value", text="")
            row.operator("bim.update_ifc_representation", icon="FILE_REFRESH", text="").index = index

        row = layout.row()
        row.prop(props, "is_parametric")
        row = layout.row()
        row.prop(props, "is_native")
        row = layout.row()
        row.prop(props, "is_swept_solid")

        row = layout.row()
        row.operator("bim.add_swept_solid")
        for index, swept_solid in enumerate(props.swept_solids):
            row = layout.row(align=True)
            row.prop(swept_solid, "name", text="")
            row.operator("bim.remove_swept_solid", icon="X", text="").index = index
            row = layout.row()
            sub = row.row(align=True)
            sub.operator("bim.assign_swept_solid_outer_curve").index = index
            sub.operator("bim.select_swept_solid_outer_curve", icon="RESTRICT_SELECT_OFF", text="").index = index
            sub = row.row(align=True)
            sub.operator("bim.add_swept_solid_inner_curve").index = index
            sub.operator("bim.select_swept_solid_inner_curves", icon="RESTRICT_SELECT_OFF", text="").index = index
            row = layout.row(align=True)
            row.operator("bim.assign_swept_solid_extrusion").index = index
            row.operator("bim.select_swept_solid_extrusion", icon="RESTRICT_SELECT_OFF", text="").index = index
        row = layout.row()
        row.prop(props, "swept_solids")


class BIM_PT_presentation_layer_data(Panel):
    bl_label = "IFC Presentation Layers"
    bl_idname = "BIM_PT_presentation"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and hasattr(context.active_object.data, "BIMMeshProperties")
        )

    def draw(self, context):
        if not context.active_object.data:
            return
        layout = self.layout
        props = context.active_object.data.BIMMeshProperties
        scene_props = context.scene.BIMProperties

        if props.presentation_layer_index != -1:
            layer = scene_props.presentation_layers[props.presentation_layer_index]
            layout.label(text=f"Assigned to: {layer.name}")
            layout.row().operator("bim.unassign_presentation_layer")
            return

        if not scene_props.presentation_layers:
            layout.label(text=f"No presentation layers are available")
            return

        layout.template_list(
            "BIM_UL_generic",
            "",
            scene_props,
            "presentation_layers",
            scene_props,
            "active_presentation_layer_index",
        )
        if scene_props.active_presentation_layer_index < len(scene_props.presentation_layers):
            op = layout.row().operator("bim.assign_presentation_layer")
            op.index = scene_props.active_presentation_layer_index


class BIM_PT_material(Panel):
    bl_label = "IFC Materials"
    bl_idname = "BIM_PT_material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.active_material is not None

    def draw(self, context):
        if not bpy.context.active_object.active_material:
            return
        props = context.active_object.active_material.BIMMaterialProperties
        layout = self.layout
        row = layout.row()
        row.prop(props, "is_external")
        row = layout.row(align=True)
        row.prop(props, "location")
        row.operator("bim.select_external_material_dir", icon="FILE_FOLDER", text="")
        row = layout.row()
        row.prop(props, "identification")
        row = layout.row()
        row.prop(props, "name")

        row = layout.row()
        row.operator("bim.fetch_external_material")

        layout.label(text="Attributes:")
        row = layout.row(align=True)
        row.prop(props, "applicable_attributes", text="")
        row.operator("bim.add_material_attribute")

        for index, attribute in enumerate(props.attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.prop(attribute, "string_value", text="")
            row.operator("bim.remove_material_attribute", icon="X", text="").attribute_index = index

        row = layout.row()
        row.prop(props, "attributes")

        layout.label(text="Property Sets:")
        row = layout.row(align=True)
        row.prop(props, "pset_name", text="")
        row.operator("bim.add_material_pset")

        for index, pset in enumerate(props.psets):
            row = layout.row(align=True)
            row.prop(pset, "name", text="")
            row.operator("bim.remove_material_pset", icon="X", text="").pset_index = index
            for prop in pset.properties:
                row = layout.row(align=True)
                row.prop(prop, "name", text="")
                row.prop(prop, "string_value", text="")


class BIM_PT_gis(Panel):
    bl_label = "IFC Georeferencing"
    bl_idname = "BIM_PT_gis"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        layout.row().prop(scene.BIMProperties, "has_georeferencing")

        layout.label(text="Map Conversion:")
        layout.row().prop(scene.MapConversion, "eastings")
        layout.row().prop(scene.MapConversion, "northings")
        layout.row().prop(scene.MapConversion, "orthogonal_height")
        layout.row().prop(scene.MapConversion, "x_axis_abscissa")
        layout.row().prop(scene.MapConversion, "x_axis_ordinate")
        layout.row().prop(scene.MapConversion, "scale")

        layout.label(text="Target CRS:")
        layout.row().prop(scene.TargetCRS, "name")
        layout.row().prop(scene.TargetCRS, "description")
        layout.row().prop(scene.TargetCRS, "geodetic_datum")
        layout.row().prop(scene.TargetCRS, "vertical_datum")
        layout.row().prop(scene.TargetCRS, "map_projection")
        layout.row().prop(scene.TargetCRS, "map_zone")
        layout.row().prop(scene.TargetCRS, "map_unit")

        row = layout.row(align=True)
        row.operator("bim.convert_local_to_global")

        layout.row().prop(scene.BIMProperties, "eastings")
        layout.row().prop(scene.BIMProperties, "northings")
        layout.row().prop(scene.BIMProperties, "orthogonal_height")

        row = layout.row(align=True)
        row.operator("bim.convert_global_to_local")

        if hasattr(bpy.context.scene, "sun_pos_properties"):
            row = layout.row(align=True)
            row.operator("bim.get_north_offset")
            row.operator("bim.set_north_offset")


class BIM_PT_presentation_layers(Panel):
    bl_label = "IFC Presentation Layers"
    bl_idname = "BIM_PT_presentation_layer"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.scene.BIMProperties

        layout.row().operator("bim.add_presentation_layer")

        if not props.presentation_layers:
            return

        layout.template_list(
            "BIM_UL_generic", "", props, "presentation_layers", props, "active_presentation_layer_index"
        )

        if props.active_presentation_layer_index < len(props.presentation_layers):
            layer = props.presentation_layers[props.active_presentation_layer_index]

            row = layout.row(align=True)
            row.prop(layer, "name")
            row.operator(
                "bim.remove_presentation_layer", icon="X", text=""
            ).index = props.active_presentation_layer_index
            row = layout.row()
            row.prop(layer, "description")
            row = layout.row()
            row.prop(layer, "identifier")
            row = layout.row()
            row.prop(layer, "layer_on")
            row = layout.row()
            row.prop(layer, "layer_frozen")
            row = layout.row()
            row.prop(layer, "layer_blocked")

            op = layout.row().operator("bim.update_presentation_layer")
            op.index = props.active_presentation_layer_index


class BIM_PT_drawings(Panel):
    bl_label = "SVG Drawings"
    bl_idname = "BIM_PT_drawings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = bpy.context.scene.DocProperties

        row = layout.row(align=True)
        row.operator("bim.add_drawing")
        row.operator("bim.refresh_drawing_list", icon="FILE_REFRESH", text="")

        if props.drawings:
            if props.active_drawing_index < len(props.drawings):
                op = row.operator("bim.open_view", icon="URL", text="")
                op.view = props.drawings[props.active_drawing_index].name
                row.operator("bim.remove_drawing", icon="X", text="").index = props.active_drawing_index
            layout.template_list("BIM_UL_generic", "", props, "drawings", props, "active_drawing_index")

        row = layout.row()
        row.operator("bim.add_ifc_file")

        for index, ifc_file in enumerate(props.ifc_files):
            row = layout.row(align=True)
            row.prop(ifc_file, "name", text="IFC #{}".format(index + 1))
            row.operator("bim.select_doc_ifc_file", icon="FILE_FOLDER", text="").index = index
            row.operator("bim.remove_ifc_file", icon="X", text="").index = index


class BIM_PT_schedules(Panel):
    bl_label = "ODS Schedules"
    bl_idname = "BIM_PT_schedules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = bpy.context.scene.DocProperties

        row = layout.row(align=True)
        row.operator("bim.add_schedule")

        if props.schedules:
            row.operator("bim.build_schedule", icon="LINENUMBERS_ON", text="")
            row.operator("bim.remove_schedule", icon="X", text="").index = props.active_schedule_index

            layout.template_list("BIM_UL_generic", "", props, "schedules", props, "active_schedule_index")

            row = layout.row()
            row.prop(props.schedules[props.active_schedule_index], "file")
            row.operator("bim.select_schedule_file", icon="FILE_FOLDER", text="")


class BIM_PT_sheets(Panel):
    bl_label = "SVG Sheets"
    bl_idname = "BIM_PT_sheets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        props = bpy.context.scene.DocProperties

        row = layout.row(align=True)
        row.prop(props, "titleblock", text="")
        row.operator("bim.add_sheet")

        if props.sheets:
            row.operator("bim.open_sheet", icon="URL", text="")
            row.operator("bim.remove_sheet", icon="X", text="").index = props.active_sheet_index

            layout.template_list("BIM_UL_generic", "", props, "sheets", props, "active_sheet_index")

        row = layout.row(align=True)
        row.operator("bim.add_drawing_to_sheet")
        row.operator("bim.add_schedule_to_sheet")
        row = layout.row()
        row.operator("bim.create_sheets")


class BIM_PT_section_plane(Panel):
    bl_label = "Temporary Section Cutaways"
    bl_idname = "BIM_PT_section_plane"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = bpy.context.scene.BIMProperties

        row = layout.row()
        row.prop(props, "should_section_selected_objects")

        row = layout.row()
        row.prop(props, "section_plane_colour")

        row = layout.row(align=True)
        row.operator("bim.add_section_plane")
        row.operator("bim.remove_section_plane")


class BIM_PT_camera(Panel):
    bl_label = "Drawing Generation"
    bl_idname = "BIM_PT_camera"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        engine = context.engine
        return context.camera and hasattr(context.active_object.data, "BIMCameraProperties")

    def draw(self, context):
        layout = self.layout

        if "/" not in context.active_object.name:
            layout.label(text="This is not a BIM camera.")
            return

        layout.use_property_split = True
        dprops = bpy.context.scene.DocProperties
        props = context.active_object.data.BIMCameraProperties

        layout.label(text="Generation Options:")

        row = layout.row()
        row.prop(dprops, "should_recut")
        row = layout.row()
        row.prop(dprops, "should_recut_selected")
        row = layout.row()
        row.prop(dprops, "should_extract")

        row = layout.row()
        row.prop(props, "is_nts")

        row = layout.row()
        row.operator("bim.generate_references")
        row = layout.row()
        row.operator("bim.resize_text")

        row = layout.row()
        row.prop(props, "target_view")

        row = layout.row()
        row.prop(props, "cut_objects")
        if props.cut_objects == "CUSTOM":
            row = layout.row()
            row.prop(props, "cut_objects_custom")

        row = layout.row()
        row.prop(props, "raster_x")
        row = layout.row()
        row.prop(props, "raster_y")

        row = layout.row()
        row.prop(props, "diagram_scale")
        if props.diagram_scale == "CUSTOM":
            row = layout.row()
            row.prop(props, "custom_diagram_scale")

        layout.label(text="Drawing Styles:")

        row = layout.row(align=True)
        row.operator("bim.add_drawing_style")

        if dprops.drawing_styles:
            layout.template_list("BIM_UL_generic", "", dprops, "drawing_styles", props, "active_drawing_style_index")

            if props.active_drawing_style_index < len(dprops.drawing_styles):
                drawing_style = dprops.drawing_styles[props.active_drawing_style_index]

                row = layout.row(align=True)
                row.prop(drawing_style, "name")
                row.operator("bim.remove_drawing_style", icon="X", text="").index = props.active_drawing_style_index

                row = layout.row()
                row.prop(drawing_style, "render_type")
                row = layout.row(align=True)
                row.prop(drawing_style, "vector_style")
                row.operator("bim.edit_vector_style", text="", icon="GREASEPENCIL")
                row = layout.row(align=True)
                row.prop(drawing_style, "include_query")
                row = layout.row(align=True)
                row.prop(drawing_style, "exclude_query")

                row = layout.row()
                row.operator("bim.add_drawing_style_attribute")

                for index, attribute in enumerate(drawing_style.attributes):
                    row = layout.row(align=True)
                    row.prop(attribute, "name", text="")
                    row.operator("bim.remove_drawing_style_attribute", icon="X", text="").index = index

                row = layout.row(align=True)
                row.operator("bim.save_drawing_style")
                row.operator("bim.activate_drawing_style")

        row = layout.row(align=True)
        row.operator("bim.cut_section", text="Create Drawing")
        op = row.operator("bim.open_view", icon="URL", text="")
        op.view = context.active_object.name.split("/")[1]


class BIM_PT_text(Panel):
    bl_label = "Text Paper Space"
    bl_idname = "BIM_PT_text"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return type(context.curve) is bpy.types.TextCurve

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.active_object.data.BIMTextProperties

        row = layout.row()
        row.operator("bim.propagate_text_data")

        row = layout.row()
        row.prop(props, "font_size")
        row = layout.row()
        row.prop(props, "symbol")
        row = layout.row()
        row.prop(props, "related_element")

        row = layout.row()
        row.operator("bim.add_variable")

        for index, variable in enumerate(props.variables):
            row = layout.row(align=True)
            row.prop(variable, "name")
            row.operator("bim.remove_variable", icon="X", text="").index = index
            row = layout.row()
            row.prop(variable, "prop_key")


class BIM_PT_owner(Panel):
    bl_label = "IFC Owner History"
    bl_idname = "BIM_PT_owner"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.BIMProperties

        if not props.person:
            layout.label(text="No people found.")
        else:
            row = layout.row()
            row.prop(props, "person")

        if not props.organisation:
            layout.label(text="No organisations found.")
        else:
            row = layout.row()
            row.prop(props, "organisation")


class BIM_PT_people(Panel):
    bl_label = "IFC People"
    bl_idname = "BIM_PT_people"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        props = context.scene.BIMProperties

        row = layout.row()
        row.operator("bim.add_person")

        if props.people:
            layout.template_list("BIM_UL_generic", "", props, "people", props, "active_person_index")

            if props.active_person_index < len(props.people):
                person = props.people[props.active_person_index]
                row = layout.row()
                row.prop(person, "name")
                row.operator("bim.remove_person", icon="X", text="").index = props.active_person_index
                row = layout.row()
                row.prop(person, "family_name")
                row = layout.row()
                row.prop(person, "given_name")
                row = layout.row()
                row.prop(person, "middle_names")
                row = layout.row()
                row.prop(person, "prefix_titles")
                row = layout.row()
                row.prop(person, "suffix_titles")
                layout.label(text="Roles:")
                draw_roles_ui(layout, person, "person")
                layout.label(text="Addresses:")
                draw_addresses_ui(layout, person, "person")


class BIM_PT_organisations(Panel):
    bl_label = "IFC Organisations"
    bl_idname = "BIM_PT_organisations"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        props = context.scene.BIMProperties

        row = layout.row()
        row.operator("bim.add_organisation")

        if props.organisations:
            layout.template_list("BIM_UL_generic", "", props, "organisations", props, "active_organisation_index")

            if props.active_organisation_index < len(props.organisations):
                organisation = props.organisations[props.active_organisation_index]
                row = layout.row()
                row.prop(organisation, "name")
                row.operator("bim.remove_organisation", icon="X", text="").index = props.active_organisation_index
                row = layout.row()
                row.prop(organisation, "description")
                layout.label(text="Roles:")
                draw_roles_ui(layout, organisation, "organisation")
                layout.label(text="Addresses:")
                draw_addresses_ui(layout, organisation, "organisation")


def draw_roles_ui(layout, parent, parent_type):
    row = layout.row()
    row.operator(f"bim.add_{parent_type}_role")

    if parent.roles:
        layout.template_list("BIM_UL_generic", "", parent, "roles", parent, "active_role_index")

        if parent.active_role_index < len(parent.roles):
            role = parent.roles[parent.active_role_index]
            row = layout.row()
            row.prop(role, "name")
            row.operator(f"bim.remove_{parent_type}_role", icon="X", text="").index = parent.active_role_index
            if role.name == "USERDEFINED":
                row = layout.row()
                row.prop(role, "user_defined_role")
            row = layout.row()
            row.prop(role, "description")


def draw_addresses_ui(layout, parent, parent_type):
    row = layout.row()
    row.operator(f"bim.add_{parent_type}_address")

    if parent.addresses:
        layout.template_list("BIM_UL_generic", "", parent, "addresses", parent, "active_address_index")

        if parent.active_address_index < len(parent.addresses):
            address = parent.addresses[parent.active_address_index]
            row = layout.row()
            row.prop(address, "name")
            row.operator(f"bim.remove_{parent_type}_address", icon="X", text="").index = parent.active_address_index
            row = layout.row()
            row.prop(address, "purpose")
            if address.purpose == "USERDEFINED":
                row = layout.row()
                row.prop(address, "user_defined_purpose")
            row = layout.row()
            row.prop(address, "description")

            if "IfcPostalAddress" in address.name:
                row = layout.row()
                row.prop(address, "internal_location")
                row = layout.row()
                row.prop(address, "address_lines")
                row = layout.row()
                row.prop(address, "postal_box")
                row = layout.row()
                row.prop(address, "town")
                row = layout.row()
                row.prop(address, "region")
                row = layout.row()
                row.prop(address, "postal_code")
                row = layout.row()
                row.prop(address, "country")
            elif "IfcTelecomAddress" in address.name:
                row = layout.row()
                row.prop(address, "telephone_numbers")
                row = layout.row()
                row.prop(address, "fascimile_numbers")
                row = layout.row()
                row.prop(address, "pager_number")
                row = layout.row()
                row.prop(address, "electronic_mail_addresses")
                row = layout.row()
                row.prop(address, "www_home_page_url")
                row = layout.row()
                row.prop(address, "messaging_ids")


class BIM_PT_context(Panel):
    bl_label = "IFC Geometric Representation Contexts"
    bl_idname = "BIM_PT_context"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        props = scene.BIMProperties

        for context in ["model", "plan"]:
            row = layout.row(align=True)
            row.prop(props, f"has_{context}_context")

            if not getattr(props, f"has_{context}_context"):
                continue

            layout.label(text="Geometric Representation Subcontexts:")
            row = layout.row(align=True)
            row.prop(props, "available_subcontexts", text="")
            row.prop(props, "available_target_views", text="")
            row.operator("bim.add_subcontext", icon="ADD", text="").context = context

            for subcontext_index, subcontext in enumerate(getattr(props, "{}_subcontexts".format(context))):
                row = layout.row(align=True)
                row.prop(subcontext, "name", text="")
                row.prop(subcontext, "target_view", text="")
                row.operator("bim.remove_subcontext", icon="X", text="").indexes = "{}-{}".format(
                    context, subcontext_index
                )


class BIM_PT_bim(Panel):
    bl_label = "Building Information Modeling"
    bl_idname = "BIM_PT_bim"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bim_properties = scene.BIMProperties

        layout.label(text="System Setup:")

        row = layout.row()
        row.operator("bim.quick_project_setup")

        row = layout.row(align=True)
        row.prop(bim_properties, "schema_dir")
        row.operator("bim.select_schema_dir", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "data_dir")
        row.operator("bim.select_data_dir", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "ifc_file")
        row.operator("bim.reload_ifc_file", icon="FILE_REFRESH", text="")
        row.operator("bim.validate_ifc_file", icon="CHECKMARK", text="")
        row.operator("bim.select_ifc_file", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "ifc_cache")

        layout.label(text="IFC Categorisation:")

        row = layout.row()
        row.prop(bim_properties, "ifc_product")
        row = layout.row()
        row.prop(bim_properties, "ifc_class")
        if bim_properties.ifc_predefined_type:
            row = layout.row()
            row.prop(bim_properties, "ifc_predefined_type")
        if bim_properties.ifc_predefined_type == "USERDEFINED":
            row = layout.row()
            row.prop(bim_properties, "ifc_userdefined_type")
        row = layout.row(align=True)
        op = row.operator("bim.assign_class")
        op.object_name = ""
        op = row.operator("bim.unassign_class", icon="X", text="")
        op.object_name = ""

        row = layout.row(align=True)
        row.operator("bim.select_class")
        row.operator("bim.select_type")

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


class BIM_PT_search(Panel):
    bl_label = "IFC Search"
    bl_idname = "BIM_PT_search"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        props = scene.BIMProperties

        row = layout.row()
        row.prop(props, "search_regex")
        row = layout.row()
        row.prop(props, "search_ignorecase")

        layout.label(text="Global ID:")
        row = layout.row(align=True)
        row.prop(props, "global_id", text="")
        row.operator("bim.select_global_id", text="", icon="VIEWZOOM")

        layout.label(text="Attribute:")
        row = layout.row(align=True)
        row.prop(props, "search_attribute_name", text="")
        row.prop(props, "search_attribute_value", text="")
        row.operator("bim.select_attribute", text="", icon="VIEWZOOM")
        row.operator("bim.colour_by_attribute", text="", icon="BRUSH_DATA")

        layout.label(text="Pset:")
        row = layout.row(align=True)
        row.prop(props, "search_pset_name", text="")
        row.prop(props, "search_prop_name", text="")
        row.prop(props, "search_pset_value", text="")
        row.operator("bim.select_pset", text="", icon="VIEWZOOM")
        row.operator("bim.colour_by_pset", text="", icon="BRUSH_DATA")


class BIM_PT_ifccsv(Panel):
    bl_label = "IFC CSV Import/Export"
    bl_idname = "BIM_PT_ifccsv"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        props = scene.BIMProperties

        row = layout.row(align=True)
        row.prop(props, "ifc_selector")
        row.operator("bim.eyedrop_ifccsv", icon="EYEDROPPER", text="")

        row = layout.row()
        row.operator("bim.add_csv_attribute")

        for index, attribute in enumerate(props.csv_attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.operator("bim.remove_csv_attribute", icon="X", text="").index = index

        row = layout.row(align=True)
        row.operator("bim.export_ifccsv", icon="EXPORT")
        row.operator("bim.import_ifccsv", icon="IMPORT")


class BIM_PT_bcf(Panel):
    bl_label = "BIM Collaboration Format (BCF)"
    bl_idname = "BIM_PT_bcf"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
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
        layout.template_list("BIM_UL_topics", "", props, "topics", props, "active_topic_index")

        row = layout.row()
        row.prop(props, "topic_description", text="")

        row = layout.row()
        row.prop(props, "viewpoints")
        row.operator("bim.activate_bcf_viewpoint", icon="SCENE", text="")

        row = layout.row()
        row.prop(props, "topic_type", text="Type")
        row = layout.row()
        row.prop(props, "topic_status", text="Status")
        row = layout.row()
        row.prop(props, "topic_priority", text="Priority")
        row = layout.row()
        row.prop(props, "topic_stage", text="Stage")
        row = layout.row()
        row.prop(props, "topic_creation_date", text="Date")
        row = layout.row()
        row.prop(props, "topic_creation_author", text="Author")
        row = layout.row()
        row.prop(props, "topic_modified_date", text="Modified On")
        row = layout.row()
        row.prop(props, "topic_modified_author", text="Modified By")
        row = layout.row()
        row.prop(props, "topic_assigned_to", text="Assigned To")
        row = layout.row()
        row.prop(props, "topic_due_date", text="Due Date")

        layout.label(text="Header Files:")
        for index, f in enumerate(props.topic_files):
            row = layout.row()
            row.prop(f, "name", text="File {} Name".format(index + 1))
            row = layout.row()
            row.prop(f, "reference", text="File {} URI".format(index + 1))
            if f.is_external:
                row.operator("bim.open_bcf_file_reference", icon="URL", text="").data = index
            else:
                row.operator("bim.open_bcf_file_reference", icon="FILE_FOLDER", text="").data = "{}/{}".format(
                    props.topic_guid, index
                )
            row = layout.row()
            row.prop(f, "date", text="File {} Date".format(index + 1))
            row = layout.row()
            row.prop(f, "ifc_project", text="File {} Project".format(index + 1))
            row = layout.row()
            row.prop(f, "ifc_spatial", text="File {} Spatial".format(index + 1))

        layout.label(text="Reference Links:")
        for index, label in enumerate(props.topic_links):
            row = layout.row()
            row.prop(label, "name", text="Link {}".format(index + 1))
            row.operator("bim.open_bcf_reference_link", icon="URL", text="").index = index

        layout.label(text="Labels:")
        for index, label in enumerate(props.topic_labels):
            row = layout.row(align=True)
            row.prop(label, "name", text="")

        layout.label(text="BIM Snippet:")
        if props.topic_has_snippet:
            row = layout.row(align=True)
            row.prop(props, "topic_snippet_type")
            if props.topic_snippet_schema:
                row.operator("bim.open_bcf_bim_snippet_schema", icon="URL", text="")

            row = layout.row(align=True)
            row.prop(props, "topic_snippet_reference")
            if props.topic_snippet_is_external:
                row.operator("bim.open_bcf_bim_snippet_reference", icon="URL", text="")
            else:
                row.operator(
                    "bim.open_bcf_bim_snippet_reference", icon="FILE_FOLDER", text=""
                ).topic_guid = props.topic_guid

        layout.label(text="Document References:")
        for index, doc in enumerate(props.topic_document_references):
            row = layout.row(align=True)
            row.prop(doc, "name", text=f"File {index+1} URI")
            if doc.is_external:
                row.operator("bim.open_bcf_document_reference", icon="URL", text="").data = "{}/{}".format(
                    props.topic_guid, index
                )
            else:
                row.operator("bim.open_bcf_document_reference", icon="FILE_FOLDER", text="").data = "{}/{}".format(
                    props.topic_guid, index
                )
            row = layout.row(align=True)
            row.prop(doc, "description", text=f"File {index+1} Description:")

        layout.label(text="Related Topics:")
        for topic in props.topic_related_topics:
            row = layout.row(align=True)
            row.operator("bim.view_bcf_topic", text=topic.name).topic_guid = topic.guid


class BIM_PT_qa(Panel):
    bl_label = "BIMTester Quality Auditing"
    bl_idname = "BIM_PT_qa"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
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
        else:
            return

        row = layout.row()
        row.operator("bim.execute_bim_tester")

        row = layout.row()
        row.operator("bim.bim_tester_purge")

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
    bl_label = "IFC BIM Server Library"
    bl_idname = "BIM_PT_library"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bim_properties = scene.BIMProperties

        layout.row().prop(scene.BIMProperties, "has_library")

        layout.label(text="Project Library:")
        layout.row().prop(scene.BIMLibrary, "location")
        layout.row().operator("bim.fetch_library_information")
        layout.row().prop(scene.BIMLibrary, "name")
        layout.row().prop(scene.BIMLibrary, "version")
        layout.row().prop(scene.BIMLibrary, "version_date")
        layout.row().prop(scene.BIMLibrary, "description")


class BIM_PT_diff(Panel):
    bl_label = "IFC Diff"
    bl_idname = "BIM_PT_diff"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
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
        row.operator("bim.visualise_diff", icon="HIDE_OFF", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "diff_old_file")
        row.operator("bim.select_diff_old_file", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "diff_new_file")
        row.operator("bim.select_diff_new_file", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "diff_relationships")

        row = layout.row()
        row.operator("bim.execute_ifc_diff")


class BIM_PT_cobie(Panel):
    bl_label = "IFC COBie"
    bl_idname = "BIM_PT_cobie"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.BIMProperties

        row = layout.row(align=True)
        row.prop(props, "cobie_ifc_file")
        row.operator("bim.select_cobie_ifc_file", icon="FILE_FOLDER", text="")

        row = layout.row()
        row.prop(props, "cobie_types")
        row = layout.row()
        row.prop(props, "cobie_components")

        row = layout.row(align=True)
        row.prop(props, "cobie_json_file")
        row.operator("bim.select_cobie_json_file", icon="FILE_FOLDER", text="")

        row = layout.row()
        op = row.operator("bim.execute_ifc_cobie", text="CSV")
        op.file_format = "csv"
        op = row.operator("bim.execute_ifc_cobie", text="ODS")
        op.file_format = "ods"
        op = row.operator("bim.execute_ifc_cobie", text="XLSX")
        op.file_format = "xlsx"


class BIM_PT_patch(Panel):
    bl_label = "IFC Patch"
    bl_idname = "BIM_PT_patch"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.BIMProperties

        row = layout.row()
        row.prop(props, "ifc_patch_recipes")
        row = layout.row(align=True)
        row.prop(props, "ifc_patch_input")
        row.operator("bim.select_ifc_patch_input", icon="FILE_FOLDER", text="")
        row = layout.row(align=True)
        row.prop(props, "ifc_patch_output")
        row.operator("bim.select_ifc_patch_output", icon="FILE_FOLDER", text="")
        row = layout.row()
        row.prop(props, "ifc_patch_args")

        row = layout.row()
        op = row.operator("bim.execute_ifc_patch")


class BIM_PT_mvd(Panel):
    bl_label = "Model View Definitions (MVD)"
    bl_idname = "BIM_PT_mvd"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        bim_properties = scene.BIMProperties

        row = layout.row()
        row.prop(bim_properties, "export_schema")
        row = layout.row()
        row.prop(bim_properties, "export_json_version")

        row = layout.row()
        row.prop(bim_properties, "ifc_import_filter")
        row = layout.row()
        row.prop(bim_properties, "ifc_selector")

        layout.label(text="Custom MVD:")

        row = layout.row()
        row.prop(bim_properties, "export_has_representations")
        row = layout.row()
        row.prop(bim_properties, "export_should_guess_quantities")
        row = layout.row()
        row.prop(bim_properties, "export_should_force_faceted_brep")
        row = layout.row()
        row.prop(bim_properties, "import_should_import_type_representations")
        row = layout.row()
        row.prop(bim_properties, "import_should_import_curves")
        row = layout.row()
        row.prop(bim_properties, "import_should_import_opening_elements")
        row = layout.row()
        row.prop(bim_properties, "import_should_import_spaces")

        layout.label(text="Experimental Modes:")

        row = layout.row()
        row.prop(bim_properties, "import_should_use_legacy")
        row = layout.row()
        row.prop(bim_properties, "import_should_import_native")
        row = layout.row()
        row.prop(bim_properties, "import_export_should_roundtrip_native")
        row = layout.row()
        row.prop(bim_properties, "import_should_use_cpu_multiprocessing")
        row = layout.row()
        row.prop(bim_properties, "import_should_import_with_profiling")
        row = layout.row()
        row.prop(bim_properties, "import_deflection_tolerance")
        row = layout.row()
        row.prop(bim_properties, "import_angular_tolerance")
        row = layout.row()
        row.prop(bim_properties, "export_json_compact")

        layout.label(text="Simplifications:")

        row = layout.row()
        row.prop(bim_properties, "import_should_import_aggregates")
        row = layout.row()
        row.prop(bim_properties, "import_should_merge_aggregates")
        row = layout.row()
        row.prop(bim_properties, "import_should_merge_by_class")
        row = layout.row()
        row.prop(bim_properties, "import_should_merge_by_material")
        row = layout.row()
        row.prop(bim_properties, "import_should_merge_materials_by_colour")
        row = layout.row()
        row.prop(bim_properties, "import_should_clean_mesh")

        layout.label(text="Vendor Workarounds:")

        row = layout.row()
        row.prop(bim_properties, "import_should_auto_set_workarounds")

        layout.label(text="RIB iTWO Workarounds:")

        row = layout.row()
        row.prop(bim_properties, "export_should_force_faceted_brep")

        layout.label(text="DESITE BIM Workarounds:")

        row = layout.row()
        row.prop(bim_properties, "export_should_force_faceted_brep")

        layout.label(text="Navisworks Workarounds:")

        row = layout.row()
        row.prop(bim_properties, "export_should_force_triangulation")

        layout.label(text="Tekla Workarounds:")

        row = layout.row()
        row.prop(bim_properties, "import_should_ignore_site_coordinates")

        layout.label(text="ProStructures Workarounds:")

        row = layout.row()
        row.prop(bim_properties, "import_should_allow_non_element_aggregates")
        row = layout.row()
        row.prop(bim_properties, "import_should_offset_model")
        row = layout.row()
        row.prop(bim_properties, "import_model_offset_coordinates")

        layout.label(text="12D Workarounds:")

        row = layout.row()
        row.prop(bim_properties, "import_should_reset_absolute_coordinates")

        layout.label(text="Civil 3D Workarounds:")

        row = layout.row()
        row.prop(bim_properties, "import_should_reset_absolute_coordinates")

        layout.label(text="Revit Workarounds:")

        row = layout.row()
        row.prop(bim_properties, "export_should_use_presentation_style_assignment")
        row = layout.row()
        row.prop(bim_properties, "import_should_guess_georeferencing")
        row = layout.row()
        row.prop(bim_properties, "import_should_ignore_site_coordinates")
        row = layout.row()
        row.prop(bim_properties, "import_should_ignore_building_coordinates")


class BIM_UL_generic(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.prop(item, "name", text="", emboss=False)
        else:
            layout.label(text="", translate=False)


class BIM_UL_topics(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.prop(item, "name", text="", emboss=False)
        else:
            layout.label(text="", translate=False)


class BIM_UL_clash_sets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.prop(item, "name", text="", emboss=False)
        else:
            layout.label(text="", translate=False)

class BIM_UL_smart_groups(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.label(text=str(item.number), translate=False, icon='NONE', icon_value=0)
        else:
            layout.label(text="", translate=False)

class BIM_UL_constraints(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.prop(item, "name", text="", emboss=False)
        else:
            layout.label(text="", translate=False)


class BIM_UL_document_information(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.prop(item, "name", text="", emboss=False)
        else:
            layout.label(text="", translate=False)


class BIM_UL_document_references(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.prop(item, "name", text="", emboss=False)
        else:
            layout.label(text="", translate=False)


class BIM_UL_classifications(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            rt = data.root
            ch = rt["children"]
            itemdata = ch[item.name]
            if itemdata.get("children", {}):
                op = layout.operator(
                    "bim.change_classification_level", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT"
                )
                op.path_sid = "%r" % active_data.id_data  # get id-data
                op.path_lst = active_data.path_from_id()  # path to view
                op.path_itm = item.name  # name of child. empty = go up
            else:
                layout.label(text="", icon="BLANK1")
            layout.prop(item, "name", text="", emboss=False)
            layout.label(text=itemdata["name"])


class BIM_ADDON_preferences(bpy.types.AddonPreferences):
    bl_idname = "blenderbim"
    svg2pdf_command: StringProperty(name="SVG to PDF Command", description="E.g. [['inkscape', svg, '-o', pdf]]")
    svg2dxf_command: StringProperty(
        name="SVG to DXF Command",
        description="E.g. [['inkscape', svg, '-o', eps], ['pstoedit', '-dt', '-f', 'dxf:-polyaslines -mm', eps, dxf, '-psarg', '-dNOSAFER']]",
    )
    svg_command: StringProperty(name="SVG Command", description="E.g. [['firefox-bin', path]]")
    pdf_command: StringProperty(name="PDF Command", description="E.g. [['firefox-bin', path]]")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("bim.open_upstream", text="Visit Homepage").page = "home"
        row.operator("bim.open_upstream", text="Visit Documentation").page = "docs"
        row = layout.row()
        row.operator("bim.open_upstream", text="Visit Wiki").page = "wiki"
        row.operator("bim.open_upstream", text="Visit Community").page = "community"
        row = layout.row()
        row.prop(self, "svg2pdf_command")
        row = layout.row()
        row.prop(self, "svg2dxf_command")
        row = layout.row()
        row.prop(self, "svg_command")
        row = layout.row()
        row.prop(self, "pdf_command")


class BIM_PT_ifcclash(Panel):
    bl_label = "IFC Clash Sets"
    bl_idname = "BIM_PT_ifcclash"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        props = scene.BIMProperties

        layout.label(text="Blender Clash:")

        row = layout.row(align=True)
        row.operator("bim.set_blender_clash_set_a")
        row.operator("bim.set_blender_clash_set_b")

        row = layout.row(align=True)
        row.operator("bim.execute_blender_clash")

        layout.label(text="IFC Clash:")

        row = layout.row(align=True)
        row.operator("bim.add_clash_set")
        row.operator("bim.import_clash_sets", text="", icon="IMPORT")
        row.operator("bim.export_clash_sets", text="", icon="EXPORT")

        if not props.clash_sets:
            return

        layout.template_list("BIM_UL_clash_sets", "", props, "clash_sets", props, "active_clash_set_index")

        if props.active_clash_set_index < len(props.clash_sets):
            clash_set = props.clash_sets[props.active_clash_set_index]

            row = layout.row(align=True)
            row.prop(clash_set, "name")
            row.operator("bim.remove_clash_set", icon="X", text="").index = props.active_clash_set_index

            row = layout.row(align=True)
            row.prop(clash_set, "tolerance")

            layout.label(text="Group A:")
            row = layout.row()
            row.operator("bim.add_clash_source").group = "a"

            for index, source in enumerate(clash_set.a):
                row = layout.row(align=True)
                row.prop(source, "name", text="")
                op = row.operator("bim.select_clash_source", icon="FILE_FOLDER", text="")
                op.index = index
                op.group = "a"
                op = row.operator("bim.remove_clash_source", icon="X", text="")
                op.index = index
                op.group = "a"

                row = layout.row(align=True)
                row.prop(source, "mode", text="")
                row.prop(source, "selector", text="")

            layout.label(text="Group B:")
            row = layout.row()
            row.operator("bim.add_clash_source").group = "b"

            for index, source in enumerate(clash_set.b):
                row = layout.row(align=True)
                row.prop(source, "name", text="")
                op = row.operator("bim.select_clash_source", icon="FILE_FOLDER", text="")
                op.index = index
                op.group = "b"
                op = row.operator("bim.remove_clash_source", icon="X", text="")
                op.index = index
                op.group = "b"

                row = layout.row(align=True)
                row.prop(source, "mode", text="")
                row.prop(source, "selector", text="")

            row = layout.row()
            row.operator("bim.execute_ifc_clash")

            row = layout.row()
            row.operator("bim.select_ifc_clash_results")


class BIM_PT_modeling_utilities(Panel):
    bl_idname = "BIM_PT_modeling_utilities"
    bl_label = "Architectural"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("bim.add_opening")


class BIM_PT_annotation_utilities(Panel):
    bl_idname = "BIM_PT_annotation_utilities"
    bl_label = "Annotation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("bim.clean_wireframes")
        row = layout.row(align=True)
        row.operator("bim.link_ifc")

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Dim", icon="ARROW_LEFTRIGHT")
        op.obj_name = "Dimension"
        op.data_type = "curve"
        op = row.operator("bim.add_annotation", text="Dim (Eq)", icon="ARROW_LEFTRIGHT")
        op.obj_name = "Equal"
        op.data_type = "curve"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Text", icon="SMALL_CAPS")
        op.data_type = "text"
        op = row.operator("bim.add_annotation", text="Leader", icon="TRACKING_BACKWARDS")
        op.obj_name = "Leader"
        op.data_type = "curve"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Stair Arrow", icon="SCREEN_BACK")
        op.obj_name = "Stair"
        op.data_type = "curve"
        op = row.operator("bim.add_annotation", text="Hidden", icon="CON_TRACKTO")
        op.obj_name = "Hidden"
        op.data_type = "mesh"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Level (Plan)", icon="SORTBYEXT")
        op.obj_name = "Plan Level"
        op.data_type = "curve"
        op = row.operator("bim.add_annotation", text="Level (Section)", icon="TRIA_DOWN")
        op.obj_name = "Section Level"
        op.data_type = "curve"

        props = bpy.context.scene.DocProperties

        row = layout.row(align=True)
        row.operator("bim.add_drawing")
        row.operator("bim.refresh_drawing_list", icon="FILE_REFRESH", text="")

        if props.drawings:
            if props.active_drawing_index < len(props.drawings):
                op = row.operator("bim.open_view", icon="URL", text="")
                op.view = props.drawings[props.active_drawing_index].name
                row.operator("bim.remove_drawing", icon="X", text="").index = props.active_drawing_index
            layout.template_list("BIM_UL_generic", "", props, "drawings", props, "active_drawing_index")

        row = layout.row()
        row.prop(props, "should_draw_decorations")


class BIM_PT_qto_utilities(Panel):
    bl_idname = "BIM_PT_qto_utilities"
    bl_label = "Quantity Take-off"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMProperties

        row = layout.row()
        layout.label(text="Results:")
        row = layout.row()
        row.prop(props, "qto_result", text="")

        row = layout.row(align=True)
        row.operator("bim.calculate_edge_lengths")
        row = layout.row(align=True)
        row.operator("bim.calculate_face_areas")
        row = layout.row(align=True)
        row.operator("bim.calculate_object_volumes")

class BIM_PT_clash_manager(Panel):
    bl_idname = "BIM_PT_clash_manager"
    bl_label = "Clash Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMProperties

        row = layout.row()
        layout.label(text="Select clash results to group:")

        row = layout.row(align=True)
        row.prop(props, "clash_results_path", text="")
        op = row.operator("bim.select_clash_results", icon="FILE_FOLDER", text="")

        row = layout.row()
        layout.label(text="Select output path for smart-grouped clashes:")

        row = layout.row(align=True)
        row.prop(props, "smart_grouped_clashes_path", text="")
        op = row.operator("bim.select_smart_grouped_clashes_path", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(props, "smart_clash_grouping_max_distance")

        row = layout.row(align=True)
        row.operator("bim.smart_clash_group")

        row = layout.row(align=True)
        row.operator("bim.load_smart_groups_for_active_clash_set")

        layout.template_list('BIM_UL_smart_groups', '', props, 'smart_clash_groups', props, 'active_smart_group_index')

        row = layout.row(align=True)
        row.operator("bim.select_smart_group")

class BIM_PT_misc_utilities(Panel):
    bl_idname = "BIM_PT_misc_utilities"
    bl_label = "Miscellaneous"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMProperties

        row = layout.row()
        row.prop(props, "override_colour", text="")
        row = layout.row(align=True)
        row.operator("bim.set_override_colour")
        row = layout.row(align=True)
        row.operator("bim.set_viewport_shadow_from_sun")


class BIM_PT_debug(Panel):
    bl_label = "IFC Debug"
    bl_idname = "BIM_PT_debug"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        props = scene.BIMDebugProperties

        row = layout.row()
        row.prop(props, "step_id", text="")
        row = layout.row()
        row.operator("bim.create_shape_from_step_id")

        row = layout.row()
        row.prop(props, "number_of_polygons", text="")
        row = layout.row()
        row.operator("bim.select_high_polygon_meshes")

        layout.label(text="Inspector:")

        row = layout.row(align=True)
        if len(props.step_id_breadcrumb) >= 2:
            row.operator("bim.rewind_inspector", icon="FRAME_PREV", text="")
        row.prop(props, "active_step_id", text="")
        row = layout.row(align=True)
        row.operator("bim.inspect_from_step_id").step_id = bpy.context.scene.BIMDebugProperties.active_step_id
        row.operator("bim.inspect_from_object")

        if props.attributes:
            layout.label(text="Direct attributes:")

        for index, attribute in enumerate(props.attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.prop(attribute, "string_value", text="")
            if attribute.int_value:
                row.operator(
                    "bim.inspect_from_step_id", icon="DISCLOSURE_TRI_RIGHT", text=""
                ).step_id = attribute.int_value

        if props.inverse_attributes:
            layout.label(text="Inverse attributes:")

        for index, attribute in enumerate(props.inverse_attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.prop(attribute, "string_value", text="")
            if attribute.int_value:
                row.operator(
                    "bim.inspect_from_step_id", icon="DISCLOSURE_TRI_RIGHT", text=""
                ).step_id = attribute.int_value


def ifc_units(self, context):
    scene = context.scene
    props = context.scene.BIMProperties
    layout = self.layout
    layout.use_property_decorate = False
    layout.use_property_split = True
    row = layout.row()
    row.prop(props, "area_unit")
    row = layout.row()
    row.prop(props, "volume_unit")
    row = layout.row()
    if bpy.context.scene.unit_settings.system == "IMPERIAL":
        row.prop(props, "imperial_precision")
    else:
        row.prop(props, "metric_precision")
