# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import uuid
import math
import sys

# sys.path.append('C:\Program Files\Python37\Lib\site-packages')
import lxml
import bspy
from bspy import Gbxml


class GbxmlExporter:
    def __init__(self):
        self.gbxml = Gbxml()
        self.campus = None

    def export(self):
        print("# Start export")
        self.campus = self.gbxml.add_element(self.gbxml.root(), "Campus")
        self.campus.set("id", "campus-1")
        name = self.gbxml.add_element(self.campus, "Name", "My project")

        location = self.gbxml.add_element(self.campus, "Location")
        self.gbxml.add_element(location, "ZipcodeOrPostalCode", "G20 0SP")
        self.gbxml.add_element(location, "Name", "London/Heathrow")
        self.gbxml.add_element(location, "Latitude", "51.480000")
        self.gbxml.add_element(location, "Longitude", "-0.450000")
        self.gbxml.add_element(location, "Elevation", "24.000000")

        building = self.gbxml.add_element(self.campus, "Building")
        building.set("id", str(uuid.uuid4()))
        building.set("buildingType", "Office")

        for object in bpy.context.selected_objects:
            self.create_space(object, building)

        # hardcoded test
        construction = self.gbxml.add_element(self.gbxml.root(), "Construction")
        construction.set("id", "defaultconstruction")
        self.gbxml.add_element(construction, "Name", "test construction name")
        u_value = self.gbxml.add_element(construction, "U-value", "0.42")
        u_value.set("unit", "WPerSquareMeterK")
        layer = self.gbxml.add_element(construction, "LayerId")
        layer.set("layerIdRef", "defaultlayer")

        layer = self.gbxml.add_element(self.gbxml.root(), "Layer")
        layer.set("id", "defaultlayer")
        material = self.gbxml.add_element(layer, "MaterialId")
        material.set("materialIdRef", "defaultmaterial")

        material = self.gbxml.add_element(self.gbxml.root(), "Material")
        material.set("id", "defaultmaterial")
        thickness = self.gbxml.add_element(material, "Thickness", "0.2")
        thickness.set("unit", "Meters")
        self.gbxml.add_element(material, "Name", "test material name")
        r_value = self.gbxml.add_element(material, "R-value", "0.13")
        r_value.set("unit", "SquareMeterKPerW")

        self.append_template("C:/cygwin64/home/moud308/Projects/New Folder/presets/light-schedule.xml")
        self.append_template("C:/cygwin64/home/moud308/Projects/New Folder/presets/window-types.xml")

        with open("C:/cygwin64/home/moud308/Projects/New Folder/out.xml", "w") as out:
            out.write(self.gbxml.xmlstring())
        print("# Validation results: {}".format(self.gbxml.validate()))
        print("# Finish export")

    def append_template(self, file):
        parser = lxml.etree.XMLParser(remove_blank_text=True)
        template = lxml.etree.parse(file, parser).findall(".")[0]
        for child in template.getchildren():
            self.gbxml.root().append(child)

    def create_space(self, object, building):
        space = self.gbxml.add_element(building, "Space")
        space.set("id", object.name)
        space.set("lightScheduleIdRef", "aim0130")  # hardcoded
        self.gbxml.add_element(space, "Name", object.name)

        light_power_per_area = self.gbxml.add_element(space, "LightPowerPerArea", "5")  # hardcoded test
        light_power_per_area.set("unit", "WattPerSquareMeter")
        calculated_area = 0

        shell_geometry = self.gbxml.add_element(space, "ShellGeometry")
        shell_geometry.set("id", "shellid")
        closed_shell = self.gbxml.add_element(shell_geometry, "ClosedShell")
        vertices_in_vg = self.get_vertices_in_vg(object, 0)
        for polygon in object.data.polygons:
            # First vg is reserved for surfaces
            if object.vertex_groups and not self.is_polygon_in_vg(polygon, vertices_in_vg):
                continue
            calculated_area += polygon.area
            self.create_poly_loop(object, polygon, closed_shell)
            self.create_space_boundary(object, polygon, space)
            self.create_surface(object, polygon)
        self.gbxml.add_element(space, "Area", str(calculated_area))
        self.gbxml.add_element(space, "Volume", str(self.get_volume(object)))

    def get_vertices_in_vg(self, object, vg_index):
        return [v.index for v in object.data.vertices if vg_index in [g.group for g in v.groups]]

    # Can move into a common Blender helper class?
    def is_polygon_in_vg(self, polygon, vertices_in_vg):
        for v in polygon.vertices:
            if v not in vertices_in_vg:
                return False
        return True

    def create_space_boundary(self, object, polygon, parent):
        space_boundary = self.gbxml.add_element(parent, "SpaceBoundary")
        space_boundary.set("isSecondLevelBoundary", "true")
        space_boundary.set("surfaceIdRef", "surface-{}-{}".format(object.name, polygon.index))
        planar_geometry = self.gbxml.add_element(space_boundary, "PlanarGeometry")
        self.create_poly_loop(object, polygon, planar_geometry)

    def create_surface(self, object, polygon):
        surface = self.gbxml.add_element(self.campus, "Surface")
        surface.set("id", "surface-{}-{}".format(object.name, polygon.index))
        surface.set("surfaceType", "ExteriorWall")
        surface.set("constructionIdRef", "defaultconstruction")
        adjacent_space_id = self.gbxml.add_element(surface, "AdjacentSpaceId")
        adjacent_space_id.set("spaceIdRef", object.name)
        rectangular_geometry = self.gbxml.add_element(surface, "RectangularGeometry")
        self.gbxml.add_element(
            rectangular_geometry, "Azimuth", str(math.degrees(math.atan2(polygon.normal[0], polygon.normal[1])))
        )
        self.gbxml.add_element(
            rectangular_geometry, "Tilt", str(math.degrees(math.atan2(polygon.normal[2], polygon.normal[1])) - 90)
        )
        planar_geometry = self.gbxml.add_element(surface, "PlanarGeometry")
        self.create_poly_loop(object, polygon, planar_geometry)
        for vg in object.vertex_groups:
            if "/".join(vg.name.split("/")[0:2]) == "openings/{}".format(polygon.index):
                vertices_in_vg = self.get_vertices_in_vg(object, vg.index)
                for p in object.data.polygons:
                    if self.is_polygon_in_vg(p, vertices_in_vg):
                        self.create_opening(object, p, surface)

    def create_opening(self, object, polygon, parent):
        opening = self.gbxml.add_element(parent, "Opening")
        opening.set("id", "opening-{}-{}".format(object.name, polygon.index))
        opening.set("windowTypeIdRef", "STD_EX11")  # hardcoded
        opening.set("openingType", "FixedWindow")  # hardcoded
        planar_geometry = self.gbxml.add_element(opening, "PlanarGeometry")
        self.create_poly_loop(object, polygon, planar_geometry)

    def create_poly_loop(self, object, polygon, parent):
        poly_loop = self.gbxml.add_element(parent, "PolyLoop")
        for vertice in polygon.vertices:
            cartesian_point = self.gbxml.add_element(poly_loop, "CartesianPoint")
            for coord in [0, 1, 2]:
                coordinate = self.gbxml.add_element(cartesian_point, "Coordinate")
                coordinate.text = str(object.data.vertices[vertice].co[coord])

    def get_volume(self, o):
        volume = 0
        ob_mat = o.matrix_world
        me = o.data
        me.calc_loop_triangles()
        for tf in me.loop_triangles:
            tfv = tf.vertices
            if len(tf.vertices) == 3:
                tf_tris = ((me.vertices[tfv[0]], me.vertices[tfv[1]], me.vertices[tfv[2]]),)
            else:
                tf_tris = (me.vertices[tfv[0]], me.vertices[tfv[1]], me.vertices[tfv[2]]), (
                    me.vertices[tfv[2]],
                    me.vertices[tfv[3]],
                    me.vertices[tfv[0]],
                )

            for tf_iter in tf_tris:
                v1 = ob_mat @ tf_iter[0].co
                v2 = ob_mat @ tf_iter[1].co
                v3 = ob_mat @ tf_iter[2].co

                volume += v1.dot(v2.cross(v3)) / 6.0
        return volume


gbxml_exporter = GbxmlExporter()
gbxml_exporter.export()
