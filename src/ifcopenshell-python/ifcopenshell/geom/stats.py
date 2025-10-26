import sys
from typing import Optional, IO
from itertools import accumulate

from . import ifcopenshell_wrapper


class TransformDefaultDict:
    def __init__(self, keyfunc=lambda x: x, default_factory=None):
        """
        Similar to collections.defaultdict, but allows for storing
        non-hashable keys by means of a transform function
        """
        self.keyfunc = keyfunc
        self.default_factory = default_factory
        self._data = {}
        self._original_keys = {}

    def __setitem__(self, key, value):
        k = self.keyfunc(key)
        self._data[k] = value
        self._original_keys[k] = key

    def __getitem__(self, key):
        k = self.keyfunc(key)
        if k in self._data:
            return self._data[k]
        if self.default_factory is not None:
            value = self.default_factory()
            self._data[k] = value
            self._original_keys[k] = key
            return value
        raise KeyError(key)

    def __contains__(self, key):
        return self.keyfunc(key) in self._data

    def __delitem__(self, key):
        k = self.keyfunc(key)
        del self._data[k]
        del self._original_keys[k]

    def __iter__(self):
        return iter(self._original_keys.values())

    def __len__(self):
        return len(self._data)

    def items(self):
        return ((self._original_keys[k], v) for k, v in self._data.items())

    def keys(self):
        return self._original_keys.values()

    def values(self):
        return self._data.values()

    def get(self, key, default=None):
        return self._data.get(self.keyfunc(key), default)

    def setdefault(self, key, default=None):
        k = self.keyfunc(key)
        if k not in self._data:
            self._data[k] = default
            self._original_keys[k] = key
        return self._data[k]

    def update(self, other):
        for k, v in other.items():
            self[k] = v

    def clear(self):
        self._data.clear()
        self._original_keys.clear()

    def __repr__(self):
        items = ", ".join(f"{k!r}: {v!r}" for k, v in self.items())
        return f"{self.__class__.__name__}({{{items}}})"


class ProductCounter:
    def __init__(self, only_with_representation=True):
        self.total = 0
        transform_func = lambda decl: decl.name() if hasattr(decl, "name") else decl
        self.counts = TransformDefaultDict(keyfunc=transform_func, default_factory=int)
        self.counts_excl = TransformDefaultDict(keyfunc=transform_func, default_factory=int)
        self.only_with_representation = only_with_representation

    def count(self, decl, values):
        if decl._is("IfcProduct"):
            if self.only_with_representation and values.get("Representation") is None:
                return
            self.counts_excl[decl] += 1
            while decl.name() != "IfcProduct":
                self.counts[decl] += 1
                decl = decl.supertype()
            self.total += 1

    def print(self, out=sys.stdout):
        if self.counts:
            results = []

            def process(ent, level=-1):
                if ent in self.counts:
                    results.append((level, ent.name(), self.counts[ent]))
                for subtype in ent.subtypes():
                    process(subtype, level=level + 1)

            prod = next(iter(self.counts.keys())).schema().declaration_by_name("ifcproduct")
            process(prod)
            max_width = max(level * 2 + len(name) for level, name, _ in results)
            for level, name, count in results:
                print(" " * (level * 2), f"{name:<{max_width - level * 2}}", ": ", count, file=out, sep="")


class BooleanResultCounter:
    def __init__(self, exclude_union=True):
        self.total = 0
        self.exclude_union = exclude_union

    def count(self, decl, values):
        if decl._is("IfcBooleanResult"):
            if self.exclude_union and values.get("Operator") == "UNION":
                return
            self.total += 1

    def print(self, out=sys.stdout):
        print("IfcBooleanResult:", self.total, file=out)


class StatsCollector:
    streamer: ifcopenshell_wrapper.InstanceStreamer
    page_size: Optional[int]
    file_stream: Optional[IO[str]]

    finalized: bool = False
    needs_data: bool = False

    counters: list

    num_semis: int = 0

    def __init__(self):
        self.streamer = ifcopenshell_wrapper.InstanceStreamer()
        self.needs_data = True
        self.counters = [ProductCounter(), BooleanResultCounter()]

    def feedFromFile(self, f: Optional[IO[str]] = None):
        if f:
            self.file_stream = f
        self.feed(self.file_stream.read(self.page_size))

    def feed(self, data: str):
        self.streamer.pushPage(data)
        self.needs_data = False
        self.num_semis = self.streamer.semicolonCount()

    @staticmethod
    def fromFilePath(fn, page_size: int = 102400):
        collector = StatsCollector()
        collector.page_size = page_size
        collector.feedFromFile(open(str(fn), encoding="ascii"))
        return collector

    def next(self):
        if self.num_semis > 0:
            if inst := self.streamer.readInstancePy(True):
                self.num_semis -= 1
                return inst["type"], dict(list(inst.items())[2:])
            else:
                self.finalized = True
                return None
        elif self.file_stream:
            self.feedFromFile()
            return self.next()
        else:
            self.needs_data = True
            return None

    def process(self):
        if n := self.next():
            decl, values = n
        else:
            return
        if decl.schema().name() == "HEADER_SECTION_SCHEMA":
            return
        for cnt in self.counters:
            cnt.count(decl, values)

    def print(self, out=sys.stdout):
        for cnt in self.counters:
            print(type(cnt).__name__, file=out)
            print("=" * len(type(cnt).__name__), file=out)
            cnt.print(out)

    def includeElementTypesBasedOnBudget(self, priorities: dict, budget):
        def specificity(decl, target):
            if decl._is(target):
                i = 0
                while decl.name() != target:
                    decl = decl.supertype()
                    i += 1
                return i
            return None

        def calc_prio(ty):
            # find most specific priority directive for the given type in ty
            return min(((specificity(ty, k), v) for k, v in priorities.items() if ty._is(k)), default=(0, 0))[1]

        sorted_types = sorted(self.counters[0].counts_excl.keys(), key=calc_prio, reverse=True)
        sorted_types = [s for s in sorted_types if not s._is("IfcFeatureElement")]
        counts = [self.counters[0].counts_excl[v] for v in sorted_types]

        ccounts = list(accumulate(counts))

        if ccounts[0] >= budget:
            # At the very least include one type
            return sorted_types[0:1]

        for i, s in enumerate(ccounts):
            if s >= budget:
                over = s - budget
                under = budget - ccounts[i - 1]
                k = i if over <= under else i - 1
                return sorted_types[0 : k + 1]

        # We're lucky we can render everything in budget
        return sorted_types[:]


if __name__ == "__main__":
    collector = StatsCollector.fromFilePath(sys.argv[1])
    while not collector.finalized:
        collector.process()
    collector.print()
    print(
        *collector.includeElementTypesBasedOnBudget(
            {
                "IfcWall": 3,
                "IfcSlab": 3,
                "IfcWindow": 2,
                "IfcDoor": 2,
                "IfcBuildingElement": 1,
            }
        )
    )
