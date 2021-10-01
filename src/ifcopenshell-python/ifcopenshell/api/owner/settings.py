# Note: it is the intent for you to override these with your own functions


def get_application(ifc):
    applications = ifc.by_type("IfcApplication") or [None]
    return applications[0]


def get_user(ifc):
    users = ifc.by_type("IfcPersonAndOrganization") or [None]
    return users[0]
