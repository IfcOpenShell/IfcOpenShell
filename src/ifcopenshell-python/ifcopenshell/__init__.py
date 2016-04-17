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

import os
import sys
import numbers
import platform
import functools
import itertools

from functools import reduce

from . import guid

python_distribution = os.path.join(platform.system().lower(),
	platform.architecture()[0],
	'python%s.%s' % platform.python_version_tuple()[:2])
sys.path.append(os.path.abspath(os.path.join(
	os.path.dirname(__file__),
	'lib', python_distribution)))

try:
	from . import ifcopenshell_wrapper
except:
	raise ImportError("IfcOpenShell not built for '%s'" % python_distribution)

class entity_instance(object):
	def __init__(self, e):
		super(entity_instance, self).__setattr__('wrapped_data', e)
	def __getattr__(self, name):
		INVALID, FORWARD, INVERSE = range(3)
		attr_cat = self.wrapped_data.get_attribute_category(name)
		if attr_cat == FORWARD:
			return entity_instance.wrap_value(self.wrapped_data.get_argument(self.wrapped_data.get_argument_index(name)))
		elif attr_cat == INVERSE:
			return entity_instance.wrap_value(self.wrapped_data.get_inverse(name))
		else: raise AttributeError("entity instance of type '%s' has no attribute '%s'"%(self.wrapped_data.is_a(), name))
	@staticmethod
	def walk(f, g, value):
		if isinstance(value, (tuple, list)): return tuple(map(functools.partial(entity_instance.walk, f, g), value))
		elif f(value): return g(value)
		else: return value
	@staticmethod
	def wrap_value(v):
		wrap = lambda e: entity_instance(e)
		is_instance = lambda e: isinstance(e, ifcopenshell_wrapper.entity_instance)
		return entity_instance.walk(is_instance, wrap, v)
	@staticmethod
	def unwrap_value(v):
		unwrap = lambda e: e.wrapped_data
		is_instance = lambda e: isinstance(e, entity_instance)
		return entity_instance.walk(is_instance, unwrap, v)
	def attribute_type(self, attr):
		attr_idx = attr if isinstance(attr, numbers.Integral) else self.wrapped_data.get_argument_index(attr)
		return self.wrapped_data.get_argument_type(attr_idx)
	def attribute_name(self, attr_idx):
		return self.wrapped_data.get_argument_name(attr_idx)
	def __setattr__(self, key, value):
		self[self.wrapped_data.get_argument_index(key)] = value
	def __getitem__(self, key):
		return entity_instance.wrap_value(self.wrapped_data.get_argument(key))
	def __setitem__(self, idx, value):
		if value is None:
			self.wrapped_data.setArgumentAsNull(idx)
		else:
			attr_type = self.attribute_type(idx).title().replace(' ', '')
			attr_type = attr_type.replace('Binary', 'String')
			attr_type = attr_type.replace('Enumeration', 'String')
			try:
				if isinstance(value, unicode): value = value.encode("utf-8")
			except: pass
			getattr(self.wrapped_data, "setArgumentAs%s" % attr_type)(idx, entity_instance.unwrap_value(value))
		return value
	def __len__(self): return len(self.wrapped_data)
	def __repr__(self): return repr(self.wrapped_data)
	def is_a(self, *args): return self.wrapped_data.is_a(*args)
	def id(self): return self.wrapped_data.id()
	def __eq__(self, other):
		if type(self) != type(other): return False
		return self.wrapped_data == other.wrapped_data
	def __hash__(self):
		return hash((self.id(), self.wrapped_data.file_pointer()))
	def __dir__(self):
		return sorted(set(itertools.chain(
			dir(type(self)),
			self.wrapped_data.get_attribute_names(),
			self.wrapped_data.get_inverse_attribute_names()
		)))


class file(object):
	def __init__(self, f=None):
		self.wrapped_data = f or ifcopenshell_wrapper.file(True)
	def create_entity(self,type,*args,**kwargs):
		e = entity_instance(ifcopenshell_wrapper.entity_instance(type))
		attrs = list(enumerate(args)) + \
			[(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]
		for idx, arg in attrs: e[idx] = arg
		self.wrapped_data.add(e.wrapped_data)
		e.wrapped_data.this.disown()
		return e
	def __getattr__(self, attr):
		if attr[0:6] == 'create': return functools.partial(self.create_entity,attr[6:])
		else: return getattr(self.wrapped_data, attr)
	def __getitem__(self, key):
		if isinstance(key, numbers.Integral):
			return entity_instance(self.wrapped_data.by_id(key))
		elif isinstance(key, str):
			return entity_instance(self.wrapped_data.by_guid(key))
	def by_id(self, id): return self[id]
	def by_guid(self, guid): return self[guid]
	def add(self, inst):
		inst.wrapped_data.this.disown()
		return entity_instance(self.wrapped_data.add(inst.wrapped_data))
	def by_type(self, type):
		return [entity_instance(e) for e in self.wrapped_data.by_type(type)]
	def traverse(self, inst):
		return [entity_instance(e) for e in self.wrapped_data.traverse(inst.wrapped_data)]
	def remove(self, inst):
		return self.wrapped_data.remove(inst.wrapped_data)
	def __iter__(self):
		return iter(self[id] for id in self.wrapped_data.entity_names())


def open(fn=None):
	return file(ifcopenshell_wrapper.open(os.path.abspath(fn))) if fn else file()


def create_entity(type,*args,**kwargs):
	e = entity_instance(ifcopenshell_wrapper.entity_instance(type))
	attrs = list(enumerate(args)) + \
		[(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]
	for idx, arg in attrs: e[idx] = arg
	return e


version = ifcopenshell_wrapper.version()
schema_identifier = ifcopenshell_wrapper.schema_identifier()
get_supertype = ifcopenshell_wrapper.get_supertype
