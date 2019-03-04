import io
import os
import csv
import platform
import tabulate
import operator
import itertools
import subprocess
import ifcopenshell

from collections import defaultdict

import mvdxml_expression

def camel(s):
    """
    Camel case conversion function
    :param s: str
    :return: camel case formatted string
    """

    s = s.title().replace(" ", "")
    if s.endswith("s"): s = s[:-1]
    return s[0].lower() + s[1:]


STANDARD_PREFIXES = {
    'rdf': '<http://www.w3.org/1999/02/22-rdf-syntax-ns#>',
    'owl': '<http://www.w3.org/2002/07/owl#>',
    'xsd': '<http://www.w3.org/2001/XMLSchema#>',
    'list':  '<https://w3id.org/list#>',
    'ifcowl': '',
    'express': '<https://w3id.org/express#>',
}

def derive_prefix(ttlfn):
    with open(ttlfn, "r") as f:
        for ln in f:
            ln.strip()
            if ln.startswith("@prefix ifcowl"):
                uri = ln.split(':', 1)[1].strip()[:-1].strip()
                print("Detected ifcowl prefix", uri)
                STANDARD_PREFIXES['ifcowl'] = uri
                break

def withschema(fn):
    """
    Decorator that takes a function and adds an IFC latebound schema definition
    in the first parameter. The schema identifier is looked up based on the
    global ifcOwl prefix.

    :param fn: input function
    :return: decorated function
    """

    def _(*args, **kwargs):
        schema_name = STANDARD_PREFIXES['ifcowl'].split('/')[-1][:-2]
        if "_" in schema_name:
            schema_name = schema_name.split('_')[0]
        S = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name)
        return fn(S, *args, **kwargs)
    return _

noop = lambda *args: None

class rule_binding(object):
    """
    Object for mapping rules to generated SPARQL variables
    """
    def __init__(self):
        pass


class builder(object):
    """
    A helper class for dealing with SPARQL query statements
    """

    def __init__(self):
        self.prefixes = {"express": "", "ifcowl": ""}
        self.statements = []

    def append(self, *stmt):
        if len(stmt) == 3:
            for i, pos in enumerate(stmt[1:]):
                for po in pos.split("/"):
                    if ":" in pos:
                        a, b = po.split(':')
                        self.prefixes[a] = ''
        self.statements.append(stmt)

    def bind(self, di):
        for k in set(self.prefixes.keys()) & set(di.keys()):
            self.prefixes[k] = di[k]

    def x(self):
        return len(self.statements)

    def __repr__(self):
        def f(s):
            S = " ".join(s)
            if len(s) == 3: S += ' .'
            return S

        def g(s):
            return "PREFIX %s: %s" % s

        return "\n".join(itertools.chain(
            (g(s) for s in self.prefixes.items()),
            (f(s) for s in self.statements)
        ))

class ifcOwl(object):
    """
    Helper class with static function for dealing with ifcOwl attribute names
    """

    @staticmethod
    @withschema
    def supertypes(S, entity):
        """
        Yields ifcOwl subtypes for the supplied entity name

        :param S: schema definition (from decorator)
        :param entity: entity name string
        :return:
        """

        a, b = entity.split('#')
        try:
            en = S.declaration_by_name(b)
            if en.__class__.__name__ == "entity":
                while en.supertype():
                    yield "%s#%s" % (a, en.supertype().name())
                    en = en.supertype()
        except: pass

    @staticmethod
    def get_names(e, c):
        """
        Returns inverse or forward attribute names for latebound entity definition

        :param e: latebound entity definition
        :param c: either 'all_attributes' or 'all_inverse_attributes'
        :return: set of attribute names
        """

        return set(map(lambda a: a.name(), getattr(e, c)()))

    @staticmethod
    @withschema
    def is_boxed(S, entity, attribute, predCount=0):
        """
        Returns whether the entity attribute should be boxed in ifcOwl. Which means
        that there is an additional indirection.

        inst:IfcRelDefinesByType_21937
            ifcowl:globalId_IfcRoot      inst:IfcGloballyUniqueId_117684 ;

        inst:IfcGloballyUniqueId_117684
            rdf:type           ifcowl:IfcGloballyUniqueId ;
            express:hasString  "2P9FPkykn0r8rCpmBxZH0w" .

        :param S: schema definition (from decorator)
        :param entity: entity name string
        :param attribute: attribute name string
        :param predCount: numeric identifier to postfix predicate identifier in case of SELECT types
        :return: either a predicate from the express namespace or a variable postfixed with predCount
        """

        en = S.declaration_by_name(entity)
        attr = [a for a in en.all_attributes() if a.name() == attribute][0]
        ty = attr.type_of_attribute()
        is_boxed = False
        while isinstance(ty, ifcopenshell.ifcopenshell_wrapper.named_type):
            ty = ty.declared_type()

        if isinstance(ty, ifcopenshell.ifcopenshell_wrapper.select_type):

            # Just assume there is going to be some boxed type in here.
            # It could be all instance references, but fact is we don't know at this moment.
            # It's likely that mvdXML will only bind to literals?

            return "?pred%d" % predCount

        else:

            while isinstance(ty, ifcopenshell.ifcopenshell_wrapper.type_declaration):
                is_boxed = True
                ty = ty.declared_type()
            if is_boxed and isinstance(ty, ifcopenshell.ifcopenshell_wrapper.simple_type):
                ty = ty.declared_type()
                return "express:has%s%s" % (ty[0].upper(), ty[1:])

            return False

    @staticmethod
    @withschema
    def name(S, entity, attribute):
        """
        Names the entity attribute according to ifcOwl

        :param S:
        :param entity:
        :param attribute:
        :return:
        """
        en = S.declaration_by_name(entity)

        while True:
            st = en.supertype()

            attribute_names = ifcOwl.get_names(en, "all_attributes") | \
                ifcOwl.get_names(en, "all_inverse_attributes")

            if st:
                attribute_names -= ifcOwl.get_names(st, "all_attributes") | \
                    ifcOwl.get_names(st, "all_inverse_attributes")

            if attribute in attribute_names:
                return "ifcowl:" + attribute[0].lower() + attribute[1:] + "_" + en.name()

            en = st

            if en is None:
                raise AttributeError("%s not found on %s" % (attribute, entity))

    @staticmethod
    @withschema
    def is_select(S, decl_name):
        """
        Returns True when the declaration is a select type

        :param S:
        :param decl_name:
        :return:
        """
        decl = S.declaration_by_name(decl_name)
        return isinstance(decl, ifcopenshell.ifcopenshell_wrapper.select_type)

    @staticmethod
    @withschema
    def is_inverse(S, entity, attribute):
        """
        When entity attribute is an INVERSE attribute, returns the opposite
        forward entity and attribute name. Otherwise returns (False, False)

        :param S:
        :param entity:
        :param attribute:
        :return:
        """

        en = S.declaration_by_name(entity)
        attrs = [a for a in en.all_inverse_attributes() if a.name() == attribute]
        if not attrs: return False, False

        a = attrs[0]
        assert a.type_of_aggregation_string() == "set"
        entity = a.entity_reference().name()
        attr = a.attribute_reference().name()
        return "ifcowl:" + entity, ifcOwl.name(entity, attr)

class convertor(object):

    @staticmethod
    def convert(item, *args, **kwargs):
        return getattr(convertor, item.__class__.__name__)(item, *args, **kwargs)

    @staticmethod
    def concept_or_applicability(concept):
        """
        Convert the Template (SELECT ... WHERE {}) structure and TemplateRule (FILTER)

        :param qtype: 0 or 1, 0 for a general query matching the applicableRootEntity
        :return:
        """

        bld = builder()
        t = concept.template()
        bld.append("# %s" % camel(concept.root.name))
        convertor.template(t, bld, concept.root.entity)
        bld.bind(STANDARD_PREFIXES)

        return bld

    @staticmethod
    def root(rootEntity):
        args = ["URI", "GlobalId"]

        b = builder()
        b.args = args
        b.append("SELECT " + " ".join("?" + a for a in args) + " WHERE {")
        b.append("?URI", "rdf:type", "ifcowl:%s" % rootEntity)
        b.append("?URI", "ifcowl:globalId_IfcRoot/express:hasString", "?GlobalId")
        b.append("}")
        b.bind(STANDARD_PREFIXES)

        return b

    @staticmethod
    def template(template, bld = None, rootEntity = None):
        if bld is None:
            bld = builder()

        if rootEntity is None:
            rootEntity = template.entity

        args = ["URI", "GlobalId"]

        def enumerate(rule, **kwargs):
            if rule.bind:
                args.append(rule.bind)

        template.traverse(enumerate)

        bld.args = args

        bld.append("SELECT " + " ".join("?" + a for a in args) + " WHERE {")

        args = set(args)

        bld.append("?URI", "rdf:type", "ifcowl:%s" % rootEntity)
        bld.append("?URI", "ifcowl:globalId_IfcRoot/express:hasString", "?GlobalId")

        nm = "?URI"
        ROOT = type('_', (), {'attribute': rootEntity})()
        # rule_stack = [ROOT]
        # name_stack = [nm]
        # callback_stack = [noop]
        # G = type('_', (object,), dict(indent = 0, nm = nm, next_nm=None, first=True))

        rule_mapping = defaultdict(rule_binding)
        rule_mapping[ROOT].name = nm

        def build(rule, parents):
            # print "AAA", rule.tag, parent.tag if parent else parent
            # print map(id, rule_stack)
            # print name_stack
            INDENT = " " * (len(parents) * 2)
            return_value = None

            if rule.optional:
                bld.append(INDENT + "OPTIONAL {")
                return_value = lambda: bld.append(INDENT + "}")

            if rule.tag == "EntityRule":
                # G.nm = G.next_nm

                if not ifcOwl.is_select(rule.attribute):
                    # SELECT types should never be qualified as they cannot be infered
                    bld.append(INDENT + rule_mapping[parents[-1]].name, "rdf:type", "ifcowl:" + rule.attribute)

                # propagate binding name
                rule_mapping[rule].name = rule_mapping[parents[-1]].name
            else:

                # if rule_stack[-1] is parent:
                #     # print "sl", id(parent), id(rule)
                #     # same level
                #     pass
                # elif parent in rule_stack:
                #     # print "up", id(parent), id(rule)
                #     while rule_stack[-1] is not parent:
                #        #  rule_stack.pop()
                #         name_stack.pop()
                #         callback_stack.pop()()
                # else:
                #     # print "dn", id(parent), id(rule)
                #     pass

                indirect = False

                if rule.bind:
                    if len(rule.nodes) == 1:
                        indirect = ifcOwl.is_boxed(parents[-1].attribute, rule.attribute, predCount=bld.x())

                if rule.bind and not indirect:
                    next_nm = "?" + rule.bind
                else:
                    next_nm = "?var%d" % bld.x()

                rule_mapping[rule].name = next_nm

                inventy, invattr = ifcOwl.is_inverse(parents[-1].attribute, rule.attribute)
                if invattr:
                    # This seems not to be necessary, because the entity name is also stated in mvdXML
                    # q.append(
                    #     next_nm,
                    #     "rdf:type",
                    #     inventy
                    # )
                    bld.append(
                        INDENT + next_nm,
                        invattr,
                        rule_mapping[parents[-1]].name
                    )
                else:
                    bld.append(
                        INDENT + rule_mapping[parents[-1]].name,
                        ifcOwl.name(parents[-1].attribute, rule.attribute),
                        next_nm
                    )

                if rule.bind and indirect:
                    # For boxed literals, only strings atm
                    bld.append(INDENT + next_nm, indirect, "?" + rule.bind)

            # rule_stack.append(rule)
            # name_stack.append(next_nm)
            # if rule.optional:
            #     callback_stack.append(lambda: q.append(INDENT+"}"))
            # else:
            #     callback_stack.append(noop)

            # print(q.statements[-1])

            return return_value

        template.traverse(build, root=ROOT, with_parents=True)

        # while callback_stack:
        #     callback_stack.pop()()

        if template.params:
            bld.append(convertor.build_filter(template))

        bld.append("}")

        return bld

    @staticmethod
    def build_filter(self):
        def v(p):
            if isinstance(p, mvdxml_expression.node):
                if p.b == "Value":
                    if p.c.lower() in {'true', 'false'}:
                        yield "(%s?%s)" % ("!" if p.c.lower() == "false" else "", p.a)
                    else:
                        yield "(?%s = %s)" % (p.a, p.c)
                elif p.b == "Exists":
                    yield "(!isBLANK(?%s))" % p.a
                else:
                    raise Exception("Unsupported " + p.b)
            elif isinstance(p, str):
                yield {
                    "and": "&&",
                    "or": "||",
                    "not": "&& !"
                }[p.lower()]
            else:
                yield "("
                for q in p:
                    yield from v(q)
                yield ")"

        return "FILTER(%s)" % " ".join(v(self.params))

def infer_subtypes(ttlfn):
    # Disabled currently
    return ttlfn

    if not os.path.exists(ttlfn + ".subclass.nt"):

        print("Infering supertype relationships")

        import hashlib
        import rdflib

        a = rdflib.namespace.RDF.type

        # Hardly possible on Windows
        # graph = rdflib.Graph("Sleepycat")
        # graph.open("store", create=True)
        # graph.parse(ttlfn)

        from sqlalchemy import create_engine
        from rdflib_sqlalchemy.store import SQLAlchemy

        if os.path.exists("db.sqlite"):
            os.unlink("db.sqlite")

        uri = rdflib.Literal("sqlite:///%(here)s/db.sqlite" % {"here": os.getcwd()})
        ident = rdflib.URIRef(hashlib.sha1(ttlfn.encode()).hexdigest())
        engine = create_engine(uri)
        store = SQLAlchemy(
            identifier=ident,
            engine=engine,
        )
        graph = rdflib.Graph(
            store,
            identifier=ident,
        )
        graph.open(uri, create=True)
        graph.parse(ttlfn, format="ttl")

        # print out all the triples in the graph
        def _():
            for subject, predicate, object in graph:
                if predicate == a:
                    for sup in ifcOwl.supertypes(object):
                        yield subject, a, rdflib.URIRef(sup)

        for stmt in list(_()):
            graph.add(stmt)

        graph.serialize(destination=ttlfn + ".subclass.nt", format="nt")

    ttlfn += ".subclass.nt"

if platform.system() == "Windows":
    JENA_SPARQL = os.path.join(os.environ.get("JENA_HOME"), "bat", "sparql.bat")
else:
    JENA_SPARQL = "sparql"

class executor(object):
    @staticmethod
    def run(CR, fn, ttlfn):
        """
        Generates SPARQL queries for the parsed MVD and executes on the building model

        :param CR: A parsed concept root
        :param fn: A filename used as the prefix to store generate SPARQL queries to disk
        :param ttlfn: A filename for the LD representation of an IFC model
        :return:
        """

        def dict_to_list(headers):
            return lambda di: [di[h] for h in headers]

        def execute(query, *args):
            sparqlfn = ".".join(itertools.chain([fn], map(str, args))) + ".sparql"
            with open(sparqlfn, "w") as f:
                print(query, file=f)

            proc = subprocess.Popen(
                [JENA_SPARQL, "--data=" + ttlfn, "--query=" + sparqlfn, "--results=CSV"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()

            csvf = io.StringIO(stdout.decode('utf-8'))

            return list(csv.DictReader(csvf))

        root_query = convertor.root(CR.entity)
        roots = execute(root_query, 0)

        print("\nFile contains %d elements of type %s" % (len(roots), CR.entity))

        passing_all = {}

        # for summary below
        num_columns = 0

        try:
            # Full MVD with multiple concepts
            is_template = False
            concept_enumerator = list(itertools.chain([CR.applicability()], CR.concepts()))
        except:
            is_template = True
            concept_enumerator = [CR]

        for ci, C in enumerate(concept_enumerator):

            num_columns += 1

            if is_template or ci > 1:
                print("\n%s" % C.name)
            else:
                print("\nApplicability")

            query = convertor.convert(C)

            print("\nSPARQL query")
            print("============")
            print(query)

            passing = execute(query, ci, 1)
            passing_guids = set(r['GlobalId'] for r in passing)

            print("\nElements passing")
            print(tabulate.tabulate(list(map(dict_to_list(query.args), passing)), query.args, tablefmt="grid"))

            print("\nElements failing concept")
            hd = ["URI", "GlobalId"]
            print(tabulate.tabulate(
                list(map(dict_to_list(hd), [r for r in roots if r["GlobalId"] not in passing_guids])), hd,
                tablefmt="grid"))

            passing_all[ci] = passing_guids

        print("\nSummary")

        for ci, C in enumerate(concept_enumerator):
            print("(%d) %s" % (ci+(0 if is_template else 0), C.name))

        def get_stats(guid):
            v = lambda i: guid in passing_all[i]
            st = [guid] + ["x" if v(i) else "" for i in range(num_columns)]
            if not is_template:
                st += ["x" if not v(0) or all(v(i) for i in range(1, num_columns)) else " "]
            return st

        hd = ["GlobalId"] + list(map(str, range(num_columns)))
        if not is_template:
            hd += ["Valid"]

        print(tabulate.tabulate(list(map(get_stats, map(operator.itemgetter("GlobalId"), roots))), hd, tablefmt="grid"))