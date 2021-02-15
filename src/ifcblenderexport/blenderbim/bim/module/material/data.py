import ifcopenshell
from blenderbim.bim.ifc import IfcStore


class Data:
    is_loaded = False
    materials = {}
    constituent_sets = {}
    constituents = {}
    layer_sets = {}
    layers = {}
    profile_sets = {}
    profiles = {}
    lists = {}
    products = {}
    _file = None

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.materials = {}
        cls.constituent_sets = {}
        cls.constituents = {}
        cls.layer_sets = {}
        cls.layers = {}
        cls.profile_sets = {}
        cls.profiles = {}
        cls.lists = {}
        cls.products = {}
        cls._file = None

    @classmethod
    def load(cls, product_id=None):
        cls._file = IfcStore.get_file()
        if not cls._file:
            return
        if product_id:
            return cls.load_product_material(product_id)
        cls.load_materials()
        cls.load_constituents()
        cls.load_layers()
        cls.load_profiles()
        cls.load_lists()
        cls.is_loaded = True

    @classmethod
    def load_materials(cls):
        cls.materials = {}
        cls.load_element("IfcMaterial", cls.materials)

    @classmethod
    def load_constituents(cls):
        cls.constituent_sets = {}
        cls.constituents = {}
        cls.load_element("IfcMaterialConstituent", cls.constituents)
        cls.load_element("IfcMaterialConstituentSet", cls.constituent_sets)

    @classmethod
    def load_layers(cls):
        cls.layer_sets = {}
        cls.layers = {}
        cls.load_element("IfcMaterialLayer", cls.layers)
        cls.load_element("IfcMaterialLayerSet", cls.layer_sets)

    @classmethod
    def load_profiles(cls):
        cls.profile_sets = {}
        cls.profiles = {}
        cls.load_element("IfcMaterialProfile", cls.profiles)
        cls.load_element("IfcMaterialProfileSet", cls.profile_sets)

    @classmethod
    def load_lists(cls):
        cls.lists = {}
        cls.load_element("IfcMaterialList", cls.lists)

    @classmethod
    def load_product_material(cls, product_id):
        cls.products[product_id] = {}
        for association in cls._file.by_id(product_id).HasAssociations:
            if association.is_a("IfcRelAssociatesMaterial"):
                cls.load_association(association, product_id)

    @classmethod
    def load_element(cls, ifc_class, to_dict):
        try:
            elements = cls._file.by_type(ifc_class)
        except:
            return
        for element in elements:
            to_dict[element.id()] = cls.get_simple_info(element)

    @classmethod
    def get_simple_info(cls, element):
        info = element.get_info()
        for key, value in info.items():
            if isinstance(value, ifcopenshell.entity_instance):
                info[key] = value.id()
            elif isinstance(value, tuple) and value and isinstance(value[0], ifcopenshell.entity_instance):
                info[key] = [v.id() for v in value]
        return info

    @classmethod
    def load_association(cls, association, product_id):
        material_select = association.RelatingMaterial
        if material_select.is_a("IfcMaterialLayerSetUsage"):  # TODO: implement usages
            material_select = material_select.ForLayerSet
        elif material_select.is_a("IfcMaterialProfileSetUsage"):  # TODO: implement usages
            material_select = material_select.ForProfileSet
        cls.products[product_id] = {"type": material_select.is_a(), "id": material_select.id()}
