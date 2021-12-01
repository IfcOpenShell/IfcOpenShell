# IfcClash - IFC-based clash detection.
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcClash.
#
# IfcClash is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcClash is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcClash.  If not, see <http://www.gnu.org/licenses/>.

import hppfcl
import numpy as np
import ifcopenshell


class Collider:
    def __init__(self, logger):
        self.logger = logger
        self.groups = {}
        self.tree = ifcopenshell.geom.tree()

    def create_group(self, name):
        self.logger.info(f"Creating group {name}")
        self.groups[name] = {"elements": {}, "objects": {}}

    def create_objects(self, name, ifc_file, iterator, elements):
        import time

        start = time.time()
        self.logger.info(f"Adding objects {name}")
        assert iterator.initialize()
        while True:
            self.tree.add_element(iterator.get_native())
            shape = iterator.get()
            self.create_object(name, shape.guid, shape)
            if not iterator.next():
                break
        self.logger.info(f"Tree finished {time.time() - start}")
        start = time.time()
        self.groups[name]["elements"].update({e.GlobalId: e for e in elements})
        self.logger.info(f"Element metadata finished {time.time() - start}")
        start = time.time()

    def create_object(self, group_name, id, shape):
        obj = hppfcl.CollisionObject(
            self.create_bvh(shape.geometry), self.create_transform(shape.transformation.matrix.data)
        )
        self.groups[group_name]["objects"][id] = obj

    def collide_internal(self, name):
        return self.collide_narrowphase(name, name, self.collide_broadphase(name, name))

    def collide_group(self, name1, name2):
        return self.collide_narrowphase(name1, name2, self.collide_broadphase(name1, name2))

    def collide_broadphase(self, name1, name2):
        import time

        start = time.time()
        self.logger.info("Starting broadphase")
        potential_collisions = []
        checked_collisions = set()
        for id, element in self.groups[name1]["elements"].items():
            checked_collisions.add(id)
            box_filter = self.tree.select_box(element)
            pairs = [
                {"id1": id, "id2": e.GlobalId}
                for e in box_filter
                if e.GlobalId not in checked_collisions and e.GlobalId in self.groups[name2]["elements"]
            ]
            potential_collisions.extend(pairs)
        self.logger.info(f"Finished broadphase {time.time() - start}")
        return potential_collisions

    def collide_narrowphase(self, name1, name2, potential_collisions):
        import time

        start = time.time()
        self.logger.info("Starting narrowphase")
        collisions = []
        for data in potential_collisions:
            result = hppfcl.CollisionResult()
            hppfcl.collide(
                self.groups[name1]["objects"][data["id1"]],
                self.groups[name2]["objects"][data["id2"]],
                hppfcl.CollisionRequest(),
                result,
            )
            if result.isCollision():
                collisions.append({"id1": data["id1"], "id2": data["id2"], "collision": result})
        self.logger.info(f"Finished narrowphase {time.time() - start}")
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
        bvh.beginModel(len(mesh_faces), len(mesh_verts))
        vertices = hppfcl.StdVec_Vec3f()
        [vertices.append(v) for v in mesh_verts]
        triangles = hppfcl.StdVec_Triangle()
        [triangles.append(hppfcl.Triangle(f[0], f[1], f[2])) for f in mesh_faces]
        bvh.addSubModel(vertices, triangles)
        bvh.endModel()
        return bvh
