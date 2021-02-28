import operator
import ifcopenshell.util.element

from xml.dom.minidom import parse


class exception(Exception): pass

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
        v = self.node.getElementsByTagName(k)[0]
        elems = [n for n in v.childNodes if n.nodeType == n.ELEMENT_NODE]
        if elems:
            return restriction(elems[0])
        else:
            return v.firstChild.nodeValue.strip()
        
    def __iter__(self):
        for k in self.parameters:
            yield k, getattr(self, k)
            
    def __str__(self):
        return self.message % dict(list(self))


class entity(facet):
    """
    The IDS entity facet currently *with* inheritance
    """
    
    parameters = ["name"]
    message = "an entity name '%(name)s'"

    def __call__(self, inst, logger):
        logger.debug("Testing %s == %s", inst.is_a(), self.name)
        # @nb with inheritance
        # return inst.is_a() == self.name
        return facet_evaluation(
            inst.is_a(self.name),
            self.message % {'name':inst.is_a()}
        )
        

class classification(facet):
    """
    The IDS classification facet by traversing the HasAssociations inverse attribute
    """
    
    parameters = ["system", "value"]
    message = "a classification reference to '%(value)s' from '%(system)s'"

    def __call__(self, inst, logger):
        refs = []
        for association in inst.HasAssociations:
            if association.is_a("IfcRelAssociatesClassification"):
                cref = association.RelatingClassification
                refs.append((cref.ReferencedSource, cref.Name))

        return facet_evaluation(
            (self.system, self.value) in refs,
            # @todo
            ''
        )
        


class property(facet):
    """
    The IDS property facet implenented using `ifcopenshell.util.element`
    """

    parameters = ["property", "propertyset", "value"]
    message = "a property '%(property)s' in '%(propertyset)s' with value '%(value)s'"

    def __call__(self, inst, logger):
        props = ifcopenshell.util.element.get_psets(inst)
        pset = props.get(self.propertyset)
        val = pset.get(self.property) if pset else None
        logger.debug("Testing %s == %s", val, self.value)
        
        di = {
            'property': self.property,
            'propertyset': self.propertyset,
            'value': val
        }
        
        if val is not None:
            msg = self.message % di
        else:
            if pset:
                msg = "a set '%(propertyset)s', but no property '%(property)'" % di
            else:
                msg = "no set '%(propertyset)s'" % di
            
        return facet_evaluation(
            val == self.value,
            msg
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
        self.options = [
            n.getAttribute("value")
            for n in node.childNodes
            if n.nodeType == n.ELEMENT_NODE and n.tagName.endswith("enumeration")
        ]

    def __eq__(self, other):
        return other in self.options

    def __repr__(self):
        return " or ".join(self.options)


class specification:
    """
    Represents the XML <specification> node and its two children <applicability> and <requirements>
    """

    def __init__(self, node):
        def parse_rules(node):
            children = [n for n in node.childNodes if n.nodeType == n.ELEMENT_NODE]
            names = map(operator.attrgetter("tagName"), children)
            classes = map(meta_facet.facets.__getitem__, names)
            return [cls(n) for cls, n in zip(classes, children)]

        phrases = [n for n in node.childNodes if n.nodeType == n.ELEMENT_NODE]
        
        len(phrases) == 2 or error("expected two child nodes for <specification>")
        phrases[0].tagName == "applicability" or error("expected <applicability>")
        phrases[1].tagName == "requirements" or error("expected <requirements>")
        
        self.applicabiliy, self.requirements = (
            boolean_and(parse_rules(phrase)) for phrase in phrases
        )

    def __call__(self, inst, logger):
        if self.applicabiliy(inst, logger):
            valid = self.requirements(inst, logger)
            if valid:
                logger.info(str(self) + "\n%s has" % inst + " " + str(valid) + " so is compliant")
            else:
                logger.error(str(self) + "\n%s has" % inst + " " + str(valid) + " so is not compliant")
                
    def __str__(self):
        return "Given an instance with %(applicabiliy)s\nWe expect %(requirements)s" % self.__dict__


class ids:
    """
    Represents the XML root <ids> node and its <specification> childNodes.
    """

    def __init__(self, fn):
        dom = parse(fn)
        ids = dom.childNodes[0]
        ids.tagName == "ids" or error("expected <ids>")

        self.specifications = [
            specification(n)
            for n in ids.childNodes
            if n.nodeType == n.ELEMENT_NODE and n.tagName == "specification"
        ]

    def validate(self, ifc_file, logger):
        for spec in self.specifications:
            for elem in ifc_file.by_type("IfcObject"):
                spec(elem, logger)


if __name__ == "__main__":
    import sys
    import logging
    import ifcopenshell

    logger = logging.getLogger("IDS")
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    ids_file = ids(sys.argv[1])
    ifc_file = ifcopenshell.open(sys.argv[2])
    ids_file.validate(ifc_file, logger)
