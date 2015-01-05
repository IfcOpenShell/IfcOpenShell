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
import functools

from . import guid
from . import ifcopenshell_wrapper

if hasattr(functools, 'reduce'): reduce = functools.reduce

class entity_instance(object):
	def __init__(self, e):
		super(entity_instance, self).__setattr__('wrapped_data', e)
	def __getattr__(self, name):
		try: return entity_instance.wrap_value(self.wrapped_data.get_argument(self.wrapped_data.get_argument_index(name)))
		except:
			try: return entity_instance.wrap_value(self.wrapped_data.get_inverse(name))
			except: raise AttributeError("entity instance of type '%s' has no attribute '%s'"%(self.wrapped_data.is_a(), name))
	@staticmethod
	def map_value(v):
		if isinstance(v, entity_instance): return v.wrapped_data
		elif isinstance(v, (tuple, list)) and len(v):
			classes = list(map(type, v))
			if float in classes: return ifcopenshell_wrapper.double_vector(v)
			elif int in classes: return ifcopenshell_wrapper.int_vector(v)
			elif str in classes: return ifcopenshell_wrapper.string_vector(v)
			elif entity_instance in classes: return list(map(lambda e: e.wrapped_data, v))
		return v
	@staticmethod
	def wrap_value(v):
		wrap = lambda e: entity_instance(e)
		if isinstance(v, ifcopenshell_wrapper.entity_instance): return wrap(v)
		elif isinstance(v, (tuple, list)) and len(v):
			classes = list(map(type, v))
			if ifcopenshell_wrapper.entity_instance in classes: return list(map(wrap, v))
		return v
	def attribute_type(self, attr):
		attr_idx = attr if isinstance(attr, int) else self.wrapped_data.get_argument_index(attr)
		return self.wrapped_data.get_argument_type(attr_idx)
	def attribute_name(self, attr_idx):
		return self.wrapped_data.get_argument_name(attr_idx)
	def __setattr__(self, key, value):
		self[self.wrapped_data.get_argument_index(key)] = value
	def __getitem__(self, key):
		return entity_instance.wrap_value(self.wrapped_data.get_argument(key))
	def __setitem__(self, idx, value):
		self.wrapped_data.set_argument(idx, entity_instance.map_value(value))
	def __len__(self): return len(self.wrapped_data)
	def __repr__(self): return repr(self.wrapped_data)
	def is_a(self, *args): return self.wrapped_data.is_a(*args)
	def id(self): return self.wrapped_data.id()


class file(object):
	instances = []
	def __init__(self, f=None):
		self.wrapped_data = f or ifcopenshell_wrapper.file(True)
	def create_entity(self,type,*args,**kwargs):
		e = entity_instance(ifcopenshell_wrapper.entity_instance(type))
		attrs = list(enumerate(args)) + \
			[(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]
		for idx, arg in attrs: e[idx] = arg
		self.wrapped_data.add(e.wrapped_data)
		self.instances.append(e)
		return e
	def __getattr__(self, attr):
		if attr[0:6] == 'create': return functools.partial(self.create_entity,attr[6:])
		else: return getattr(self.wrapped_data, attr)
	def __getitem__(self, key):
		if isinstance(key, int):
			return entity_instance(self.wrapped_data.by_id(key))
		elif isinstance(key, str):
			return entity_instance(self.wrapped_data.by_guid(key))
	def by_type(self, type):
		return [entity_instance(e) for e in self.wrapped_data.by_type(type)]
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

