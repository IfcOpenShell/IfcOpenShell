#!/usr/bin/env python3

import collision
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.selector
import multiprocessing
import numpy as np
import json
import sys
import argparse
import logging


class Mesh:
    faces: []
    vertices: []


class IfcClasher:
    def __init__(self, settings):
        self.settings = settings
        self.geom_settings = ifcopenshell.geom.settings()
        self.clash_sets = []
        self.clash_data = {'meshes': {}}
        self.global_data = {'meshes': {}, 'matrices': {}}

    def clash(self):
        for clash_set in self.clash_sets:
            self.process_clash_set(clash_set)

    def process_clash_set(self, clash_set):
        for ab in ['a', 'b']:
            self.settings.logger.info(f'Creating collision manager {ab} ...')
            clash_set[f'{ab}_cm'] = collision.CollisionManager()
            self.settings.logger.info(f'Loading files {ab} ...')
            for data in clash_set[ab]:
                data['ifc'] = ifcopenshell.open(data['file'])
                self.patch_ifc(data['ifc'])
                self.settings.logger.info(f'Purging unnecessary elements {ab} ...')
                self.purge_elements(data)
                self.settings.logger.info(f'Creating collision data for {ab} ...')
                if len(data['ifc'].by_type('IfcElement')) > 0:
                    self.add_collision_objects(data, clash_set[f'{ab}_cm'])

        if 'b' in clash_set and clash_set['b']:
            results = clash_set['a_cm'].in_collision_other(clash_set['b_cm'], return_data=True)
        else:
            results = clash_set['a_cm'].in_collision_internal(return_data=True)

        if not results[0]:
            return

        tolerance = clash_set['tolerance'] if 'tolerance' in clash_set else 0.01
        clash_set['clashes'] = {}

        for contact in results[1]:
            a_global_id, b_global_id = contact.names
            a = self.get_element(clash_set['a'], a_global_id)
            if 'b' in clash_set and clash_set['b']:
                b = self.get_element(clash_set['b'], b_global_id)
            else:
                b = self.get_element(clash_set['a'], b_global_id)
            if contact.raw.penetration_depth < tolerance:
                continue

            # fcl returns contact data for faces that aren't actually
            # penetrating, but just touching. If our tolerance is zero, then we
            # consider these as clashes and we move on. If our tolerance is not
            # zero, fcl has a strange behaviour where the penetration depth can
            # be a large number even though objects are just touching
            # https://github.com/flexible-collision-library/fcl/issues/503 In
            # this case, I don't trust the penetration depth and I run my own
            # triangle-triangle intersection test. Optimistically, this skips
            # the false positives. Conservatively, we let the user manually deal
            # with the false positives and we mark it as a clash.
            is_optimistic = True # TODO: let user configure this

            if is_optimistic and tolerance != 0:
                # We'll now check if the contact data's two faces are actually
                # intersecting, using this brute force check:
                # https://stackoverflow.com/questions/7113344/find-whether-two-triangles-intersect-or-not
                # I'm not very good at this kind of code. If you know this stuff
                # please help rewrite this.

                # Get vertices of clashing tris
                p1 = self.global_data['meshes'][contact.names[0]].faces[contact.index(contact.names[0])]
                p2 = self.global_data['meshes'][contact.names[1]].faces[contact.index(contact.names[1])]
                m1 = self.global_data['matrices'][contact.names[0]]
                m2 = self.global_data['matrices'][contact.names[1]]
                v1 = []
                v2 = []

                for v in p1:
                    v1.append((m1 @ np.array([*self.global_data['meshes'][contact.names[0]].vertices[v], 1]))[0:3].round(2))
                for v in p2:
                    v2.append((m2 @ np.array([*self.global_data['meshes'][contact.names[1]].vertices[v], 1]))[0:3].round(2))

                tri1_x = 0
                tri2_x = 0
                tri1_x += 1 if self.intersect_line_triangle(v1[0], v1[1], v2[0], v2[1], v2[2]) is not None else 0
                tri1_x += 1 if self.intersect_line_triangle(v1[1], v1[2], v2[0], v2[1], v2[2]) is not None else 0
                tri1_x += 1 if self.intersect_line_triangle(v1[2], v1[0], v2[0], v2[1], v2[2]) is not None else 0

                tri2_x += 1 if self.intersect_line_triangle(v2[0], v2[1], v1[0], v1[1], v1[2]) is not None else 0
                tri2_x += 1 if self.intersect_line_triangle(v2[1], v2[2], v1[0], v1[1], v1[2]) is not None else 0
                tri2_x += 1 if self.intersect_line_triangle(v2[2], v2[0], v1[0], v1[1], v1[2]) is not None else 0
                intersections = [tri1_x, tri2_x]
                if intersections == [0, 2] or intersections == [2, 0] or intersections == [1, 1]:
                    # This is a penetrating collision
                    pass
                else:
                    # This is probably two triangles which just touch
                    continue

            key = f'{a_global_id}-{b_global_id}'

            if key in clash_set['clashes'] \
                    and clash_set['clashes'][key]['penetration_depth'] > contact.raw.penetration_depth:
                continue

            clash_set['clashes'][key] = {
                'a_global_id': a_global_id,
                'b_global_id': b_global_id,
                'a_ifc_class': a.is_a(),
                'b_ifc_class': b.is_a(),
                'a_name': a.Name,
                'b_name': b.Name,
                'normal': list(contact.raw.normal),
                'position': list(contact.raw.pos),
                'penetration_depth': contact.raw.penetration_depth
            }

    # https://stackoverflow.com/questions/42740765/intersection-between-line-and-triangle-in-3d
    def intersect_line_triangle(self, q1, q2, p1, p2, p3):
        def signed_tetra_volume(a,b,c,d):
            return np.sign(np.dot(np.cross(b-a,c-a),d-a)/6.0)

        s1 = signed_tetra_volume(q1,p1,p2,p3)
        s2 = signed_tetra_volume(q2,p1,p2,p3)

        if s1 != s2:
            s3 = signed_tetra_volume(q1,q2,p1,p2)
            s4 = signed_tetra_volume(q1,q2,p2,p3)
            s5 = signed_tetra_volume(q1,q2,p3,p1)
            if s3 == s4 and s4 == s5:
                n = np.cross(p2-p1,p3-p1)
                t = -np.dot(q1,n-p1) / np.dot(q1,q2-q1)
                return q1 + t * (q2-q1)
        return None

    def export(self):
        results = self.clash_sets.copy()
        for result in results:
            del result['a_cm']
            del result['b_cm']
            for ab in ['a', 'b']:
                for data in result[ab]:
                    if 'ifc' in data:
                        del data['ifc']
        with open(self.settings.output, 'w', encoding='utf-8') as clashes_file:
            json.dump(results, clashes_file, indent=4)

    def get_element(self, clash_group, global_id):
        for data in clash_group:
            try:
                element = data['ifc'].by_guid(global_id)
                if element:
                    return element
            except:
                pass

    def purge_elements(self, data):
        if 'selector' not in data:
            for element in data['ifc'].by_type('IfcSpace'):
                data['ifc'].remove(element)
            return

        selector = ifcopenshell.util.selector.Selector()
        elements = selector.parse(data['ifc'], data['selector'])

        if data['mode'] == 'e':
            for element in data['ifc'].by_type('IfcElement') + data['ifc'].by_type('IfcSpatialStructureElement'):
                if element in elements:
                    data['ifc'].remove(element)
        elif data['mode'] == 'i':
            for element in data['ifc'].by_type('IfcElement') + data['ifc'].by_type('IfcSpatialStructureElement'):
                if element not in elements:
                    data['ifc'].remove(element)

    def add_collision_objects(self, data, cm):
        self.clash_data['meshes'] = {}
        iterator = ifcopenshell.geom.iterator(self.geom_settings, data['ifc'], multiprocessing.cpu_count())
        valid_file = iterator.initialize()
        if not valid_file:
            return False
        old_progress = -1
        while True:
            progress = iterator.progress() // 2
            if progress > old_progress:
                print("\r[" + "#" * progress + " " * (50 - progress) + "]", end="")
                old_progress = progress
            self.add_collision_object(data, cm, iterator.get())
            if not iterator.next():
                break

    def add_collision_object(self, data, cm, shape):
        if shape is None:
            return
        element = data['ifc'].by_id(shape.guid)
        self.settings.logger.info('Creating object {}'.format(element))
        mesh_name = f'mesh-{shape.geometry.id}'
        if mesh_name in self.clash_data['meshes']:
            mesh = self.clash_data['meshes'][mesh_name]
        else:
            mesh = self.create_mesh(shape)
            self.clash_data['meshes'][mesh_name] = mesh
        self.global_data['meshes'][shape.guid] = mesh

        m = shape.transformation.matrix.data
        mat = np.array(
            [
                [m[0], m[3], m[6], m[9]],
                [m[1], m[4], m[7], m[10]],
                [m[2], m[5], m[8], m[11]],
                [0, 0, 0, 1]
            ]
        )

        mat.transpose()
        self.global_data['matrices'][shape.guid] = mat
        cm.add_object(shape.guid, mesh, mat)

    def create_mesh(self, shape):
        f = shape.geometry.faces
        v = shape.geometry.verts
        mesh = Mesh()
        mesh.vertices = np.array([[v[i], v[i + 1], v[i + 2]]
                 for i in range(0, len(v), 3)])
        mesh.faces = np.array([[f[i], f[i + 1], f[i + 2]]
                 for i in range(0, len(f), 3)])
        return mesh

    def patch_ifc(self, ifc_file):
        project = ifc_file.by_type('IfcProject')[0]
        sites = self.find_decomposed_ifc_class(project, 'IfcSite')
        for site in sites:
            self.patch_placement_to_origin(site)
        buildings = self.find_decomposed_ifc_class(project, 'IfcBuilding')
        for building in buildings:
            self.patch_placement_to_origin(building)

    def find_decomposed_ifc_class(self, element, ifc_class):
        results = []
        rel_aggregates = element.IsDecomposedBy
        if not rel_aggregates:
            return results
        for rel_aggregate in rel_aggregates:
            for part in rel_aggregate.RelatedObjects:
                if part.is_a(ifc_class):
                    results.append(part)
                results.extend(self.find_decomposed_ifc_class(part, ifc_class))
        return results

    def patch_placement_to_origin(self, element):
        element.ObjectPlacement.RelativePlacement.Location.Coordinates = (0., 0., 0.)
        if element.ObjectPlacement.RelativePlacement.Axis:
            element.ObjectPlacement.RelativePlacement.Axis.DirectionRatios = (0., 0., 1.)
        if element.ObjectPlacement.RelativePlacement.RefDirection:
            element.ObjectPlacement.RelativePlacement.RefDirection.DirectionRatios = (1., 0., 0.)


class IfcClashSettings:
    def __init__(self):
        self.logger = None
        self.output = 'clashes.json'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Clashes geometry between two IFC files')
    parser.add_argument(
        'input',
        type=str,
        help='A JSON dataset describing a series of clashsets')
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='The JSON diff file to output. Defaults to output.json',
        default='output.json')
    args = parser.parse_args()

    settings = IfcClashSettings()
    settings.output = args.output
    settings.logger = logging.getLogger('Clash')
    settings.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    settings.logger.addHandler(handler)
    ifc_clasher = IfcClasher(settings)
    with open(args.input, 'r') as clash_sets_file:
        ifc_clasher.clash_sets = json.loads(clash_sets_file.read())
    ifc_clasher.clash()
    ifc_clasher.export()
