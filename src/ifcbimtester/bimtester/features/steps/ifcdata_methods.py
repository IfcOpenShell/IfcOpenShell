from utils import IfcFile


def provide_ifcfile_by_argument(context):
    try:
        IfcFile.load(context.config.userdata.get("ifcfile"))
    except:
        assert False, (
            _("The IFC {} file could not be loaded")
            .format(context.config.userdata.get('ifcfile'))
        )


def has_ifcdata_specific_schema(context, target_schema):
    real_schema = IfcFile.get().schema
    assert real_schema == target_schema, (
        _("We expected a schema of {} but instead got {}")
        .format(target_schema, real_schema)
    )
