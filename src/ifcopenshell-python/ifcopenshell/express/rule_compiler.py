import ast
import os
import re
import sys
import json
import hashlib
import operator
import functools
import itertools

import ifcopenshell.express
import ifcopenshell.express.express_parser

import networkx as nx

from codegen import indent

DEBUG = False


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
            i = f"{i:03d}"
            nid = f"{name or 'root'}/{k or i}"
            g.add_node(nid, label=k)
            if name:
                g.add_edge(name, nid)
            write_to_graph(v, nid)

    write_to_graph(tree)

    to_remove = set()

    # Remove intermediate anonymous nodes. Often the result of ZeroOrMore() productions in
    # bootstrap.py that result in an intermediate list index node in to_tree()

    # Start with the intermediate nodes and filter out root (needs to have predecessors)
    intermediate = [
        n
        for n in g.nodes
        if g.nodes[n].get("label") is None and list(g.predecessors(n))
    ]

    for n in intermediate:
        pr = list(g.predecessors(n))
        if len(pr) == 1 and g.nodes[pr[0]].get("label"):
            # when eliminating a grouping node with heterogeneous content
            # rather copy the predecessor node label to the grouping node
            # and later delete the predecessor
            sc = list(g.successors(n))
            if len(sc) > 1:
                sc_labels = list(map(lambda x: g.nodes[x].get("label"), sc))
                if len(set(sc_labels)) > 1 and None not in sc_labels:
                    g.nodes[n]["label"] = g.nodes[pr[0]].get("label")
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
        if (
            len(list(g.successors(n))) == 0
            and g.nodes[n].get("label")
            not in ifcopenshell.express.express_parser.all_rules
        ):
            g.nodes[n]["is_terminal"] = True

    return g


def write_dot(fn, g):

    with open(fn, "w") as f:

        def w(*args, **kwargs):
            print(*args, file=f, **kwargs)

        w("digraph", "{")

        def nodename(n):
            return "N" + hashlib.md5(n.encode()).hexdigest()

        def format(di):
            Q = '"'
            inner = ",".join(
                f"{k}={'' if v.startswith('<') else Q}{v}{'' if v.startswith('<') else Q}"
                for k, v in di.items()
            )
            if inner:
                inner = f"[{inner}]"
            return inner

        for n in g.nodes:
            lbl = g.nodes[n].get("label")
            if lbl:
                attrs = {"label": lbl}
            else:
                attrs = {"label": n}

            if g.nodes[n].get("is_terminal"):
                attrs["shape"] = "rect"
                attrs["label"] = f"\\\"{attrs['label']}\\\""
            else:
                attrs["shape"] = "none"

            w(nodename(n), format(attrs), ";", sep="")

        for a, b in g.edges:
            w(nodename(a), "->", nodename(b), ";")

        w("}", flush=True)


from pyparsing import *

SLASH = Suppress("/")
identifier = Word(alphanums + "_")
rule = identifier + (ZeroOrMore(SLASH + identifier))


def paths(G, root, length):
    if length == 1:
        yield (G.nodes[root].get("label"),)
        return

    sd = dict(nx.bfs_successors(G, root, depth_limit=length - 1))

    def r(x, p=None):
        if p and len(p) == length:
            yield tuple(map(lambda n: G.nodes[n].get("label"), p))
        else:
            for y in sd.get(x, []):
                yield from r(y, (p or [x]) + [y])

    yield from r(root)


class context:
    def __init__(self, graph, rules):
        self.graph = graph
        self.rules = rules

    def __getattr__(self, k):
        def inner():
            for r in self.rules:
                label_id_pairs = map(
                    lambda n: (self.graph.nodes[n].get("label"), n),
                    # itertools.chain.from_iterable(
                    #     dict(nx.bfs_successors(self.graph, r)).values()
                    # )
                    self.graph.successors(r),
                )
                matching = filter(lambda p: p[0] == k, label_id_pairs)
                yield from map(operator.itemgetter(1), matching)

        return context(self.graph, list(inner()))

    def has_inverse(self, a):
        for r in self.rules:
            if a in map(
                lambda n: self.graph.nodes[n].get("label"), self.graph.predecessors(r)
            ):
                return True
        return False

    def __iter__(self):
        for r in self.rules:
            yield context(self.graph, [r])

    def descendants(self):
        return [
            b.rules[0][len(self.rules[0]) + 1 :]
            for b in self.branches(allow_multiple=True)
        ]

    def __repr__(self):
        try:
            s = "\n\n" + str(self)
        except:
            s = ""
        return f"<rule_context ({' '.join(self.descendants())})>{s}"

    def __str__(self):
        assert len(self.rules) == 1
        nodes = itertools.chain(
            self.rules,
            itertools.chain.from_iterable(
                dict(nx.bfs_successors(self.graph, self.rules[0])).values()
            ),
        )
        terminals_or_values = list(
            filter(
                lambda n: self.graph.nodes[n].get("is_terminal")
                or self.graph.nodes[n].get("value"),
                nodes,
            )
        )
        # assert len(terminals) == 1
        attrs = [self.graph.nodes[tv] for tv in terminals_or_values]
        attrs = [a.get("value", a["label"]) for a in attrs]
        attr_types = list(map(type, attrs))
        if empty in attr_types[0:1]:
            return ""
        attrs = list(filter(lambda s: isinstance(s, str), attrs))
        return attrs[0]

    def __eq__(self, other):
        return self.graph == other.graph and self.rules == other.rules

    def __hash__(self):
        return hash(self.rules)

    def branches(self, allow_multiple=False, exclude=()):
        if not allow_multiple:
            assert len(self.rules) == 1
        combined = sum(
            [
                sorted(
                    (context(self.graph, [n]) for n in self.graph.successors(R)),
                    key=lambda c: c.rules[0] if c.rules else "",
                )
                for R in self.rules
            ],
            [],
        )
        return [c for c in combined if c not in exclude]

    def parent(self):
        assert len(self.rules) == 1
        return context(self.graph, list(self.graph.predecessors(self.rules[0])))

    def branch(self, i):
        return self.branches()[i]

    def __len__(self):
        return len(self.rules)

    def __getitem__(self, k):
        return list(self)[k]

    def key(self):
        parts = list(
            map(
                lambda s: tuple(map(lambda p: "n" if p.isdigit() else p, s.split("/"))),
                self.rules,
            )
        )
        assert len(set(parts)) == 1
        return [x for x in parts[0][::-1] if x != "n"][0]


# @todo
context_class = context


class codegen_rule:
    def __init__(self, pattern, fn):
        self.pattern = tuple(rule.parseString(pattern))
        self.fn = fn
        if not hasattr(codegen_rule, "all_rules"):
            codegen_rule.all_rules = []
        codegen_rule.all_rules.append(self)

    def __call__(self, graph, node):
        # try:
        v = self.fn(context(graph, [node]))
        # except:
        #     v = "ERROR!!"
        graph.nodes[node]["value"] = v
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
{indent(8, context.algorithm_head.local_decl)}
{indent(8, context.stmt.branches()) if context.stmt else ''}
{indent(8, context.where_clause.domain_rule)}
"""


class empty:
    pass


wb = r"\b"


def process_type_decl(scope, context):
    class_name = context.type_id if scope == "type" else context.entity_head.entity_id

    attributes = []

    if scope == "entity":

        def get_attributes(nm):
            ent = schema.entities[nm]
            if ent.supertypes:
                yield from get_attributes(ent.supertypes[0])
            yield from [a.name for a in ent.attributes]
            yield from [a.name for a in ent.inverse]
            # redeclared do not need to be printed, because they're emitted
            # as part of supertype
            yield from [a[0] for a in ent.derive if isinstance(a[0], str)]

        # @todo derived and inverse attributes
        attributes = list(get_attributes(class_name))

    def format_rule(domain_rule):
        return f"""
class {class_name}_{domain_rule.rule_label_id}:
    SCOPE = "{scope}"
    TYPE_NAME = "{class_name}"
    RULE_NAME = "{domain_rule.rule_label_id}"

    @staticmethod    
    def __call__(self):
{indent(8, (f"{a.lower()} = self.{a}" for a in attributes if re.search(f'{wb}{a.lower()}{wb}', str(domain_rule))))}
{indent(8, domain_rule)}
"""

    rule_parent = context if scope == "type" else context.entity_body

    statements = []

    if rule_parent.where_clause:
        # @todo should we not try to maintain a 1-1 correspondence?
        statements.extend(map(format_rule, rule_parent.where_clause.branches()))

    if scope == "entity":

        def format_derived(derived_attr):
            slash = "\\"
            return f"""
def calc_{class_name}_{str(derived_attr.attribute_decl.redeclared_attribute.qualified_attribute.attribute_qualifier)[1:] if derived_attr.attribute_decl.redeclared_attribute else derived_attr.attribute_decl}(self):
{indent(4, (f"{a.lower()} = self.{a}" for a in attributes if re.search(f'{wb}{a.lower()}{wb}', str(derived_attr.expression))))}
{indent(4, f"return {slash}")}
{indent(4, derived_attr.expression)}
"""

        if context.entity_body.derive_clause:
            statements.extend(
                map(format_derived, context.entity_body.derive_clause.branches())
            )

    return "\n\n".join(statements)


def process_domain_rule(context):
    return f"""
assert ({context.expression}) is not False
"""


def wrap_parens(s):
    s = str(s)
    if " " in s:
        s = "(%s)" % s
    return s


def process_expression(context):
    def concat(a, b, **kwargs):
        return " ".join(
            map(
                str,
                sum(
                    zip(
                        [None] + a.branches(**kwargs),
                        map(wrap_parens, b.branches(**kwargs)),
                    ),
                    (),
                )[1:],
            )
        )

    if context.rel_op_extended:
        if context.term:
            # IfcSameValue
            return concat(
                context.rel_op_extended,
                context,
                allow_multiple=True,
                exclude=[context.rel_op_extended],
            )
        else:
            if len(context.simple_expression.branches()) == 2 and str(context.rel_op_extended) == 'in':
                # IfcBlobTexture
                try:
                    is_literal_str_list = set(map(type, ast.literal_eval(str(context.simple_expression.branches()[1])))) == {str}
                except:
                    is_literal_str_list = False
                if is_literal_str_list:
                    a, b = map(str, context.simple_expression.branches())
                    return f"{a}.lower() {str(context.rel_op_extended)} {b}"
            return concat(context.rel_op_extended, context.simple_expression)
    elif context.multiplication_like_op:
        if str(context.multiplication_like_op.branches()[0]) == "||":
            all_args = {}
            most_concrete_type = None
            most_concrete_type_inheritance_chain_length = -1

            for s in context.factor.branches():
                typename, args = str(s).split("(", 1)
                args = args[:-1]

                break_points = [[0]]
                bracket_nesting = 0
                for i, tk in enumerate(args):
                    if tk in "[(":
                        bracket_nesting += 1
                    if tk in ")]":
                        bracket_nesting -= 1
                    if tk == "," and bracket_nesting == 0:
                        break_points[-1].append(i)
                        break_points.append([i + 1])

                break_points[-1].append(len(args))

                # @todo don't depend on registered schema
                S = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema.name)
                entity = S.declaration_by_name(typename)
                entity_attributes = entity.attributes()

                def count_chain_length(ent):
                    length = 0
                    while ent:
                        ent = ent.supertype()
                        length += 1
                    return length

                args = [args[slice(*x)] for x in break_points]

                for i, arg in filter(lambda p: p[1], enumerate(args)):
                    all_args[entity_attributes[i].name()] = arg

                cl = count_chain_length(entity)
                if cl > most_concrete_type_inheritance_chain_length:
                    most_concrete_type = entity.name()
                    most_concrete_type_inheritance_chain_length = cl

            return f"{most_concrete_type}({', '.join(f'{a[0]}={a[1]}' for a in all_args.items())})"
        else:
            return concat(context.multiplication_like_op, context.factor)
    elif context.add_like_op:
        if context.factor or len(context.term) > 1:
            # @todo now sure why this is required (in IfcCrossProduct)
            # @todo not sure what's going on here, why we have both factor and term as direct child productions of simple_expression (in IfcDotProduct)
            return concat(
                context.add_like_op,
                context,
                allow_multiple=True,
                exclude=[context.add_like_op],
            )
        else:
            return concat(context.add_like_op, context.term)


def process_interval(context):
    op0, op1 = context.interval_op.branches()
    return " ".join(
        map(
            str,
            (
                context.interval_low,
                op0,
                context.interval_item,
                op1,
                context.interval_high,
            ),
        )
    )


def simple_concat(context):
    # simple_factor:
    # only to join unary op (-) with number literal
    # primary:
    # only to join index with qualifyable operand

    def qualifier_position(s):
        # @todo this is a really ugly hack, can we not depend on stable branch order and why?

        # unary operators
        if s in ("-", "+", "not"):
            return -1

        # qualifiers
        if s and s[0] in (".", "["):
            return 1

        # default
        return 0

    branches = sorted(map(str, context.branches()), key=qualifier_position)

    # sorting no longer necessary as we sort in branches() now
    # correction: still necessary, apparently.
    # branches = list(map(str, context.branches()))

    if len(branches) == 2 and branches[0] == "not":
        return f"{branches[0]} {wrap_parens(branches[1])}"
    else:
        v = "".join(branches)

    return v


def process_rel_op(context):
    # @todo the distinction between value comparison and instance comparison
    if str(context) == "<>" or str(context) == ":<>:":
        return "!="
    elif str(context) == "=" or str(context) == ":=:":
        return "=="


def process_if_stmt(context):
    s = f"if {context.logical_expression if context.logical_expression.branches() else context.expression}:\n{indent(4, context.stmt.branches())}"
    if context.else_stmt:
        s += f"\nelse:\n{indent(4, context.else_stmt.branches())}"
    return s


def process_repeat_stmt(context):
    ic = context.repeat_control.increment_control
    return f"for {ic.variable_id} in range({ic.bound_1}, {ic.bound_2} + 1):\n{indent(4, context.stmt.branches())}"


def process_function_decl(context):
    arguments = map(
        str.lower,
        map(
            str,
            context.function_head.formal_parameter.parameter_id.branches(
                allow_multiple=True
            ),
        ),
    )
    return f"def {context.function_head.function_id}({', '.join(arguments)}):\n{indent(4, context.algorithm_head.local_decl)}\n{indent(4, context.stmt.branches())}"


def process_query(context):
    return f"[{str(context.variable_id).lower()} for {str(context.variable_id).lower()} in {context.aggregate_source} if {context.logical_expression if context.logical_expression and context.logical_expression.branches() else context.expression}]"


def process_local_variable(context):
    if context.expression:
        expr = str(context.expression)
        if (
            context.parameter_type.generalized_types.general_aggregation_types.general_set_type
        ):
            expr = re.sub("(\[[^\]]*\])", "express_set(\\1)", expr)

        return "%s = %s" % (str(context.variable_id).lower(), expr)
    else:
        return empty()


def process_function_call(context):
    nm = f"{context.built_in_function if context.built_in_function else context.function_ref}"
    args = f"{context.actual_parameter_list if context.actual_parameter_list and context.actual_parameter_list.branches() else ''}"
    if nm == "exists" and "[" in args:
        # exists check if it receives a callable to catch IndexError, because express semantics
        # dictate that out of bounds index returned unknown (IfcTypeObject_WR1)
        wrap = "lambda: "
    else:
        wrap = ""
    return f"{nm}({wrap}{args})"


def make_lowercase(context):
    return str(context).lower()


def make_lowercase_if(fn):
    def inner(context):
        if fn(context):
            return make_lowercase(context)

    return inner


def process_assignment(context):
    lhs = str(context.general_ref)
    if context.qualifier:
        lhs += str(context.qualifier)
    if m := re.match(r"^([^\[]+)\[([^\[]+)\]$", lhs):
        # @todo ugly regex hack
        aggr, index = m.groups()
        return (
            f"temp = list({aggr})\ntemp[{index}] = {context.expression}\n{aggr} = temp"
        )
    else:
        return "%s = %s" % (lhs, context.expression)


def process_case_action(context):
    first = context.parent().branches().index(context)
    pred = "elif" if first else "if"
    if re.match(r"^'[a-z0-9]+'$", str(context.expression)):
        # @todo this is yet again an ugly hack
        lower = ".lower()"
    else:
        lower = ""
    return f"{pred} {context.parent().expression}{lower} == {context.expression}:\n{indent(4, context.stmt.branches())}"


def process_case_statement(context):
    branches = context.branches(
        exclude=[
            getattr(context, v)
            for v in context.descendants()
            if not v.startswith("case_action")
        ]
    )
    if context.stmt and context.stmt.branches():
        branches += [f"else:\n{indent(4, context.stmt)}"]
    return "\n".join(map(str, branches))


def process_aggregate_initializer(context):
    if context.element.repetition:
        return "([%s] * %s)" % (context.element.expression, context.element.repetition)
    else:
        return "[%s]" % ",".join(
            map(str, context.element.branches() if context.element else ())
        )


def process_index(context):
    if context.parent().key() == "index_qualifier":
        return context
    else:
        return "[%s - EXPRESS_ONE_BASED_INDEXING]" % context


# implemented sizeof() function in generated code
# codegen_rule("built_in_function/SIZEOF", lambda context: f"len")
# @todo
codegen_rule("function_call", process_function_call)
codegen_rule(
    "actual_parameter_list",
    lambda context: ",".join(
        map(str, context.expression.branches() if context.expression else [])
    ),
)
codegen_rule("entity_decl", functools.partial(process_type_decl, "entity"))
codegen_rule("rule_decl", process_rule_decl)
codegen_rule("type_decl", functools.partial(process_type_decl, "type"))
codegen_rule("function_decl", process_function_decl)
codegen_rule("domain_rule", process_domain_rule)
codegen_rule("expression", process_expression)
codegen_rule("simple_expression", process_expression)
codegen_rule("logical_expression", process_expression)
codegen_rule("term", process_expression)
codegen_rule("query_expression", process_query)
codegen_rule("aggregate_initializer", process_aggregate_initializer)
codegen_rule("interval", process_interval)
codegen_rule("simple_factor", simple_concat)
codegen_rule("primary", simple_concat)
codegen_rule("qualifier", simple_concat)
codegen_rule("return_stmt", lambda context: "return %s" % context)
codegen_rule(
    "compound_stmt", lambda context: "\n".join(map(str, context.stmt.branches()))
)
codegen_rule("if_stmt", process_if_stmt)
codegen_rule("repeat_stmt", process_repeat_stmt)
# codegen_rule("index", lambda context: '**express_index(%s)' % context)
codegen_rule("index", process_index)
codegen_rule("index_qualifier", process_index)
codegen_rule("group_qualifier", lambda context: empty())
codegen_rule("attribute_qualifier", lambda context: ".%s" % context)
codegen_rule("rel_op", process_rel_op)
codegen_rule(
    "built_in_constant", lambda context: "None" if str(context) == "?" else str(context)
)
codegen_rule("assignment_stmt", process_assignment)
codegen_rule("local_variable", process_local_variable)
codegen_rule("local_decl", lambda context: "\n".join(map(str, context.branches())))
codegen_rule("general_ref/parameter_ref", make_lowercase)
codegen_rule(
    "qualifiable_factor/attribute_ref",
    make_lowercase_if(
        lambda context: str(context)
        not in set(map(str, schema.all_declarations.keys()))
    ),
)
codegen_rule("case_action", process_case_action)
codegen_rule("case_stmt", process_case_statement)
codegen_rule("escape_stmt", lambda context: "break")

codegen_rule("XOR", lambda context: "^")
codegen_rule("MOD", lambda context: "%")
codegen_rule("TRUE", lambda context: "True")
codegen_rule("FALSE", lambda context: "False")


class AttributeGetattrTransformer(ast.NodeTransformer):
    def visit_Attribute(self, node):
        parents = []
        n = node
        while n := getattr(n, "parent", 0):
            parents.append(n)

        custom_funcs = "is_entity", "usedin", "express_len", "express_getitem", "typeof"
        function_defs = [p.name for p in parents if isinstance(p, ast.FunctionDef)]
        if any(fn in function_defs for fn in custom_funcs):
            return node

        # Check if the Attribute node is the target of an assignment statement
        if isinstance(node.ctx, ast.Store):
            return node

        if node.attr == "create_entity":
            return node

        new_value = self.visit(node.value)

        # Replace the Attribute node with a call to the built-in `getattr` function
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id="getattr", ctx=ast.Load()),
                args=[
                    new_value,
                    ast.Str(s=node.attr),
                    ast.Name(id="INDETERMINATE", ctx=ast.Load()),
                ],
                keywords=[],
            ),
            node,
        )

    def visit_Subscript(self, node):
        parents = []
        n = node
        while n := getattr(n, "parent", 0):
            parents.append(n)

        custom_funcs = "is_entity", "usedin", "express_len", "express_getitem", "typeof"
        function_defs = [p.name for p in parents if isinstance(p, ast.FunctionDef)]
        if any(fn in function_defs for fn in custom_funcs):
            return node

        # Check if the Attribute node is the target of an assignment statement
        if isinstance(node.ctx, ast.Store):
            return node

        assert (
            isinstance(node.slice, ast.Name)
            or isinstance(node.slice, ast.Constant)
            or isinstance(node.slice, ast.BinOp)
        )

        new_value = self.visit(node.value)

        # Replace the Attribute node with a call to the built-in `getattr` function
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id="express_getitem", ctx=ast.Load()),
                args=[
                    new_value,
                    node.slice,
                    ast.Name(id="INDETERMINATE", ctx=ast.Load()),
                ],
                keywords=[],
            ),
            node,
        )

    def assign_parent_refs(self, tree):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node


if __name__ == "__main__":
    import io
    import sys
    import shutil
    import subprocess

    schema = ifcopenshell.express.express_parser.parse(sys.argv[1]).schema
    
    try:
        ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema.name)
    except:
        # @nb note the difference here between:
        # 
        #  - ifcopenshell.express.express_parser.parse
        #  - ifcopenshell.express.parse.parse
        # 
        # First generates a pyparsing AST
        # 
        # Second populates a latebound schema
        # that can be registered in C++.
        builder = ifcopenshell.express.parse(sys.argv[1])
        ifcopenshell.register_schema(builder)

    try:
        ofn = sys.argv[2]
    except IndexError as e:
        ofn = os.path.join(os.path.dirname(__file__), "rules", f"{schema.name}.py")
    output = io.StringIO()

    print("import ifcopenshell", file=output, sep="\n")

    print(
        """
def exists(v):
    if callable(v):
        try: return v() is not None
        except IndexError as e: return False
    else: return v is not None
""",
        "\n",
        file=output,
        sep="\n",
    )
    print(
        "def nvl(v, default): return v if v is not None else default",
        "\n",
        file=output,
        sep="\n",
    )

    print(
        """
def is_entity(inst):
    if isinstance(inst, ifcopenshell.entity_instance):
        schema_name = inst.is_a(True).split('.')[0].lower()
        decl = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(inst.is_a())
        return isinstance(decl, ifcopenshell.ifcopenshell_wrapper.entity)
    return False

def express_len(v):
    if isinstance(v, ifcopenshell.entity_instance) and not is_entity(v):
        v = v[0]
    elif v is None or v is INDETERMINATE:
        return INDETERMINATE
    return len(v)

old_range = range

def range(*args):
    if INDETERMINATE in args:
        return
    yield from old_range(*args)

sizeof = express_len
hiindex = express_len
blength = express_len
""",
        file=output,
        sep="\n",
    )

    print("loindex = lambda x: 1", file=output, sep="\n")
    print("from math import *", file=output, sep="\n")

    # @todo this will get us in trouble when evaluating the truthness
    print("unknown = 'UNKNOWN'", file=output, sep="\n")

    print(
        """
def usedin(inst, ref_name):
    if inst is None:
        return []
    _, __, attr = ref_name.split('.')
    def filter():
        for ref, attr_idx in inst.wrapped_data.file.get_inverse(inst, allow_duplicate=True, with_attribute_indices=True):
            if ref.wrapped_data.get_attribute_names()[attr_idx].lower() == attr:
                yield ref
    return list(filter())


class express_set(set):
    def __mul__(self, other):
        return express_set(set(other) & self)
    __rmul__ = __mul__
    def __add__(self, other):
        def make_list(v):
            # Comply with 12.6.3 Union operator
            if isinstance(v, (list, tuple, set, express_set)):
                return list(v)
            else:
                return [v]
        return express_set(list(self) + make_list(other))
    __radd__ = __add__
    def __repr__(self):
        return repr(set(self))
    def __getitem__(self, k):
        # @todo this is obviously not stable, but should be good enough?
        return list(self)[k]


def express_getitem(aggr, idx, default):
    if aggr is None: return default
    if isinstance(aggr, ifcopenshell.entity_instance) and not is_entity(aggr):
        aggr = aggr[0]
    try: return aggr[idx]
    except IndexError as e: return None


EXPRESS_ONE_BASED_INDEXING = 1


def typeof(inst):
    if not inst:
        # If V evaluates to indeterminate (?), an empty set is returned.
        return express_set([])
    schema_name = inst.is_a(True).split('.')[0].lower()
    def inner():
        decl = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(inst.is_a())
        while decl:
            yield '.'.join((schema_name, decl.name().lower()))
            if isinstance(decl, ifcopenshell.ifcopenshell_wrapper.entity):
                decl = decl.supertype()
            else:
                decl = decl.declared_type()
                while isinstance(decl, ifcopenshell.ifcopenshell_wrapper.named_type):
                    decl = decl.declared_type()
                if not isinstance(decl, ifcopenshell.ifcopenshell_wrapper.type_declaration):
                    break
    return express_set(inner())

class indeterminate_type:
    def __bool__(self):
        return False
    def bop(self, *other):
        return self
    __lt__= bop
    __le__= bop
    __eq__= bop
    __ne__= bop
    __gt__= bop
    __ge__= bop
    __add__= bop
    __radd__= bop
    __sub__= bop
    __rsub__= bop
    __mul__= bop
    __rmul__= bop
    __truediv__= bop
    __floordiv__= bop
    __rtruediv__= bop
    __rfloordiv__= bop
    __mod__= bop
    __rmod__= bop
    __pow__= bop
    __rpow__= bop
    __neg__= bop
    __pos__= bop
    __getitem__ = bop
    __getattr__ = bop

INDETERMINATE = indeterminate_type()

""",
        file=output,
        sep="\n",
    )

    print(
        "class enum_namespace:\n    def __getattr__(self, k):\n        return k.upper()",
        "\n",
        file=output,
        sep="\n",
    )

    for k, v in schema.enumerations.items():
        print(f"{k} = enum_namespace()", "\n", file=output, sep="\n")

        for vi in v.values:
            print(f"{vi.lower()} = {k}.{vi}", "\n", file=output, sep="\n")

    for k in schema.entities.keys():
        print(
            f"def {k}(*args, **kwargs): return ifcopenshell.create_entity({k!r}, {schema.name!r}, *args, **kwargs)",
            "\n",
            file=output,
            sep="\n",
        )

    for nm in schema.all_declarations.keys():
        print(nm)

        tree = ifcopenshell.express.express_parser.to_tree(schema[nm])

        if DEBUG:
            with open(f"{nm}.json", "w") as f:
                json.dump(tree, f, indent=2)

        G = to_graph(tree)
        rule_code = codegen_rule.apply(G)

        if DEBUG:
            for n in G.nodes.values():
                if v := n.get("value"):
                    if isinstance(v, str):
                        nl = "\n"
                        es = "\\n"
                        n[
                            "label"
                        ] = f'<<table cellborder="0" cellpadding="0"><tr><td><b>{n.get("label")}</b></td></tr><tr><td align="left" balign="left">{v.replace("<", "&lt;").replace(">", "&gt;").replace(nl, "<br/>")}</td></tr></table>>'
                    elif isinstance(v, empty):
                        n[
                            "label"
                        ] = f'<<table cellborder="0" cellpadding="0"><tr><td><b>{n.get("label")}</b></td></tr><tr><td align="left" balign="left">---</td></tr></table>>'

            fn = f"{nm}.dot"
            write_dot(fn, G)
            subprocess.call([shutil.which("dot") or "dot", fn, "-O", "-Tpng"])

        print(rule_code, "\n", file=output, sep="\n")

    tree = ast.parse(output.getvalue())
    trsf = AttributeGetattrTransformer()
    trsf.assign_parent_refs(tree)
    trsf.visit(tree)

    if ofn == "-":
        print(ast.unparse(tree))
    else:
        with open(ofn, "w") as f:
            f.write(ast.unparse(tree))
