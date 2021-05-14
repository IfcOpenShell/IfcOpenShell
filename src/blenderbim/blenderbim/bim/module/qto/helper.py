import bmesh


def calculate_height(obj):
    return obj.dimensions[2]


def calculate_volume(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = bm.calc_volume()
    bm.free()
    return result
