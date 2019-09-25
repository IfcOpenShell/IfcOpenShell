import os
import math
import svgwrite
import time

import OCC.gp
import OCC.Geom
import OCC.Bnd
import OCC.BRepBndLib
import OCC.BRep
import OCC.BRepPrimAPI
import OCC.BRepAlgoAPI
import OCC.BRepBuilderAPI
import OCC.BRepAlgo
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

from OCC.TopoDS import topods

import ifcopenshell
import ifcopenshell.geom

class IfcCutter:
    def __init__(self):
        self.product_shapes = []
        self.background_elements = []
        self.cut_polygons = []
        self.ifc_file = None
        self.unit = None
        self.section_box = {
            'top_left_corner': (-3., -2.45, 4.75),
            'projection': (0., 1., 0.),
            'x_axis': (1., 0., 0.),
            'x': 15.,
            'y': 7.,
            'z': 3.5,
            'shape': None,
            'face': None
        }

    def cut(self):
        self.ifc_file = ifcopenshell.open('output.ifc')
        self.get_units()
        self.get_product_shapes()
        self.create_section_box()
        self.get_cut_polygons()
        self.get_background_elements()
        self.sort_background_elements()

    def get_units(self):
        unit_assignment = self.ifc_file.by_type('IfcUnitAssignment')[0]
        for unit in unit_assignment.Units:
            if unit.UnitType == 'LENGTHUNIT':
                self.unit = unit
                break

    def get_product_shapes(self):
        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_PYTHON_OPENCASCADE, True)
        products = self.ifc_file.by_type('IfcProduct')
        for product in products:
            if product.is_a('IfcOpeningElement') or product.is_a('IfcSite'):
                continue
            if product.Representation is not None:
                shape = ifcopenshell.geom.create_shape(settings, product).geometry
                self.product_shapes.append((product, shape))

    def sort_background_elements(self):
        new_list = sorted(self.background_elements, key=lambda k: k['z'])
        self.background_elements = new_list

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
        destination = OCC.gp.gp_Ax3(
            top_left_corner,
            OCC.gp.gp_Dir(0, 0, 1),
            OCC.gp.gp_Dir(1, 0, 0))
        self.transformation = OCC.gp.gp_Trsf()
        self.transformation.SetTransformation(source, destination)

        transformed_face = OCC.BRepBuilderAPI.BRepBuilderAPI_Transform(
            self.section_box['face'], self.transformation).Shape()
        exp = OCC.TopExp.TopExp_Explorer(transformed_face, OCC.TopAbs.TopAbs_VERTEX)
        transformed_vertex = OCC.BRep.BRep_Tool.Pnt(topods.Vertex(exp.Current()))

        self.transformation.SetTranslationPart(
            OCC.gp.gp_Vec(-transformed_vertex.X(), -transformed_vertex.Y(), 0))

    def get_background_elements(self):
        for product, shape in self.product_shapes:
            print('Processing product {} '.format(product.Name))
            intersection = OCC.BRepAlgoAPI.BRepAlgoAPI_Common(self.section_box['shape'], shape).Shape()
            intersection_edges = self.get_booleaned_edges(intersection)
            if len(intersection_edges) <= 0:
                continue

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
                zpos, zmax = self.calculate_face_zpos(face)
                self.build_new_face(face, zpos, product)
                self.get_split_edges(edge_face_map, face, zmax, product)
                exp.Next()

    def calculate_face_zpos(self, face):
        bbox = OCC.Bnd.Bnd_Box()
        OCC.BRepBndLib.brepbndlib_Add(face, bbox)
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
                edge_angle = math.degrees(self.get_angle_between_faces(face, adjface))
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
                area = self.get_area(new_face)
                if area == 0:
                    self.background_elements.append({
                        'raw': product,
                        'geometry': new_wire,
                        'geometry_face': new_face,
                        'type': 'polyline',
                        'z': zpos
                        })
                else:
                    self.background_elements.append({
                        'raw': product,
                        'geometry': new_wire,
                        'geometry_face': new_face,
                        'type': 'polygon',
                        'z': zpos
                        })
            except:
                print('Could not build face')
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
        for product, shape in self.product_shapes:
            section = OCC.BRepAlgoAPI.BRepAlgoAPI_Section(self.section_box['face'], shape).Shape()
            section_edges = self.get_booleaned_edges(section)
            if len(section_edges) <= 0:
                continue
            wires = self.connect_edges_into_wires(section_edges)
            for i in range(wires.Length()):
                wire_shape = wires.Value(i+1)

                transformed_wire = OCC.BRepBuilderAPI.BRepBuilderAPI_Transform(
                    wire_shape, self.transformation)
                wire_shape = transformed_wire.Shape()

                wire = topods.Wire(wire_shape)

                self.cut_polygons.append({
                    'raw': product,
                    'geometry': wire
                    })

    def connect_edges_into_wires(self, unconnected_edges):
        edges = OCC.TopTools.TopTools_HSequenceOfShape()
        edges_handle = OCC.TopTools.Handle_TopTools_HSequenceOfShape(edges)
        wires = OCC.TopTools.TopTools_HSequenceOfShape()
        wires_handle = OCC.TopTools.Handle_TopTools_HSequenceOfShape(wires)

        for edge in unconnected_edges:
            edges.Append(edge)

        OCC.ShapeAnalysis.ShapeAnalysis_FreeBounds.ConnectEdgesToWires(edges_handle, 1e-5, True, wires_handle)
        return wires_handle.GetObject()

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
        ifcopenshell.geom.utils.set_shape_transparency(section_face_display, 0.5)
        section_box_display = ifcopenshell.geom.utils.display_shape(self.section_box['shape'])
        ifcopenshell.geom.utils.set_shape_transparency(section_box_display, 0.2)

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

class SvgWriter():
    def __init__(self, ifc_cutter):
        self.ifc_cutter = ifc_cutter
        self.scale = 1 / 100 # 1:100

    def write(self):
        self.calculate_scale()
        self.svg = svgwrite.Drawing('test.svg',
            size=('{}mm'.format(self.ifc_cutter.section_box['x'] * self.scale),
                '{}mm'.format(self.ifc_cutter.section_box['y'] * self.scale)),
            viewBox=('0 0 {} {}'.format(
                self.ifc_cutter.section_box['x'] * self.scale,
                self.ifc_cutter.section_box['y'] * self.scale)))
        self.draw_background_elements()
        self.draw_cut_polygons()
        self.svg.save()

    def calculate_scale(self):
        # TODO: properly handle units
        if self.ifc_cutter.unit.Name == 'METRE':
            self.scale *= 1000

    def draw_background_elements(self):
        for element in self.ifc_cutter.background_elements:
            if element['type'] == 'polygon':
                self.draw_polygon(element, 'white', 0)
            elif element['type'] == 'polyline':
                self.draw_polyline(element)
            elif element['type'] == 'line':
                self.draw_line(element)

    def draw_cut_polygons(self):
        for polygon in self.ifc_cutter.cut_polygons:
            self.draw_polygon(polygon, 'red', 0.5)

    def draw_polyline(self, element):
        exp = OCC.BRepTools.BRepTools_WireExplorer(element['geometry'])
        points = []
        while exp.More():
            point = OCC.BRep.BRep_Tool.Pnt(exp.CurrentVertex())
            points.append((point.X() * self.scale, -point.Y() * self.scale))
            exp.Next()
        self.svg.add(self.svg.polyline(points=points))

    def draw_line(self, element):
        exp = OCC.TopExp.TopExp_Explorer(element['geometry'], OCC.TopAbs.TopAbs_VERTEX)
        points = []
        while exp.More():
            point = OCC.BRep.BRep_Tool.Pnt(topods.Vertex(exp.Current()))
            points.append((point.X() * self.scale, -point.Y() * self.scale))
            exp.Next()
        self.svg.add(self.svg.line(start=points[0], end=points[1],
            stroke=svgwrite.rgb(0, 0, 0, '%'), stroke_width=0.2))

    def draw_polygon(self, polygon, fill, stroke_width):
        exp = OCC.BRepTools.BRepTools_WireExplorer(polygon['geometry'])
        points = []
        while exp.More():
            point = OCC.BRep.BRep_Tool.Pnt(exp.CurrentVertex())
            points.append((point.X() * self.scale, -point.Y() * self.scale))
            exp.Next()
        self.svg.add(self.svg.polygon(
            points=points, fill=fill,
            stroke=svgwrite.rgb(0, 0, 0, '%'),
            stroke_width=stroke_width,
            stroke_linejoin='round'
            ))

print('# Starting process')
start_time = time.time()
ifc_cutter = IfcCutter()
#ifc_cutter = IfcCutterDebug()
svg_writer = SvgWriter(ifc_cutter)
ifc_cutter.cut()
svg_writer.write()
print('# Process finished in {:.2f} seconds'.format(time.time() - start_time))
