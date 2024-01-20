import time
import operator
import datetime
import itertools
import functools
from functools import reduce

import ifcopenshell

def get_mem():
    try:
        import psutil
    except:
        return None
    process = psutil.Process()
    return process.memory_info().rss // 1024 // 1024


def trace(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"Function {func.__name__} started at {datetime.datetime.fromtimestamp(start_time)}")
        if get_mem():
            print(f"Process using {get_mem()} MB")
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} finished in {end_time - start_time}")
        if get_mem():
            print(f"Process using {get_mem()} MB")
        return result

    return wrapper


def to_tuple(eq):
    try:
        n = len(eq)
    except:
        n = oc_len(eq)
        eq = [eq.get(i) for i in range(n)]
    return tuple(eq)


to_double = lambda n: tuple(v.to_double() for v in to_tuple(n))


def oc_len(tup):
    # @todo implement in C++
    return int(type(tup).__name__.split("_")[-1])


make_default = lambda pairs: dict((k, [v[1] for v in vs]) for k, vs in itertools.groupby(pairs, key=operator.itemgetter(0)))


def dot(a, b):
    a, b = to_tuple(a), to_tuple(b)
    return reduce(operator.add, map(operator.mul, a, b))


def negate(sign):
    def iden(tup):
        return tup

    def neg(tup):
        return tuple(-v for v in to_tuple(tup))

    return neg if sign == -1 else iden


def to_opaque(tup):
    if len(tup) == 3:
        v = ifcopenshell.ifcopenshell_wrapper.OpaqueCoordinate_3()
    if len(tup) == 4:
        v = ifcopenshell.ifcopenshell_wrapper.OpaqueCoordinate_4()
    for i, vv in enumerate(tup):
        v.set(i, vv)
    return v


create_epeck = ifcopenshell.ifcopenshell_wrapper.create_epeck
epeck_cache = {}
double_cache = {}

def reserialize(v, to_double=False):
    """
    Copy an arbitrarily precise rational from CGAL by serializing and
    deserializing to string or double. Can be useful to flatten the
    depth of operands, trim away precision or create non-reference counted
    copies for use in multi-threaded contexts.
    """
    st = v.to_string()
    if to_double:
        val = double_cache.get(st)
        if val is not None:
            return val
        # @todo can we do this on the str?
        stn = (-v).to_string()
        val = double_cache.get(stn)
        if val is not None:
            return -val
        d = create_epeck(v.to_double())
        double_cache[st] = d
        return d
    else:
        # this does seem to shave off a bit of RAM usage, but even better
        # would be to not compute the result altogether, so cache tuples of
        # operation and operands prior to evaluating. But we don't know
        # how expensive the serialization to str is...
        val = epeck_cache.get(st)
        if val:
            return val
        ep = create_epeck(st)
        epeck_cache[st] = ep
        return ep

