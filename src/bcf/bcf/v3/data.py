class Project:
    def __init__(self):
        self.project_id = ""
        self.name = ""


class BimSnippet:
    def __init__(self):
        self.snippet_type = None
        self.is_external = False
        self.reference = None
        self.reference_schema = None


class DocumentReference:
    def __init__(self):
        self.description = None
        self.document_guid = None
        self.url = None
        self.guid = None


class RelatedTopic:
    def __init__(self):
        self.guid = None


class HeaderFile:
    def __init__(self):
        self.file_name = ""
        self.date = None
        self.reference = ""
        self.ifc_project = None
        self.ifc_spatial_structure_element = None
        self.is_external = True


class Header:
    def __init__(self):
        self.files = []


class Topic:
    def __init__(self):
        self.reference_links = []
        self.title = ""
        self.priority = None
        self.index = None  # Deprecated, stored, but ignored
        self.labels = []
        self.creation_date = None
        self.creation_author = None
        self.modified_date = None
        self.modified_author = None
        self.due_date = None
        self.assigned_to = None
        self.stage = None
        self.description = None
        self.bim_snippet = None
        self.document_references = []
        self.related_topics = []
        self.topic_status = None
        self.topic_type = None
        self.guid = None

        self.header = None
        self.comments = {}
        self.viewpoints = {}
        self.server_assigned_id = ""


class Comment:
    def __init__(self):
        self.guid = None
        self.date = None
        self.author = ""
        self.comment = ""
        self.viewpoint = None
        self.modified_date = None
        self.modified_author = ""


class ViewSetupHints:
    def __init__(self):
        self.spaces_visible = False
        self.space_boundaries_visible = False
        self.openings_visible = False


class Component:
    def __init__(self):
        self.originating_system = None
        self.authoring_tool_id = None
        self.ifc_guid = None


class ComponentVisibility:
    def __init__(self):
        self.exceptions = []
        self.default_visibility = False
        self.view_setup_hints = None


class Color:
    def __init__(self):
        self.color = None
        self.components = []


class Components:
    def __init__(self):

        self.selection = []
        self.visibility = None
        self.coloring = []


class Point:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0


class Direction(Point):
    pass


class OrthogonalCamera:
    def __init__(self):
        self.camera_view_point = Point()
        self.camera_direction = Direction()
        self.camera_up_vector = Direction()
        self.view_to_world_scale = 1.0
        self.aspect_ratio = 1.0


class PerspectiveCamera:
    def __init__(self):
        self.camera_view_point = Point()
        self.camera_direction = Direction()
        self.camera_up_vector = Direction()
        self.field_of_view = 60.0
        self.aspect_ratio = 1.0


class Line:
    def __init__(self):
        self.start_point = Point()
        self.end_point = Point()


class ClippingPlane:
    def __init__(self):
        self.location = Point()
        self.direction = Direction()


class Bitmap:
    def __init__(self):
        self.reference = ""  # Only in BCF-XML
        self.bitmap_data = None  # Only in BCF-API
        self.bitmap_format = "PNG"  # Enum of png or jpg
        self.location = Point()
        self.normal = Direction()
        self.up = Direction()
        self.height = 1.0


class Viewpoint:
    def __init__(self):
        self.guid = None
        self.viewpoint = None
        self.snapshot = None
        self.index = None

        self.components = None  # It's not a list, despite the plural name
        self.orthogonal_camera = None
        self.perspective_camera = None
        self.lines = []
        self.clipping_planes = []
        self.bitmaps = []
