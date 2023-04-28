import bpy
import blenderbim.core.tool
import blenderbim.tool as tool
from ifcopenshell.util.selector import Selector


class Search(blenderbim.core.tool.Search):
    @classmethod
    def from_selector_query(cls, query):
        """Returns a list of products from a selector query"""
        return Selector().parse(tool.Ifc.get(), query)
