# Note: it is the intent for you to override these with your own functions


def get_application(ifc):
    return (ifc.by_type("IfcApplication") or [None])[0]


def get_user(ifc):
    return (ifc.by_type("IfcPersonAndOrganization") or [None])[0]


get_application_factory = get_application
get_application_backup = get_application
get_user_factory = get_user
get_user_backup = get_user


def factory_reset():
    """Reset the get_user and get_application functions to what came out of box

    When you are developing a custom application, you will typically override
    the get_user and get_application function to your own needs. Sometimes you
    want to reset it to before you monkey-patched it. This function does that
    reset.
    """
    global get_application_factory
    global get_application_backup
    global get_application
    global get_user_factory
    global get_user_backup
    global get_user
    get_application_backup = get_application
    get_application = get_application_factory
    get_user_backup = get_user
    get_user = get_user_factory


def restore():
    """Restore the get_user and get_application function prior to a reset

    In case you want to restore the monkey-patched version of get_user and
    get_application that existed before you applied a factory_reset(), this
    function will do that.
    """
    global get_application_factory
    global get_application_backup
    global get_application
    global get_user_factory
    global get_user_backup
    global get_user
    get_application = get_application_backup
    get_user = get_user_backup
