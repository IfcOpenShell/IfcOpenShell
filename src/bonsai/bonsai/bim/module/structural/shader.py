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

import gpu
from typing import Literal

class DecorationShader:
    "shader for the load decorations"

    def __init__(self):
        pass

    def new(self, pattern: Literal["PERPENDICULAR DISTRIBUTED FORCE",
            "PARALLEL DISTRIBUTED FORCE",
            "DISTRIBUTED MOMENT",
            "SINGLE FORCE",
            "SINGLE MOMENT",
            "PLANAR LOAD",]) -> gpu.types.GPUShader:
        """pattern: string description of the desired shader
        Possible values
        PERPENDICULAR DISTRIBUTED FORCE: pattern for distributed force
                                         perpendicular to the curve member axis
        PARALLEL DISTRIBUTED FORCE: pattern for distributed force
                                    along the curve member axis
        DISTRIBUTED MOMENT: pattern for distributed moment in curve members
        SINGLE FORCE: pattern for single forces
        SINGLE MOMENT: pattern for single moments
        PLANAR LOAD: pattern for planar loads
        """
        valid_patterns = {
            "PERPENDICULAR DISTRIBUTED FORCE",
            "PARALLEL DISTRIBUTED FORCE",
            "DISTRIBUTED MOMENT",
            "SINGLE FORCE",
            "SINGLE MOMENT",
            "PLANAR LOAD",
        }
        if pattern not in valid_patterns:
            raise ValueError(
                """pattern must be one of:
                             PERPENDICULAR DISTRIBUTED FORCE
                             PARALLEL DISTRIBUTED FORCE,
                             DISTRIBUTED MOMENT,
                             SINGLE FORCE,
                             SINGLE MOMENT,
                             PLANAR LOAD"""
            )
        if "DISTRIBUTED" in pattern.upper():
            shader = self.get_linear_shader(pattern)
            return shader
        elif "SINGLE" in pattern.upper():
            shader = self.get_point_shader(pattern)
            return shader
        elif "PLANAR" in pattern.upper():
            shader = self.get_planar_shader()
            return shader

    def get_linear_shader(self, pattern: Literal["PERPENDICULAR DISTRIBUTED FORCE",
            "PARALLEL DISTRIBUTED FORCE",
            "DISTRIBUTED MOMENT"]) -> gpu.types.GPUShader:
        """pattern: type of pattern
        PERPENDICULAR DISTRIBUTED FORCE
        PARALLEL DISTRIBUTED FORCE,
        DISTRIBUTED MOMENT,
        """
        vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
        vert_out.smooth("VEC3", "forces")
        vert_out.smooth("VEC3", "co")

        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.push_constant("MAT4", "viewProjectionMatrix")
        shader_info.push_constant("VEC4", "color")
        shader_info.push_constant("FLOAT", "spacing")
        shader_info.push_constant("FLOAT", "maxload")

        shader_info.vertex_in(0, "VEC3", "position")
        shader_info.vertex_in(1, "VEC3", "sin_quad_lin_forces")
        shader_info.vertex_in(2, "VEC3", "coord")

        shader_info.vertex_out(vert_out)
        shader_info.fragment_out(0, "VEC4", "FragColor")

        shader_info.vertex_source(
            "void main()"
            "{"
            "  gl_Position = viewProjectionMatrix * vec4(position, 1.0f);"
            "  co = coord;"
            "  forces = sin_quad_lin_forces;"
            "}"
        )

        if pattern == "PERPENDICULAR DISTRIBUTED FORCE":
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
                "float d = clamp(top+b+c,0.0,0.9)*mask;"
                "if (d == 0.0) discard;"
                "FragColor = vec4(color.xyz,d*color.w);"
                "}"
            )

        elif pattern == "PARALLEL DISTRIBUTED FORCE":
            shader_info.fragment_source(
                "void main()"
                "{"
                "float y = co.y;"
                "float x = step(0.,y)*(co.z-co.x)+step(y,0.)*(co.x);"
                "float abs_y = abs(y);"
                "float a = abs(mod(abs_y,spacing)-0.5*spacing)*5.0;"
                "float a2 = mod(x,3.0*spacing);"
                "float b = step(a,a2)*step(a2,1.2*spacing);"
                "float c = step(0.8*spacing,mod(abs_y+0.4*spacing,spacing))"
                "*(step(1.2*spacing,a2))*step(a2,2.5*spacing);"
                "float sinvalue = forces.x;"
                "float quadraticvalue = forces.y;"
                "float linearvalue = forces.z;"
                "x = co.x/co.z;"
                "float f = (sin(x*3.1416)*sinvalue"
                "+(-4.*x*x+4.*x)*quadraticvalue"
                "+linearvalue)/maxload;"
                "float mask = step(0.,y)*step(y,f)+step(y,0.)*step(f,y);"
                "float top = step(abs(y-f),0.2*1.2*spacing);"
                "float d = clamp(top+b+c,0.0,0.9)*mask;"
                "if (d == 0.0) discard;"
                "FragColor = vec4(color.xyz,d*color.w);"
                "}"
            )

        elif pattern == "DISTRIBUTED MOMENT":
            shader_info.fragment_source(
                "void main()"
                "{"
                "float x = step(co.y,0.)*(co.x)+step(0.,co.y)*(co.z-co.x);"
                "float y = step(co.y,-0.00001)*(co.y)+step(0.,co.y)*(0.-co.y);"
                "x = mod((0.5/spacing)*x,1.4)-0.7;"
                "y = mod((0.5/spacing)*y,1.4)-0.7;"
                "float abs_y = abs(y);"
                "vec2 st = vec2(1.9*x,y);"
                "vec2 orig = vec2(0.,0.);"
                "float circ = step(distance(st,orig),0.33)*step(0.27,distance(st,orig));"
                "float tri_mask = step(st.y,st.x)+step(-st.x,st.y);"
                "float circ_arrow = step(st.x,4.0*st.y-0.75)*step(0.25*st.y-0.34,st.x)*(1.-tri_mask);"
                "float circmask = step(distance(st,orig),0.1)+step(0.5,distance(st,orig))+step(st.x,0.);"
                "float body = step(-0.03,st.y)*step(st.y,0.03)*step(-0.3,x)*step(x,0.576);"
                "float body_arrow = step(-0.5+3.*st.y,x)*step(-0.5-3.*st.y,x)*step(x,-0.3);"
                "float d = clamp(circmask*(body+body_arrow)+circ_arrow+circ*tri_mask,0.,1.);"
                "float sinvalue = forces.x;"
                "float quadraticvalue = forces.y;"
                "float linearvalue = forces.z;"
                "x = co.x/co.z;"
                "float f = (sin(x*3.1416)*sinvalue"
                "+(-4.*x*x+4.*x)*quadraticvalue"
                "+linearvalue)/maxload;"
                "float mask = step(0.,co.y)*step(co.y,f)+step(co.y,0.)*step(f,co.y);"
                "float top = step(abs(co.y-f),0.2*1.2*spacing);"
                "d = clamp(top+d,0.0,0.9)*mask;"
                "if (d == 0.0) discard;"
                "FragColor = vec4(color.xyz,d*color.w);"
                "}"
            )

        shader = gpu.shader.create_from_info(shader_info)
        del vert_out
        del shader_info
        return shader

    def get_point_shader(self, pattern: Literal["SINGLE FORCE","SINGLE MOMENT"]) -> gpu.types.GPUShader:
        """param: pattern: type of pattern
        SINGLE FORCE,
        SINGLE MOMENT"""
        vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
        vert_out.smooth("VEC3", "co")

        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.push_constant("MAT4", "viewProjectionMatrix")
        shader_info.push_constant("VEC4", "color")
        shader_info.push_constant("FLOAT", "spacing")

        shader_info.vertex_in(0, "VEC3", "position")
        shader_info.vertex_in(1, "VEC3", "coord")

        shader_info.vertex_out(vert_out)
        shader_info.fragment_out(0, "VEC4", "FragColor")

        shader_info.vertex_source(
            "void main()" "{" "  gl_Position = viewProjectionMatrix * vec4(position, 1.0f);" "  co = coord;" "}"
        )

        if pattern == "SINGLE FORCE":
            shader_info.fragment_source(
                "void main()"
                "{"
                "float body = step(abs(co.x),0.2*spacing)*step(2.*spacing,co.y);"
                "float arrow = step(3.5*abs(co.x)+0.02,abs(co.y))*step(co.y,2.*spacing)*step(0.,co.y);"
                "float d = clamp(body+arrow,0.0,0.5);"
                "if (d == 0.0) discard;"
                "FragColor = vec4(color.xyz,d*color.w);"
                "}"
            )

        elif pattern == "SINGLE MOMENT":
            shader_info.fragment_source(
                "void main()"
                "{"
                "float circ = step(distance(co.xy,vec2(0.,0.)),0.33)*step(0.27,distance(co.xy,vec2(0.,0.)));"
                "float mask = step(co.y,co.x)+step(-co.x,co.y);"
                "float circ_arrow = step(co.x,4.0*co.y-0.75)*step(0.25*co.y-0.34,co.x)*(1.-mask);"
                "float d = clamp(circ_arrow+circ*mask,0.0,0.5);"
                "if (d == 0.0) discard;"
                "FragColor = vec4(color.xyz,d*color.w);"
                "}"
            )

        shader = gpu.shader.create_from_info(shader_info)
        del vert_out
        del shader_info
        return shader

    def get_planar_shader(self) -> gpu.types.GPUShader:
        """shader for planar loads"""
        vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
        vert_out.smooth("VEC3", "co")

        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.push_constant("MAT4", "viewProjectionMatrix")
        shader_info.push_constant("VEC4", "color")
        shader_info.push_constant("FLOAT", "spacing")

        shader_info.vertex_in(0, "VEC3", "position")
        shader_info.vertex_in(1, "VEC3", "coord")

        shader_info.vertex_out(vert_out)
        shader_info.fragment_out(0, "VEC4", "FragColor")

        shader_info.vertex_source(
            "void main()" "{" "  gl_Position = viewProjectionMatrix * vec4(position, 1.0f);" "  co = coord;" "}"
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
            "float mask = step(0.,y)*step(y,0.98)+step(y,0.)*step(0.98,y);"
            "float top = step(abs(y-0.98),0.2*1.2*spacing);"
            "float d = clamp(0.2*y+(top+b+c)*mask,0.0,0.4);"
            "FragColor = vec4(color.xyz,d*color.w);"
            "}"
        )

        shader = gpu.shader.create_from_info(shader_info)
        del vert_out
        del shader_info
        return shader
