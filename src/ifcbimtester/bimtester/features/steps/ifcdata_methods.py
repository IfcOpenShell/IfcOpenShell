from utils import IfcFile


def has_ifcdata_specific_schema(context, target_schema):
    real_schema = IfcFile.get().schema
    assert real_schema == target_schema, (
        _("We expected a schema of {} but instead got {}")
        .format(target_schema, real_schema)
    )
