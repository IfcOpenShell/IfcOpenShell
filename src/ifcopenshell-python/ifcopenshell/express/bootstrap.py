# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import string
import operator
import itertools

from pyparsing import *

try:
    from functools import reduce
except:
    pass


class Expression:
    def __init__(self, contents):
        self.contents = contents[0]

    def __repr__(self):
        if self.op is None:
            return repr(self.contents)
        c = [isinstance(c, str) and c or str(c) for c in self.contents]
        if "%s" in self.op:
            return self.op % (" ".join(c))
        else:
            return "(%s)" % (" %s " % self.op).join(c)

    def __iter__(self):
        return self.contents.__iter__()


class Union(Expression):
    op = "|"


class Concat(Expression):
    op = "+"


class Optional(Expression):
    op = "Optional(%s)"


class Repeated(Expression):
    op = "ZeroOrMore(%s)"


class Term(Expression):
    op = None


class Keyword:
    def __init__(self, contents):
        self.contents = contents[0]

    def __repr__(self):
        return self.contents


class Terminal:
    def __init__(self, contents):
        self.contents = contents[0]
        s = self.contents
        self.is_keyword = len(s) >= 4 and s[0 :: len(s) - 1] == '""' and all(c in alphanums + "_" for c in s[1:-1])

    def __repr__(self):
        ty = "CaselessKeyword" if self.is_keyword else "CaselessLiteral"
        return "%s(%s)" % (ty, self.contents)


LPAREN = Suppress("(")
RPAREN = Suppress(")")
LBRACK = Suppress("[")
RBRACK = Suppress("]")
LBRACE = Suppress("{")
RBRACE = Suppress("}")
EQUALS = Suppress("=")
VBAR = Suppress("|")
PERIOD = Suppress(".")
HASH = Suppress("#")

identifier = Word(alphanums + "_")
keyword = Word(alphanums + "_").setParseAction(Keyword)
expression = Forward()
optional = Group(LBRACK + expression + RBRACK).setParseAction(Optional)
repeated = Group(LBRACE + expression + RBRACE).setParseAction(Repeated)
terminal = quotedString.setParseAction(Terminal)
term = (keyword | terminal | optional | repeated | (LPAREN + expression + RPAREN)).setParseAction(Term)
concat = Group(term + OneOrMore(term)).setParseAction(Concat)
factor = concat | term
union = Group(factor + OneOrMore(VBAR + factor)).setParseAction(Union)
rule = identifier + EQUALS + expression + PERIOD

expression << (union | factor)

grammar = OneOrMore(Group(rule))
grammar.ignore(HASH + restOfLine)

express = grammar.parseFile(os.path.join(os.path.dirname(__file__), "express.bnf"))


def find_bytype(expr, ty, li=None):
    if li is None:
        li = []
    if isinstance(expr, Term):
        expr = expr.contents
    if isinstance(expr, ty):
        li.append(expr)
        return set(li)
    elif isinstance(expr, Expression):
        for term in expr:
            find_bytype(term, ty, li)
    return set(li)


actions = {
    "type_decl": "TypeDeclaration",
    "entity_decl": "EntityDeclaration",
    "enumeration_type": "EnumerationType",
    "aggregation_types": "AggregationType",
    "general_aggregation_types": "AggregationType",
    "select_type": "SelectType",
    "binary_type": "BinaryType",
    "subtype_declaration": "SubTypeExpression",
    "supertype_constraint": "SuperTypeExpression",
    "derive_clause": "AttributeList",
    "inverse_clause": "AttributeList",
    "inverse_attr": "InverseAttribute",
    "bound_spec": "BoundSpecification",
    "explicit_attr": "ExplicitAttribute",
    "width_spec": "WidthSpec",
    "string_type": "StringType",
    "named_types": "NamedType",
    "simple_types": "SimpleType",
    "function_decl": "FunctionDeclaration",
    "rule_decl": "RuleDeclaration",
}

to_emit = set(id for id, expr in express)
emitted = set()
to_combine = set(["simple_id"])
statements = []

terminals = reduce(lambda x, y: x | y, (find_bytype(e, Terminal) for id, e in express))
keywords = list(filter(operator.attrgetter("is_keyword"), terminals))
negated_keywords = map(lambda s: "~%s" % s, keywords)
no_action = {"letter", "digit", "digits", "real_literal", "integer_literal", "string_literal", "simple_string_literal", "letter", "not_quote", "not_paren_star_quote_special"}

while True:
    emitted_in_loop = set()
    for id, expr in express:
        kws = map(repr, find_bytype(expr, Keyword))
        found = [k in emitted for k in kws]
        if id in to_emit and all(found):
            emitted_in_loop.add(id)
            emitted.add(id)
            stmt = "(%s)" % expr
            if id in to_combine:
                stmt = " + ".join(itertools.chain(negated_keywords, ("originalTextFor(Combine%s)" % stmt,)))
            if id not in no_action and not isinstance(expr.contents, Keyword) and not id in to_combine:
                node_type = "ListNode" if "ZeroOrMore" in stmt else "Node"
                action = actions.get(id, 'lambda s, loc, t: %s(s, loc, t, rule="%s")' % (node_type, id))
                stmt = "%s.setParseAction(%s)" % (stmt, action)
            statements.append('%s = %s("%s")' % (id, stmt, id))
    to_emit -= emitted_in_loop
    if not emitted_in_loop:
        break

for id in to_emit:
    statements.append('%s = Forward()("%s")' % (id, id))

for id in to_emit:
    expr = [e for k, e in express if k == id][0]
    stmt = "(%s)" % expr
    if id in to_combine:
        stmt = "Suppress%s" % stmt
    if id not in no_action and not isinstance(expr.contents, Keyword):
        children = list(map(operator.attrgetter('contents'), reduce(lambda x, y: x | y, (find_bytype(e, Keyword) for e in [expr]))))
        has_duplicates = len(children) > len(set(children))
        node_type = "ListNode" if ("ZeroOrMore" in stmt or has_duplicates) else "Node"
        action = ".setParseAction(%s)" % (
            actions[id] if id in actions else 'lambda s, loc, t: %s(s, loc, t, rule="%s")' % (node_type, id)
        )
        stmt = "(%s)%s" % (stmt, action)
    statements.append("%s << %s" % (id, stmt))

if __name__ == "__main__":
    print("""
# This file is generated by IfcOpenShell ifcexpressparser bootstrap.py

from __future__ import annotations
import os
import sys
import pickle

import schema
import mapping

from pyparsing import *
from nodes import *

def parse(fn: str) -> mapping.Mapping:
    cache_file = fn + ".cache.dat"
    if os.path.exists(cache_file) and os.path.getmtime(cache_file) >= os.path.getmtime(fn):
        with open(cache_file, "rb") as f:
            m = pickle.load(f)
    else:      
        %s

        syntax.ignore("--" + restOfLine)
        syntax.ignore(Regex(r"\((?:\*(?:[^*]*\*+)+?\))"))
        ast = syntax.parseFile(fn)
        s = schema.Schema(ast)
        m = mapping.Mapping(s)

        with open(cache_file, "wb") as f:
            pickle.dump(m, f, protocol=0)
    return m
            
if __name__ == "__main__":
    m = parse(sys.argv[1])
    import importlib
    for output in sys.argv[2:]:
        mdl = importlib.import_module(output)
        mdl.Generator(m).emit()
    sys.stdout.write(m.schema.name)
""" % ("\n        ".join(statements))
    )
