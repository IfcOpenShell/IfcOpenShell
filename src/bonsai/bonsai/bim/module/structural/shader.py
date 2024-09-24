import bpy
import gpu
import numpy as np
from math import sin
from mathutils import Vector, Matrix
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.attribute
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore


class ShaderInfo:
    def __init__(self,shader_type: str):
        self.is_empty = True
        self.shader = None
        self.shader_type = shader_type
        self.args = {}
        self.indices = []
        self.text_info = []
        self.info = []
    
    def update(self):
        self.info = []
        self.get_linear_loads()
        if len(self.info):
            self.is_empty = False
        
    def get_shader(self):
        """ param: shader_type: type of shader in ["DistributedLoad", "PointLoad"]
        return: shader"""
        if self.shader_type == "DistributedLoad":
            vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
            vert_out.smooth('VEC3', "forces")
            vert_out.smooth('VEC3', "co")
        
            shader_info = gpu.types.GPUShaderCreateInfo()
            shader_info.push_constant('MAT4', "viewProjectionMatrix")
            shader_info.push_constant('VEC4', "color")
            shader_info.push_constant('FLOAT', "spacing")
            shader_info.push_constant('FLOAT', "maxload")
        
            shader_info.vertex_in(0, 'VEC3', "position")
            shader_info.vertex_in(1, 'VEC3', "sin_quad_lin_forces")
            shader_info.vertex_in(2, 'VEC3', "coord")
            
            shader_info.vertex_out(vert_out)
            shader_info.fragment_out(0, 'VEC4', "FragColor")
        
            shader_info.vertex_source(
                "void main()"
                "{"
                "  gl_Position = viewProjectionMatrix * vec4(position, 1.0f);"
                "  co = coord;"
                "  forces = sin_quad_lin_forces;"
                "  gl_Position = viewProjectionMatrix * vec4(position, 1.0f);"
                "}"
            )
        
        
            shader_info.fragment_source(
            "void main()"
            "{"
                "float x = co.x;"
                "float y = co.y;"
                "float abs_y = abs(y);"
        
                "float a = abs(mod(x,spacing)-0.5*spacing)*5.0;"
                "float b = step(a,abs_y)*(step(abs_y,1.2*spacing));"
                "float c = step(0.8*spacing,mod(x+0.4*spacing,spacing))*(step(1.2*spacing,abs_y));"
        
                "float sinvalue = forces.x;"
                "float quadraticvalue = forces.y;"
                "float linearvalue = forces.z;"
                "x = co.x/co.z;"
                "float f = (sin(x*3.1416)*sinvalue"
                      "+(-4.*x*x+4.*x)*quadraticvalue"
                      "+linearvalue)/maxload;"
                "float mask = step(0.,y)*step(y,f)+step(y,0.)*step(f,y);"
            
                "float top = step(abs(y-f),0.2*1.2*spacing);"
                "float d = clamp(0.1+top+b+c,0.0,0.5)*mask;"
        
                "FragColor = vec4(color.xyz,d*color.w);"
            "}"
            )
        
            shader = gpu.shader.create_from_info(shader_info)
            del vert_out
            del shader_info
            return shader


    def get_linear_loads(self): #for now it only works for distributed loads
        coords = []
        indices = []
        load_info = []
        coords_for_shader = []
        color = []
        text_info = []
        uniforms = []
        info = []
    
        list_of_curve_members = tool.Ifc.get().by_type("IfcStructuralCurveMember")
        for member in list_of_curve_members:
            activity_list = [getattr(a, 'RelatedStructuralActivity', None) for a in getattr(member, 'AssignedStructuralActivity', None)
                             if getattr(a, 'RelatedStructuralActivity', None).is_a() in ['IfcStructuralCurveAction','IfcStructuralLinearAction']]
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
            if blender_object.type == 'MESH':
                start_co = blender_object.matrix_world @ blender_object.data.vertices[0].co
                end_co = blender_object.matrix_world @ blender_object.data.vertices[1].co
            x_axis = Vector(end_co-start_co).normalized()
            z_direction = getattr(member, 'Axis')
            #local coordinates
            z_axis = Vector(getattr(z_direction, 'DirectionRatios', None)).normalized()
            y_axis = z_axis.cross(x_axis).normalized()
            z_axis = x_axis.cross(y_axis).normalized()
            global_to_local = Matrix(((x_axis.x,y_axis.x,z_axis.x,0),
                                      (x_axis.y,y_axis.y,z_axis.y,0),
                                      (x_axis.z,y_axis.z,z_axis.z,0),
                                      (0,0,0,1)))
    
            #get shader args for each direction
            reference_frame = 'GLOBAL_COORDS' #make it a scene property so it can be changed in a panel
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
            shader = self.get_shader()
            member_length =  Vector(end_co-start_co).length
            loads_dict, maxforce = get_loads_per_direction(activity_list,global_to_local,member_length)
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

                addindex = len(coords)
                counter = 0
                for i in range(len(polyline)-1):
                    current = Vector(polyline[i]+[0])
                    nextitem = Vector(polyline[i+1]+[0])

                    if any([current.y, nextitem.y,constant,quadratic,sinus]): #if there is load in the z direction
                        negative = -direction + start_co + x_axis*current.x
                        positive = direction + start_co + x_axis*current.x
                        coords.append(negative)
                        coords_for_shader.append((current.x, 1.0,member_length))
                        load_info.append((sinus, quadratic, current.y + constant))
                        color.append(color_axis)
                        #info to render load value
                        x = current.x/member_length
                        func = sin(x*3.1416)*sinus + (-4.*x*x+4.*x)*quadratic+constant+current.y
                        if func:
                            text_info.append(
                                {"position": -direction*func/maxforce + start_co + x_axis*current.x,
                                "normal": direction.cross(x_axis).normalized(), "text": f'{func:.2f} '}
                                )
                        maxforce = max(maxforce,abs(func))
                        coords.append(positive)
                        coords_for_shader.append((current[0],-1.0,member_length))
                        load_info.append((sinus, quadratic, current.y + constant))
                        color.append(color_axis)

                        indices.append((0 + counter + addindex,
                                        1 + counter + addindex,
                                        2 + counter + addindex))
                        indices.append((3 + counter + addindex,
                                        2 + counter + addindex,
                                        1 + counter + addindex))
                        if i == len(polyline)-2:
                            negative = -direction + start_co + x_axis*nextitem.x
                            positive = direction + start_co + x_axis*nextitem.x
                            coords.append(negative)
                            coords_for_shader.append((nextitem.x, 1.0,member_length))
                            load_info.append((sinus, quadratic, nextitem.y + constant))
                            color.append(color_axis)
                            #info to render load value
                            x = nextitem.x/member_length
                            func = sin(x*3.1416)*sinus + (-4.*x*x+4.*x)*quadratic+constant+nextitem.y
                            if func:
                                text_info.append(
                                    {"position": -direction*func/maxforce + start_co + x_axis*nextitem.x,
                                    "normal": direction.cross(x_axis).normalized(), "text": f'{func:.2f} '}
                                    )
                            maxforce = max(maxforce,abs(func))
                            coords.append(positive)
                            coords_for_shader.append((nextitem.x,-1.0,member_length))
                            load_info.append((sinus, quadratic, nextitem.y + constant))
                            color.append(color_axis)

                        counter += 2
                if len(coords):
                    self.info.append(
                    {
                        "shader": shader,
                        "args": {"position": coords, "sin_quad_lin_forces": load_info,"coord": coords_for_shader},
                        "indices": indices,
                        "uniforms": [["color", color_axis],["spacing", 0.2],["maxload",maxforce]]
                    }
                )
                coords = []
                load_info = []
                coords_for_shader = []
                indices = []
            for info in self.info:
                info["uniforms"][2][1] = maxforce

        self.text_info = text_info


def get_loads_per_direction(activity_list,global_to_local,member_length):
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
    loads_dict = get_loads_dict(activity_list,global_to_local)
    const = loads_dict["constant force"]
    quad = loads_dict["quadratic force"]
    sinus = loads_dict["sinus force"]
    loads = loads_dict["load configuration"]
    unique_list = getuniquepositionlist(loads)
    final_list = []
    for pos in unique_list:
        value = get_before_and_after(pos,loads)
        if value["before"] == value["after"]:
            final_list.append([pos]+value["before"])
        else:
            final_list.append([pos]+value["before"])
            final_list.append([pos]+value["after"])
    
    if not len(final_list) and any(const+quad+sinus):
        final_list.append([0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        final_list.append([member_length,0.0,0.0,0.0,0.0,0.0,0.0])
        
    elif len(final_list) and any(const+quad+sinus):
        if final_list[0][0]: #if first item location is not 0 append an item at the zero
            final_list = [[0.0,0.0,0.0,0.0,0.0,0.0,0.0]]+final_list
        else:
            del final_list[0]
        if abs(final_list[-1][0] - member_length) > 0.01:
            final_list.append([member_length,0.0,0.0,0.0,0.0,0.0,0.0])
        else:
            del final_list[-1]
        
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
                max_load = max(max_load,abs(func))
            inner_dict = return_value[key]
            inner_dict["constant"] = const[component]
            inner_dict["quadratic"] = quad[component]
            inner_dict["sinus"] = sinus[component]
            inner_dict["polyline"] = polyline[key]
            return_value[key] = inner_dict

    return return_value, max_load+abs(sinus[component]+quad[component])


def getuniquepositionlist(load_config_list):
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

def interp1d(l1,l2, pos):
    """ 1d linear interpolation for the vector components"""
    fac = (l2[1]-l1[1])/(l2[0]-l1[0])
    v = l1[1] + fac*(pos-l1[0])
    return v

def interpolate(pos,loadinfo,start,end,key):
    """ interpolate the result vectors between load poits"""
    result = Vector((0,0,0))
    for i in range(3):
        value1 = [loadinfo[start]["pos"], loadinfo[start][key][i]] #[position, force_component]
        value2= [loadinfo[end]["pos"], loadinfo[end][key][i]] #      [position, force_component]
        result[i] = interp1d(value1,value2, pos) #             interpolated [position, force_component]
    return result

def get_before_and_after(pos,load_config_list):
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
                force_before += interpolate(pos,config,start,end,"forces")
                force_after += interpolate(pos,config,start,end,"forces")
                moment_before += interpolate(pos,config,start,end,"moments")
                moment_after += interpolate(pos,config,start,end,"moments")
            start += 1
            end -=1
    return_value = {
        "before": [force_before.x,force_before.y,force_before.z,
                   moment_before.x,moment_before.y,moment_before.z],
           "after": [force_after.x, force_after.y, force_after.z,
                  moment_after.x, moment_after.y, moment_after.z]
                  }
    return return_value

def get_loads_dict(activity_list,global_to_local):
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
                   "load configuration": list				-> list of load configurations for linear
                                                            and polyline distributions of linear loads
                   }
       description of "load configuration":
    list[							-> one item (list)for each IfcStructuralCurveAction applied in the member
                                        with IfcStructuralLoadConfiguration as the applied load
         list[						-> one item (dict) for each item found in the 
                                        Locations attribute of IfcLoadConfiguration
               dict{
                  "pos": float,		-> local position along curve length
                  "descr": string,	-> describe if the item is at the star, middle or end of the list
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
    load_configurations = []

    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get(),"LENGTHUNIT")

    def get_force_vector(load,transform_matrix):
        x = 0 if getattr(load, 'LinearForceX', 0) is None else getattr(load, 'LinearForceX', 0)
        y = 0 if getattr(load, 'LinearForceY', 0) is None else getattr(load, 'LinearForceY', 0)
        z = 0 if getattr(load, 'LinearForceZ', 0) is None else getattr(load, 'LinearForceZ', 0)
        return transform_matrix @ Vector((x,y,z))

    def get_moment_vector(load,transform_matrix):
        x = 0 if getattr(load, 'LinearMomentX', 0) is None else getattr(load, 'LinearMomentX', 0)
        y = 0 if getattr(load, 'LinearMomentY', 0) is None else getattr(load, 'LinearMomentY', 0)
        z = 0 if getattr(load, 'LinearMomentZ', 0) is None else getattr(load, 'LinearMomentZ', 0)
        return transform_matrix @ Vector((x,y,z))

    for activity in activity_list:
        load = activity.AppliedLoad
        global_or_local = activity.GlobalOrLocal
        reference_frame = 'GLOBAL_COORDS' #make it a scene property so it can be changed in a panel
        transform_matrix = Matrix()
        if reference_frame == 'LOCAL_COORDS' and global_or_local != reference_frame:
            transform_matrix = global_to_local
        elif reference_frame == 'GLOBAL_COORDS' and global_or_local != reference_frame:
            transform_matrix = global_to_local.invert()
        #values for linear loads
        if load.is_a('IfcStructuralLoadConfiguration'):
            locations = getattr(load, 'Locations', [])
            values = [l for l in getattr(load, 'Values', None)
                    if l.is_a() == "IfcStructuralLoadLinearForce"
                    ]
            config_list = []
            for i,l in enumerate(values):
                forcevalues = get_force_vector(l,transform_matrix)
                momentvalues = get_moment_vector(l,transform_matrix)
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
            load_configurations.append(config_list)
        else:
            forcevalues = get_force_vector(load,transform_matrix)
            momentvalues = get_moment_vector(load,transform_matrix)
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
                   "load configuration": load_configurations
                   }
    return return_value
