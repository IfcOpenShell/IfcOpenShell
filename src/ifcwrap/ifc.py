import string
import functools
import ifc_wrapper

if hasattr(functools, 'reduce'): reduce = functools.reduce

class entity_instance:
	def __init__(self, e):
		super().__setattr__('wrapped_data', e)
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
			if float in classes: return ifc_wrapper.doubles(v)
			elif int in classes: return ifc_wrapper.ints(v)
			elif str in classes: return ifc_wrapper.strings(v)
			elif entity_instance in classes: return list(map(lambda e: e.wrapped_data, v))
		return v
	@staticmethod
	def wrap_value(v):
		wrap = lambda e: entity_instance(e)
		if isinstance(v, ifc_wrapper.entity_instance): return wrap(v)
		elif isinstance(v, (tuple, list)) and len(v):
			classes = list(map(type, v))
			if ifc_wrapper.entity_instance in classes: return list(map(wrap, v))
		return v
	def __setattr__(self, key, value):
		self[self.wrapped_data.get_argument_index(key)] = value
	def __getitem__(self, key):
		return entity_instance.wrap_value(self.wrapped_data.get_argument(self.wrapped_data.get_argument_index(name)))
	def __setitem__(self, idx, value):
		self.wrapped_data.set_argument(idx, entity_instance.map_value(value))
	def __len__(self): return len(self.wrapped_data)
	def __repr__(self): return repr(self.wrapped_data)


class file:
	instances = []
	def __init__(self, f):
		self.wrapped_data = f
	def create_entity(self,type,*args,**kwargs):
		e = entity_instance(ifc_wrapper.entity_instance(type))
		attrs = list(enumerate(args)) + \
			[(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]
		for idx, arg in attrs: e[idx] = arg
		self.wrapped_data.add(e.wrapped_data)
		self.instances.append(e)
		return e
	def __getattr__(self,attr):
		if attr[0:6] == 'create': return functools.partial(self.create_entity,attr[6:])
	def __getitem__(self, key):
		if isinstance(key, int):
			return entity_instance(self.wrapped_data.by_id(key))
		elif isinstance(key, str):
			return entity_instance(self.wrapped_data.by_guid(key))
	def by_type(self, type):
		return [entity_instance(e) for e in self.wrapped_data.by_type(type)]
	def write(self, fn):
		self.wrapped_data.write(fn)


class guid:
	chars = string.digits + string.ascii_uppercase + string.ascii_lowercase + '_$'
	@staticmethod
	def compress(g):
		bs = [int(g[i:i+2], 16) for i in range(0, len(g), 2)]
		def b64(v, l=4):
			return ''.join([guid.chars[(v // (64**i))%64] for i in range(l)][::-1])
		return ''.join([b64(bs[0], 2)] + [b64((bs[i] << 16) + (bs[i+1] << 8) + bs[i+2]) for i in range(1,16,3)])
	@staticmethod
	def expand(g):
		def b64(v):
			return reduce(lambda a, b: a * 64 + b, map(lambda c: guid.chars.index(c), v))
		bs = [b64(g[0:2])]
		for i in range(5):
			d = b64(g[2+4*i:6+4*i])
			bs += [(d >> (8*(2-j)))%256 for j in range(3)]
		return ''.join(['%02x'%b for b in bs])
	@staticmethod
	def split(g):
		return '{%s-%s-%s-%s-%s}'%(g[:8], g[8:12], g[12:16], g[16:20], g[20:])


def open(fn):
	return file(ifc_wrapper.open(fn))

def create_shape(inst, settings): return ifc_wrapper.create_shape(inst.wrapped_data, settings)

def clean(): return ifc_wrapper.clean()

DISABLE_OPENING_SUBTRACTIONS = ifc_wrapper.DISABLE_OPENING_SUBTRACTIONS
DISABLE_OBJECT_PLACEMENT = ifc_wrapper.DISABLE_OBJECT_PLACEMENT
SEW_SHELLS = ifc_wrapper.SEW_SHELLS
