import pathlib
import sys
import json
import hashlib
import operator
import functools
import itertools
import tempfile

import ifcopenshell.express

import networkx as nx

def to_graph(tree):
    g = nx.DiGraph()

    # Convert 
    def write_to_graph(val, name=None):
        if isinstance(val, list):
            pairs = ((None, v) for v in val)
        elif isinstance(val, dict):
            pairs = val.items()
        else:
            assert name
            g.add_edge(name, name + "_value")
            return g.add_node(name + "_value", label=val)

        for i, (k, v) in enumerate(pairs):
            nid = f"{name or 'root'}_{k or i}"
            g.add_node(nid, label=k)
            if name:
                g.add_edge(name, nid)
            write_to_graph(v, nid)

    write_to_graph(tree)

    to_remove = set()

    # Remove intermediate anonymous nodes. Often the result of ZeroOrMore() productions in
    # bootstrap.py that result in an intermediate list index node in to_tree()
    
    # Start with the intermediate nodes and filter out root (needs to have predecessors)
    intermediate = [n for n in g.nodes if g.nodes[n].get('label') is None and list(g.predecessors(n))]
    
    for n in intermediate:
        pr = list(g.predecessors(n))
        if len(pr) == 1 and g.nodes[pr[0]].get('label'):
            # when eliminating a grouping node with heterogeneous content
            # rather copy the predecessor node label to the grouping node
            # and later delete the predecessor
            sc = list(g.successors(n))
            if len(sc) > 1:
                sc_labels = list(map(lambda x: g.nodes[x].get('label'), sc))
                if len(set(sc_labels)) > 1 and None not in sc_labels:
                    g.nodes[n]['label'] = g.nodes[pr[0]].get('label')
                    to_remove.add(pr[0])
                    continue
                    
        for ab in itertools.product(g.predecessors(n), g.successors(n)):
            g.add_edge(*ab)
        g.remove_node(n)
    
    # The removal process above can decide to not fold the anonymous node, but rather
    # the predecessor of it, in which case it is deleted in this step.    
    for n in to_remove:
        for ab in itertools.product(g.predecessors(n), g.successors(n)):
            g.add_edge(*ab)
        g.remove_node(n)
        
    for n in g.nodes:
        if len(list(g.successors(n))) == 0 and g.nodes[n].get('label') not in ifcopenshell.express.express_parser.all_rules:
            g.nodes[n]['is_terminal'] = True
        
    return g
    
def write_dot(fn, g):
        
    with open(fn, "w") as f:

        def w(*args, **kwargs):
            print(*args, file=f, **kwargs)

        w("digraph", "{")

        def nodename(n):
            return "N"+hashlib.md5(n.encode()).hexdigest()

        def format(di):
            Q = '"'
            inner = ",".join(f"{k}={'' if v.startswith('<') else Q}{v}{'' if v.startswith('<') else Q}" for k, v in di.items())
            if inner:
                inner = f"[{inner}]"
            return inner

        for n in g.nodes:
            lbl = g.nodes[n].get('label')
            if lbl:
                attrs = {"label": lbl}
            else:
                attrs = {"label": n}
                
            if g.nodes[n].get('is_terminal'):
                attrs["shape"] = "rect"
                attrs["label"] = f"\\\"{attrs['label']}\\\""
            else:
                attrs["shape"] = "none"       
                
            w(nodename(n), format(attrs), ";", sep="")
            
        for a,b in g.edges:
            w(nodename(a), "->", nodename(b), ";")

        w("}", flush=True)
        
        
def indent(n, s):
    if isinstance(s, str):
        strs = [s]
    else:
        strs = s
    splitted = itertools.chain.from_iterable(map(functools.partial(str.split, sep="\n"), map(str, strs)))
    return "\n".join(" "*n + l for l in splitted)
        

from pyparsing import *
SLASH = Suppress("/")
identifier = Word(alphanums + "_")
rule = identifier + (ZeroOrMore(SLASH + identifier))

def paths(G, root, length):
    if length == 1:
        yield (G.nodes[root].get('label'),)
        return
        
    sd = dict(nx.bfs_successors(G, root, depth_limit=length-1))
    def r(x, p=None):
        if p and len(p) == length:
            yield tuple(map(lambda n: G.nodes[n].get('label'), p))
        else:
            for y in sd.get(x, []):
                yield from r(y, (p or [x])+[y])
    yield from r(root)


class context:
    def __init__(self, graph, rules):
        self.graph = graph
        self.rules = rules
        
    def __getattr__(self, k):
        def inner():
            for r in self.rules:
                label_id_pairs = map(
                    lambda n: (self.graph.nodes[n].get('label'), n),
                    # itertools.chain.from_iterable(
                    #     dict(nx.bfs_successors(self.graph, r)).values()
                    # )
                    self.graph.successors(r)
                )
                matching = filter(lambda p: p[0] == k, label_id_pairs)
                yield from map(operator.itemgetter(1), matching)
            
        return context(self.graph, list(inner()))

    def __iter__(self):
        for r in self.rules:
            yield context(self.graph, [r])
        
    def __str__(self):
        assert len(self.rules) == 1
        nodes = itertools.chain(self.rules, itertools.chain.from_iterable(
            dict(nx.bfs_successors(self.graph, self.rules[0])).values()
        ))
        terminals_or_values = list(filter(
            lambda n: self.graph.nodes[n].get('is_terminal') or self.graph.nodes[n].get('value'),
            nodes
        ))
        # assert len(terminals) == 1
        attrs = self.graph.nodes[terminals_or_values[0]]
        return attrs.get('value', attrs['label'])


    def branches(self):
        assert len(self.rules) == 1
        return [context(self.graph, [n]) for n in self.graph.successors(self.rules[0])]
        
        
    def branch(self, i):
        return self.branches()[i]

    def __len__(self):
        return len(self.rules)

    def __getitem__(self, k):
        return list(self)[k]
        

class codegen_rule:
    def __init__(self, pattern, fn):
        self.pattern = tuple(rule.parseString(pattern))
        self.fn = fn
        if not hasattr(codegen_rule, 'all_rules'):
            codegen_rule.all_rules = []
        codegen_rule.all_rules.append(self)
        
    def __call__(self, graph, node):
        v = self.fn(context(graph, [node]))
        graph.nodes[node]['value'] = v
        return v

    @staticmethod
    def apply(G):
        v = None
        for n in reversed(list(nx.topological_sort(G))):
            for r in codegen_rule.all_rules:
                if r.pattern in paths(G, n, len(r.pattern)):
                    v = r(G, n)
        return v

def process_rule_decl(context):
    return f"""
class {context.rule_head.rule_id}:
    SCOPE = "file"

    @staticmethod    
    def __call__(file):
        {context.rule_head.entity_ref} = file.by_type("{context.rule_head.entity_ref}")
{indent(8, context.where_clause.domain_rule)}
"""

def process_type_decl(scope, context):
    class_name = context.type_id if scope == 'type' else context.entity_head.entity_id

    attributes = []

    if scope == 'entity':
        # @todo derived attributes
        attributes = [a.attribute_decl.attribute_id for a in context.entity_body.explicit_attr]    

    def inner(domain_rule):
        return f"""
class {class_name}_{domain_rule.rule_label_id}:
    SCOPE = "{scope}"
    TYPE_NAME = "{class_name}"
    RULE_NAME = "{domain_rule.rule_label_id}"

    @staticmethod    
    def __call__(self):
{indent(8, (f"{a} = self.{a}" for a in attributes))}
{indent(8, domain_rule)}
"""

    rule_parent = context if scope == 'type' else context.entity_body

    # @todo should we not try to maintain a 1-1 correspondence?
    return "\n\n".join(map(inner, rule_parent.where_clause.branches()))

def process_domain_rule(context):
    return f"""
assert {context.expression}
"""

def process_expression(context):
    if len(context.simple_expression.term) == 2 and context.rel_op_extended:
        return f"{context.simple_expression.term[0]} {context.rel_op_extended} {context.simple_expression.term[1]}"
    elif context.simple_expression.term.multiplication_like_op:
        return " ".join(map(str, sum(zip(
            [None] + context.simple_expression.term.multiplication_like_op.branches(),
            map(lambda n: '(%s)' % n, context.simple_expression.term.factor.branches())
        ), ())[1:]))
    elif context.simple_expression.add_like_op:
        return " ".join(map(str, sum(zip(
            [None] + context.simple_expression.add_like_op.branches(),
            map(lambda n: '(%s)' % n, context.simple_expression.term.branches())
        ), ())[1:]))

def process_interval(context):
    op0, op1 = context.interval_op.branches()
    return " ".join(map(str, (
        context.interval_low,
        op0,
        context.interval_item,
        op1,
        context.interval_high
    )))


def simple_concat(context):
    # simple_factor:
    # only to join unary op (-) with number literal
    # primary:
    # only to join index with qualifyable operand

    def qualifier_position(s):
        # @todo this is a really ugly hack, can we not depend on stable branch order and why?
        
        # unary operators
        if s in ("-", "+", "not"): return -1

        # qualifiers
        if s and s[0] in ('.', '['): return 1

        # default
        return 0

    branches = sorted(map(str, context.branches()), key=qualifier_position)

    concat = ""
    if len(branches) == 2 and branches[0] == 'not':
        concat = " "

    v = concat.join(branches)
    return v


def process_rel_op(context):
    if str(context) == "<>":
        return "!="
    elif str(context) == "=":
        return "=="

codegen_rule("built_in_function/SIZEOF", lambda context: f"len")
codegen_rule("function_call", lambda context: f"{context.branch(0)}({context.branch(1)})")
codegen_rule("actual_parameter_list", lambda context: ','.join(map(str, context.branches())))
codegen_rule("entity_decl", functools.partial(process_type_decl, 'entity'))
codegen_rule("rule_decl", process_rule_decl)
codegen_rule("type_decl", functools.partial(process_type_decl, 'type'))
codegen_rule("domain_rule", process_domain_rule)
codegen_rule("expression", process_expression)
codegen_rule("aggregate_initializer", lambda context: '[%s]' % ','.join(map(str, context.element.branches())))
codegen_rule("interval", process_interval)
codegen_rule("simple_factor", simple_concat)
codegen_rule("primary", simple_concat)
codegen_rule("index", lambda context: '[%s]' % context)
# @nb group_qualifier is ignored on purpose (?)
codegen_rule("attribute_qualifier", lambda context: '.%s' % context)
codegen_rule("rel_op", process_rel_op)

def reverse_compile(s):
    return s.strip().replace('len(', 'SIZEOF(').replace('assert ', '')

if __name__ == "__main__":
    import sys
    import shutil
    import subprocess

    schema = ifcopenshell.express.express_parser.parse(sys.argv[1]).schema
    output = open(pathlib.Path(tempfile.gettempdir()) / f"{schema.name}.py", "w")

    print("def exists(v): return v is not None", "\n", file=output, sep='\n')

    print("class enum_namespace:\n    def __getattr__(self, k):\n        return k", "\n", file=output, sep='\n')

    for k, v in schema.enumerations.items():
        print(f"{k} = enum_namespace()", "\n", file=output, sep='\n')

    for nm in ["IfcSingleProjectInstance", "IfcBoxAlignment", "IfcCompoundPlaneAngleMeasure", "IfcPositiveLengthMeasure", "IfcActorRole", "IfcAddress", 'IfcPostalAddress', 'IfcTelecomAddress', 'IfcAirTerminalType']: #["IfcExtrudedAreaSolid"] + list(schema.rules.keys()) + list(schema.functions.keys()):

        print(nm)
        print(len(nm) * '=')
        
        tree = ifcopenshell.express.express_parser.to_tree(schema[nm])
                
        json.dump(tree, sys.stdout, indent=2)
        
        G = to_graph(tree)
        rule_code = codegen_rule.apply(G)

        for n in G.nodes.values():
            if v := n.get('value'):
                nl = "\n"
                es = "\\n"
                n['label'] = f'<<table cellborder="0" cellpadding="0"><tr><td><b>{n.get("label")}</b></td></tr><tr><td align="left" balign="left">{v.replace("<", "&lt;").replace(">", "&gt;").replace(nl, "<br/>")}</td></tr></table>>'
        
        fn = f"{nm}.dot"
        write_dot(fn, G)

        subprocess.call([shutil.which("dot") or "dot", fn, "-O", "-Tpng"])

        print(rule_code, "\n", file=output, sep='\n')

    output.close()
