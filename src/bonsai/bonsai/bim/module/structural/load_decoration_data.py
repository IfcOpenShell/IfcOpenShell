import bpy
import gpu
import bmesh
import numpy as np
from math import sin
from mathutils import Vector, Matrix
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.attribute
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.structural.shader import DecorationShader


class ShaderInfo:
    def __init__(self):
        self.is_empty = True
        self.shader = DecorationShader()
        #self.shader_type = shader_type
        #self.args = {}
        #self.indices = []
        self.curve_members = {}
        self.point_members = {}
        self.surface_members = {}
        self.text_info = []
        self.info = []
        self.force_unit = ""
        self.linear_force_unit = ""
        self.planar_force_unit = ""
    
    def update(self):
        self.info = []
        self.text_info = []
        self.curve_members = {}
        self.point_members = {}
        self.surface_members = {}
        self.get_force_units()
        self.get_strucutural_elements_and_activities()
        self.get_linear_loads()
        self.get_point_loads()
        self.get_planar_loads()
        if len(self.info):
            self.is_empty = False
    
    def get_force_units(self):
        def get_unit_symbol(unit: ifcopenshell.entity_instance) -> str:
            prefix_symbols = {
                "EXA": "E",
                "PETA": "P",
                "TERA": "T",
                "GIGA": "G",
                "MEGA": "M",
                "KILO": "k",
                "HECTO": "h",
                "DECA": "da",
                "DECI": "d",
                "CENTI": "c",
                "MILLI": "m",
                "MICRO": "μ",
                "NANO": "n",
                "PICO": "p",
                "FEMTO": "f",
                "ATTO": "a",
            }

            unit_symbols = {
                # si units
                "CUBIC_METRE": "m3",
                "GRAM": "g",
                "SECOND": "s",
                "SQUARE_METRE": "m2",
                "METRE": "m",
                "NEWTON": "N",
                "PASCAL": "Pa",
                # conversion based units
                "pound-force": "lbf",
                'pound-force per square inch': "psi",
                "thou": "th",
                "inch": "in",
                "foot": "ft",
                "yard": "yd",
                "mile": "mi",
                "square thou": "th2",
                "square inch": "in2",
                "square foot": "ft2",
                "square yard": "yd2",
                "acre": "ac",
                "square mile": "mi2",
                "cubic thou": "th3",
                "cubic inch": "in3",
                "cubic foot": "ft3",
                "cubic yard": "yd3",
                "cubic mile": "mi3",
                "litre": "L",
                "fluid ounce UK": "fl oz",
                "fluid ounce US": "fl oz",
                "pint UK": "pt",
                "pint US": "pt",
                "gallon UK": "gal",
                "gallon US": "gal",
                "degree": "°",
                "ounce": "oz",
                "pound": "lb",
                "ton UK": "ton",
                "ton US": "ton",
                "lbf": "lbf",
                "kip": "kip",
                "psi": "psi",
                "ksi": "ksi",
                "minute": "min",
                "hour": "hr",
                "day": "day",
                "btu": "btu",
                "fahrenheit": "°F",
            }
            symbol = ""
            if unit.is_a("IfcSIUnit"):
                symbol += prefix_symbols.get(unit.Prefix, "")
            symbol += unit_symbols.get(unit.Name.replace("METER", "METRE"), "?")
            return symbol
        
        force_units = [u for u in tool.Ifc.get().by_type("IfcNamedUnit")
                       if u.UnitType == "FORCEUNIT"]
        linear_force_units = [u for u in tool.Ifc.get().by_type("IfcDerivedUnit")
                              if u.UnitType == "LINEARFORCEUNIT"]
        planar_force_units = [u for u in tool.Ifc.get().by_type("IfcDerivedUnit")
                              if u.UnitType == "PLANARFORCEUNIT"]
        
        conversion_force_unit = [u for u in force_units if u.is_a("IfcConversionBasedUnit")]
        if len(conversion_force_unit) == 0:
            conversion_force_unit.append(force_units[0])
        self.force_unit = get_unit_symbol(conversion_force_unit[0])
        first = ""
        second = ""
        for e in linear_force_units[0].Elements:
            if e.Unit.UnitType == "FORCEUNIT":
                first = get_unit_symbol(e.Unit)
            if e.Unit.UnitType == "LENGTHUNIT":
                second = get_unit_symbol(e.Unit)
        self.linear_force_unit = first + "/" + second
        first = ""
        second = ""
        for e in planar_force_units[0].Elements:
            if e.Unit.UnitType == "FORCEUNIT":
                first = get_unit_symbol(e.Unit)
            if e.Unit.UnitType == "LENGTHUNIT":
                second = get_unit_symbol(e.Unit)+"2"
            if e.Unit.UnitType == "AREAUNIT":
                second = get_unit_symbol(e.Unit)
        self.planar_force_unit = first + "/" + second
        
    def get_strucutural_elements_and_activities(self):

        def populate_members_dict(dict_name,element, activity, factor):
            dic = getattr(self,dict_name,None)
            if dic is None:
                return
            member = dic.get(element.GlobalId)
            if member is None:
                dic.update({
                    element.GlobalId: {
                        "member": element,
                        "activities": [(activity,factor)]}
                    })
            else:
                member["activities"].append((activity,factor))

        def recursive_subgroups(groups, rec_limit, activity_type, factor = 1):
            if len(groups) == 0 or rec_limit == 0:
                return None
            for group in groups:
                subgorups = []
                activities = []
                relationship = [rel for rel in group.IsGroupedBy]
                coef = getattr(group, 'Coefficient', 1.0)
                group_coef =  coef if coef is not None else 1.0
                rel_factor = 1.0

                for rel in relationship:
                    if rel.is_a("IfcRelAssignsToGroupByFactor"):
                        rel_factor = rel.Factor if rel.Factor is not None else 1.0
                    objects = rel.RelatedObjects
                    subgorups = [sg for sg in objects if sg.is_a("IfcStructuralLoadGroup")]
                    activities = [a for a in objects if a.is_a("IfcStructuralActivity")]
                    factor = factor*group_coef*rel_factor
                    for activity in activities:
                        if len(activity.AssignedToStructuralItem):
                            element = activity.AssignedToStructuralItem[0].RelatingElement
                            if element is not None:
                                if activity_type == "Action":
                                    if element.is_a("IfcStructuralCurveMember"):
                                        populate_members_dict("curve_members",element,activity,factor)
                                    elif element.is_a("IfcStructuralPointConnection"):
                                        populate_members_dict("point_members",element,activity,factor)
                                    elif element.is_a("IfcStructuralSurfaceMember"):
                                        populate_members_dict("surface_members",element,activity,factor)

                                elif activity_type == "External Reaction" and getattr(element,"AppliedCondition",None) is not None:
                                    if element.is_a("IfcStructuralCurveMember"):
                                        populate_members_dict("curve_members",element,activity,factor)
                                    elif element.is_a("IfcStructuralPointConnection"):
                                        populate_members_dict("point_members",element,activity,factor)
                                    elif element.is_a("IfcStructuralSurfaceMember"):
                                        populate_members_dict("surface_members",element,activity,factor)
                    recursive_subgroups(subgorups,rec_limit-1,activity_type,factor=factor)
        
        props = bpy.context.scene.BIMStructuralProperties
        group_definition_id = int(props.load_group_to_show)
        file = IfcStore.get_file()
        groups = [file.by_id(group_definition_id)]
        recursive_subgroups(groups,10,props.activity_type)

    def get_planar_loads(self):
        list_of_surfaces = self.surface_members
        shader = self.shader.get("PLANAR LOAD")
        maximum = 0
        for value in list_of_surfaces.values():
            surf = value["member"]
            activity_list = [getattr(a, 'RelatedStructuralActivity', None) for a in getattr(surf, 'AssignedStructuralActivity', None)
                             if getattr(a, 'RelatedStructuralActivity', None).is_a() in ['IfcStructuralPlanarAction','IfcStructuralSurfaceAction']]
            activity_list = value["activities"]
            if len(activity_list) == 0:
                continue
            rotation = self.get_surface_member_rotation(surf)
            values = self.get_planar_loads_values(activity_list,rotation)
            if maximum == 0:
                maximum = max([abs(float(i)) for i in values])
                if maximum == 0:
                    continue
            props = bpy.context.scene.BIMStructuralProperties
            reference_frame = props.reference_frame
            orientation = np.eye(3)
            if reference_frame == "LOCAL_COORDS":
                orientation = rotation
            blender_object: bpy.types.Object = IfcStore.get_element(getattr(surf, 'GlobalId', None))
            mat = blender_object.matrix_world
            mesh: bpy.types.Mesh = blender_object.data
            
            positions = []
            indices = []
            coord = []
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.triangulate(bm, faces = bm.faces)
            bm.edges.ensure_lookup_table()
            bm.verts.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            add_index = len(positions)
            for v in bm.verts:
                p1 = np.array(mat @ v.co)
                positions.append(p1)
                p2 = p1 - (orientation@values)*0.2/maximum
                positions.append(p2)
                coord.append((float(p1[0]+p1[1]),0,1))
                coord.append((float(p1[0]+p1[1]),1,1))
            for e in bm.edges:
                if len(e.link_faces) > 1:
                    continue
                indices.append((2*e.verts[0].index,
                                2*e.verts[0].index+1,
                                2*e.verts[1].index))
                indices.append((2*e.verts[0].index+1,
                                2*e.verts[1].index,
                                2*e.verts[1].index+1))
            for p in bm.faces:
                indices.append((2*p.verts[0].index+1,
                                2*p.verts[1].index+1,
                                2*p.verts[2].index+1))
            bmesh.ops.dissolve_limit(bm, angle_limit = 0.01, verts = bm.verts, edges = bm.edges)
            bm.faces.ensure_lookup_table()
            center = bm.faces[0].calc_center_bounds()

            self.text_info.append(
                {"position": mat @ center - Vector((orientation@values)*0.2/maximum),
                "normal": Vector(mesh.polygons[0].normal),
                "text": f'{values[2]:.5f} {self.planar_force_unit}'}
                )
            
            self.info.append(
                    {
                        "shader": shader,
                        "args": {"position": positions, "coord": coord},
                        "indices": indices,
                        "uniforms": [["color", (0.2,0,1,1)],["spacing", 0.2]]
                    }
            )
    def get_planar_loads_values(self, activity_list,element_rotation_matrix):
        values = np.zeros((3))
        for item in activity_list:
            activity = item[0]
            factor = item[1]
            load = activity.AppliedLoad
            temp = np.zeros((3))
            if load is not None and load.is_a("IfcStructuralLoadPlanarForce"):
                temp[0] = load.PlanarForceX if load.PlanarForceX is not None else 0
                temp[1] = load.PlanarForceY if load.PlanarForceY is not None else 0
                temp[2] = load.PlanarForceZ if load.PlanarForceZ is not None else 0
            temp = temp*factor
            transform = self.get_activity_transform_matrix(activity,element_rotation_matrix)
            values += transform@temp
        return values

    def get_surface_member_rotation(self,surface_member):
        representation = ifcopenshell.util.representation.get_representation(surface_member, "Model")
        repr_item = representation.Items[0]
        placement = ifcopenshell.util.placement.get_axis2placement(repr_item.FaceSurface.Position)
        rotation = placement[0:3,0:3]
        return rotation

    def get_point_connection_rotation(self, point_connection):
        if point_connection.ConditionCoordinateSystem is not None:
            placement = ifcopenshell.util.placement.get_axis2placement(point_connection.ConditionCoordinateSystem)
        else:
            placement = np.eye(4)
        rotation = placement[0:3,0:3]
        return rotation
    
    def get_curve_member_rotation(self, curve_member):
        z = curve_member.Axis.DirectionRatios
        edge = curve_member.Representation.Representations[0].Items[0]
        origin = edge.EdgeStart.VertexGeometry.Coordinates
        end = edge.EdgeEnd.VertexGeometry.Coordinates
        x = [c2 - c1 for c1, c2 in zip(origin, end)]
        placement = ifcopenshell.util.placement.a2p(origin,z,x)
        rotation = placement[0:3,0:3]
        return rotation
    
    def get_activity_transform_matrix(self, activity, element_rotation_matrix):
        "provides the transformation matrix to convert between reference frames"
        global_or_local = activity.GlobalOrLocal
        props = bpy.context.scene.BIMStructuralProperties
        reference_frame = props.reference_frame
        transform_matrix = np.eye(3)
        if reference_frame == 'LOCAL_COORDS' and global_or_local != reference_frame:
            transform_matrix = np.linalg.inv(element_rotation_matrix)
        elif reference_frame == 'GLOBAL_COORDS' and global_or_local != reference_frame:
            transform_matrix = element_rotation_matrix
        return transform_matrix

    def get_point_loads(self):
        list_of_point_connections = tool.Ifc.get().by_type("IfcStructuralPointConnection")
        list_of_point_connections = self.point_members
        for value in list_of_point_connections.values():
            conn = value["member"]
            activity_list = [getattr(a, 'RelatedStructuralActivity', None) for a in getattr(conn, 'AssignedStructuralActivity', None)
                             if getattr(a, 'RelatedStructuralActivity', None).is_a() in ['IfcStructuralPointAction']]
            activity_list = value["activities"]
            if len(activity_list) == 0:
                continue
            blender_object = IfcStore.get_element(getattr(conn, 'GlobalId', None))
            if blender_object.type == 'MESH':
                conn_location = blender_object.matrix_world @ blender_object.data.vertices[0].co
                #get local coordinates of the connection
                rotation = self.get_point_connection_rotation(conn)
                loads = self.get_point_loads_values(activity_list, rotation)
                self.get_point_shader_args(loads, conn_location, rotation)

    def get_point_shader_args(self,loads, location, rotation):
        location = np.array(location)
        indices = []
        text_info = []
        direction_dict = {
                "fx": (np.array((1,0,0)),np.array((0,1,0)),np.array((0,0,1))),
                "fy": (np.array((0,1,0)),np.array((1,0,0)),np.array((0,0,1))),
                "fz": (np.array((0,0,1)),np.array((0,1,0)),np.array((1,0,0))),
                "mx": (np.array((0,1,0)),np.array((0,0,1))),
                "my": (np.array((1,0,0)),np.array((0,0,1))),
                "mz": (np.array((1,0,0)),np.array((0,1,0))),
            }
        keys = ["fx","fy","fz","mx","my","mz"]
        props = bpy.context.scene.BIMStructuralProperties
        reference_frame = props.reference_frame
        if reference_frame == "LOCAL_COORDS":
            for key in keys:
                tup = direction_dict[key]
                li = []
                for item in tup:
                    li.append(rotation@item)
                direction_dict[key] = li
        
        for i, key in enumerate(keys):
            if loads[i] == 0:
                continue
            color = (1,0,0,1)
            if i in [1,4]:
                color = (0,1,0,1)
            elif i in [2,5]:
                color = (0,0,1,1)
            d1 = -(direction_dict[key][0]*loads[i])
            d1 = d1/np.linalg.norm(d1)
            if i < 3:
                d2 = direction_dict[key][1]
                d3 = direction_dict[key][2]
                p1 = location
                p2 = location + d1 + d2
                p3 = location + d1 - d2
                p4 = location + d1 + d3
                p5 = location + d1 - d3
                position = [p1,p2,p3,p4,p5]
                indices = [(0,1,2),(0,3,4)]
                c1 = (0,0,0)
                c2 = (1,1,0)
                c3 = (-1,1,0)
                coords_for_shader = [c1,c2,c3,c2,c3]
                shader = self.shader.get("SINGLE FORCE")
                self.info.append(
                    {
                        "shader": shader,
                        "args": {"position": position,"coord": coords_for_shader},
                        "indices": indices,
                        "uniforms": [["color", color],["spacing", 0.2]]
                    }
                )
                self.text_info.append(
                                {"position": location + d1,
                                "normal": d2/np.linalg.norm(d2),
                                "text": f'{loads[i]:.2f} {self.force_unit}'}
                                )
            else:
                d2 = d2 = direction_dict[key][1]
                p1 = location - d2
                p2 = location + d1 + d2
                p3 = location - d1 + d2
                position = [p1,p2,p3]
                indices = [(0,1,2)]
                c1 = (-1,0,0)
                c2 = (1,1,0)
                c3 = (1,-1,0)
                coords_for_shader = [c1,c2,c3]
                shader = self.shader.get("SINGLE MOMENT")
                self.info.append(
                    {
                        "shader": shader,
                        "args": {"position": position,"coord": coords_for_shader},
                        "indices": indices,
                        "uniforms": [["color", color]]
                    }
                )
                self.text_info.append(
                                {"position": location +0.25*(d1 + d2),
                                "normal": d2/np.linalg.norm(d2),
                                "text": f'{loads[i]:.2f} {self.force_unit}'}#change to moment unit
                                )

    def get_point_loads_values(self,activity_list,element_rotation_matrix):
        result_list = np.zeros(6)
        attr_list = ['ForceX','ForceY','ForceZ','MomentX','MomentY','MomentZ']
        for item in activity_list:
            activity = item[0]
            factor = item[1]
            load = activity.AppliedLoad
            temp = np.zeros(6)
            for i, attr in enumerate(attr_list):
                value = 0 if getattr(load, attr, 0) is None else getattr(load, attr, 0)
                temp[i] += value*factor
            transform_3 = self.get_activity_transform_matrix(activity,element_rotation_matrix)
            transform_6 = np.zeros((6,6))
            transform_6[0:3,0:3] = transform_3
            transform_6[3:6,3:6] = transform_3
            result_list += transform_6@temp

        return result_list


    def get_linear_loads(self): #for now it only works for distributed loads
        position = []
        indices = []
        sin_quad_lin = []
        coords_for_shader = []
        color = []
        text_info = []
        uniforms = []
        info = []
    
        list_of_curve_members = tool.Ifc.get().by_type("IfcStructuralCurveMember")
        list_of_curve_members = self.curve_members
        for value in list_of_curve_members.values():
            member = value["member"]
            activity_list = [getattr(a, 'RelatedStructuralActivity', None) for a in getattr(member, 'AssignedStructuralActivity', None)
                             if getattr(a, 'RelatedStructuralActivity', None).is_a() in ['IfcStructuralCurveAction','IfcStructuralLinearAction']]
            activity_list = value["activities"]
            if len(activity_list) == 0:
                continue
            # member is a structural curve member
            # get Axis attribute from member -> (IFCDIRECTION)
            # get Representation attribute from member -> (IFCPRODUCTDEFINITIONSHAPE)
            # get Representations attribute from Representation -> (IFCTOPOLOGYREPRESENTATION)
            # get Items attribute from Representations -> (IFCEDGE)
            # get EdgeStart attribute from Items -> (IFCVERTEX)
            # get EdgeEnd attribure from Items -> (IFCVERTEX)
            # using blender just get the global coordinates of the first and second vertex in the mesh
    
            blender_object = IfcStore.get_element(getattr(member, 'GlobalId', None))
            
            start_co = blender_object.matrix_world @ blender_object.data.vertices[0].co
            end_co = blender_object.matrix_world @ blender_object.data.vertices[1].co
            x_axis = Vector(end_co-start_co).normalized()
            z_direction = getattr(member, 'Axis')
            #local coordinates
            z_axis = Vector(getattr(z_direction, 'DirectionRatios', None)).normalized()
            y_axis = z_axis.cross(x_axis).normalized()
            z_axis = x_axis.cross(y_axis).normalized()
            rot = self.get_curve_member_rotation(member)
            global_to_local = Matrix(((x_axis.x,y_axis.x,z_axis.x),
                                      (x_axis.y,y_axis.y,z_axis.y),
                                      (x_axis.z,y_axis.z,z_axis.z),
                                      ))
            global_to_local = Matrix(rot)
    
            #get shader args for each direction
            props = bpy.context.scene.BIMStructuralProperties
            reference_frame = props.reference_frame #make it a scene property so it can be changed in a panel
            is_local =  reference_frame == 'LOCAL_COORDS'
            x_match = abs(Vector((1,0,0)).dot(x_axis)) > 0.99
            y_match = abs(Vector((0,1,0)).dot(x_axis)) > 0.99
            z_match = abs(Vector((0,0,1)).dot(x_axis)) > 0.99
            direction_dict = {
                "fx": y_axis+z_axis if is_local else Vector((1,0,0)) if not x_match else Vector((0,1,1)),
                "fy": y_axis if is_local else Vector((0,1,0)) if not y_match else Vector((1,0,1)),
                "fz": z_axis if is_local else Vector((0,0,1)) if not z_match else Vector((1,1,0)),
                "mx": z_axis-y_axis if is_local or x_match else Vector((1,0,0)).cross(x_axis),
                "my": z_axis if is_local else Vector((-1,0,1)) if y_match else Vector((0,1,0)).cross(x_axis).normalized(),
                "mz": y_axis if is_local else Vector((-1,1,0)) if z_match else Vector((0,0,1)).cross(x_axis).normalized()
            }
            match_dict = {'fx': x_match or is_local, 'fy': y_match, 'fz': z_match}
            member_length =  Vector(end_co-start_co).length
            loads_dict, maxforce, point_loads = self.get_loads_per_direction(activity_list,global_to_local,member_length)
            if len(point_loads):
                for item in point_loads:
                    for sub_item in item:
                        pos = sub_item["pos"]
                        values = sub_item["values"]
                        pos_vector = start_co + x_axis*pos
                        self.get_point_shader_args(values,pos_vector)
            if loads_dict is None:
                continue
            keys = ["fx","fy","fz","mx","my","mz"]

            for key in keys:
                polyline = loads_dict[key]["polyline"]
                sinus = loads_dict[key]["sinus"]
                quadratic = loads_dict[key]["quadratic"]
                constant = loads_dict[key]["constant"]
                direction = direction_dict[key] #depends on the key and on the frame of reference
                color_axis = (0,0,1,1)
                if 'x' in key:
                    color_axis = (1,0,0,1)
                if 'y' in key:
                    color_axis = (0,1,0,1)
                
                if 'f' in key:
                    if match_dict[key]:
                        shader = self.shader.get("PARALLEL DISTRIBUTED FORCE")
                    else:
                        shader = self.shader.get("PERPENDICULAR DISTRIBUTED FORCE")
                else:
                    shader = self.shader.get("DISTRIBUTED MOMENT")

                addindex = len(position)
                counter = 0
                for i in range(len(polyline)-1):
                    current = Vector(polyline[i]+[0])
                    nextitem = Vector(polyline[i+1]+[0])

                    if any([current.y, nextitem.y,constant,quadratic,sinus]): #if there is load in the z direction
                        negative = -1*direction + start_co + x_axis*current.x
                        positive = direction + start_co + x_axis*current.x
                        position.append(negative)
                        coords_for_shader.append((current.x, 1.0,member_length))
                        sin_quad_lin.append((sinus, quadratic, current.y + constant))
                        color.append(color_axis)
                        #info to render load value
                        x = current.x/member_length
                        func = sin(x*3.1416)*sinus + (-4.*x*x+4.*x)*quadratic+constant+current.y
                        if func:
                            text_info.append(
                                {"position": -1*direction*func/maxforce + start_co + x_axis*current.x,
                                "normal": direction.cross(x_axis).normalized(),
                                "text": f'{func:.2f} {self.linear_force_unit}'}
                                )
                        maxforce = max(maxforce,abs(func))
                        position.append(positive)
                        coords_for_shader.append((current[0],-1.0,member_length))
                        sin_quad_lin.append((sinus, quadratic, current.y + constant))
                        color.append(color_axis)

                        indices.append((0 + counter + addindex,
                                        1 + counter + addindex,
                                        2 + counter + addindex))
                        indices.append((3 + counter + addindex,
                                        2 + counter + addindex,
                                        1 + counter + addindex))
                        if i == len(polyline)-2:
                            negative = -1*direction + start_co + x_axis*nextitem.x
                            positive = direction + start_co + x_axis*nextitem.x
                            position.append(negative)
                            coords_for_shader.append((nextitem.x, 1.0,member_length))
                            sin_quad_lin.append((sinus, quadratic, nextitem.y + constant))
                            color.append(color_axis)
                            #info to render load value
                            x = nextitem.x/member_length
                            func = sin(x*3.1416)*sinus + (-4.*x*x+4.*x)*quadratic+constant+nextitem.y
                            if func:
                                text_info.append(
                                    {"position": -1*direction*func/maxforce + start_co + x_axis*nextitem.x,
                                    "normal": direction.cross(x_axis).normalized(),
                                    "text": f'{func:.2f} {self.linear_force_unit}'}
                                    )
                            maxforce = max(maxforce,abs(func))
                            position.append(positive)
                            coords_for_shader.append((nextitem.x,-1.0,member_length))
                            sin_quad_lin.append((sinus, quadratic, nextitem.y + constant))
                            color.append(color_axis)

                        counter += 2
                if len(position):
                    self.info.append(
                    {
                        "shader": shader,
                        "args": {"position": position, "sin_quad_lin_forces": sin_quad_lin,"coord": coords_for_shader},
                        "indices": indices,
                        "uniforms": [["color", color_axis],["spacing", 0.2],["maxload",maxforce]]
                    }
                )
                position = []
                sin_quad_lin = []
                coords_for_shader = []
                indices = []
            for info in self.info:
                info["uniforms"][2][1] = maxforce

        self.text_info = text_info


    def get_loads_per_direction(self,activity_list,global_to_local,member_length):
        """ returns a dict with values for applied loads in each direction
        return = {
                    "fx": values_in_this_direction
                    "fy": values_in_this_direction
                    "fz": values_in_this_direction
                    "mx": values_in_this_direction
                    "my": values_in_this_direction
                    "mz": values_in_this_direction
                    }
        values_in_this_direction = {
                                    "constant": float,
                                    "quadratic": float,
                                    "sinus": float,
                                    "polyline": list[(position: float, load: float),...]
                                    }
        """
        loads_dict = self.get_loads_dict(activity_list,global_to_local)
        const = loads_dict["constant force"]
        quad = loads_dict["quadratic force"]
        sinus = loads_dict["sinus force"]
        loads = loads_dict["linear load configuration"]
        unique_list = self.getuniquepositionlist(loads)
        final_list = []
        return_value = None
        max_load = 0
        for pos in unique_list:
            value = self.get_before_and_after(pos,loads)
            if value["before"] == value["after"]:
                final_list.append([pos]+value["before"])
            else:
                final_list.append([pos]+value["before"])
                final_list.append([pos]+value["after"])
        
        if not len(final_list) and any(const+quad+sinus):
            final_list.append([0.0,0.0,0.0,0.0,0.0,0.0,0.0])
            final_list.append([member_length,0.0,0.0,0.0,0.0,0.0,0.0])
        
        elif len(final_list):
            if final_list[0][0] and any(const+quad+sinus): #if first item location is not 0 append an item at the zero
                final_list = [[0.0,0.0,0.0,0.0,0.0,0.0,0.0]]+final_list
            else:
                del final_list[0]
            if abs(final_list[-1][0] - member_length) > 0.01  and any(const+quad+sinus):
                final_list.append([member_length,0.0,0.0,0.0,0.0,0.0,0.0])
            else:
                del final_list[-1]
        if len(final_list):
            array = np.array(final_list) #7xn -> ["pos","fx","fy","fz","mx","my","mz"]
            keys = ["fx","fy","fz","mx","my","mz"]
            polyline = {
                        "fx": [],
                        "fy": [],
                        "fz": [],
                        "mx": [],
                        "my": [],
                        "mz": [],
                        }
            return_value = {
                        "fx": {"constant": 0, "quadratic": 0,"sinus": 0,"polyline": []},
                        "fy": {"constant": 0, "quadratic": 0,"sinus": 0,"polyline": []},
                        "fz": {"constant": 0, "quadratic": 0,"sinus": 0,"polyline": []},
                        "mx": {"constant": 0, "quadratic": 0,"sinus": 0,"polyline": []},
                        "my": {"constant": 0, "quadratic": 0,"sinus": 0,"polyline": []},
                        "mz": {"constant": 0, "quadratic": 0,"sinus": 0,"polyline": []},
                        }
            max_load = 0
            for component, key in enumerate(keys):
                if(any([sinus[component], quad[component], const[component]]) or
                    any(item for item in array[:,component+1])):

                    for currentitem in final_list:
                        polyline[key].append([currentitem[0],currentitem[component+1]])
                        x = currentitem[0]/member_length
                        func = sin(x*3.1416)*sinus[component] + (-4.*x*x+4.*x)*quad[component]+const[component]+currentitem[component+1]
                        max_load = max(max_load,abs(sinus[component]+quad[component]+const[component]+currentitem[component+1]))
                    inner_dict = return_value[key]
                    inner_dict["constant"] = const[component]
                    inner_dict["quadratic"] = quad[component]
                    inner_dict["sinus"] = sinus[component]
                    inner_dict["polyline"] = polyline[key]
                    return_value[key] = inner_dict

        return return_value, max_load, loads_dict["point load configuration"]


    def getuniquepositionlist(self, load_config_list):
        """return an ordereded list of unique locations based on the load configuration list
    ex: load_config_list = [[{"pos":1.0,...},{"pos":3.0,...}],
                            [{"pos":2.0,...},{"pos":3.0,...}],
                            [{"pos":1.5,...},{"pos":2.5,...}]]
            return = [1.0, 1.5, 2.0, 2.5, 3.0]
    """
        unique = []
        for config in load_config_list:
            for info in config:
                if info["pos"] in unique:
                    continue
                unique.append(info["pos"])
        unique.sort()
        return unique

    def interp1d(self,l1,l2, pos):
        """ 1d linear interpolation for the vector components"""
        fac = (l2[1]-l1[1])/(l2[0]-l1[0])
        v = l1[1] + fac*(pos-l1[0])
        return v

    def interpolate(self,pos,loadinfo,start,end,key):
        """ interpolate the result vectors between load poits"""
        result = Vector((0,0,0))
        for i in range(3):
            value1 = [loadinfo[start]["pos"], loadinfo[start][key][i]] #[position, force_component]
            value2= [loadinfo[end]["pos"], loadinfo[end][key][i]] #      [position, force_component]
            result[i] = self.interp1d(value1,value2, pos) #             interpolated [position, force_component]
        return result

    def get_before_and_after(self,pos,load_config_list):
        """ get total values for forces and moments with polilyne distribution
            before and after the position
    ex: load_config_list = [[{"pos":1.0,...,"forces":(1,0,0),...},{"pos":3.0,...,"forces":(3,0,0),...}],
                            [{"pos":2.0,...,"forces":(1,0,0),...},{"pos":3.0,...,"forces":(1,0,0),...}],
                            [{"pos":1.5,...,"forces":(1,0,0),...},{"pos":2.5,...,"forces":(1,0,0),...}]]
            pos = 2.0
            return = {
                        "before": (3,0,0,0,0,0),  ->(fx, fy, fz, mx, my, mz)
                        " after": (4,0,0,0,0,0)   ->(fx, fy, fz, mx, my, mz)
                    }
    """
        force_before = Vector((0,0,0))
        force_after = Vector((0,0,0))
        moment_before = Vector((0,0,0))
        moment_after = Vector((0,0,0))

        for config in load_config_list:
            if pos < config[0]["pos"] or pos > config[-1]["pos"]:
                continue
            start = 0
            end = len(config)-1
            while end-start > 0:
                if pos < config[start]["pos"] or pos > config[end]["pos"]:
                    break
                if config[start]["pos"] == pos:
                    if config[start]["descr"] in ['start','middle']:
                        force_after += config[start]["forces"]
                        moment_after += config[start]["moments"]
                    elif config[start]["descr"] in ['end','middle']:
                        force_before += config[start]["forces"]
                        moment_before += config[start]["moments"]

                elif config[end]["pos"] == pos:
                    if config[end]["descr"] in ['start','middle']:
                        force_after += config[end]["forces"]
                        moment_after += config[end]["moments"]
                    elif config[end]["descr"] in ['end','middle']:
                        force_before += config[end]["forces"]
                        moment_before += config[end]["moments"]

                elif end-start == 1:
                    force_before += self.interpolate(pos,config,start,end,"forces")
                    force_after += self.interpolate(pos,config,start,end,"forces")
                    moment_before += self.interpolate(pos,config,start,end,"moments")
                    moment_after += self.interpolate(pos,config,start,end,"moments")
                start += 1
                end -=1
        return_value = {
            "before": [force_before.x,force_before.y,force_before.z,
                    moment_before.x,moment_before.y,moment_before.z],
            "after": [force_after.x, force_after.y, force_after.z,
                    moment_after.x, moment_after.y, moment_after.z]
                    }
        return return_value

    def get_loads_dict(self,activity_list,element_rotation_matrix):
        """
        get load list
        activity_list: list of IfcStructuralCurveAction or IfcStructuralCurveReaction 
                        applied in the structural curve member
        global_to_local: transformation matrix from global coordinates to local coordinetes
        return: dict{
                    "constant force": (fx,fy,fz,mx,my,mz),	-> sum of linear loads applied with 
                                                                constant distribution
                    "quadratic force": (fx,fy,fz,mx,my,mz),	-> sum of linear loads applied with
                                                                quadratic distribution
                    "sinus force": (fx,fy,fz,mx,my,mz),		-> sum of linear loads applied with 
                                                                sinus distribution
                    "lienar load configuration": list				-> list of load configurations for linear
                                                                and polyline distributions of linear loads
                    }
        description of "linear load configuration":
        list[							-> one item (list)for each IfcStructuralCurveAction applied in the member
                                            with IfcStructuralLoadConfiguration as the applied load
            list[						-> one item (dict) for each item found in the 
                                            Locations attribute of IfcLoadConfiguration
                dict{
                    "pos": float,		-> local position along curve length
                    "descr": string,	-> describe if the item is at the start, middle or end of the list
                    "forces": Vector,	-> linear force applied at that point
                    "moments": Vector	-> linear moment applied at that point
                    }
                ]
            ]
            """
        constant_force = Vector((0,0,0))
        constant_moment = Vector((0,0,0))
        quadratic_force = Vector((0,0,0))
        quadratic_moment = Vector((0,0,0))
        sinus_force = Vector((0,0,0))
        sinus_moment = Vector((0,0,0))
        linear_load_configurations = []
        point_load_configurations = []

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get(),"LENGTHUNIT")

        def get_force_vector(load,transform_matrix,factor = 1.0):
            x = 0 if getattr(load, 'LinearForceX', 0) is None else getattr(load, 'LinearForceX', 0)
            y = 0 if getattr(load, 'LinearForceY', 0) is None else getattr(load, 'LinearForceY', 0)
            z = 0 if getattr(load, 'LinearForceZ', 0) is None else getattr(load, 'LinearForceZ', 0)
            return transform_matrix @ (Vector((x,y,z))*factor)

        def get_moment_vector(load,transform_matrix,factor = 1.0):
            x = 0 if getattr(load, 'LinearMomentX', 0) is None else getattr(load, 'LinearMomentX', 0)
            y = 0 if getattr(load, 'LinearMomentY', 0) is None else getattr(load, 'LinearMomentY', 0)
            z = 0 if getattr(load, 'LinearMomentZ', 0) is None else getattr(load, 'LinearMomentZ', 0)
            return transform_matrix @ (Vector((x,y,z))*factor)

        for item in activity_list:
            activity = item[0]
            factor = item[1]
            load = activity.AppliedLoad
            global_or_local = activity.GlobalOrLocal
            props = bpy.context.scene.BIMStructuralProperties
            reference_frame = props.reference_frame #make it a scene property so it can be changed in a panel
            transform_matrix = Matrix()
            if reference_frame == 'LOCAL_COORDS' and global_or_local != reference_frame:
                transform_matrix = element_rotation_matrix
                transform_matrix.invert()
            elif reference_frame == 'GLOBAL_COORDS' and global_or_local != reference_frame:
                transform_matrix = element_rotation_matrix
            #values for linear loads
            if load.is_a('IfcStructuralLoadConfiguration'):
                locations = getattr(load, 'Locations', [])
                values = [l for l in getattr(load, 'Values', None)
                        if l.is_a() == "IfcStructuralLoadLinearForce"
                        ]
                config_list = []
                for i,l in enumerate(values):
                    forcevalues = get_force_vector(l,transform_matrix,factor)
                    momentvalues = get_moment_vector(l,transform_matrix,factor)
                    if i == 0:
                        descr = 'start'
                    elif i == len(values)-1:
                        descr = 'end'
                    else:
                        descr = 'middle'
                    config_list.append(
                        {"pos": locations[i][0]*unit_scale,
                        "descr": descr,
                        "forces":forcevalues,
                        "moments":momentvalues}
                    )
                linear_load_configurations.append(config_list)
                #load configurations with point loads
                values = [l for l in getattr(load, 'Values', None)
                        if l.is_a() == "IfcStructuralLoadSingleForce"
                        ]
                attr_list = ['ForceX','ForceY','ForceZ','MomentX','MomentY','MomentZ']
                config_list = []
                for i,load in enumerate(values):
                    result_list = [0,0,0,0,0,0]
                    for j, attr in enumerate(attr_list):
                        value = 0 if getattr(load, attr, 0) is None else getattr(load, attr, 0)
                        result_list[j] += value*factor
                    config_list.append(
                        {"pos": locations[i][0]*unit_scale,
                         "values": result_list}
                    )
                point_load_configurations.append(config_list)

            else:
                forcevalues = get_force_vector(load,transform_matrix,factor)
                momentvalues = get_moment_vector(load,transform_matrix,factor)
                if 'CONST' == getattr(activity, 'PredefinedType', None) or activity.is_a('IfcStructuralLinearAction'):
                    constant_force += forcevalues
                    constant_moment += momentvalues
                elif 'PARABOLA' == getattr(activity, 'PredefinedType', None):
                    quadratic_force += forcevalues
                    quadratic_moment += momentvalues
                elif 'SINUS' == getattr(activity, 'PredefinedType', None):
                    sinus_force += forcevalues
                    sinus_moment += momentvalues
        return_value = {
                    "constant force": [constant_force.x,constant_force.y,constant_force.z,
                                        constant_moment.x,constant_moment.y,constant_moment.z],
                    "quadratic force": [quadratic_force.x,quadratic_force.y,quadratic_force.z,
                                        quadratic_moment.x,quadratic_moment.y,quadratic_moment.z],
                    "sinus force": [sinus_force.x,sinus_force.y,sinus_force.z,
                                    sinus_moment.x,sinus_moment.y,sinus_moment.z],
                    "linear load configuration": linear_load_configurations,
                    "point load configuration": point_load_configurations
                    }
        return return_value
