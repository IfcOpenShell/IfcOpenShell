import ifcopenshell
import ifcopenshell.geom
import numpy as np
import fcl

class IfcClasher:
    def __init__(self):
        self.settings = ifcopenshell.geom.settings()
        self.tolerance = 0.01
        self.a = None
        self.b = None
        self.a_geoms = []
        self.b_geoms = []
        self.a_objs = []
        self.b_objs = []
        self.a_global_ids = []
        self.b_global_ids = []
        self.a_geom_to_global_id = {}
        self.b_geom_to_global_id = {}
        self.a_manager = None
        self.b_manager = None
        self.clashes = []

    def clash(self):
        self.load_files()
        for ab in ('a', 'b'):
            self.create_collision_objects(ab)
            self.create_manager(ab)
            self.create_data_maps(ab)

        req = fcl.CollisionRequest(num_max_contacts=1, enable_contact=True)
        rdata = fcl.CollisionData(request = req)
        self.a_manager.collide(self.b_manager, rdata, fcl.defaultCollisionCallback)
        for contact in rdata.result.contacts:
            if contact.penetration_depth < self.tolerance:
                continue
            self.clashes.append({
                'a': self.a_geom_to_global_id[id(contact.o1)],
                'b': self.b_geom_to_global_id[id(contact.o2)],
                'normal': contact.normal,
                'position': contact.pos,
                'penetration_depth': contact.penetration_depth
            })

    def load_files(self):
        self.a = ifcopenshell.open('/home/dion/a.ifc')
        self.b = ifcopenshell.open('/home/dion/b.ifc')

    def create_collision_objects(self, ab):
        elements = getattr(self, ab).by_type('IfcElement')
        for element in elements:
            shape = ifcopenshell.geom.create_shape(self.settings, element)
            mesh = self.create_mesh(element, shape)
            transform = self.get_transform(element)
            getattr(self, '{}_geoms'.format(ab)).append(mesh)
            getattr(self, '{}_objs'.format(ab)).append(fcl.CollisionObject(mesh, transform))
            getattr(self, '{}_global_ids'.format(ab)).append(element.GlobalId)

    def create_manager(self, ab):
        name = '{}_manager'.format(ab)
        setattr(self, name, fcl.DynamicAABBTreeCollisionManager())
        getattr(self, name).registerObjects(getattr(self, '{}_objs'.format(ab)))
        getattr(self, name).setup()

    def create_data_maps(self, ab):
        setattr(self, '{}_geom_to_global_id'.format(ab),
            {
                id(geom) : global_id
                for geom, global_id
                in zip(
                    getattr(self, '{}_geoms'.format(ab)),
                    getattr(self, '{}_global_ids'.format(ab))
                )
            }
        )

    def get_transform(self, element):
        m = self.get_local_placement(element.ObjectPlacement)
        R = np.array(
            [
                [m[0][0], m[1][0], m[2][0]],
                [m[0][1], m[1][1], m[2][1]],
                [m[0][2], m[1][2], m[2][2]]
            ]
        )
        T = np.array([m[0][3], m[1][3], m[2][3]])
        return fcl.Transform(R, T)

    def create_mesh(self, element, shape):
        f = shape.geometry.faces
        v = shape.geometry.verts
        vertices = np.array([[v[i], v[i + 1], v[i + 2]]
                 for i in range(0, len(v), 3)])
        faces = np.array([[f[i], f[i + 1], f[i + 2]]
                 for i in range(0, len(f), 3)])
        m = fcl.BVHModel()
        m.beginModel(len(vertices), len(faces))
        m.addSubModel(vertices, faces)
        m.endModel()
        return m

    def get_local_placement(self, plc):
        if plc.PlacementRelTo is None:
            parent = np.eye(4)
        else:
            parent = self.get_local_placement(plc.PlacementRelTo)
        return np.dot(self.get_axis2placement(plc.RelativePlacement), parent)

    def a2p(self, o, z, x):
        y = np.cross(z, x)
        r = np.eye(4)
        r[:-1,:-1] = x,y,z
        r[-1,:-1] = o
        return r.T

    def get_axis2placement(self, plc):
        z = np.array(plc.Axis.DirectionRatios if plc.Axis else (0,0,1))
        x = np.array(plc.RefDirection.DirectionRatios if plc.RefDirection else (1,0,0))
        o = plc.Location.Coordinates
        return self.a2p(o,z,x)

ifc_clasher = IfcClasher()
ifc_clasher.clash()
import pprint
pprint.pprint(ifc_clasher.clashes)
