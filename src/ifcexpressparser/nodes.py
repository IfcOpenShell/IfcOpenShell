###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

import string
import collections

class Node:
    def __init__(self, tokens = None):
        self.tokens = tokens or []
        self.init()
    def tokens_of_type(self, cls):
        return [t for t in self.tokens if isinstance(t, cls)]
    def single_token_of_type(self, cls, k = None, v = None):
        ts = [t for t in self.tokens if isinstance(t, cls) and (k is None or getattr(t, k) == v)]
        return ts[0] if len(ts) == 1 else None


class TypeDeclaration(Node):
    name = property(lambda self: self.tokens[1])
    type = property(lambda self: self.tokens[3])
    def init(self):
        assert self.tokens[0] == 'type'
        assert isinstance(self.type, UnderlyingType)
    def __repr__(self):
        return "%s = TypeDeclaration(%s)" % (self.name, self.type)


class EntityDeclaration(Node):
    name = property(lambda self: self.tokens[1])
    attributes = property(lambda self: self.tokens_of_type(ExplicitAttribute))
    def init(self):
        assert self.tokens[0] == 'entity'
        s = self.single_token_of_type(SubtypeExpression)
        self.inverse = self.single_token_of_type(AttributeList, 'type', 'inverse')
        self.derive = self.single_token_of_type(AttributeList, 'type', 'derive')
        self.supertypes = s.types if s else []
    def __repr__(self):
        builder = ""
        builder += "Entity(%s)" % (self.name)
        if len(self.supertypes):
            builder += "\n  Supertypes: %s"%(",".join(self.supertypes))
        if len(self.attributes):
            builder += "\n  Attributes: %s"%("".join(["\n    %s"%a for a in self.attributes]))
        if self.derive:
            builder += "\n  Derive:"
            builder += str(self.derive)
        if self.inverse:
            builder += "\n  Inverse:"
            builder += str(self.inverse)
        builder += "\n"
        return builder


class UnderlyingType(Node):
    type = property(lambda self: self.tokens[0])
    def init(self):
        pass
    def __repr__(self):
        return repr(self.type)


class EnumerationType(Node):
    type = property(lambda self: self.tokens[0])
    values = property(lambda self: self.tokens[3::2])
    def init(self):
        assert self.type == 'enumeration'
    def __repr__(self):
        return ",".join(self.values)


class AggregationType(Node):
    aggregate_type = property(lambda self: self.tokens[0])
    bounds = property(lambda self: None if self.tokens[1] == 'of' else self.tokens[1])
    type = property(lambda self: self.tokens[-1])
    def init(self):
        assert self.bounds is None or isinstance(self.bounds, BoundSpecification)
    def __repr__(self):
        return "%s%s of %s"%(self.aggregate_type, self.bounds, self.type)


class SelectType(Node):
    type = property(lambda self: self.tokens[0])
    values = property(lambda self: self.tokens[2::2])
    def init(self):
        assert self.type == 'select'
    def __repr__(self):
        return ",".join(self.values)


class SubSuperTypeExpression(Node):
    type = property(lambda self: self.tokens[0])
    types = property(lambda self: self.tokens[3::2])
    def init(self):
        assert self.type == self.class_type


class SubtypeExpression(SubSuperTypeExpression):
    class_type = 'subtype'


class AttributeList(Node):
    elements = property(lambda self: self.tokens[1:])
    def __init__(self, ty, toks):
        self.type = ty
        Node.__init__(self, toks)
    def init(self):
        assert self.type == self.tokens[0]
    def __repr__(self):
        return "".join(["\n    %s"%s for s in self.elements])


class InverseAttribute(Node):
    name = property(lambda self: self.tokens[0])
    type = property(lambda self: self.tokens[2])
    bounds = property(lambda self: None if len(self.tokens) != 9 else self.tokens[3])
    entity = property(lambda self: self.tokens[-4])
    attribute = property(lambda self: self.tokens[-2])
    def init(self):
        assert self.bounds is None or isinstance(self.bounds, BoundSpecification)
    def __repr__(self):
        return "%s = %s.%s (%s%s)"%(self.name, self.entity, self.attribute, self.type, self.bounds or "")


class DerivedAttribute(Node):
    def init(self):
        name_index = list(self.tokens).index(':') - 1
        self.name = self.tokens[name_index]
    def __repr__(self):
        return str(self.name)


class BinaryType(Node):
    def init(self):
        pass
    def __repr__(self):
        return "binary"


class BoundSpecification(Node):
    lower = property(lambda self: self.tokens[1])
    upper = property(lambda self: self.tokens[3])
    def init(self):
        # assert self.lower in string.digits or self.lower == '?'
        # assert self.upper in string.digits or self.upper == '?'
        pass
    def __repr__(self):
        return "[%s:%s]"%(self.lower, self.upper)


class ExplicitAttribute(Node):
    name = property(lambda self: self.tokens[0])
    type = property(lambda self: self.tokens[-2])
    optional = property(lambda self: len(self.tokens) == 5 and self.tokens[-3] == 'optional')
    def init(self):
        # NB: This assumes a single name per attribute
        # definition, which is not necessarily the case.
        if self.tokens[0] == "self":
            i = list(self.tokens).index(":")
            self.tokens = self.tokens[i-1:]
        assert self.tokens[1] == ':'
    def __repr__(self):
        return "%s : %s%s" % (self.name, self.type, " ?" if self.optional else "")

        
class WidthSpec(Node):
    def init(self):
        if self.tokens[-1] == "fixed":
            self.tokens[-1:] = []
        assert (self.tokens[0], self.tokens[-1]) == ("(", ")")
        self.width = int("".join(self.tokens[1:-1]))
        
class StringType(Node):
    def init(self):
        pass
    def __repr__(self):
        return "string"
