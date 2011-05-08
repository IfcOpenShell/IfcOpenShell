import bpy, mathutils
from bpy.props import *
from io_utils import ImportHelper

class ImportIFC(bpy.types.Operator, ImportHelper):
    '''Load an IFC File'''
    bl_idname = "import_scene.ifc"
    bl_label = "Import IFC"

    filename_ext = ".ifc"
    filter_glob = StringProperty(default="*.ifc", options={'HIDDEN'})
    
    def execute(self, context):
        import IFCimport
        IFCimport.init_objs(self.filepath)
        ids = {}
        while True:
            ob = IFCimport.current_obj()
            print (ob.name)
            if not ob.type in ['IFCSPACE','IFCOPENINGELEMENT']:
                f = ob.mesh.faces
                v = ob.mesh.verts
                m = ob.matrix
                if ob.mesh.id in ids: me = ids[ob.mesh.id]
                else:
                    verts = []
                    faces = []
                    for i in range(0,len(f),3):
                        faces.append([f[i+0],f[i+1],f[i+2]])
                    for i in range(0,len(v),3):
                        verts.append([v[i+0],v[i+1],v[i+2]])
                    me = bpy.data.meshes.new('mesh%d'%ob.mesh.id)
                    me.from_pydata(verts,[],faces)
                    if ob.type in bpy.data.materials:
                        mat = bpy.data.materials[ob.type]
                        mat.use_fake_user = True
                    else: mat = bpy.data.materials.new(ob.type)
                    me.materials.append(mat)
                    ids[ob.mesh.id] = me
                bob = bpy.data.objects.new(ob.name,me)
                bob.matrix_world = mathutils.Matrix([m[0],m[1],m[2],0],[m[3],m[4],m[5],0],[m[6],m[7],m[8],0],[m[9],m[10],m[11],1])
                bpy.context.scene.objects.link(bob)
                me.update()
            if not IFCimport.next_obj(): break
        return {'FINISHED'}
    
def menu_func_import(self, context):
    self.layout.operator(ImportIFC.bl_idname, text="Industry Foundation Classes (.ifc)")
def register():
    bpy.types.INFO_MT_file_import.append(menu_func_import)
register()