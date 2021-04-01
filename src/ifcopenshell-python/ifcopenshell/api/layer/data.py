import ifcopenshell
import ifcopenshell.util.date
from datetime import datetime


class Data:
    is_loaded = False
    items = {}
    layers = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.items = {}
        cls.layers = {}

    @classmethod
    def load(cls, file):
        cls._file = file
        if not cls._file:
            return
        cls.load_layers()
        cls.is_loaded = True

    @classmethod
    def load_layers(cls):
        cls.layers = {}
        cls.items = {}
        for layer in cls._file.by_type("IfcPresentationLayerAssignment"):
            data = layer.get_info()
            if layer.AssignedItems:
                for item in layer.AssignedItems:
                    cls.items.setdefault(item.id(), []).append(layer.id())
            del data["AssignedItems"]
            cls.layers[layer.id()] = data
