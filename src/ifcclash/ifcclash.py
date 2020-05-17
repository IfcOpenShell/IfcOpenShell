#!python

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
        self.tolerance = 0.01
        self.a = []
        self.b = []
        self.a_cm = None
        self.b_cm = None
        self.clashes = {}

    def clash(self):
        for ab in ['a', 'b']:
            self.settings.logger.info(f'Creating collision manager {ab} ...')
            setattr(self, f'{ab}_cm', collision.CollisionManager())
            self.settings.logger.info(f'Loading files {ab} ...')
            for data in getattr(self, ab):
                data['ifc'] = ifcopenshell.open(data['file'])
                self.patch_ifc(data['ifc'])
                self.settings.logger.info(f'Purging unnecessary elements {ab} ...')
                self.purge_elements(data)
                self.settings.logger.info(f'Creating collision data for {ab} ...')
                if len(data['ifc'].by_type('IfcElement')) > 0:
                    self.add_collision_objects(data, getattr(self, f'{ab}_cm'))
        results = self.a_cm.in_collision_other(self.b_cm, return_data=True)

        if not results[0]:
            return

        for contact in results[1]:
            a_global_id, b_global_id = contact.names
            a = self.get_element('a', a_global_id)
            b = self.get_element('b', b_global_id)
            if contact.raw.penetration_depth < self.tolerance:
                continue
            key = f'{a_global_id}-{b_global_id}'
            if key in self.clashes \
                    and self.clashes[key]['penetration_depth'] > contact.raw.penetration_depth:
                continue
            self.clashes[key] = {
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

    def export(self):
        with open(self.settings.output, 'w', encoding='utf-8') as clashes_file:
            json.dump(list(self.clashes.values()), clashes_file, indent=4)

    def get_element(self, ab, global_id):
        for data in getattr(self, ab):
            try:
                element = data['ifc'].by_guid(global_id)
                if element:
                    return element
            except:
                pass

    def purge_elements(self, data):
        if not data['selector']:
            for element in data['ifc'].by_type('IfcSpace'):
                ifc_file.remove(element)
            return

        selector = ifcopenshell.util.selector.Selector()
        elements = selector.parse(data['ifc'], data['selector'])

        if data['mode'] == 'e':
            for element in data['ifc'].by_type('IfcElement'):
                if element in elements:
                    data['ifc'].remove(element)
        elif data['mode'] == 'i':
            for element in data['ifc'].by_type('IfcElement'):
                if element not in elements:
                    data['ifc'].remove(element)

    def add_collision_objects(self, data, cm):
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
        if mesh_name in data['meshes']:
            mesh = data['meshes'][mesh_name]
        else:
            mesh = self.create_mesh(shape)
            data['meshes'][mesh_name] = mesh

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
        '-a',
        type=str,
        nargs='+',
        help='The IFC files containing group A of objects to clash')
    parser.add_argument(
        '-b',
        type=str,
        nargs='+',
        help='The IFC files containing group B of objects to clash')
    parser.add_argument(
        '-as',
        '--a-selector',
        type=str,
        nargs='+',
        help='Selector queries for each IFC file in group A')
    parser.add_argument(
        '-bs',
        '--b-selector',
        type=str,
        nargs='+',
        help='Selector queries for each IFC file in group B')
    parser.add_argument(
        '-am',
        '--a-mode',
        type=str,
        nargs='+',
        help='Selection mode for each file in group A. "i" for include, and "e" for exclude')
    parser.add_argument(
        '-bm',
        '--b-mode',
        type=str,
        nargs='+',
        help='Selection mode for each file in group B. "i" for include, and "e" for exclude')
    parser.add_argument(
        '-t',
        '--tolerance',
        type=float,
        help='The distance tolerance that clashes should exceed',
        default=0.01)
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='The JSON diff file to output. Defaults to clashes.json',
        default='clashes.json')
    args = parser.parse_args()

    settings = IfcClashSettings()
    settings.output = args.output
    settings.logger = logging.getLogger('Clash')
    settings.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    settings.logger.addHandler(handler)
    ifc_clasher = IfcClasher(settings)
    for ab in ['a', 'b']:
        getattr(ifc_clasher, ab).extend([{
                'file': a,
                'meshes': {},
                'selector': '',
                'mode': ''
            } for i, a in enumerate(getattr(args, ab))])

        if getattr(args, f'{ab}_selector'):
            for i, selector in enumerate(getattr(args, f'{ab}_selector')):
                getattr(ifc_clasher, ab)[i]['selector'] = selector

        if getattr(args, f'{ab}_mode'):
            for i, mode in enumerate(getattr(args, f'{ab}_mode')):
                getattr(ifc_clasher, ab)[i]['mode'] = mode
    ifc_clasher.tolerance = args.tolerance
    ifc_clasher.clash()
    ifc_clasher.export()
