import os
import math
import time
import numpy
import pickle
import pystache
import sys
from pathlib import Path
from . import annotation
mathutils = sys.modules.get('mathutils')
if mathutils is not None:
    from mathutils import Vector
    from mathutils import geometry
from math import degrees
import xml.etree.ElementTree as ET

import svgwrite
import OCC.gp
import OCC.Geom
import OCC.Bnd
import OCC.BRepBndLib
import OCC.BRep
import OCC.BRepPrimAPI
import OCC.BRepAlgoAPI
import OCC.BRepBuilderAPI
import OCC.TopOpeBRepTool
import OCC.TopOpeBRepBuild
import OCC.ShapeExtend
import OCC.GProp
import OCC.BRepGProp
import OCC.GC
import OCC.ShapeAnalysis
import OCC.TopTools
import OCC.TopExp
import OCC.HLRAlgo
import OCC.HLRBRep
import OCC.TopLoc
import OCC.Bnd
import OCC.BRepBndLib
import OCC.BRepTools
import OCC.TopoDS
import OCC.GeomLProp
import OCC.IntCurvesFace

from OCC.TopoDS import topods

import ifcopenshell
import ifcopenshell.geom

cwd = os.path.dirname(os.path.realpath(__file__))
this_file = os.path.join(cwd, 'cut_ifc.py')

def get_booleaned_edges(shape):
    edges = []
    exp = OCC.TopExp.TopExp_Explorer(shape, OCC.TopAbs.TopAbs_EDGE)
    while exp.More():
        edges.append(topods.Edge(exp.Current()))
        exp.Next()
    return edges

def connect_edges_into_wires(unconnected_edges):
    edges = OCC.TopTools.TopTools_HSequenceOfShape()
    edges_handle = OCC.TopTools.Handle_TopTools_HSequenceOfShape(edges)
    wires = OCC.TopTools.TopTools_HSequenceOfShape()
    wires_handle = OCC.TopTools.Handle_TopTools_HSequenceOfShape(wires)

    for edge in unconnected_edges:
        edges.Append(edge)

    OCC.ShapeAnalysis.ShapeAnalysis_FreeBounds.ConnectEdgesToWires(edges_handle, 1e-5, True, wires_handle)
    return wires_handle.GetObject()

def do_cut(process_data):
    global_id, shape, section, trsf_data = process_data

    axis = OCC.gp.gp_Ax2(
        OCC.gp.gp_Pnt(
            trsf_data['top_left_corner'][0],
            trsf_data['top_left_corner'][1],
            trsf_data['top_left_corner'][2]),
        OCC.gp.gp_Dir(
            trsf_data['projection'][0],
            trsf_data['projection'][1],
            trsf_data['projection'][2]),
        OCC.gp.gp_Dir(
            trsf_data['x_axis'][0],
            trsf_data['x_axis'][1],
            trsf_data['x_axis'][2])
        )
    source = OCC.gp.gp_Ax3(axis)
    destination = OCC.gp.gp_Ax3(
        OCC.gp.gp_Pnt(0, 0, 0),
        OCC.gp.gp_Dir(0, 0, -1),
        OCC.gp.gp_Dir(1, 0, 0))
    transformation = OCC.gp.gp_Trsf()
    transformation.SetDisplacement(source, destination)

    cut_polygons = []
    section = OCC.BRepAlgoAPI.BRepAlgoAPI_Section(section, shape).Shape()
    section_edges = get_booleaned_edges(section)
    if len(section_edges) <= 0:
        return cut_polygons
    wires = connect_edges_into_wires(section_edges)
    for i in range(wires.Length()):
        wire_shape = wires.Value(i+1)

        transformed_wire = OCC.BRepBuilderAPI.BRepBuilderAPI_Transform(
            wire_shape, transformation)
        wire_shape = transformed_wire.Shape()

        wire = topods.Wire(wire_shape)
        face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(wire).Face()

        points = []
        exp = OCC.BRepTools.BRepTools_WireExplorer(wire)
        while exp.More():
            point = OCC.BRep.BRep_Tool.Pnt(exp.CurrentVertex())
            points.append((point.X(), -point.Y()))
            exp.Next()
        cut_polygons.append({ 'global_id': global_id, 'points': points })
    return cut_polygons


class IfcCutter:
    def __init__(self):
        self.ifc_attribute_extractor = None
        self.product_shapes = []
        self.background_elements = []
        self.cut_polygons = []
        self.template_variables = {}
        self.data_dir = ''
        self.ifc_files = []
        self.unit = None
        self.resolved_pixels = set()
        self.should_get_background = False
        self.shapes_pickle_file = 'shapes.pickle'
        self.text_pickle_file = 'text.pickle'
        self.cut_pickle_file = 'cut.pickle'
        self.should_recut = True
        self.should_extract = True
        self.diagram_name = None
        self.background_image = None
        self.section_box = {
            'projection': (0, 1, 0),
            'x_axis': (1, 0, 0),
            'y_axis': (0, 0, -1),
            'top_left_corner': (-2, 2, 8),
            'x': 14,
            'y': 9,
            'z': 2,
            'shape': None,
            'face': None
        }

    def cut(self):
        start_time = time.time()
        print('# Load files')
        self.load_ifc_files()
        print('# Timer logged at {:.2f} seconds'.format(time.time() - start_time))
        start_time = time.time()
        print('# Extract template variables')
        self.get_template_variables()
        print('# Timer logged at {:.2f} seconds'.format(time.time() - start_time))
        start_time = time.time()
        print('# Get product shapes')
        self.get_product_shapes()
        print('# Timer logged at {:.2f} seconds'.format(time.time() - start_time))
        start_time = time.time()
        print('# Create section box')
        self.create_section_box()
        print('# Timer logged at {:.2f} seconds'.format(time.time() - start_time))
        start_time = time.time()
        print('# Get cut polygons')
        self.get_cut_polygons()
        print('# Timer logged at {:.2f} seconds'.format(time.time() - start_time))

        if not self.should_get_background:
            return

        start_time = time.time()
        print('# Get background elements')
        self.get_background_elements()
        print('# Timer logged at {:.2f} seconds'.format(time.time() - start_time))
        start_time = time.time()
        print('# Sort background elements')
        self.sort_background_elements(reverse=True)
        print('# Timer logged at {:.2f} seconds'.format(time.time() - start_time))
        start_time = time.time()
        print('# Merge background_elements')
        self.merge_background_elements()
        print('# Timer logged at {:.2f} seconds'.format(time.time() - start_time))
        start_time = time.time()
        print('# Sort background elements')
        self.sort_background_elements()
        print('# Timer logged at {:.2f} seconds'.format(time.time() - start_time))

    def load_ifc_files(self):
        if not self.should_recut and not self.should_extract:
            return

        loaded_files = []
        for ifc_file in self.ifc_files:
            print('Loading file {} ...'.format(ifc_file))
            if ifc_file:
                loaded_files.append(ifcopenshell.open(ifc_file))
        self.ifc_files = loaded_files

    def get_template_variables(self):
        if not self.should_extract:
            if os.path.isfile(self.text_pickle_file):
                with open(self.text_pickle_file, 'rb') as text_file:
                    self.template_variables = pickle.load(text_file)
            return

        data = {}
        for text_obj in self.text_objs:
            text_obj_data = {}
            text_body = text_obj.data.body
            for variable in text_obj.data.BIMTextProperties.variables:
                element = self.get_ifc_element(variable.global_id)
                if element:
                    text_obj_data[variable.name] = self.ifc_attribute_extractor.get_element_key(element, variable.prop_key)
            if text_obj_data:
                data[text_obj.name] = text_obj_data

        with open(self.text_pickle_file, 'wb') as text_file:
            pickle.dump(data, text_file, protocol=pickle.HIGHEST_PROTOCOL)

        self.template_variables = data

    def get_product_shapes(self):
        if not self.should_recut:
            return

        shape_map = {}

        if os.path.isfile(self.shapes_pickle_file):
            with open(self.shapes_pickle_file, 'rb') as shape_file:
                shape_map = pickle.load(shape_file)

        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_PYTHON_OPENCASCADE, True)
        products = []
        for ifc_file in self.ifc_files:
            # TODO: This should perhaps be configurable, e.g. spaces cut to show zones in the drawing
            products.extend(ifc_file.by_type('IfcElement'))
        total_products = len(products)
        for i, product in enumerate(products):
            print('{}/{} geometry processed ...'.format(i, total_products), end='\r', flush=True)
            if product.is_a('IfcOpeningElement') or product.is_a('IfcSite'):
                continue
            if product.Representation is not None:
                try:
                    if product.GlobalId in shape_map:
                        shape = shape_map[product.GlobalId]
                    else:
                        shape = ifcopenshell.geom.create_shape(settings, product).geometry
                        shape_map[product.GlobalId] = shape
                    self.product_shapes.append((product, shape))
                except:
                    print('Failed to create shape for {}'.format(product))

        if not os.path.isfile(self.shapes_pickle_file):
            with open(self.shapes_pickle_file, 'wb') as shape_file:
                pickle.dump(shape_map, shape_file, protocol=pickle.HIGHEST_PROTOCOL)

    def sort_background_elements(self, reverse=None):
        if reverse:
            new_list = sorted(self.background_elements, key=lambda k: -k['z'])
        else:
            new_list = sorted(self.background_elements, key=lambda k: k['z'])
        self.background_elements = new_list

    def process_grid(self, face, resolution):
        try:
            bbox = self.get_bbox(face)
            xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
        except:
            return
        current_x = 0
        current_y = 0
        is_visible = False
        while current_x < self.section_box['x']:
            current_y = 0
            while current_y > -self.section_box['y']:
                if current_x < xmin \
                    or current_x > xmax \
                    or current_y < ymin \
                    or current_y > ymax:
                    current_y -= resolution
                    continue
                if (current_x, current_y) in self.resolved_pixels:
                    current_y -= resolution
                    continue
                point = numpy.array((current_x, current_y, 0))
                hit = self.raycast(face, point)
                if hit:
                    is_visible = True
                    self.resolved_pixels.add((current_x, current_y))
                current_y -= resolution
            current_x += resolution
        return is_visible

    def merge_background_elements(self):
        background_elements = []

        resolution = 0.1 # 10cm

        # DO CUT
        total_product_shapes = len(self.cut_polygons)
        n = 0
        for element in self.cut_polygons:
            #print('{}/{} background elements processed ...'.format(n, total_product_shapes), end='\r', flush=True)
            print('{}/{} cut polygons processed ...'.format(n, total_product_shapes))
            print('{} resolved pixels'.format(len(self.resolved_pixels)))
            n += 1
            self.process_grid(element['geometry_face'], resolution)

        # DO BACKGROUND
        total_product_shapes = len(self.background_elements)
        n = 0
        for element in self.background_elements:
            #print('{}/{} background elements processed ...'.format(n, total_product_shapes), end='\r', flush=True)
            print('{}/{} background elements processed ...'.format(n, total_product_shapes))
            print('{} resolved pixels'.format(len(self.resolved_pixels)))
            n += 1
            if element['type'] != 'polygon':
                background_elements.append(element)
                continue
            is_visible = self.process_grid(element['geometry_face'], resolution)
            if is_visible:
                background_elements.append(element)

        print('##### BEFORE it had {} and after it had {}'.format(
            len(self.background_elements), len(background_elements)))
        self.background_elements = background_elements
        return

    def create_section_box(self):
        top_left_corner = OCC.gp.gp_Pnt(
            self.section_box['top_left_corner'][0],
            self.section_box['top_left_corner'][1],
            self.section_box['top_left_corner'][2])
        axis = OCC.gp.gp_Ax2(
            top_left_corner,
            OCC.gp.gp_Dir(
                self.section_box['projection'][0],
                self.section_box['projection'][1],
                self.section_box['projection'][2]),
            OCC.gp.gp_Dir(
                self.section_box['x_axis'][0],
                self.section_box['x_axis'][1],
                self.section_box['x_axis'][2])
            )
        section_box = OCC.BRepPrimAPI.BRepPrimAPI_MakeBox(
            axis, self.section_box['x'], self.section_box['y'], self.section_box['z']
            )
        self.section_box['shape'] = section_box.Shape()
        self.section_box['face'] = section_box.BottomFace()

        source = OCC.gp.gp_Ax3(axis)
        self.transformation_data = {
            'top_left_corner': self.section_box['top_left_corner'],
            'projection': self.section_box['projection'],
            'x_axis': self.section_box['x_axis']
        }
        destination = OCC.gp.gp_Ax3(
            OCC.gp.gp_Pnt(0, 0, 0),
            OCC.gp.gp_Dir(0, 0, -1),
            OCC.gp.gp_Dir(1, 0, 0))
        self.transformation_dest = destination
        self.transformation = OCC.gp.gp_Trsf()
        self.transformation.SetDisplacement(source, destination)

    def get_background_elements(self):
        total_product_shapes = len(self.product_shapes)
        n = 0
        intersections = []
        compound = OCC.TopoDS.TopoDS_Compound()
        builder = OCC.BRep.BRep_Builder()
        builder.MakeCompound(compound)
        for product, shape in self.product_shapes:
            builder.Add(compound, shape)

            print('{}/{} background elements processed ...'.format(n, total_product_shapes), end='\r', flush=True)
            #print('Processing product {} '.format(product.Name))
            n += 1

            intersection = OCC.BRepAlgoAPI.BRepAlgoAPI_Common(self.section_box['shape'], shape).Shape()
            intersection_edges = self.get_booleaned_edges(intersection)
            if len(intersection_edges) <= 0:
                continue
            intersections.append(intersection)

            transformed_intersection = OCC.BRepBuilderAPI.BRepBuilderAPI_Transform(
                intersection, self.transformation)
            intersection = transformed_intersection.Shape()

            edge_face_map = OCC.TopTools.TopTools_IndexedDataMapOfShapeListOfShape()
            OCC.TopExp.topexp.MapShapesAndAncestors(
                    intersection, OCC.TopAbs.TopAbs_EDGE,
                    OCC.TopAbs.TopAbs_FACE, edge_face_map)

            exp = OCC.TopExp.TopExp_Explorer(intersection, OCC.TopAbs.TopAbs_FACE)
            while exp.More():
                face = topods.Face(exp.Current())
                normal = self.get_normal(face)
                # Cull back-faces
                if normal.Z() <= 0:
                    exp.Next()
                    continue
                zpos, zmax = self.calculate_face_zpos(face)
                self.build_new_face(face, zpos, product)
                self.get_split_edges(edge_face_map, face, zmax, product)
                exp.Next()

    def get_raycast_hits(self, shape):
        resolution = 0.1 # 5cm
        hits = []
        current_x = 0
        current_y = 0
        while current_x < self.section_box['x'] /2:
            current_y = 0
            while current_y < self.section_box['y']/4:
                point = numpy.array(self.section_box['top_left_corner'])
                point = numpy.add(point, current_x * numpy.array(self.section_box['x_axis']))
                point = numpy.add(point, current_y * numpy.array(self.section_box['y_axis']))
                hit = self.raycast(shape, point)
                if hit:
                    hits.append(hit)
                current_y += resolution
            current_x += resolution
            print('row down')
        return hits

    def raycast(self, shape, point):
        raycast = OCC.IntCurvesFace.IntCurvesFace_ShapeIntersector()
        raycast.Load(shape, 0.01)
        line = OCC.gp.gp_Lin(
            OCC.gp.gp_Pnt(float(point[0]), float(point[1]), float(point[2])),
            OCC.gp.gp_Dir( 0, 0, -1))
        raycast.Perform(line, 0, self.section_box['z'])
        return raycast.NbPnt() != 0

    def raycast_at_projection_dir(self, shape, point):
        raycast = OCC.IntCurvesFace.IntCurvesFace_ShapeIntersector()
        raycast.Load(shape, 0.01)
        line = OCC.gp.gp_Lin(
            OCC.gp.gp_Pnt(float(point[0]), float(point[1]), float(point[2])),
            OCC.gp.gp_Dir(
                self.section_box['projection'][0],
                self.section_box['projection'][1],
                self.section_box['projection'][2]))
        raycast.Perform(line, 0, self.section_box['z'])
        if raycast.NbPnt() != 0:
            # The smaller WParameter is the closer z-index
            # Should be the first
            return { 'face': raycast.Face(1), 'z': raycast.WParameter(1) }

    def get_bbox(self, shape):
        bbox = OCC.Bnd.Bnd_Box()
        OCC.BRepBndLib.brepbndlib_Add(shape, bbox)
        return bbox

    def calculate_face_zpos(self, face):
        bbox = self.get_bbox(face)
        xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
        zpos = zmin + ((zmax - zmin)/2)
        return zpos, zmax

    def get_split_edges(self, edge_face_map, face, zmax, product):
        exp2 = OCC.TopExp.TopExp_Explorer(face, OCC.TopAbs.TopAbs_EDGE)
        while exp2.More():
            edge = topods.Edge(exp2.Current())
            adjface = OCC.TopoDS.TopoDS_Face()
            getadj = OCC.TopOpeBRepBuild.TopOpeBRepBuild_Tools.GetAdjacentFace(face, edge, edge_face_map, adjface)
            if getadj:
                try:
                    edge_angle = math.degrees(self.get_angle_between_faces(face, adjface))
                except:
                    # TODO: Figure out when a math domain error might occur,
                    # because it does, sometimes.
                    edge_angle = 0
                if edge_angle > 30 and edge_angle < 160:
                    newedge = self.build_new_edge(edge, zmax+0.01)
                    if newedge:
                        self.background_elements.append({
                            'raw': product,
                            'geometry': newedge,
                            'type': 'line',
                            'z': zmax+0.01
                            })
            exp2.Next()

    def get_angle_between_faces(self, f1, f2):
        return self.convert_dot_product_to_angle(
            self.get_dot_product_of_normals(
                self.get_normal(f1), self.get_normal(f2)))

    def get_normal(self, face):
        surface = OCC.Geom.Handle_Geom_Surface(OCC.BRep.BRep_Tool.Surface(face))
        props = OCC.GeomLProp.GeomLProp_SLProps(surface, 0, 0, 1, .001)
        return props.Normal()

    def get_dot_product_of_normals(self, n1, n2):
        return n1.X() * n2.X() + n1.Y() * n2.Y() + n1.Z() * n2.Z()

    def convert_dot_product_to_angle(self, dp):
        return math.acos(dp)

    def is_same_point(self, p1, p2):
        return p1.X() == p2.X() \
            and p1.Y() == p2.Y() \
            and p1.Z() == p2.Z()

    def build_new_edge(self, edge, zpos):
        exp = OCC.TopExp.TopExp_Explorer(edge, OCC.TopAbs.TopAbs_VERTEX)
        new_vertices = []
        while exp.More():
            current_vertex = topods.Vertex(exp.Current())
            current_point = OCC.BRep.BRep_Tool.Pnt(current_vertex)
            current_point.SetZ(zpos)
            new_vertices.append(OCC.BRepBuilderAPI.BRepBuilderAPI_MakeVertex(current_point).Vertex())
            exp.Next()
        try:
            return OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(
                new_vertices[0], new_vertices[1]
            ).Edge()
        except:
            return None

    def build_new_face(self, face, zpos, product):
        exp = OCC.TopExp.TopExp_Explorer(face, OCC.TopAbs.TopAbs_WIRE)
        while exp.More():
            wireexp = OCC.BRepTools.BRepTools_WireExplorer(topods.Wire(exp.Current()))
            new_wire_builder = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeWire()
            first_vertex = None
            previous_vertex = None
            while wireexp.More():
                current_vertex = wireexp.CurrentVertex()
                current_point = OCC.BRep.BRep_Tool.Pnt(current_vertex)
                # Dodgy technique to squash in Z axis
                current_point.SetZ(zpos)
                current_vertex = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeVertex(current_point).Vertex()
                if not first_vertex:
                    first_vertex = current_vertex
                if not previous_vertex:
                    previous_vertex = current_vertex
                else:
                    try:
                        new_wire_builder.Add(topods.Edge(
                            OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(
                                previous_vertex, current_vertex
                            ).Edge()))
                        previous_vertex = current_vertex
                    except:
                        pass
                wireexp.Next()

                # make last edge
                if not wireexp.More():
                    try:
                        new_wire_builder.Add(topods.Edge(
                            OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(
                                current_vertex, first_vertex
                            ).Edge()))
                    except:
                        pass
            try:
                new_wire = new_wire_builder.Wire()
                new_face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(new_wire).Face()
                self.background_elements.append({
                    'raw': product,
                    'geometry': new_wire,
                    'geometry_face': new_face,
                    'type': 'polygon',
                    'z': zpos
                    })
            except:
                #print('Could not build face')
                pass
            exp.Next()

    def get_area(self, shape):
        gprops = OCC.GProp.GProp_GProps()
        OCC.BRepGProp.brepgprop.SurfaceProperties(shape, gprops)
        return gprops.Mass()

    def get_booleaned_edges(self, shape):
        edges = []
        exp = OCC.TopExp.TopExp_Explorer(shape, OCC.TopAbs.TopAbs_EDGE)
        while exp.More():
            edges.append(topods.Edge(exp.Current()))
            exp.Next()
        return edges

    def get_cut_polygons(self):
        if self.should_recut:
            self.get_fresh_cut_polygons()
            self.pickle_cut_polygons()
        else:
            self.get_pickled_cut_polygons()

    def pickle_cut_polygons(self):
        with open(self.cut_pickle_file, 'wb') as pickle_file:
            pickle.dump(self.cut_polygons, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    def get_fresh_cut_polygons(self):
        process_data = [(p.GlobalId, s, self.section_box['face'], self.transformation_data) for p, s in self.product_shapes]

        import multiprocessing
        import bpy
        multiprocessing.set_executable(bpy.app.binary_path_python)

        with multiprocessing.Pool(9) as p:
            results = p.map(do_cut, process_data)
            for result in results:
                polygons = [self.get_polygon_metadata(p, 'cut') for p in result if p['points']]
                self.cut_polygons.extend(polygons)

    def get_polygon_metadata(self, polygon, position):
        polygon['metadata'] = {
            'classes': self.get_classes(self.get_ifc_element(polygon['global_id']), position)
        }
        return polygon

    def get_ifc_element(self, global_id):
        # TODO: make this less bad
        element = None
        for ifc_file in self.ifc_files:
            try:
                element = ifc_file.by_id(global_id)
                return element
            except:
                pass

    def get_classes(self, element, position):
        classes = [position, element.is_a()]
        for association in element.HasAssociations:
            if association.is_a('IfcRelAssociatesMaterial'):
                classes.append('material-{}'.format(self.get_material_name(association.RelatingMaterial)))
        classes.append('globalid-{}'.format(element.GlobalId))
        return classes

    def get_material_name(self, element):
        if hasattr(element, 'Name') and element.Name:
            return element.Name
        return element.id()

    def get_pickled_cut_polygons(self):
        if os.path.isfile(self.cut_pickle_file):
            with open(self.cut_pickle_file, 'rb') as pickle_file:
                self.cut_polygons = pickle.load(pickle_file)


class IfcCutterDebug(IfcCutter):
    def cut(self):
        self.occ_display = ifcopenshell.geom.utils.initialize_display()
        super().cut()

    def create_section_box(self):
        super().create_section_box()
        self.display_everything_with_section_plane()

    def get_cut_polygons(self):
        super().get_cut_polygons()
        self.display_cut_polygons()

    def get_background_elements(self):
        super().get_background_elements()
        self.display_background_elements()

    def display_everything_with_section_plane(self):
        section_face_display = ifcopenshell.geom.utils.display_shape(self.section_box['face'])
        ifcopenshell.geom.utils.set_shape_transparency(section_face_display, 0.8)
        section_box_display = ifcopenshell.geom.utils.display_shape(self.section_box['shape'])
        ifcopenshell.geom.utils.set_shape_transparency(section_box_display, 0.5)

        transformed_box = OCC.BRepBuilderAPI.BRepBuilderAPI_Transform(
            self.section_box['shape'], self.transformation)
        box_display = ifcopenshell.geom.utils.display_shape(transformed_box.Shape())
        ifcopenshell.geom.utils.set_shape_transparency(box_display, 0.2)

        for shape in self.product_shapes:
            ifcopenshell.geom.utils.display_shape(shape[1])
        input('Debug: showing everything with section plane.')

    def display_cut_polygons(self):
        self.occ_display.EraseAll()
        for polygon in self.cut_polygons:
            ifcopenshell.geom.utils.display_shape(polygon['geometry'], clr='BLACK')
            face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(polygon['geometry']).Face()
            face_display = ifcopenshell.geom.utils.display_shape(face)
            ifcopenshell.geom.utils.set_shape_transparency(face_display, 0.5)
        input('Debug: showing cut polygons.')

    def display_background_elements(self):
        self.occ_display.EraseAll()
        for element in self.background_elements:
            if element['type'] == 'line':
                ifcopenshell.geom.utils.display_shape(element['geometry'], clr='PURPLE')
            elif element['type'] == 'polyline':
                ifcopenshell.geom.utils.display_shape(element['geometry_face'], clr='RED')
            elif element['type'] == 'polygon':
                ifcopenshell.geom.utils.display_shape(element['geometry_face'])
        input('Debug: showing background elements.')


class External(svgwrite.container.Group):
    def __init__(self, xml, **extra):
        self.xml = xml

        # Remove namespace
        ns = u'{http://www.w3.org/2000/svg}'
        nsl = len(ns)
        for elem in self.xml.getiterator():
            if elem.tag.startswith(ns):
                elem.tag = elem.tag[nsl:]

        super(External, self).__init__(**extra)

    def get_xml(self):
        return self.xml


class SvgWriter():
    def __init__(self, ifc_cutter):
        self.ifc_cutter = ifc_cutter
        self.human_scale = 'NTS'
        self.scale = 1 / 100 # 1:100

    def write(self):
        self.calculate_scale()
        self.output = os.path.join(
            self.ifc_cutter.data_dir,
            'diagrams',
            self.ifc_cutter.diagram_name + '.svg'
        )
        self.svg = svgwrite.Drawing(
            self.output,
            debug=False,
            size=('{}mm'.format(self.width), '{}mm'.format(self.height)),
            viewBox=('0 0 {} {}'.format(self.width, self.height)),
            id='root',
            data_scale=self.human_scale
        )

        self.add_stylesheet()
        self.add_markers()
        self.add_symbols()
        self.add_patterns()
        self.draw_background_image()
        self.draw_background_elements()
        self.draw_cut_polygons()
        self.draw_annotations()
        self.svg.save(pretty=True)

    def calculate_scale(self):
        # TODO: properly handle units
        if self.ifc_cutter.unit == 'METRE':
            self.scale *= 1000
        self.raw_width = self.ifc_cutter.section_box['x']
        self.raw_height = self.ifc_cutter.section_box['y']
        self.width = self.raw_width * self.scale
        self.height = self.raw_height * self.scale

    def add_stylesheet(self):
        with open('{}styles/default.css'.format(self.ifc_cutter.data_dir), 'r') as stylesheet:
            self.svg.defs.add(self.svg.style(stylesheet.read()))

    def add_markers(self):
        tree = ET.parse('{}templates/markers.svg'.format(self.ifc_cutter.data_dir))
        root = tree.getroot()
        for child in root.getchildren():
            self.svg.defs.add(External(child))

    def add_symbols(self):
        tree = ET.parse('{}templates/symbols.svg'.format(self.ifc_cutter.data_dir))
        root = tree.getroot()
        for child in root.getchildren():
            self.svg.defs.add(External(child))

    def add_patterns(self):
        return
        tree = ET.parse('{}templates/patterns.svg'.format(self.ifc_cutter.data_dir))
        root = tree.getroot()
        for child in root.getchildren():
            self.svg.defs.add(External(child))

    def draw_background_image(self):
        self.svg.add(self.svg.image(
            os.path.join('..', 'diagrams', os.path.basename(self.ifc_cutter.background_image)), **{
                'width': self.width,
                'height': self.height
            }
        ))

    def draw_background_elements(self):
        for element in self.ifc_cutter.background_elements:
            if element['type'] == 'polygon':
                self.draw_polygon(element, 'background')
            elif element['type'] == 'polyline':
                self.draw_polyline(element, 'background')
            elif element['type'] == 'line':
                self.draw_line(element, 'background')

    def draw_annotations(self):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2

        if self.ifc_cutter.equal_obj:
            self.draw_dimension_annotations(self.ifc_cutter.equal_obj, text_override='EQ')
        if self.ifc_cutter.dimension_obj:
            self.draw_dimension_annotations(self.ifc_cutter.dimension_obj)

        for grid_obj in self.ifc_cutter.grid_objs:
            matrix_world = grid_obj.matrix_world
            for edge in grid_obj.data.edges:
                classes = ['annotation', 'grid']
                v0_global = matrix_world @ grid_obj.data.vertices[edge.vertices[0]].co.xyz
                v1_global = matrix_world @ grid_obj.data.vertices[edge.vertices[1]].co.xyz
                v0 = self.project_point_onto_camera(v0_global)
                v1 = self.project_point_onto_camera(v1_global)
                start = Vector(((x_offset + v0.x), (y_offset - v0.y)))
                end = Vector(((x_offset + v1.x), (y_offset - v1.y)))
                vector = end - start
                line = self.svg.add(self.svg.line(start=tuple(start * self.scale),
                    end=tuple(end * self.scale), class_=' '.join(classes)))
                line['marker-start'] = 'url(#grid-marker)'
                line['marker-end'] = 'url(#grid-marker)'
                line['stroke-dasharray'] = '12.5, 3, 3, 3'
                self.svg.add(self.svg.text(grid_obj.name.split('/')[1], insert=tuple(start * self.scale), **{
                    'font-size': annotation.Annotator.get_svg_text_size(5.0),
                    'font-family': 'OpenGost Type B TT',
                    'text-anchor': 'middle',
                    'alignment-baseline': 'middle',
                    'dominant-baseline': 'middle'
                }))
                self.svg.add(self.svg.text(grid_obj.name.split('/')[1], insert=tuple(end * self.scale), **{
                    'font-size': annotation.Annotator.get_svg_text_size(5.0),
                    'font-family': 'OpenGost Type B TT',
                    'text-anchor': 'middle',
                    'alignment-baseline': 'middle',
                    'dominant-baseline': 'middle'
                }))

        if self.ifc_cutter.hidden_obj:
            matrix_world = self.ifc_cutter.hidden_obj.matrix_world
            for edge in self.ifc_cutter.hidden_obj.data.edges:
                classes = ['annotation', 'hidden']
                v0_global = matrix_world @ self.ifc_cutter.hidden_obj.data.vertices[edge.vertices[0]].co.xyz
                v1_global = matrix_world @ self.ifc_cutter.hidden_obj.data.vertices[edge.vertices[1]].co.xyz
                v0 = self.project_point_onto_camera(v0_global)
                v1 = self.project_point_onto_camera(v1_global)
                start = Vector(((x_offset + v0.x), (y_offset - v0.y)))
                end = Vector(((x_offset + v1.x), (y_offset - v1.y)))
                vector = end - start
                line = self.svg.add(self.svg.line(start=tuple(start * self.scale),
                    end=tuple(end * self.scale), class_=' '.join(classes)))
                line['stroke-dasharray'] = '3, 2'

        if self.ifc_cutter.leader_obj:
            matrix_world = self.ifc_cutter.leader_obj.matrix_world
            for spline in self.ifc_cutter.leader_obj.data.splines:
                classes = ['annotation', 'leader']
                points = self.get_spline_points(spline)
                projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
                d = ' '.join(['L {} {}'.format(
                    (x_offset + p.x) * self.scale, (y_offset - p.y) * self.scale)
                    for p in projected_points])
                d = 'M{}'.format(d[1:])
                path = self.svg.add(self.svg.path(d=d, class_=' '.join(classes)))
                path['marker-end'] = 'url(#leader-marker)'

        if self.ifc_cutter.plan_level_obj:
            for spline in self.ifc_cutter.plan_level_obj.data.splines:
                classes = ['annotation', 'plan-level']
                points = self.get_spline_points(spline)
                d = ' '.join(['L {} {}'.format((x_offset + p.co.x) * self.scale, (y_offset - p.co.y) * self.scale) for p in points])
                d = 'M{}'.format(d[1:])
                path = self.svg.add(self.svg.path(d=d, class_=' '.join(classes)))
                path['marker-end'] = 'url(#plan-level-marker)'
                text_position = Vector((
                    (x_offset + points[0].co.x) * self.scale,
                    ((y_offset - points[0].co.y) * self.scale) - 2.5
                ))
                # TODO: unhardcode m unit
                rl = ((self.ifc_cutter.plan_level_obj.matrix_world @
                    points[0].co).xyz + self.ifc_cutter.plan_level_obj.location).z
                if points[0].co.x > points[-1].co.x:
                    text_anchor = 'end'
                else:
                    text_anchor = 'start'
                self.svg.add(self.svg.text('RL +{:.3f}m'.format(rl), insert=tuple(text_position), **{
                    'font-size': annotation.Annotator.get_svg_text_size(2.5),
                    'font-family': 'OpenGost Type B TT',
                    'text-anchor': text_anchor,
                    'alignment-baseline': 'baseline',
                    'dominant-baseline': 'baseline'
                }))

        if self.ifc_cutter.section_level_obj:
            matrix_world = self.ifc_cutter.section_level_obj.matrix_world
            for spline in self.ifc_cutter.section_level_obj.data.splines:
                classes = ['annotation', 'section-level']
                points = self.get_spline_points(spline)
                projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
                d = ' '.join(['L {} {}'.format(
                    (x_offset + p.x) * self.scale, (y_offset - p.y) * self.scale)
                    for p in projected_points])
                d = 'M{}'.format(d[1:])
                path = self.svg.add(self.svg.path(d=d, class_=' '.join(classes)))
                path['marker-start'] = 'url(#section-level-marker)'
                path['stroke-dasharray'] = '12.5, 3, 3, 3'
                text_position = Vector((
                    (x_offset + projected_points[0].x) * self.scale,
                    ((y_offset - projected_points[0].y) * self.scale) - 3.5
                ))
                # TODO: unhardcode m unit
                rl = (matrix_world @ points[0].co.xyz).z
                self.svg.add(self.svg.text('RL +{:.3f}m'.format(rl), insert=tuple(text_position), **{
                    'font-size': annotation.Annotator.get_svg_text_size(2.5),
                    'font-family': 'OpenGost Type B TT',
                    'text-anchor': 'start',
                    'alignment-baseline': 'baseline',
                    'dominant-baseline': 'baseline'
                }))

        if self.ifc_cutter.stair_obj:
            for spline in self.ifc_cutter.stair_obj.data.splines:
                classes = ['annotation', 'stair']
                points = self.get_spline_points(spline)
                d = ' '.join(['L {} {}'.format((x_offset + p.co.x) * self.scale, (y_offset - p.co.y) * self.scale) for p in points])
                d = 'M{}'.format(d[1:])
                start = Vector(((x_offset + points[0].co.x), (y_offset - points[0].co.y)))
                next_point = Vector(((x_offset + points[1].co.x), (y_offset - points[1].co.y)))
                text_position = (start * self.scale) - ((next_point - start).normalized() * 5)
                path = self.svg.add(self.svg.path(d=d, class_=' '.join(classes)))
                path['marker-start'] = 'url(#stair-marker-start)'
                path['marker-end'] = 'url(#stair-marker-end)'
                self.svg.add(self.svg.text('UP', insert=tuple(text_position), **{
                    'font-size': annotation.Annotator.get_svg_text_size(2.5),
                    'font-family': 'OpenGost Type B TT',
                    'text-anchor': 'middle',
                    'alignment-baseline': 'middle',
                    'dominant-baseline': 'middle'
                }))

        self.draw_text_annotations()

    def draw_text_annotations(self):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2

        for text_obj in self.ifc_cutter.text_objs:
            loc, rot, scale = self.ifc_cutter.camera_obj.matrix_world.decompose()
            pos = (text_obj.location - self.ifc_cutter.camera_obj.location) @ rot.to_matrix()
            text_position = Vector(((x_offset + pos.x), (y_offset - pos.y)))

            if text_obj.data.BIMTextProperties.symbol != 'None':
                self.svg.add(self.svg.use(
                    '#{}'.format(text_obj.data.BIMTextProperties.symbol),
                    insert=tuple(text_position * self.scale)
                ))

            if text_obj.data.align_x == 'CENTER':
                text_anchor = 'middle'
            elif text_obj.data.align_x == 'RIGHT':
                text_anchor = 'end'
            else:
                text_anchor = 'start'

            if text_obj.data.align_y == 'CENTER':
                alignment_baseline = 'middle'
            elif text_obj.data.align_y == 'TOP':
                alignment_baseline = 'hanging'
            else:
                alignment_baseline = 'baseline'

            text_body = text_obj.data.body
            if text_obj.name in self.ifc_cutter.template_variables:
                text_body = pystache.render(text_body, self.ifc_cutter.template_variables[text_obj.name])

            for line_number, text_line in enumerate(text_body.split('\n')):
                self.svg.add(self.svg.text(
                    text_line,
                    insert=tuple((text_position * self.scale) + Vector((0, 3.5*line_number))),
                    **{
                        'font-size': annotation.Annotator.get_svg_text_size(text_obj.data.BIMTextProperties.font_size),
                        'font-family': 'OpenGost Type B TT',
                        'text-anchor': text_anchor,
                        'alignment-baseline': alignment_baseline,
                        'dominant-baseline': alignment_baseline
                    }
                ))

    def draw_dimension_annotations(self, dimension_obj, text_override=None):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2

        matrix_world = dimension_obj.matrix_world
        for spline in dimension_obj.data.splines:
            points = self.get_spline_points(spline)
            for i, p in enumerate(points):
                if i+1 >= len(points):
                    continue
                classes = ['annotation', 'dimension', 'blahblah']
                v0_global = matrix_world @ points[i].co.xyz
                v1_global = matrix_world @ points[i+1].co.xyz
                v0 = self.project_point_onto_camera(v0_global)
                v1 = self.project_point_onto_camera(v1_global)
                start = Vector(((x_offset + v0.x), (y_offset - v0.y)))
                end = Vector(((x_offset + v1.x), (y_offset - v1.y)))
                mid = ((end - start) / 2) + start
                # TODO: hardcoded meters to mm conversion, until I properly do units
                vector = end - start
                perpendicular = Vector((vector.y, -vector.x)).normalized()
                dimension = (v1_global - v0_global).length * 1000
                sheet_dimension = ((end*self.scale) - (start*self.scale)).length
                if sheet_dimension < 5: # annotation can't fit
                    # offset text to right of marker
                    text_position = (end * self.scale) + perpendicular + (3 * vector.normalized())
                else:
                    text_position = (mid * self.scale) + perpendicular
                rotation = degrees(vector.angle_signed(Vector((1, 0))))
                line = self.svg.add(self.svg.line(start=tuple(start * self.scale),
                    end=tuple(end * self.scale), class_=' '.join(classes)))
                line['marker-start'] = 'url(#dimension-marker-start)'
                line['marker-end'] = 'url(#dimension-marker-end)'
                if text_override is not None:
                    text = text_override
                else:
                    text = str(round(dimension))
                self.svg.add(self.svg.text(text, insert=tuple(text_position), **{
                    'transform': 'rotate({} {} {})'.format(
                        rotation,
                        text_position.x,
                        text_position.y
                    ),
                    'font-size': annotation.Annotator.get_svg_text_size(2.5),
                    'font-family': 'OpenGost Type B TT',
                    'text-anchor': 'middle'
                }))

    def project_point_onto_camera(self, point):
        return self.ifc_cutter.camera_obj.matrix_world.inverted() @ geometry.intersect_line_plane(
            point.xyz,
            point.xyz-Vector(self.ifc_cutter.section_box['projection']),
            self.ifc_cutter.camera_obj.location,
            Vector(self.ifc_cutter.section_box['projection'])
            )

    def get_spline_points(self, spline):
        return spline.bezier_points if spline.bezier_points else spline.points

    def draw_cut_polygons(self):
        for polygon in self.ifc_cutter.cut_polygons:
            self.draw_polygon(polygon, 'cut')

    def draw_polyline(self, element, position):
        classes = self.get_classes(element['raw'], position)
        exp = OCC.BRepTools.BRepTools_WireExplorer(element['geometry'])
        points = []
        while exp.More():
            point = OCC.BRep.BRep_Tool.Pnt(exp.CurrentVertex())
            points.append((point.X() * self.scale, -point.Y() * self.scale))
            exp.Next()
        self.svg.add(self.svg.polyline(points=points, class_=' '.join(classes)))

    def draw_line(self, element, position):
        classes = self.get_classes(element['raw'], position)
        exp = OCC.TopExp.TopExp_Explorer(element['geometry'], OCC.TopAbs.TopAbs_VERTEX)
        points = []
        while exp.More():
            point = OCC.BRep.BRep_Tool.Pnt(topods.Vertex(exp.Current()))
            points.append((point.X() * self.scale, -point.Y() * self.scale))
            exp.Next()
        self.svg.add(self.svg.line(start=points[0], end=points[1], class_=' '.join(classes)))

    def draw_polygon(self, polygon, position):
        points = [(p[0] * self.scale, p[1] * self.scale) for p in polygon['points']]
        self.svg.add(self.svg.polygon(points=points, class_=' '.join(polygon['metadata']['classes'])))
