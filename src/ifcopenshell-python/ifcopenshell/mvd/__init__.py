import sys
import mvdxml_expression

from xml.dom.minidom import parse, Element

import sparql

class rule(object):
    """
    A class for representing an mvdXML EntityRule or AttributeRule
    """

    def __init__(self, tag, attribute, nodes, bind=None, optional=False):
        self.tag, self.attribute, self.nodes, self.bind = tag, attribute, nodes, bind
        self.optional = optional

    def to_string(self, indent=0):
        return "%s%s%s[%s](%s%s)%s" % ("\n" if indent else "", " "*indent, self.tag, self.attribute, "".join(n.to_string(indent+2) for n in self.nodes), ("\n" + " "*indent) if len(self.nodes) else "", (" -> %s" % self.bind) if self.bind else "")

    def __repr__(self):
        return self.to_string()
    
class template(object):
    """
    Representation of an mvdXML template
    """

    def __init__(self, concept, root, params=None, rules=None):
        self.concept, self.root, self.params = concept, root, params
        self.rules = rules or []
        self.entity = str(root.attributes['applicableEntity'].value)
        self.name = root.attributes['name'].value
        
    def bind(self, params):
        return template(self.concept, self.root, params, self.rules)
        
    def parse(self):
        for rules in self.root.childNodes:
            if not isinstance(rules, Element): continue
            
            for r in rules.childNodes:
                if not isinstance(r, Element): continue
                self.rules.append(self.parse_rule(r))

                
    def traverse(self, fn, root=None, with_parents=False):
        def _(n, p=root, ps=[root]):
            if with_parents:
                close = fn(rule=n, parents=ps)
            else:
                close = fn(rule=n, parent=p)

            for s in n.nodes:
                _(s, n, ps + [n])

            if close:
                close()

        for r in self.rules:
            _(r)
                
    def parse_rule(self, root):
        def visit(node, prefix=""):
            r = None
            n = node
            nm = None
            p = prefix
            optional=False
            
            if node.tagName == "AttributeRule":
                r = node.attributes["AttributeName"].value
                try:
                    nm = node.attributes["RuleID"].value
                except:
                    # without binding, it's wrapped in a SPARQL OPTIONAL {} clause
                    # Aim is to insert this clause once as high in the stack as possible
                    # All topmost attribute rules are optional anyway as in the binding requirements on existence is specified

                    def child_has_ruleid_or_prefix(node):
                        if type(node).__name__ == "Element":
                            if "RuleID" in node.attributes or "IdPrefix" in node.attributes:
                                return True
                            for n in node.childNodes:
                                if child_has_ruleid_or_prefix(n): return True

                    optional = node.parentNode.tagName == "Rules" or not child_has_ruleid_or_prefix(node)
            elif node.tagName == "EntityRule":
                r = node.attributes["EntityName"].value
            elif node.tagName == "References":
                ref = node.getElementsByTagName("Template")[0].attributes['ref'].value
                n = self.concept.template(ref).root
                try: p = p + node.attributes["IdPrefix"].value
                except: pass
                
            def _(n):
                for subnode in n.childNodes:
                    if not isinstance(subnode, Element): continue
                    for x in visit(subnode, p): yield x

            if r:
                yield rule(node.tagName, r, list(_(n)), (p + nm) if nm else nm, optional=optional)
            else:
                for subnode in n.childNodes:
                    if not isinstance(subnode, Element): continue
                    for x in visit(subnode, p): yield x
            
        return list(visit(root))[0]

class concept_or_applicability(object):
    """
    Representation of either a mvdXML Concept or the Applicability node. Basically a structure
    for the hierarchical TemplateRule
    """

    def __init__(self, root, c):
        self.root = root
        self.concept_node = c
        try:
            self.name = c.attributes["name"].value
        except:
            # probably applicability and not concept
            self.name = "Applicability"

    def template(self, id = None):
        if id is None:
            id = self.concept_node.getElementsByTagName("Template")[0].attributes['ref'].value

        for node in self.root.dom.getElementsByTagName("ConceptTemplate"):
            if node.attributes["uuid"].value == id:
                t = template(self, node)
                t.parse()
                t_with_rules = t.bind(self.rules())
                return t_with_rules


    def rules(self):
        # Get the top most TemplateRule and traverse
        rules = self.concept_node.getElementsByTagName("TemplateRules")[0]

        def visit(rules):
            def _():
                for i, r in enumerate([c for c in rules.childNodes if isinstance(c, Element)]):
                    if i:
                        yield rules.attributes["operator"].value
                    if r.tagName == "TemplateRules":
                        yield visit(r)
                    elif r.tagName == "TemplateRule":
                        yield mvdxml_expression.parse(r.attributes["Parameters"].value)
                    else:
                        raise Exception()

            return list(_())

        return visit(rules)
    
class concept_root(object):
    def __init__(self, dom, root):
        self.dom, self.root = dom, root
        self.name = root.attributes['name'].value
        self.entity = str(root.attributes['applicableRootEntity'].value)

    def applicability(self):
        return concept_or_applicability(self, self.root.getElementsByTagName("Applicability")[0])
        
    def concepts(self):
        for c in self.root.getElementsByTagName("Concept"):
            yield concept_or_applicability(self, c)

    @staticmethod
    def parse(fn):
        dom = parse(fn)
        try:
            root = dom.getElementsByTagName("ConceptRoot")[0]
            CR = concept_root(dom, root)
            return CR
        except:
            root = dom.getElementsByTagName("ConceptTemplate")[0]
            t = template(None, root)
            t.parse()
            return t


if __name__ == "__main__":

    if len(sys.argv) == 3:
        ttlfn, mvdfn = sys.argv[1:]
        sparql.derive_prefix(ttlfn)
        ttlfn = sparql.infer_subtypes(ttlfn)
        MVD = concept_root.parse(mvdfn)
        sparql.executor.run(MVD, mvdfn, ttlfn)

    else:
        mvdfn = sys.argv[1]
        MVD = concept_root.parse(mvdfn)

        def dump(rule, parents):
            print(" " * len(parents), rule.tag, rule.attribute)

        for c in MVD.concepts():
            print(c.name)
            print()

            t = c.template()
            print("RootEntity", t.entity)
            t.traverse(dump, with_parents=True)
            print(" ".join(map(str, t.params)))

            print()
