import bpy.props
import bpy.types


class AuginProperties(bpy.types.PropertyGroup):
    username: bpy.props.StringProperty(name="Username")
    password: bpy.props.StringProperty(name="Password")
    token: bpy.props.StringProperty(name="Token")
    project_name: bpy.props.StringProperty(name="Project Name")
    project_filename: bpy.props.StringProperty(name="IFC Filename")
    is_success: bpy.props.BoolProperty(name="Is Successful Upload", default=False)
