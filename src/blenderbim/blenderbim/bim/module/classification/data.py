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

#import ifcopenshell
import ifcopenshell.util.date

def refresh():
    ClassificationData.is_loaded = False

class ClassificationData:
    is_loaded = False
    products = {}
    #classifications = {}  #list of available classifications, es. Omniclass, Uniclass,etc..
    #references = {}  #list of available ifcclassificationsreferences in the current file
    library_file = None                
    library_classifications = {}       #Called in operator
    library_references = {}

    #@classmethod #TODO ??
    #def purge(cls):
    #    cls.is_loaded = False
    #    cls.products = {}
    #    cls.classifications = {}
    #    cls.references = {}
    #    cls.library_file = None
    #    cls.library_classifications = {}
    #    cls.library_references = {}

    @classmethod
    def load(cls,  product_id=None):
        cls._file = tool.Ifc.get()
        cls.data = {
            "classifications" : cls.get_classifications(),  #cls.load_classifications() OLD
            "references" : cls.get_references(),  #cls.load_references() OLD
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
    def get_classifications(cls):
        results = {}
        #cls.classifications = {}       OLD
        for classification in cls._file.by_type("IfcClassification"):
            info = classification.get_info()
            if cls._file.schema == "IFC2X3" and info["EditionDate"]:
                info["EditionDate"] = ifcopenshell.util.date(info.EditionDate).isoformat()
            results = {
                classification.id() : info,
            }
            #results.append(
            #    {
            #        "id" : classification.id(),
            #        "info" : info,
            #    }
            #)
            #cls.classifications[classification.id()] = data    OLD
        return results

    @classmethod
    def get_references(cls):
        results = {}
        #cls.references = {}        OLD
        for reference in cls._file.by_type("IfcClassificationReference"):
            info = reference.get_info()
            if reference.ReferencedSource:
                # data["ReferencedSource"] = cls.get_referenced_source(reference.ReferencedSource)
                info["ReferencedSource"] = reference.ReferencedSource.id()
            results = {
                reference.id() : info,
            }

            #results.append(
            #    {
            #        "id": reference.id(),
            #        "info" : info,
            #    }
            #)
            #cls.references[reference.id()] = data
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