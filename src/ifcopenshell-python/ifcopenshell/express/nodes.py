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


import io
import string
import operator
import collections
import bootstrap

class Node:
    def __init__(self, s, loc, tokens, rule=None):
        self.rule = rule or (type(self).__name__)
        self.tokens = tokens.asDict()
        self.flat = sum([getattr(t, "flat", [t]) for t in tokens.asList()], [])
        if rule is None:
            self.init()

    def __repr__(self):
        return "%s(%s)" % (self.rule, ",".join("%s:%s" % i for i in self.tokens.items()))

    def __getattr__(self, k):
        return self.tokens.get(k)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    def init(self):
        pass

    def any(self):
        return next(iter(self.tokens.values()))


class ListNode:
    def __init__(self, s, loc, tokens, rule=None):
        self.rule = rule or (type(self).__name__)
        self.tokens = tokens.asList()
        self.dict_tokens = collections.defaultdict(list)

        rules_as_list = set()
        for t in self.tokens:
            r = getattr(t, 'rule', None)
            if r:
                rules_as_list.add(r)
                self.dict_tokens[r].append(t)
                
        for r, t in tokens.asDict().items():
            if r not in rules_as_list:
                self.dict_tokens[r].append(t)
                
        self.flat = sum([getattr(t, "flat", [t]) for t in self.tokens], [])

    def __repr__(self):
        return "%s[%s]" % (self.rule, ",".join("%s" % i for i in self.tokens))

    def __iter__(self):
        return iter(self.tokens)
    
    # Somehow indexing messes up the pyparsing results, so instead of x[0] use list(x)[0]
    # def __getitem__(self, i):
    #     return self.tokens[i]

    def init(self):
        pass


class SimpleType(Node):
    def get_type(self):
        t = self.any()
        if type(t) == Node:
            return t.any()
        else:
            t = t[0]
        if type(t) == Node:
            return t.any().any()
        else:
            return t

    type = property(get_type)

    def __repr__(self):
        return str(self.type)


def format_clause(exp):
    def whitespace(t):
        if t in {"=", "|", "<*", "or", "in", "<>", "and"}:
            return " %s " % t
        return t

    return "".join(whitespace(term) for term in exp.flat)


class TypeDeclaration(Node): 
    name = property(lambda self: self.type_id[0])
    utype = property(lambda self: self.underlying_type.any().any())
    type = property(lambda self: self.utype[0] if isinstance(self.utype, list) else self.utype)

    def init(self):

        assert hasattr(self, "TYPE")

        self.where = []
        clause = self.where_clause
        if clause:
            clause = list(clause[0])

            self.where = [(r.simple_id, format_clause(r.expression[0])) for r in clause[1::2]]

    def __repr__(self):
        s = "TYPE %s = %s;\n" % (self.name, self.type)
        if self.where:
            s += " WHERE\n"
            for nm_exp in self.where:
                s += "    %s : %s;\n" % nm_exp
        s += "END_TYPE;"
        return s


class EntityDeclaration(Node):
    name = property(lambda self: self.entity_head[0].entity_id[0])
    supertype = property(lambda self: self.entity_head[0].subsuper[0].supertype_constraint)
    subtype = property(lambda self: self.entity_head[0].subsuper[0].subtype_declaration)
    supertypes = property(lambda self: [self.subtype.super_type] if self.subtype else [])

    def get_abstract(self):
        if self.entity_head[0].subsuper[0].supertype_constraint:
            return self.entity_head[0].subsuper[0].supertype_constraint.abstract
        else:
            return False

    abstract = property(get_abstract)

    def init(self):
        def redeclared_attribute(a):
            try:
                return (
                    a.attribute_decl.redeclared_attribute.qualified_attribute.group_qualifier.simple_id,
                    a.attribute_decl.redeclared_attribute.qualified_attribute.attribute_qualifier.simple_id,
                )
            except:
                return a.attribute_decl.simple_id

        assert self.flat[0] == "entity"

        self.attributes = [a for a in self.entity_body[0] if isinstance(a, ExplicitAttribute)]
        self.inverse = []
        alist = [x for x in self.entity_body[0] if isinstance(x, AttributeList) and x.type == "inverse"]
        if alist:
            self.inverse = alist[0]

        self.derive = []
        alist = [x for x in self.entity_body[0] if isinstance(x, AttributeList) and x.type == "derive"]
        if alist:
            alist = alist[0]
            self.derive = [(redeclared_attribute(a), format_clause(a.expression[0])) for a in alist]

        self.where = []
        clause = [r for r in self.entity_body[0] if r.rule == "where_clause"]
        if clause:
            clause = list(clause[0])

            self.where = [(r.simple_id, format_clause(r.expression[0])) for r in clause[1::2]]

        self.unique = []
        clause = [r for r in self.entity_body[0] if r.rule == "unique_clause"]
        if clause:
            clause = clause[0]
            self.unique = [(r[0], r[2].simple_id) for r in map(list, list(clause)[1::2])]

    def __repr__(self):
        strm = io.StringIO()

        print("ENTITY %s" % self.name, file=strm)

        if self.supertype:
            print("", self.supertype, file=strm)
        if self.subtype:
            print("", self.subtype, file=strm)

        strm.seek(strm.tell() - 1)
        print(";", file=strm)

        for a in self.attributes:
            print("    ", a, ";", file=strm, sep="")

        if self.derive:
            print(" DERIVE", file=strm)
            for nm, exp in self.derive:
                if isinstance(nm, tuple):
                    nm = "SELF\\%s.%s" % nm
                print("    %s : %s;" % (nm, exp), file=strm)

        if self.inverse:
            print(" INVERSE", file=strm)
            print(self.inverse, file=strm)

        if self.where:
            print(" WHERE", file=strm)
            for nm_exp in self.where:
                print("    %s : %s;" % nm_exp, file=strm)

        if self.unique:
            print(" UNIQUE", file=strm)
            for nm_exp in self.unique:
                print("    %s : %s;" % nm_exp, file=strm)

        print("END_ENTITY;", file=strm)
        return strm.getvalue()


class EnumerationType(Node):
    values = property(lambda self: list(self.enumeration_type[2])[1::2])

    def __repr__(self):
        return "ENUMERATION OF (" + ",".join(self.values) + ")"


class NamedType(Node):
    type = property(lambda self: self.simple_id)

    def __repr__(self):
        return self.type


def do_try(fn):
    try:
        return fn()
    except: pass


def get_rule_id(x):
    if not isinstance(x, str):
        x = type(x).__name__
    matches = [k for k, v in bootstrap.actions.items() if v == x]
    if matches:
        return matches[0]

rule_dependencies = {
    k: list(map(operator.attrgetter('contents'), bootstrap.reduce(lambda x, y: x | y, (bootstrap.find_bytype(e, bootstrap.Keyword) for e in [v])))) \
    for k, v in bootstrap.express
}

all_rules = [k for k, e in bootstrap.express]

rule_definitions = {k: v for k, v in bootstrap.express}

def to_tree(x, key=None):
        
    def prune(di):
        # translate class names back to grammar rules if nested actions are encountered
        di = {get_rule_id(k) or k: v for k, v in di.items()}
        
        def replace_synonyms(x):
            for y in x:
                yield y
                if False: # y in di:
                    # production element from grammar is found in parsed data,
                    # return that.

                    # we now always explore other synonym, because more often than not we loose data otherwise
                    yield y
                else:
                    # lookup rule
                    rule = [e for k, e in bootstrap.express if k == y][0]

                    def is_synonym(rl):
                        if isinstance(rl, bootstrap.Term) and isinstance(rl.contents, bootstrap.Keyword):
                            return rl.contents.contents

                    # is this a synonym? then processs that
                    if S := is_synonym(rule):
                        yield S
                        # Do this recursively
                        yield from replace_synonyms([S])
                    
                    # is this a concatenation with zero or more synonyms? then also processs that
                    # @todo catches:
                    #    - simple_expression = term { add_like_op term } .
                    # but should probably also work on
                    #    - a = b { b }
                    # in which case the second Concat would be eliminated
                    elif isinstance(rule, bootstrap.Concat) and \
                            len(rule.contents) == 2 and \
                            is_synonym(rule.contents[0]) and \
                            isinstance(rule.contents[1].contents, bootstrap.Repeated) and \
                            isinstance(rule.contents[1].contents.contents[0], bootstrap.Concat) and \
                            str(rule.contents[1].contents.contents[0].contents[1]) == str(rule.contents[0]):
                        S = is_synonym(rule.contents[0])
                        yield S
                        # Do this recursively
                        yield from replace_synonyms([S])

        subrules = list(replace_synonyms(rule_dependencies[key]))

        if key == "aggregation_types":
            # hack hack hack apparently the parser can't distinguish these
            subrules += list(replace_synonyms(rule_dependencies["general_aggregation_types"]))
        
        if rule_dependencies[key] and not subrules:
            # sometimes an intermediate production rule is missing
            # from the pyparsing output, e.g from parameter to simple_expression
            # directly. Recover from this.
            subrules = sum(map(rule_dependencies.__getitem__, rule_dependencies[key]), [])
        
        if not isinstance(rule_definitions[key], bootstrap.Union):
            # Filter out terminals when not a union. E.g no
            # reason to retain TYPE, END_TYPE, but operators
            # such as IN, LIKE should be retained.
            subrules = list(filter(str.islower, subrules))

        vs = list(di.values())

        return {k: v for k, v in di.items() if k in subrules or (k == key and len(vs) == 1 and vs[0] not in all_rules)}
        
    def simplify(di):
        if isinstance(di, list):
            if set(map(type, di)) == {str} and set(map(len, di)) == {1}:
                return "".join(di)
            return [simplify(v) for v in di]
        elif isinstance(di, dict) and len(di) == 1 and next(iter(di.values())) == {}:
            return next(iter(di.keys()))
        elif isinstance(di, dict):
            return {k: simplify(v) for k, v in di.items()}
        else:
            return di
        
    if isinstance(x, ListNode):
        d = to_tree(x.dict_tokens, key=get_rule_id(x) or key)

        if key == 'if_stmt':
            # The definition of if statement if (roughy):
            #   'if' expr 'then' stmt+ 'else' stmt+
            # this causes stmt to be joined under the same
            # dict key. The code below creates an artifical
            # `else_stmt` that collects the second group
            # of stmts.

            statements = x.dict_tokens['stmt']
            
            else_index = None
            if_nesting = 0
            for i, tk in enumerate(x.flat): 
                if tk == 'if': if_nesting += 1
                if tk == 'end_if': if_nesting -= 1
                if tk == 'else' and if_nesting == 1:
                    else_index = i

            if else_index:
                indices = []
                for s in statements:
                    for i in range(max(indices, default=0), len(x.flat)):
                        if x.flat[i:i+len(s.flat)] == s.flat:
                            indices.append(i)
                            break

                assert len(indices) == len(statements)
                before_else = [i < else_index for i in indices]

                else_stmt = [st for b, st in zip(before_else, d['stmt']) if not b]
                d['stmt'] = [st for b, st in zip(before_else, d['stmt']) if b]

                if else_stmt:
                    d['else_stmt'] = else_stmt
        
        if key == 'formal_parameter':
            # Not so pretty hack to fix the overwriting of simple_id-like
            # ast nodes. The full solution would probably to register parse
            # actions. And directly reassign.
            pid = d['parameter_id'][0][0]
            d['parameter_id'][0] = x.flat[:x.flat.index(pid)+1:2]

        if key is None:
            return {get_rule_id(x): d}
        return d
    elif isinstance(x, Node):
        d = to_tree(x.tokens, key=get_rule_id(x) or key)
        if key is None:
            return {get_rule_id(x): d}
        return d
    elif isinstance(x, dict):
        # d = {k: to_tree(v, key=k) for k, v in x.items()}
        # not fully understood, but when finding specific node Types and production rules, prioritize the former
        d = {get_rule_id(k) or k: to_tree(v, key=k) for k, v in sorted(x.items(), key=lambda p: get_rule_id(p[0]) is not None)}
        return simplify(prune(d))
    elif isinstance(x, list):
        return [to_tree(v, key=key) for v in x]
    else:
        return x


class AggregationType(Node):
    aggregate_type = property(lambda self: self.flat[0])
    bounds = property(lambda self: (list(self.tokens.values())[0][0].bound_spec or [None])[0])
    unique = property(lambda self: list(self.tokens.values())[0][0].UNIQUE is not None)

    def get_type(self):
        v = list(self.tokens.values())[0][0]
        if v.instantiable_type:
            try:
                return v.instantiable_type.concrete_types.simple_id or v.instantiable_type.concrete_types.simple_types
            except:
                return v.instantiable_type
        elif v.parameter_type.simple_types:
            return v.parameter_type.simple_types
        elif v.parameter_type.named_types:
            return v.parameter_type.named_types
        elif v.parameter_type.generalized_types.general_aggregation_types:
            return v.parameter_type.generalized_types.general_aggregation_types
        elif do_try(lambda: v.parameter_type.generalized_types.generic_type.generic_type[0].GENERIC):
            return do_try(lambda: v.parameter_type.generalized_types.generic_type.generic_type[0].GENERIC)
        else:
            import pdb

            pdb.set_trace()
            raise ValueError()

    type = property(get_type)

    def init(self):
        assert self.bounds is None or isinstance(self.bounds, BoundSpecification)

    def __repr__(self):
        return "%s%s of %s%s" % (self.aggregate_type, self.bounds, "unique " if self.unique else "", self.type)


class SelectType(Node):
    values = property(lambda self: list(self.select_type[1])[1::2])

    def __repr__(self):
        return "SELECT (" + ",".join(map(str, self.values)) + ")"


class SuperTypeExpression(Node):
    abstract = property(lambda self: self.abstract_supertype_declaration is not None)

    def get_sub_types(self):
        if self.abstract:
            constraint = self.abstract_supertype_declaration[0]
        else:
            constraint = self.supertype_rule[0]
        return [
            list(list(s)[0])[0].simple_id for s in list(list(list(constraint.subtype_constraint[0].supertype_expression[0])[0])[0].one_of[0])[2::2]
        ]

    sub_types = property(get_sub_types)

    def __repr__(self):
        return "%sSUPERTYPE OF(ONEOF(%s))" % ("ABSTRACT " if self.abstract else "", ",".join(self.sub_types))


class SubTypeExpression(Node):
    super_type = property(lambda self: self.entity_ref[0])

    def __repr__(self):
        return "SUBTYPE OF(%s)" % self.super_type


class AttributeList(ListNode):
    type = property(lambda self: self.flat[0] if self.flat[0] in {"inverse", "derive"} else "explicit")

    def __repr__(self):
        return "\n".join(["    %s;" % s for s in self.tokens[1:]])

    def __iter__(self):
        return iter(self.tokens[1:])

    def __len__(self):
        return len(self.tokens[1:])


class InverseAttribute(Node):
    name = property(lambda self: self.attribute_decl.simple_id)
    type = property(lambda self: self.flat[2] if self.flat[2] != self.flat[-4] else None)
    bounds = property(lambda self: self.bound_spec[0] if self.bound_spec else None)
    entity = property(lambda self: self.entity_ref[0])
    attribute = property(lambda self: self.attribute_ref[0])

    def __repr__(self):
        def _():
            yield self.name
            yield ":"
            if self.type:
                yield self.type.upper()
                yield "OF"
            if self.bounds:
                yield self.bounds
            yield self.entity
            yield "FOR"
            yield self.attribute

        return " ".join(map(str, _()))


"""
class DerivedAttribute(Node):
    def init(self):
        return
        name_index = list(self.tokens).index(':') - 1
        self.name = self.tokens[name_index]
    def __repr__(self):
        return str(self.name)
"""


class BinaryType(Node):
    def __repr__(self):
        return "binary"


class BoundSpecification(Node):
    lower = property(lambda self: self.flat[1])
    upper = property(lambda self: self.flat[3])

    def __repr__(self):
        return "[%s:%s]" % (self.lower, self.upper)


class ExplicitAttribute(Node):
    name = property(lambda self: self.attribute_decl.simple_id)
    optional = property(lambda self: self.OPTIONAL is not None)

    def get_type(self):
        v = next(iter(self.parameter_type.tokens.values()))
        if v.general_aggregation_types:
            return v.general_aggregation_types
        else:
            return v

    type = property(get_type)

    def __repr__(self):
        return "%s : %s%s" % (self.name, "optional " if self.optional else "", self.type)


class WidthSpec(Node):
    fixed = property(lambda self: self.FIXED is not None)

    def init(self):
        self.width = int("".join(list(self.width)[0].flat))

    def __repr__(self):
        return "(%d)%s" % (self.width, " fixed" if self.fixed else "")


class StringType(Node):
    width = property(lambda self: self.width_spec[0] if self.width_spec else None)

    def __repr__(self):
        s = "string"
        if self.width:
            s += " " + repr(self.width)
        return s


class ProcedureDeclaration(ListNode):
    @property
    def name(self):
        return self.flat[1]
        
        
class FunctionDeclaration(ProcedureDeclaration):
    pass
    
class RuleDeclaration(ProcedureDeclaration):
    pass
