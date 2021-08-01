import hppfcl
import numpy as np
from aabbtree import AABB
from aabbtree import AABBTree


class Collider:
    def __init__(self):
        self.groups = {}

    def create_group(self, name):
        self.groups[name] = {"tree": AABBTree(), "objects": {}}

    def create_object(self, group_name, id, shape):
        obj = hppfcl.CollisionObject(
            self.create_bvh(shape.geometry), self.create_transform(shape.transformation.matrix.data)
        )
        aabb = obj.getAABB()
        c = aabb.center()
        x = aabb.width()
        y = aabb.height()
        z = aabb.depth()
        aabb = AABB([(c[0] - x / 2, c[0] + x / 2), (c[1] - y / 2, c[1] + y / 2), (c[2] - z / 2, c[2] + z / 2)])
        self.groups[group_name]["tree"].add(aabb, id)
        self.groups[group_name]["objects"][id] = (aabb, obj)

    def collide_internal(self, name):
        print('starting internal collision')
        return self.collide_narrowphase(self.collide_broadphase(name, name))

    def collide_group(self, name1, name2):
        print('starting group collision')
        return self.collide_narrowphase(self.collide_broadphase(name1, name2))

    def collide_broadphase(self, name1, name2):
        print('Begin broad phase')
        potential_collisions = []
        checked_collisions = set()
        i = 0
        for id, obj_data in self.groups[name1]["objects"].items():
            aabb, obj = obj_data
            collision_stack = [self.groups[name2]["tree"]]
            checked_collisions.add(id)
            i += 1
            while i % 1000 == 0:
                print(i, '...')
            while collision_stack:
                node = collision_stack.pop()
                if node.value == id or node.value in checked_collisions:
                    continue
                if node.does_overlap(aabb):
                    if node.is_leaf:
                        potential_collisions.append(
                            {
                                "id1": id,
                                "obj1": obj,
                                "id2": node.value,
                                "obj2": self.groups[name2]["objects"][node.value][1],
                            }
                        )
                    else:
                        collision_stack.append(node.left)
                        collision_stack.append(node.right)
        return potential_collisions

    def collide_narrowphase(self, potential_collisions):
        print('Begin narrow phase')
        collisions = []
        for data in potential_collisions:
            result = hppfcl.CollisionResult()
            hppfcl.collide(data["obj1"], data["obj2"], hppfcl.CollisionRequest(), result)
            if result.isCollision():
                collisions.append({"id1": data["id1"], "id2": data["id2"], "collision": result})
                print({"id1": data["id1"], "id2": data["id2"], "collision": result})
        return collisions

    def create_transform(self, m):
        mat = np.array([[m[0], m[3], m[6], m[9]], [m[1], m[4], m[7], m[10]], [m[2], m[5], m[8], m[11]], [0, 0, 0, 1]])
        mat.transpose()
        return hppfcl.Transform3f(mat[:3, :3], mat[:3, 3])

    def create_bvh(self, mesh):
        v = mesh.verts
        f = mesh.faces
        mesh_verts = np.array([[v[i], v[i + 1], v[i + 2]] for i in range(0, len(v), 3)])
        mesh_faces = [(int(f[i]), int(f[i + 1]), int(f[i + 2])) for i in range(0, len(f), 3)]

        bvh = hppfcl.BVHModelOBB()
        bvh.beginModel(num_tris=len(mesh.faces), num_vertices=len(mesh_verts))
        vertices = hppfcl.StdVec_Vec3f()
        [vertices.append(v) for v in mesh_verts]
        triangles = hppfcl.StdVec_Triangle()
        [triangles.append(hppfcl.Triangle(f[0], f[1], f[2])) for f in mesh_faces]
        bvh.addSubModel(vertices, triangles)
        bvh.endModel()
        return bvh
