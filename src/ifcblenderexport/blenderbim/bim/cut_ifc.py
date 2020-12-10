import os
import re
import math
import time
import numpy
import pickle
import multiprocessing

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
import ifcopenshell.util.selector
import ifcopenshell.util.element

cwd = os.path.dirname(os.path.realpath(__file__))
this_file = os.path.join(cwd, "cut_ifc.py")


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
        gp.gp_Pnt(trsf_data["top_left_corner"][0], trsf_data["top_left_corner"][1], trsf_data["top_left_corner"][2]),
        gp.gp_Dir(trsf_data["projection"][0], trsf_data["projection"][1], trsf_data["projection"][2]),
        gp.gp_Dir(trsf_data["x_axis"][0], trsf_data["x_axis"][1], trsf_data["x_axis"][2]),
    )
    source = gp.gp_Ax3(axis)
    destination = gp.gp_Ax3(gp.gp_Pnt(0, 0, 0), gp.gp_Dir(0, 0, -1), gp.gp_Dir(1, 0, 0))
    transformation = gp.gp_Trsf()
    transformation.SetDisplacement(source, destination)

    cut_polygons = []
    section = BRepAlgoAPI.BRepAlgoAPI_Section(section, shape).Shape()
    section_edges = get_booleaned_edges(section)
    if len(section_edges) <= 0:
        return cut_polygons
    wires = connect_edges_into_wires(section_edges)
    for i in range(wires.Length()):
        wire_shape = wires.Value(i + 1)

        transformed_wire = BRepBuilderAPI.BRepBuilderAPI_Transform(wire_shape, transformation)
        wire_shape = transformed_wire.Shape()

        wire = topods.Wire(wire_shape)
        face = BRepBuilderAPI.BRepBuilderAPI_MakeFace(wire).Face()

        points = []
        exp = BRepTools.BRepTools_WireExplorer(wire)
        while exp.More():
            point = BRep.BRep_Tool.Pnt(exp.CurrentVertex())
            points.append((point.X(), -point.Y()))
            exp.Next()
        cut_polygons.append({"global_id": global_id, "metadata": {}, "points": points})
    return cut_polygons


class IfcCutter:
    def __init__(self):
        self.time = None
        self.selector = ifcopenshell.util.selector.Selector()
        self.product_shapes = []
        self.background_elements = []
        self.cut_polygons = []
        self.template_variables = {}
        self.metadata = {}
        self.data_dir = ""
        self.vector_style = ""
        self.ifc_filenames = []
        self.ifc_files = {}
        self.resolved_pixels = set()
        self.text_pickle_file = "text.pickle"
        self.metadata_pickle_file = "metadata.pickle"
        self.cut_pickle_file = "cut.pickle"
        self.should_recut = True
        self.should_recut_selected = True
        self.cut_objects = ""
        self.selected_global_ids = []
        self.should_extract = True
        self.diagram_name = None
        self.background_image = None
        self.section_box = {
            "projection": (0, 1, 0),
            "x_axis": (1, 0, 0),
            "y_axis": (0, 0, -1),
            "top_left_corner": (-2, 2, 8),
            "x": 14,
            "y": 9,
            "z": 2,
            "shape": None,
            "face": None,
        }

    def cut(self):
        self.profile_code("Starting cut process")
        self.load_ifc_files()
        self.profile_code("Load IFC files")
        self.get_template_variables()
        self.profile_code("Get template variables")
        self.get_product_shapes()
        self.profile_code("Get product shapes")
        self.create_section_box()
        self.profile_code("Create section box")
        self.get_cut_polygons()
        self.profile_code("Get cut polygons")
        self.get_annotation()
        self.profile_code("Get annotation")
        self.get_cut_polygon_metadata()
        self.profile_code("Get cut polygon metadata")

    def profile_code(self, message):
        if not self.time:
            self.time = time.time()
        print("{} :: {:.2f}".format(message, time.time() - self.time))
        self.time = time.time()

    def load_ifc_files(self):
        if not self.should_recut and not self.should_extract:
            return

        loaded_files = []
        for filename in self.ifc_filenames:
            print("Loading file {} ...".format(filename))
            if filename:
                self.ifc_files[filename] = ifcopenshell.open(filename)

    def get_template_variables(self):
        if not self.should_extract:
            if os.path.isfile(self.text_pickle_file):
                with open(self.text_pickle_file, "rb") as text_file:
                    self.template_variables = pickle.load(text_file)
            return

        data = {}
        for text_obj in self.text_objs:
            text_obj_data = self.get_text_variables(text_obj)
            if text_obj_data:
                data[text_obj.name] = text_obj_data

        with open(self.text_pickle_file, "wb") as text_file:
            pickle.dump(data, text_file, protocol=pickle.HIGHEST_PROTOCOL)

        self.template_variables = data

    def get_text_variables(self, text_obj):
        text_obj_data = {}
        text_body = text_obj.data.body
        related_element = text_obj.data.BIMTextProperties.related_element
        if not related_element:
            return
        global_id = related_element.BIMObjectProperties.attributes.get("GlobalId")
        if not global_id:
            return
        element = self.get_ifc_element(global_id.string_value)
        for variable in text_obj.data.BIMTextProperties.variables:
            if element:
                if "{{" in variable.prop_key:
                    prop_key = variable.prop_key.split("{{")[1].split("}}")[0]
                    prop_value = self.selector.get_element_value(element, prop_key)
                    variable_value = eval(variable.prop_key.replace("{{" + prop_key + "}}", str(prop_value)))
                else:
                    variable_value = self.selector.get_element_value(element, variable.prop_key)
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
                self.data_dir, "cache", "shapes", "{}.pickle".format(os.path.basename(filename))
            )
            shape_map = {}
            if self.should_recut_selected and os.path.isfile(shape_pickle):
                with open(shape_pickle, "rb") as shape_file:
                    shape_map = pickle.load(shape_file)

            products.extend(self.selector.parse(ifc_file, self.cut_objects))

            selected_elements = []
            for i, product in enumerate(products):
                if (
                    product.is_a("IfcOpeningElement")
                    or product.is_a("IfcSite")
                    or product.Representation is None
                    or self.has_annotation(product)
                ):
                    continue
                try:
                    if self.should_recut_selected and product.GlobalId in self.selected_global_ids:
                        selected_elements.append(product)
                    elif product.GlobalId in shape_map:
                        shape = shape_map[product.GlobalId]
                        self.add_product_shape(product, shape)
                    else:
                        selected_elements.append(product)
                except:
                    print("Failed to create shape for {}".format(product))

            if selected_elements:
                total = 0
                checkpoint = time.time()
                iterator = ifcopenshell.geom.iterator(
                    settings, ifc_file, multiprocessing.cpu_count(), include=selected_elements
                )
                valid_file = iterator.initialize()
                if valid_file:
                    while True:
                        total += 1
                        if total % 250 == 0:
                            print("{} elements processed in {:.2f}s ...".format(total, time.time() - checkpoint))
                            checkpoint = time.time()
                        shape = iterator.get()
                        shape_map[shape.data.guid] = shape.geometry
                        self.add_product_shape(ifc_file.by_guid(shape.data.guid), shape.geometry)
                        if not iterator.next():
                            break

            with open(shape_pickle, "wb") as shape_file:
                pickle.dump(shape_map, shape_file, protocol=pickle.HIGHEST_PROTOCOL)

    def add_product_shape(self, product, shape):
        self.product_shapes.append((product, shape))

    def has_annotation(self, element):
        for representation in element.Representation.Representations:
            if (
                representation.ContextOfItems.ContextType == "Plan"
                and representation.ContextOfItems.ContextIdentifier == "Annotation"
            ):
                return True
        return False

    def create_section_box(self):
        top_left_corner = gp.gp_Pnt(
            self.section_box["top_left_corner"][0],
            self.section_box["top_left_corner"][1],
            self.section_box["top_left_corner"][2],
        )
        axis = gp.gp_Ax2(
            top_left_corner,
            gp.gp_Dir(
                self.section_box["projection"][0], self.section_box["projection"][1], self.section_box["projection"][2]
            ),
            gp.gp_Dir(self.section_box["x_axis"][0], self.section_box["x_axis"][1], self.section_box["x_axis"][2]),
        )
        section_box = BRepPrimAPI.BRepPrimAPI_MakeBox(
            axis, self.section_box["x"], self.section_box["y"], self.section_box["z"]
        )
        self.section_box["shape"] = section_box.Shape()
        self.section_box["face"] = section_box.BottomFace()

        source = gp.gp_Ax3(axis)
        self.transformation_data = {
            "top_left_corner": self.section_box["top_left_corner"],
            "projection": self.section_box["projection"],
            "x_axis": self.section_box["x_axis"],
        }
        destination = gp.gp_Ax3(gp.gp_Pnt(0, 0, 0), gp.gp_Dir(0, 0, -1), gp.gp_Dir(1, 0, 0))
        self.transformation_dest = destination
        self.transformation = gp.gp_Trsf()
        self.transformation.SetDisplacement(source, destination)

    def get_bbox(self, shape):
        bbox = Bnd.Bnd_Box()
        BRepBndLib.brepbndlib_Add(shape, bbox)
        return bbox

    def calculate_face_zpos(self, face):
        bbox = self.get_bbox(face)
        xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
        zpos = zmin + ((zmax - zmin) / 2)
        return zpos, zmax

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

    def get_annotation(self):
        import mathutils

        self.annotation_objs = []
        settings_2d = ifcopenshell.geom.settings()
        settings_2d.set(settings_2d.INCLUDE_CURVES, True)
        settings_py = ifcopenshell.geom.settings()
        settings_py.set(settings_py.USE_PYTHON_OPENCASCADE, True)
        for ifc_file in self.ifc_files.values():
            for element in ifc_file.by_type("IfcElement"):
                annotation_representation = None
                box_representation = None
                if not element.Representation:
                    continue # This can occur for aggregates
                for representation in element.Representation.Representations:
                    if (
                        representation.ContextOfItems.ContextType == "Plan"
                        and representation.ContextOfItems.ContextIdentifier == "Annotation"
                    ):
                        annotation_representation = representation
                    elif (
                        representation.ContextOfItems.ContextType == "Model"
                        and representation.ContextOfItems.ContextIdentifier == "Box"
                    ):
                        box_representation = representation
                if not annotation_representation or not box_representation:
                    continue

                # This is bad code. See bug #85 to make it slightly less bad.
                # Effectively if the bbox does not intersect with the camera
                # plane, then we should "continue" and not process the 2D
                # wireframe. This approach works but is not very smart.
                for subelement in ifc_file.traverse(box_representation):
                    if subelement.is_a("IfcBoundingBox"):
                        block = ifc_file.createIfcBlock(
                            ifc_file.createIfcAxis2Placement3D(subelement.Corner, None, None),
                            subelement.XDim,
                            subelement.YDim,
                            subelement.ZDim,
                        )
                        for inverse in ifc_file.get_inverse(subelement):
                            ifcopenshell.util.element.replace_attribute(inverse, subelement, block)
                element.Representation.Representations = [box_representation]
                shape = ifcopenshell.geom.create_shape(settings_py, element)

                section = BRepAlgoAPI.BRepAlgoAPI_Section(self.section_box["face"], shape.geometry).Shape()
                section_edges = get_booleaned_edges(section)

                if len(section_edges) <= 0:
                    # The bounding box of the annotation object does not
                    # intersect with the camera plane, so don't bother drawing
                    # the annotation
                    continue

                # Monkey patch - see bug #771.
                element.Representation.Representations = [annotation_representation]
                shape = ifcopenshell.geom.create_shape(settings_2d, element)
                if hasattr(shape, "geometry"):
                    geometry = shape.geometry
                else:
                    geometry = shape
                e = geometry.edges
                v = geometry.verts
                m = shape.transformation.matrix.data
                mat = mathutils.Matrix(
                    ([m[0], m[1], m[2], 0], [m[3], m[4], m[5], 0], [m[6], m[7], m[8], 0], [m[9], m[10], m[11], 1])
                )
                mat.transpose()
                self.annotation_objs.append(
                    {
                        "raw": element,
                        "classes": self.get_classes(element, "annotation"),
                        "edges": [[e[i], e[i + 1]] for i in range(0, len(e), 2)],
                        "vertices": [mat @ mathutils.Vector((v[i], v[i + 1], v[i + 2])) for i in range(0, len(v), 3)],
                    }
                )

    def get_cut_polygon_metadata(self):
        if not self.should_extract:
            if os.path.isfile(self.metadata_pickle_file):
                with open(self.metadata_pickle_file, "rb") as metadata_file:
                    self.metadata = pickle.load(metadata_file)

            for polygon in self.cut_polygons:
                if polygon["global_id"] in self.metadata:
                    polygon["metadata"] = self.metadata[polygon["global_id"]]
            return

        for polygon in self.cut_polygons:
            metadata = {"classes": self.get_classes(self.get_ifc_element(polygon["global_id"]), "cut")}
            self.metadata[polygon["global_id"]] = metadata
            polygon["metadata"] = metadata

        with open(self.metadata_pickle_file, "wb") as metadata_file:
            pickle.dump(self.metadata, metadata_file, protocol=pickle.HIGHEST_PROTOCOL)

    def pickle_cut_polygons(self):
        with open(self.cut_pickle_file, "wb") as pickle_file:
            pickle.dump(self.cut_polygons, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    def get_fresh_cut_polygons(self):
        process_data = [
            (p.GlobalId, s, self.section_box["face"], self.transformation_data) for p, s in self.product_shapes
        ]

        import bpy

        multiprocessing.set_executable(bpy.app.binary_path_python)

        with multiprocessing.Pool(9) as p:
            results = p.map(do_cut, process_data)
            for result in results:
                polygons = [p for p in result if p["points"]]
                self.cut_polygons.extend(polygons)

    def get_polygon_metadata(self, polygon, position):
        polygon["metadata"] = {"classes": self.get_classes(self.get_ifc_element(polygon["global_id"]), position)}
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
        material = ifcopenshell.util.element.get_material(element)
        if material:
            classes.append(
                "material-{}".format(
                    re.sub("[^0-9a-zA-Z]+", "", self.get_material_name(material))
                )
            )
        classes.append("globalid-{}".format(element.GlobalId))
        for attribute in self.attributes:
            result = self.selector.get_element_value(element, attribute)
            if result:
                classes.append(
                    "{}-{}".format(re.sub("[^0-9a-zA-Z]+", "", attribute), re.sub("[^0-9a-zA-Z]+", "", result))
                )
        return classes

    def get_material_name(self, element):
        if hasattr(element, "Name") and element.Name:
            return element.Name
        elif hasattr(element, "LayerSetName") and element.LayerSetName:
            return element.LayerSetName
        return "mat-" + str(element.id())

    def get_pickled_cut_polygons(self):
        if os.path.isfile(self.cut_pickle_file):
            with open(self.cut_pickle_file, "rb") as pickle_file:
                self.cut_polygons = pickle.load(pickle_file)
