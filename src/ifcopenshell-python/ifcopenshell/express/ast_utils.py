import sys
import json
import hashlib
import itertools

import ifcopenshell.express

def to_graph(tree):

    import networkx as nx
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
            inner = ",".join(f"{k}=\"{v}\"" for k, v in di.items())
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
    "\n".join(" "*n + l for l in s.split("\n"))
        
class codegen_rule:
    def __init__(self, pattern, fn):
        self.pattern = pattern
        self.fn = fn
        
    def __call__(self, graph):
        for x in self.match(self, graph, self.pattern):
            self.fn(x)


def process_rule_decl(context):
    return f"""
class {context.rule_head.rule_id}:
    def __init__(self, file):
        self.file = file
        
    def validate(self):
{indent(8, [f"validate_{r}() for r in context.domain_rule.rule_label_id"])}
        
{indent(4, context.domain_rule)}
"""

def process_domain_rule(context):
    return f"""
def validate_{context.rule_label_id}(self):
    return context.expression
"""

def process_expression(context):
    if len(context.term) == 2 and context.rel_op_extended:
        return "{context.term[0]} {context.rel_op_extended} {context.term[1]}"

codegen_rule("built_in_function/SIZEOF", lambda context: return f"len")
codegen_rule("function_call", lambda context: return f"{context.branch[0]}(context.branch[1])")
codegen_rule("actual_parameter_list", lambda context: return ','.join(context.branch)")
codegen_rule("rule_decl", process_rule_decl)
codegen_rule("domain_rule", process_domain_rule)

if __name__ == "__main__":
    import shutil
    import subprocess
    
    schema = ifcopenshell.express.express_parser.parse("IFC2X3_tc1.exp").schema
    for nm in ["IfcSingleProjectInstance"]: #["IfcExtrudedAreaSolid"] + list(schema.rules.keys()) + list(schema.functions.keys()):

        print(nm)
        print(len(nm) * '=')
        
        tree = ifcopenshell.express.express_parser.to_tree(schema[nm])
                
        json.dump(tree, sys.stdout, indent=2)
        
        fn = f"{nm}.dot"
        write_dot(fn, to_graph(tree))

        print(subprocess.call([shutil.which("dot") or "dot", fn, "-O", "-Tpng"]))