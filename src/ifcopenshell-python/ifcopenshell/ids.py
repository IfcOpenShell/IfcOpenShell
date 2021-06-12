import operator
import ifcopenshell.util.element

from xmlschema import XMLSchema


class exception(Exception):
    pass


def error(msg):
    raise exception(msg)


class facet_evaluation:
    """
    The evaluation of a facet with data from IFC. Converts to bool and has a human readable string format.
    """

    def __init__(self, success, str):
        self.success = success
        self.str = str

    def __bool__(self):
        return self.success

    def __str__(self):
        return self.str


class meta_facet(type):
    """
    A metaclass for automatically registering facets in a map to be instantiated based on XML tagnames.
    """

    facets = {}

    def __new__(cls, clsname, bases, attrs):
        newclass = super(meta_facet, cls).__new__(cls, clsname, bases, attrs)
        meta_facet.facets[clsname] = newclass
        return newclass


class facet(metaclass=meta_facet):
    """
    The base class for IDS facets. IDS facets are functors constructed from
    XML nodes that return True or False. A getattr method is provided for
    conveniently extracting XML child node text content.
    """ 

    def __init__(self, node):
        self.node = node

    def __getattr__(self, k):
        if k in self.node:
            v = self.node[k]
            if isinstance(v, dict):  #is restriction?
                return restriction(v['xs:restriction'][0])
            else:
                return v
        else:
            return None

    def __iter__(self):
        for k in self.parameters:
            yield k, getattr(self, k)

    def __str__(self):
        di = dict(list(self))
        for k, v in di.items():
            if isinstance(v, str) and not len(v):
                di[k] = "not specified"
        return self.message % di


class entity(facet):
    """
    The IDS entity facet currently *with* inheritance
    """

    parameters = ["name", "predefinedtype"]
    
    def __call__(self, inst, logger):
        # @nb with inheritance
        if self.predefinedtype and hasattr(inst, "PredefinedType"):
            self.message = "an entity name '%(name)s' of predefined type '%(predefinedtype)s'"
            return facet_evaluation(
                inst.is_a(self.name) and inst.PredefinedType == self.predefinedtype,
                self.message % {"name": inst.is_a(), "predefinedtype": inst.PredefinedType}
                )
        else:
            self.message = "an entity name '%(name)s'"
            return facet_evaluation(
                inst.is_a(self.name),
                self.message % {"name": inst.is_a()}
                )
        

class classification(facet):
    """
    The IDS classification facet by traversing the HasAssociations inverse attribute
    """

    parameters = ["system", "value"]
    message = "a classification reference '%(value)s' from '%(system)s'"

    def __call__(self, inst, logger):
        refs = []
        for association in inst.HasAssociations:
            if association.is_a("IfcRelAssociatesClassification"):
                cref = association.RelatingClassification
                refs.append((cref.ReferencedSource.Name, cref.Identification))  # before was .ItemReference instead of .Identification

        if refs:
            return facet_evaluation(
                (self.system, self.value) in refs,
                self.message % {"system": refs[0][0], "value": refs[0][1]}
            )
        else:
            return facet_evaluation(
                False,
                "has no classification"
            )


class property(facet):
    """
    The IDS property facet implenented using `ifcopenshell.util.element`
    """

    parameters = ["name", "propertyset", "value"]
    message = "a property '%(name)s' in '%(propertyset)s' with a value %(value)s"

    def __call__(self, inst, logger):
        props = ifcopenshell.util.element.get_psets(inst)
        pset = props.get(self.propertyset)
        val = pset.get(self.name) if pset else None

        di = {
            "name": self.name,
            "propertyset": self.propertyset,
            "value": "'%s'" % val,
        }

        if val is not None:
            msg = self.message % di
        else:
            if pset:
                msg = "no property '%(name)s' in a set '%(propertyset)s'" % di
            else:
                msg = "no set '%(propertyset)s'" % di

        return facet_evaluation(
            val == self.value,
            msg
            )


class material(facet):
    """
    The IDS material facet by traversing the HasAssociations inverse attribute
    """
    parameters = ["value"]
    message = "a material '%(value)s'"

    def __call__(self, inst, logger):
        material_relations = [rel for rel in inst.HasAssociations if rel.is_a("IfcRelAssociatesMaterial")]
        materials = []
        for rel in material_relations:
            #TODO test all subtypes of material definitions
            if rel.RelatingMaterial.is_a() == "IfcMaterial":
                materials.append(rel.RelatingMaterial.Name)
            elif rel.RelatingMaterial.is_a() == "IfcMaterialMaterialList":  #DEPRECATED in IFC4
                [materials.append(mat.Name) for mat in rel.RelatingMaterial]
            elif rel.RelatingMaterial.is_a() == "IfcMaterialConstituentSet":
                [materials.append(mat.Material.Name) for mat in rel.RelatingMaterial.MaterialConstituents]
            elif rel.RelatingMaterial.is_a() == "IfcMaterialLayerSet":
                [materials.append(mat.Name) for mat in rel.RelatingMaterial.MaterialLayers]
            elif rel.RelatingMaterial.is_a() == "IfcMaterialLayerSetUsage":
                layers = rel.RelatingMaterial.ForLayerSet.MaterialLayers
                [materials.append(layer.Material.Name) for layer in layers]
            elif rel.RelatingMaterial.is_a() == "IfcMaterialProfileSet":
                [materials.append(mat.Material.Name) for mat in rel.RelatingMaterial.MaterialProfiles]
            elif rel.RelatingMaterial.is_a() == "IfcMaterialProfileSetUsage":
                profileSets = rel.RelatingMaterial.ForProfileSet.MaterialProfiles
                [materials.append(pset.Material.Name) for pset in profileSets]
            else:
                logger.error({'guid':inst.GlobalId, 'result':'ERROR', 'sentence':'IfcRelAssociatesMaterial not implemented'})

        return facet_evaluation(
            self.value in materials,
            self.message % {"value": self.value},
        )


class boolean_logic:
    """
    Boolean conjunction over a collection of functions
    """

    def __init__(self, terms):
        self.terms = terms

    def __call__(self, *args):
        eval = [t(*args) for t in self.terms]
        join = [" and ", " or "][self.fold == any]
        return facet_evaluation(
            self.fold(eval),
            join.join(map(str, eval))
            )

    def __str__(self):
        return [" and ", " or "][self.fold == any].join(map(str, self.terms))


class boolean_and(boolean_logic):
    fold = all


class boolean_or(boolean_logic):
    fold = any


class restriction:
    """
    The value restriction from XSD implemented as a list of values and a containment test
    """

    def __init__(self, node):

        self.restriction_on = node['@base'][3:]
        self.type = ""
        self.options = []
  
        for n in node:
            if n[0:3] == "xs:":
                if n[3:] == "enumeration":
                    self.type = "enumeration"
                    for x in node[n]:
                        self.options.append(x["@value"])
                elif n[8:] == "clusive":
                    self.type = "bounds"
                    if n[3:6] == 'min':
                        self.options.insert(0,'>')
                    else:
                        self.options.insert(0,'<')
                    if n[6:9] == 'Inc':
                        self.options[0] += '='
                    self.options[0] += node[n]['@value']
            #TODO implement other restrictions
            #     elif n.nodeType == n.ELEMENT_NODE and (n.tagName.endswith("Inclusive") or n.tagName.endswith("Exclusive")):
            #         self.type = "bounds"
            #         self.options.append(n.getAttribute("value"))
            #     elif n.nodeType == n.ELEMENT_NODE and n.tagName.endswith("length"):
            #         self.type = "length"
            #         self.options.append(n.getAttribute("value"))
            #     elif n.nodeType == n.ELEMENT_NODE and n.tagName.endswith("pattern"):
            #         self.type = "pattern"
            #         self.options.append(n.getAttribute("value"))
            #TODO add min/maxLength
            #TODO add fractionDigits
            #TODO add totalDigits
            #TODO add whiteSpace
                else:
                    logger.error({'result':'ERROR', 'sentence':'Restriction not implemented'})

    def __eq__(self, other):
        if self.type == "enumeration":
            return other in self.options
        elif self.type == "bounds":
            result = True
            for op in self.options:
                if not(eval(str(other)+op)):
                    result = False
            return result
        elif self.type == "length":
            return False    #TODO
        elif self.type == "pattern":
            return False    #TODO
        #TODO add min/maxLength
        #TODO add fractionDigits
        #TODO add totalDigits
        #TODO add whiteSpace
 
    def __repr__(self):
        if self.type == "enumeration":
            return "'%s'" % "' or '".join(self.options)
        elif self.type == "bounds":
            self.options.sort()
            return "of type '%s', having a value %s" % (self.restriction_on, ' and '.join(self.options))
        elif self.type == "length":
            return "of type '%s' with a length of %s" % (self.restriction_on, str(self.options[0]))
        elif self.type == "pattern":
            return "of type '%s' respecting pattern '%s'" % (self.restriction_on, self.options[0])
        #TODO add min/maxLength
        #TODO add fractionDigits
        #TODO add totalDigits
        #TODO add whiteSpace

class specification:
    """
    Represents the XML <specification> node and its two children <applicability> and <requirements>
    """

    def __init__(self, node):
        def parse_rules(node):
            names = [req for req in node for n in node[req]]
            children = [child for req in node for child in node[req]]
            classes = map(meta_facet.facets.__getitem__, names)
            return [cls(n) for cls, n in zip(classes, children)]

        self.applicability = boolean_and(parse_rules(node['applicability']))
        self.requirements = boolean_and(parse_rules(node['requirements']))

    def __call__(self, inst, logger):
        if self.applicability(inst, logger):
            global ifc_checked
            ifc_checked += 1
            valid = self.requirements(inst, logger)

            if valid:
                global ifc_passed
                ifc_passed += 1
                logger.info({'guid':inst.GlobalId, 'result':valid.success,'sentence':str(self) + "\n" + inst.is_a() + " '" + str(inst.Name) + "' (#" + str(inst.id()) + ") has " + str(valid) + " so is compliant"})
            else:
                logger.error({'guid':inst.GlobalId, 'result':valid.success, 'sentence':str(self) + "\n" + inst.is_a() + " '" + str(inst.Name) + "' (#" + str(inst.id()) + ") has " + str(valid) + " so is not compliant"})

    def __str__(self):
        return "Given an instance with %(applicability)s\nWe expect %(requirements)s" % self.__dict__


class ids:
    """
    Represents the XML root <ids> node and its <specification> childNodes.
    """

    def __init__(self, fn):
        ids_schema = XMLSchema("http://standards.buildingsmart.org/IDS/ids.xsd")
        ids_schema.validate(fn)

        ids = ids_schema.to_dict(fn)
        self.specifications = [specification(s) for s in ids['specification']]

    def validate(self, ifc_file, logger):
        for spec in self.specifications:
            for elem in ifc_file.by_type("IfcObject"):
                spec(elem, logger)


ifc_checked = 0
ifc_passed = 0
if __name__ == "__main__":
    import time
    start_time = time.time()
    import sys, os
    import logging
    import ifcopenshell
    from datetime import date

    filename = os.path.join(os.getcwd(), str(date.today())+"_ids_result.txt")

    logger = logging.getLogger("IDS")
    logging.basicConfig(filename=filename, level=logging.INFO, format="%(message)s")
    logging.FileHandler(filename, mode='w')

    ids_file = ids(sys.argv[1])
    ifc_file = ifcopenshell.open(sys.argv[2])

    ids_file.validate(ifc_file, logger)
    
    print("Out of %s IFC elements, %s were checked against %s requirements in %s specification(s) and %s of them passed (%s).\nRuntime=%ss. Results saved to %s" 
    % (len(ifc_file.by_type('IfcProduct')), ifc_checked, len(ids_file.specifications[0].requirements.terms), len(ids_file.specifications), ifc_passed, str(ifc_passed/ifc_checked*100)+'%', round(time.time() - start_time, 2), filename))

