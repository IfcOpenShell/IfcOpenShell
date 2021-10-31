# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.tool as tool

import ifcopenshell.util.date

def refresh():
    ClassificationsData.is_loaded = False

class ClassificationsData:
    is_loaded = False
    library_file = None
    library_classifications = {}

    @classmethod
    def load(cls):
        cls._file = tool.Ifc.get()
        cls.data = {
            "classifications" : cls.get_classifications(),  #ClassificationsData  list of available classifications, es. Omniclass, Uniclass,etc..
        }
        cls.is_loaded = True

    @classmethod
    def get_classifications(cls):
        results = {}
        for classification in cls._file.by_type("IfcClassification"):
            info = classification.get_info()
            if cls._file.schema == "IFC2X3" and info["EditionDate"]:
                info["EditionDate"] = ifcopenshell.util.date(info.EditionDate).isoformat()
            results = {
                classification.id() : info,
            }

        return results

    @classmethod
    def get_referenced_source(cls, reference):
        if reference.is_a("IfcClassification"):
            return reference
        elif reference.is_a("IfcClassificationReference") and reference.ReferencedSource:
            return cls.get_referenced_source(reference.ReferencedSource)

    @classmethod
    def load_library(cls, filepath):
        cls.library_file = ifcopenshell.open(filepath)
        cls.library_classifications = {}
        for classification in cls.library_file.by_type("IfcClassification"):
            cls.library_classifications[classification.id()] = classification.Name


class ClassificationReferencesData:
    is_loaded = False
    products = {}
    #library_references = {}  #never called

    @classmethod
    def load(cls,  product_id=None):
        cls._file = tool.Ifc.get()
        cls.data = {
            "references" : cls.get_references(),  #list of available ifcclassificationsreferences in the current file
        }
        if product_id:
            cls.load_product_classifications(product_id)
        cls.is_loaded = True
    
    @classmethod
    def load_product_classifications(cls, product_id):
        product = cls._file.by_id(product_id)
        cls.products[product_id] = []
        if not product.HasAssociations:
            return
        for association in product.HasAssociations:
            if association.is_a("IfcRelAssociatesClassification"):
                cls.products[product_id].append(association.RelatingClassification.id())

    @classmethod
    def get_references(cls):
        results = {}
        for reference in cls._file.by_type("IfcClassificationReference"):
            info = reference.get_info()
            if reference.ReferencedSource:
                # data["ReferencedSource"] = cls.get_referenced_source(reference.ReferencedSource)
                info["ReferencedSource"] = reference.ReferencedSource.id()
            results = {
                reference.id() : info,
            }
        return results