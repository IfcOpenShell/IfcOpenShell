import os
import math
import time
import numpy
import pickle
import sys

try:
    from OCC.Core import (
        gp,
        Geom,
        Bnd,
        BRepBndLib,
        BRep,
        BRepPrimAPI,
        BRepAlgoAPI,
        BRepBuilderAPI,
        TopOpeBRepTool,
        TopOpeBRepBuild,
        ShapeExtend,
        GProp,
        BRepGProp,
        GC,
        ShapeAnalysis,
        TopTools,
        TopExp,
        TopAbs,
        HLRAlgo,
        HLRBRep,
        TopLoc,
        Bnd,
        BRepBndLib,
        BRepTools,
        TopoDS,
        GeomLProp,
        IntCurvesFace,
    )
    from OCC.Core.TopoDS import topods
except ImportError:
    from OCC import (
        gp,
        Geom,
        Bnd,
        BRepBndLib,
        BRep,
        BRepPrimAPI,
        BRepAlgoAPI,
        BRepBuilderAPI,
        TopOpeBRepTool,
        TopOpeBRepBuild,
        ShapeExtend,
        GProp,
        BRepGProp,
        GC,
        ShapeAnalysis,
        TopTools,
        TopExp,
        TopAbs,
        HLRAlgo,
        HLRBRep,
        TopLoc,
        Bnd,
        BRepBndLib,
        BRepTools,
        TopoDS,
        GeomLProp,
        IntCurvesFace,
    )
    from OCC.TopoDS import topods

import ifcopenshell
import ifcopenshell.geom

cwd = os.path.dirname(os.path.realpath(__file__))
this_file = os.path.join(cwd, 'cut_ifc.py')

def get_booleaned_edges(shape):
    edges = []
    exp = TopExp.TopExp_Explorer(shape, TopAbs.TopAbs_EDGE)
    while exp.More():
        edges.append(topods.Edge(exp.Current()))
        exp.Next()
    return edges

def connect_edges_into_wires(unconnected_edges):
    edges = TopTools.TopTools_HSequenceOfShape()
    edges_handle = TopTools.Handle_TopTools_HSequenceOfShape(edges)
    wires = TopTools.TopTools_HSequenceOfShape()
    wires_handle = TopTools.Handle_TopTools_HSequenceOfShape(wires)

    for edge in unconnected_edges:
        edges.Append(edge)

    ShapeAnalysis.ShapeAnalysis_FreeBounds.ConnectEdgesToWires(edges_handle, 1e-5, True, wires_handle)
    return wires_handle.GetObject()

def do_cut(process_data):
    global_id, shape, section, trsf_data = process_data

    axis = gp.gp_Ax2(
        gp.gp_Pnt(
            trsf_data['top_left_corner'][0],
            trsf_data['top_left_corner'][1],
            trsf_data['top_left_corner'][2]),
        gp.gp_Dir(
            trsf_data['projection'][0],
            trsf_data['projection'][1],
            trsf_data['projection'][2]),
        gp.gp_Dir(
            trsf_data['x_axis'][0],
            trsf_data['x_axis'][1],
            trsf_data['x_axis'][2])
        )
    source = gp.gp_Ax3(axis)
    destination = gp.gp_Ax3(
        gp.gp_Pnt(0, 0, 0),
        gp.gp_Dir(0, 0, -1),
        gp.gp_Dir(1, 0, 0))
    transformation = gp.gp_Trsf()
    transformation.SetDisplacement(source, destination)

    cut_polygons = []
    section = BRepAlgoAPI.BRepAlgoAPI_Section(section, shape).Shape()
    section_edges = get_booleaned_edges(section)
    if len(section_edges) <= 0:
        return cut_polygons
    wires = connect_edges_into_wires(section_edges)
    for i in range(wires.Length()):
        wire_shape = wires.Value(i+1)

        transformed_wire = BRepBuilderAPI.BRepBuilderAPI_Transform(
            wire_shape, transformation)
        wire_shape = transformed_wire.Shape()

        wire = topods.Wire(wire_shape)
        face = BRepBuilderAPI.BRepBuilderAPI_MakeFace(wire).Face()

        points = []
        exp = BRepTools.BRepTools_WireExplorer(wire)
        while exp.More():
            point = BRep.BRep_Tool.Pnt(exp.CurrentVertex())
            points.append((point.X(), -point.Y()))
            exp.Next()
        cut_polygons.append({ 'global_id': global_id, 'metadata': {}, 'points': points })
    return cut_polygons


class IfcCutter:
    def __init__(self):
        self.ifc_attribute_extractor = None
        self.product_shapes = []
        self.background_elements = []
        self.cut_polygons = []
        self.template_variables = {}
        self.metadata = {}
        self.data_dir = ''
        self.ifc_filenames = []
        self.ifc_files = {}
        self.resolved_pixels = set()
        self.should_get_background = False
        self.text_pickle_file = 'text.pickle'
        self.metadata_pickle_file = 'metadata.pickle'
        self.cut_pickle_file = 'cut.pickle'
        self.should_recut = True
        self.should_recut_selected = True
        self.selected_global_ids = []
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
        start_time = time.time()
        print('# Get cut polygon metadata')
        self.get_cut_polygon_metadata()
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
        for filename in self.ifc_filenames:
            print('Loading file {} ...'.format(filename))
            if filename:
                self.ifc_files[filename] = ifcopenshell.open(filename)

    def get_template_variables(self):
        if not self.should_extract:
            if os.path.isfile(self.text_pickle_file):
                with open(self.text_pickle_file, 'rb') as text_file:
                    self.template_variables = pickle.load(text_file)
            return

        data = {}
        for text_obj in self.text_objs:
            text_obj_data = self.get_text_variables(text_obj)
            if text_obj_data:
                data[text_obj.name] = text_obj_data

        with open(self.text_pickle_file, 'wb') as text_file:
            pickle.dump(data, text_file, protocol=pickle.HIGHEST_PROTOCOL)

        self.template_variables = data

    def get_text_variables(self, text_obj):
        text_obj_data = {}
        text_body = text_obj.data.body
        related_element = text_obj.data.BIMTextProperties.related_element
        if not related_element:
            return
        global_id = related_element.BIMObjectProperties.attributes.get('GlobalId')
        if not global_id:
            return
        element = self.get_ifc_element(global_id.string_value)
        for variable in text_obj.data.BIMTextProperties.variables:
            if element:
                if '{{' in variable.prop_key:
                    prop_key = variable.prop_key.split('{{')[1].split('}}')[0]
                    prop_value = self.ifc_attribute_extractor.get_element_key(element, prop_key)
                    variable_value = eval(variable.prop_key.replace('{{' + prop_key + '}}', str(prop_value)))
                else:
                    variable_value = self.ifc_attribute_extractor.get_element_key(element, variable.prop_key)
                text_obj_data[variable.name] = variable_value
        return text_obj_data

    def get_product_shapes(self):
        if not self.should_recut:
            return

        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_PYTHON_OPENCASCADE, True)
        products = []

        for filename, ifc_file in self.ifc_files.items():
            shape_pickle = os.path.join(
                self.data_dir, 'cache', 'shapes', '{}.pickle'.format(os.path.basename(filename)))
            shape_map = {}
            if self.should_recut_selected and os.path.isfile(shape_pickle):
                with open(shape_pickle, 'rb') as shape_file:
                    shape_map = pickle.load(shape_file)

            # TODO: This should perhaps be configurable, e.g. spaces cut to show zones in the drawing
            products.extend(ifc_file.by_type('IfcElement'))

            total_products = len(products)
            for i, product in enumerate(products):
                print('{}/{} geometry processed ...'.format(i, total_products), end='\r', flush=True)
                if product.is_a('IfcOpeningElement') \
                        or product.is_a('IfcSite') \
                        or product.Representation is None \
                        or self.has_annotation(product):
                    continue
                try:
                    if self.should_recut_selected \
                            and product.GlobalId in self.selected_global_ids:
                        shape = ifcopenshell.geom.create_shape(settings, product).geometry
                        shape_map[product.GlobalId] = shape
                    elif product.GlobalId in shape_map:
                        shape = shape_map[product.GlobalId]
                    else:
                        shape = ifcopenshell.geom.create_shape(settings, product).geometry
                        shape_map[product.GlobalId] = shape
                    self.product_shapes.append((product, shape))
                except:
                    print('Failed to create shape for {}'.format(product))

            with open(shape_pickle, 'wb') as shape_file:
                pickle.dump(shape_map, shape_file, protocol=pickle.HIGHEST_PROTOCOL)

    def has_annotation(self, element):
        for representation in element.Representation.Representations:
            if representation.ContextOfItems.ContextType == 'Plan' \
                    and representation.ContextOfItems.ContextIdentifier == 'Annotation':
                return True
        return False

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
        top_left_corner = gp.gp_Pnt(
            self.section_box['top_left_corner'][0],
            self.section_box['top_left_corner'][1],
            self.section_box['top_left_corner'][2])
        axis = gp.gp_Ax2(
            top_left_corner,
            gp.gp_Dir(
                self.section_box['projection'][0],
                self.section_box['projection'][1],
                self.section_box['projection'][2]),
            gp.gp_Dir(
                self.section_box['x_axis'][0],
                self.section_box['x_axis'][1],
                self.section_box['x_axis'][2])
            )
        section_box = BRepPrimAPI.BRepPrimAPI_MakeBox(
            axis, self.section_box['x'], self.section_box['y'], self.section_box['z']
            )
        self.section_box['shape'] = section_box.Shape()
        self.section_box['face'] = section_box.BottomFace()

        source = gp.gp_Ax3(axis)
        self.transformation_data = {
            'top_left_corner': self.section_box['top_left_corner'],
            'projection': self.section_box['projection'],
            'x_axis': self.section_box['x_axis']
        }
        destination = gp.gp_Ax3(
            gp.gp_Pnt(0, 0, 0),
            gp.gp_Dir(0, 0, -1),
            gp.gp_Dir(1, 0, 0))
        self.transformation_dest = destination
        self.transformation = gp.gp_Trsf()
        self.transformation.SetDisplacement(source, destination)

    def get_background_elements(self):
        total_product_shapes = len(self.product_shapes)
        n = 0
        intersections = []
        compound = TopoDS.TopoDS_Compound()
        builder = BRep.BRep_Builder()
        builder.MakeCompound(compound)
        for product, shape in self.product_shapes:
            builder.Add(compound, shape)

            print('{}/{} background elements processed ...'.format(n, total_product_shapes), end='\r', flush=True)
            #print('Processing product {} '.format(product.Name))
            n += 1

            intersection = BRepAlgoAPI.BRepAlgoAPI_Common(self.section_box['shape'], shape).Shape()
            intersection_edges = self.get_booleaned_edges(intersection)
            if len(intersection_edges) <= 0:
                continue
            intersections.append(intersection)

            transformed_intersection = BRepBuilderAPI.BRepBuilderAPI_Transform(
                intersection, self.transformation)
            intersection = transformed_intersection.Shape()

            edge_face_map = TopTools.TopTools_IndexedDataMapOfShapeListOfShape()
            TopExp.topexp.MapShapesAndAncestors(
                    intersection, TopAbs.TopAbs_EDGE,
                    TopAbs.TopAbs_FACE, edge_face_map)

            exp = TopExp.TopExp_Explorer(intersection, TopAbs.TopAbs_FACE)
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
        raycast = IntCurvesFace.IntCurvesFace_ShapeIntersector()
        raycast.Load(shape, 0.01)
        line = gp.gp_Lin(
            gp.gp_Pnt(float(point[0]), float(point[1]), float(point[2])),
            gp.gp_Dir( 0, 0, -1))
        raycast.Perform(line, 0, self.section_box['z'])
        return raycast.NbPnt() != 0

    def raycast_at_projection_dir(self, shape, point):
        raycast = IntCurvesFace.IntCurvesFace_ShapeIntersector()
        raycast.Load(shape, 0.01)
        line = gp.gp_Lin(
            gp.gp_Pnt(float(point[0]), float(point[1]), float(point[2])),
            gp.gp_Dir(
                self.section_box['projection'][0],
                self.section_box['projection'][1],
                self.section_box['projection'][2]))
        raycast.Perform(line, 0, self.section_box['z'])
        if raycast.NbPnt() != 0:
            # The smaller WParameter is the closer z-index
            # Should be the first
            return { 'face': raycast.Face(1), 'z': raycast.WParameter(1) }

    def get_bbox(self, shape):
        bbox = Bnd.Bnd_Box()
        BRepBndLib.brepbndlib_Add(shape, bbox)
        return bbox

    def calculate_face_zpos(self, face):
        bbox = self.get_bbox(face)
        xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
        zpos = zmin + ((zmax - zmin)/2)
        return zpos, zmax

    def get_split_edges(self, edge_face_map, face, zmax, product):
        exp2 = TopExp.TopExp_Explorer(face, TopAbs.TopAbs_EDGE)
        while exp2.More():
            edge = topods.Edge(exp2.Current())
            adjface = TopoDS.TopoDS_Face()
            getadj = TopOpeBRepBuild.TopOpeBRepBuild_Tools.GetAdjacentFace(face, edge, edge_face_map, adjface)
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
        surface = Geom.Handle_Geom_Surface(BRep.BRep_Tool.Surface(face))
        props = GeomLProp.GeomLProp_SLProps(surface, 0, 0, 1, .001)
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
        exp = TopExp.TopExp_Explorer(edge, TopAbs.TopAbs_VERTEX)
        new_vertices = []
        while exp.More():
            current_vertex = topods.Vertex(exp.Current())
            current_point = BRep.BRep_Tool.Pnt(current_vertex)
            current_point.SetZ(zpos)
            new_vertices.append(BRepBuilderAPI.BRepBuilderAPI_MakeVertex(current_point).Vertex())
            exp.Next()
        try:
            return BRepBuilderAPI.BRepBuilderAPI_MakeEdge(
                new_vertices[0], new_vertices[1]
            ).Edge()
        except:
            return None

    def build_new_face(self, face, zpos, product):
        exp = TopExp.TopExp_Explorer(face, TopAbs.TopAbs_WIRE)
        while exp.More():
            wireexp = BRepTools.BRepTools_WireExplorer(topods.Wire(exp.Current()))
            new_wire_builder = BRepBuilderAPI.BRepBuilderAPI_MakeWire()
            first_vertex = None
            previous_vertex = None
            while wireexp.More():
                current_vertex = wireexp.CurrentVertex()
                current_point = BRep.BRep_Tool.Pnt(current_vertex)
                # Dodgy technique to squash in Z axis
                current_point.SetZ(zpos)
                current_vertex = BRepBuilderAPI.BRepBuilderAPI_MakeVertex(current_point).Vertex()
                if not first_vertex:
                    first_vertex = current_vertex
                if not previous_vertex:
                    previous_vertex = current_vertex
                else:
                    try:
                        new_wire_builder.Add(topods.Edge(
                            BRepBuilderAPI.BRepBuilderAPI_MakeEdge(
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
                            BRepBuilderAPI.BRepBuilderAPI_MakeEdge(
                                current_vertex, first_vertex
                            ).Edge()))
                    except:
                        pass
            try:
                new_wire = new_wire_builder.Wire()
                new_face = BRepBuilderAPI.BRepBuilderAPI_MakeFace(new_wire).Face()
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
        gprops = GProp.GProp_GProps()
        BRepGProp.brepgprop.SurfaceProperties(shape, gprops)
        return gprops.Mass()

    def get_booleaned_edges(self, shape):
        edges = []
        exp = TopExp.TopExp_Explorer(shape, TopAbs.TopAbs_EDGE)
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

    def get_cut_polygon_metadata(self):
        if not self.should_extract:
            if os.path.isfile(self.metadata_pickle_file):
                with open(self.metadata_pickle_file, 'rb') as metadata_file:
                    self.metadata = pickle.load(metadata_file)

            for polygon in self.cut_polygons:
                if polygon['global_id'] in self.metadata:
                    polygon['metadata'] = self.metadata[polygon['global_id']]
            return

        for polygon in self.cut_polygons:
            metadata = { 'classes': self.get_classes(self.get_ifc_element(polygon['global_id']), 'cut') }
            self.metadata[polygon['global_id']] = metadata
            polygon['metadata'] = metadata

        with open(self.metadata_pickle_file, 'wb') as metadata_file:
            pickle.dump(self.metadata, metadata_file, protocol=pickle.HIGHEST_PROTOCOL)

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
                polygons = [p for p in result if p['points']]
                self.cut_polygons.extend(polygons)

    def get_polygon_metadata(self, polygon, position):
        polygon['metadata'] = {
            'classes': self.get_classes(self.get_ifc_element(polygon['global_id']), position)
        }
        return polygon

    def get_ifc_element(self, global_id):
        # TODO: make this less bad
        element = None
        for ifc_file in self.ifc_files.values():
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

        transformed_box = BRepBuilderAPI.BRepBuilderAPI_Transform(
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
            face = BRepBuilderAPI.BRepBuilderAPI_MakeFace(polygon['geometry']).Face()
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
