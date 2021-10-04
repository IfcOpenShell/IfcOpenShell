def edit_object_placement(ifc, surveyor, obj=None):
    element = ifc.get_entity(obj)
    if element:
        ifc.run("geometry.edit_object_placement", product=element, matrix=surveyor.get_absolute_matrix(obj))
