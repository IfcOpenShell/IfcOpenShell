class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        # TINs exported from 12D may contain dense or highly obtuse triangles.
        # Although these will load in Revit, you will not be able to use Revit's
        # Spot Coordinate or Spot Elevation tool.
        #
        # See bug: https://github.com/Autodesk/revit-ifc/issues/511
        #
        # The solution will merge vertices closer than 10mm to prevent dense
        # portions of the TIN at a minor sacrifice of surveying accuracy. It
        # will also triangulate all meshes to prevent non-coplanar surfaces, and
        # delete any obtuse triangles where one of their XY angles is less than
        # 0.3 degrees. Therefore the result will contain some minor "holes" in
        # the TIN, but these holes will only be in dense triangles that Revit
        # can't handle anyway and won't affect most coordination tasks.
        #
        # This patch is designed to only work on 12D IFC exports. It also
        # requires you to run it using Blender, as the geometric modification
        # uses the Blender geometry engine.
        import bpy
        import bmesh
        import blenderbim.tool as tool
        from math import degrees

        bpy.ops.bim.load_project(filepath=self.src)

        old_history_size = tool.Ifc.get().history_size
        old_undo_steps = bpy.context.preferences.edit.undo_steps
        tool.Ifc.get().history_size = 0
        bpy.context.preferences.edit.undo_steps = 0

        angle_threshold = 0.3

        for obj in bpy.data.objects:
            if not obj.BIMObjectProperties.ifc_definition_id or not obj.data:
                continue
            data = obj.data
            bm = bmesh.new()
            bm.from_mesh(data)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
            bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
            bm.faces.ensure_lookup_table()
            for polygon in bm.faces:
                v1, v2, v3 = [v.co.to_2d() for v in polygon.verts]
                d1 = degrees((v2 - v1).angle(v3 - v1))
                d2 = degrees((v3 - v2).angle(v1 - v2))
                d3 = degrees((v1 - v3).angle(v2 - v3))
                if d1 < angle_threshold or d2 < angle_threshold or d3 < angle_threshold:
                    bm.faces.remove(polygon)
            bm.to_mesh(data)
            bm.free()
            bpy.ops.bim.update_representation(obj=obj.name, ifc_representation_class="")

        tool.Ifc.get().history_size = old_history_size
        bpy.context.preferences.edit.undo_steps = old_undo_steps

        self.file = tool.Ifc.get()
