# Build fix: remove `boost_system` from CMake components

`Boost.System` became header-only in Boost 1.69. Boost 1.90.0 no longer ships a compiled library or CMake config for it, so `find_package(Boost REQUIRED COMPONENTS system ...)` fails.

## Fix

`cmake/CMakeLists.txt`:

```diff
-    set(BOOST_COMPONENTS system program_options regex thread date_time iostreams)
+    set(BOOST_COMPONENTS program_options regex thread date_time iostreams)
```

The headers are still available; no linking is needed.

# Build fix: add `template` keyword for dependent template member calls

Calling a template member function through a dependent expression (e.g. `storage->has_attribute_value<T>(...)` where `storage`'s type depends on a template parameter) requires the `template` keyword to disambiguate from a less-than comparison.

## Error

```
src/ifcparse/IfcParse.cpp:1856:67: error: expected primary-expression before '>' token
 1856 |                     if (storage->has_attribute_value<express::Base>(attr_index)) {
      |                                                                   ^
```

Six identical errors at lines 1856, 1865, 1896, 1905, 1934, 1943.

## Fix

`src/ifcparse/IfcParse.cpp`:

```diff
-storage->has_attribute_value<express::Base>(attr_index)
+storage->template has_attribute_value<express::Base>(attr_index)

-storage->has_attribute_value<Blank>(attr_index)
+storage->template has_attribute_value<Blank>(attr_index)
```

Applied at all six call sites in `in_memory_file_storage::read_from_stream`.

# Linker fix: missing explicit template instantiations for `InstanceStreamer`

`InstanceStreamer` is a class template with methods defined in `IfcParse.cpp`, not the header. Without explicit instantiations, the linker can't find the symbols when the SWIG wrapper loads.

## Error

```
ImportError: undefined symbol: _ZN8IfcParse16InstanceStreamerINS_10FileReaderINS_14FullBufferImplEEEEC1EPS3_PNS_7IfcFileE
  (IfcParse::InstanceStreamer<FileReader<FullBufferImpl>>::InstanceStreamer(FileReader<FullBufferImpl>*, IfcFile*))
```

## Fix

Cannot use `template class InstanceStreamer<...>` because some constructors have `static_assert` guards that reject certain reader types. Instead, instantiate each member function individually per reader type, only including the constructors valid for that type.

`src/ifcparse/IfcParse.cpp` (after the last `InstanceStreamer` method definition):

```cpp
// FullBufferImpl
template IfcParse::InstanceStreamer<FileReader<FullBufferImpl>>::InstanceStreamer(IfcParse::IfcFile*);
template IfcParse::InstanceStreamer<FileReader<FullBufferImpl>>::InstanceStreamer(const std::string&, bool, IfcParse::IfcFile*);
template IfcParse::InstanceStreamer<FileReader<FullBufferImpl>>::InstanceStreamer(void*, int, IfcParse::IfcFile*);
template IfcParse::InstanceStreamer<FileReader<FullBufferImpl>>::InstanceStreamer(FileReader<FullBufferImpl>*, IfcParse::IfcFile*);
// ... plus ensure_header, initialize_header, hasSemicolon, semicolonCount,
//     pushPage, bypassTypes, readInstance

// PushedSequentialImpl — same pattern, different valid constructors

// MMapFileReader (ifdef USE_MMAP) — same pattern
```

# Linker fix: `FullBufferImpl` missing buffer constructor

SWIG's `stream_from_string` calls `InstanceStreamer<FileReader<FullBufferImpl>>(void*, int, IfcFile*)`, but the `(void*, int)` constructor previously hit a `static_assert` for `FullBufferImpl` — it only allowed `PushedSequentialImpl`.

## Error

```
ImportError: undefined symbol: _ZN8IfcParse16InstanceStreamerINS_10FileReaderINS_14FullBufferImplEEEEC1EPviPNS_7IfcFileE
  (InstanceStreamer<FileReader<FullBufferImpl>>::InstanceStreamer(void*, int, IfcFile*))
```

## Fix

Three changes to make `FullBufferImpl` support buffer-based and default construction:

`src/ifcparse/FileReader.h` — add buffer constructor to `FullBufferImpl`:

```diff
 class IFC_PARSE_API FullBufferImpl {
 public:
     explicit FullBufferImpl(const std::string& fn);
+    FullBufferImpl(void* data, size_t length);
```

`src/ifcparse/FileReader.h` — add `FileReader(void*, size_t)` forwarding constructor:

```diff
+    FileReader(void* data, size_t length)
+        : cursor_(0) {
+        if constexpr (std::is_same_v<Impl, FullBufferImpl>) {
+            impl_ = std::make_shared<Impl>(data, length);
+        } else {
+            static_assert(...);
+        }
+    }
```

`src/ifcparse/FileReader.cpp` — implement the constructor:

```cpp
FullBufferImpl::FullBufferImpl(void* data, size_t length)
    : buf_(static_cast<char*>(data), static_cast<char*>(data) + length)
    , size_(length) {
}
```

`src/ifcparse/IfcParse.cpp` — extend the two `InstanceStreamer` constructors to accept `FullBufferImpl`:

```diff
 // InstanceStreamer(IfcFile*):
+    } else if constexpr (std::is_same_v<Reader, FileReader<FullBufferImpl>>) {
+        owned_stream_ = std::make_unique<Reader>(nullptr, (size_t)0);

 // InstanceStreamer(void*, int, IfcFile*):
+    } else if constexpr (std::is_same_v<Reader, FileReader<FullBufferImpl>>) {
+        owned_stream_ = std::make_unique<Reader>(data, (size_t)length);
```

# Runtime fix: segfault in `parse_context::push()` due to vector reallocation

`parse_context_pool` stores nodes in a `std::vector<parse_context>`. During parsing, `load()` takes a `parse_context&` parameter and calls `context.push()`, which calls `pool_->make()`. If the pool's vector reallocates (via `emplace_back`), all existing references into the vector — including the `context` reference held by the caller — become dangling. Subsequent access through the dangling reference causes a segfault.

Triggered by larger IFC files (e.g. `ISSUE_159_kleine_Wohnung_R22.ifc`, 9.5 MB) that cause enough pool growth to trigger reallocation.

## Error

```
Thread 1 received signal SIGSEGV, Segmentation fault.
0x... in IfcParse::parse_context::push()
  #1  in_memory_file_storage::load(...)   // context& is dangling after reallocation
  #2  in_memory_file_storage::load(...)   // parent call
  #3  InstanceStreamer::readInstance()
```

## Fix

`src/ifcparse/storage.h` — change the pool container from `std::vector` to `std::deque`, which does not invalidate references on `push_back`/`emplace_back`:

```diff
+#include <deque>

 struct parse_context_pool {
-    std::vector<parse_context> nodes_;
+    std::deque<parse_context> nodes_;
```

# Runtime fix: `express::Base` comparison operators throw on null/expired instances

`express::Base::operator<` and `operator==` called `data()`, which throws `std::runtime_error("Trying to access deleted instance reference")` when the internal `weak_ptr` is expired. A default-constructed `express::Base` (the value-type equivalent of a null pointer) always has an expired `weak_ptr`.

## Why this model triggers it

The bug requires two conditions to coincide:

1. A representation is shared by **more than one product** (via `IfcRepresentationMap` / `IfcMappedItem`).
2. At least one of those products has **no material association**, so `get_single_material_association()` returns `express::Base{}` (the null equivalent).

In `advanced_model.ifc`, Body representations like `#449` (Body/Brep) have a single `IfcRepresentationMap` (`#453`) with 13 `IfcMappedItem` usages, meaning 13 products share the geometry. Some of those products (e.g. `IfcFlowTerminal` instances) have no `IfcRelAssociatesMaterial`, so `get_single_material_association` returns `express::Base{}`.

Smaller or simpler models don't hit this because either:
- Every representation maps to only 1 product → `reuse_ok_` short-circuits at `products.size() == 1` before reaching the material check.
- Every product has a material association → no null `express::Base` is ever inserted into the set.

## Exact call sequence

```
Iterator::initialize()
  try {
    mapping::get_representations(reps, filters_)
      addRepresentationsFromDefaultContexts(representations)
        → collects reps from subcontexts in order:
          Axis (#115): 143 reps
          Body (#117): 7550 reps
          FootPrint (#119): 12 reps

      for (auto representation : representations):

        ── Axis reps (indices 0–142) ──────────────────────────
        products_represented_by(rep, rmap)
          → OfProductRepresentation: 1 product each
        filter_products(products, filters)   → 1 product
        reuse_ok_(ifcproducts)
          → products.size() == 1 → return true  ← SHORT-CIRCUIT, no material check
        representation_mapped_to(rep)        → null (no MappedItem)
        → task created.  143 tasks accumulated.

        ── First Body rep #449 (Body/Brep) ────────────────────
        products_represented_by(#449, rmap)
          → OfProductRepresentation: empty
          → RepresentationMap: 1 map (#453)
          → MapUsage: 13 MappedItems → traces through to 13 IfcProducts
        filter_products(products, filters)   → 13 products
        reuse_ok_(ifcproducts)               ← CRASH HERE
          → products.size() == 1?  NO (13 products)
          → for each product:
              find_openings(product)          → OK
              get_single_material_association(product)
                → some products have no IfcRelAssociatesMaterial
                → returns express::Base{}     (expired weak_ptr)
              associated_single_materials.insert(result)
                → std::set::insert calls operator<
                → operator< calls data()
                → data() calls data_.lock() → expired → THROWS
                  "Trying to access deleted instance reference"

  } catch (const std::exception& e) {
    Logger::Error(e)       ← exception caught here, get_representations aborted
  }

  → reps contains only the 143 Axis tasks created before the throw
  → all 143 Axis reps have Curve2D geometry → map(representation) returns null
  → no valid elements produced → initialize() returns false
```

In the old pointer-based code, `reuse_ok_` used `std::set<const IfcUtil::IfcBaseEntity*>` and `get_single_material_association` returned `nullptr`. Inserting `nullptr` into a `std::set<T*>` is a plain pointer comparison — no dereference, no throw. The refactoring to `std::set<express::Base>` changed the comparison from pointer comparison to `express::Base::operator<`, which unconditionally dereferences through `data()`.

## Error

```
[Error] Trying to access deleted instance reference
[Notice] Created 143 tasks for 143 products    ← only Axis reps; all Body reps lost
initialize() returned: False
```

## Fix

`src/ifcparse/express.h` — use `weak_ptr::lock().get()` instead of `data()` so that expired pointers compare as `nullptr` (matching old raw-pointer semantics):

```diff
     bool operator<(const Base& other) const {
-        return data() < other.data();
+        auto a = data_.lock();
+        auto b = other.data_.lock();
+        return a.get() < b.get();
     }

     bool operator==(const Base& other) const {
-        return data() == other.data();
+        auto a = data_.lock();
+        auto b = other.data_.lock();
+        return a.get() == b.get();
     }
```

# Runtime fix: `entity_instance` missing `get_inverse` due to SWIG `%rename` collision

Accessing inverse attributes (e.g. `element.IsDecomposedBy`) on any entity raises `AttributeError: entity instance of type 'IFC2X3.IfcProject' has no attribute 'get_inverse'`.

## Why

`entity_instance_mixin.__getattr__` (line 106 of `entity_instance.py`) calls `self.get_inverse(name)` when it detects an inverse attribute. Since the mixin inherits into the SWIG-generated `entity_instance` class (via the `object = custom_base` hack in `IfcParseWrapper.i:936`), `self.get_inverse` must resolve to a method on the SWIG class.

However, `IfcParseWrapper.i:70` has a global rename:

```
%rename("get_inverses_by_declaration") get_inverse;
```

This was intended for `ifcopenshell::file::get_inverse` (which takes an entity + declaration and returns instances by reference), but SWIG `%rename` is global — it also renames the `%extend express::Base` method `get_inverse(const std::string& a)` at line 551. So the Python-side `entity_instance` class exposes the method as `get_inverses_by_declaration`, not `get_inverse`.

The old code (`v0.8.0`) didn't hit this because `__getattr__` called `self.wrapped_data.get_inverse(name)` on an inner `ifcopenshell_wrapper.entity_instance` object — but in that old layout, the inner object was constructed differently and the rename didn't apply the same way (or the method had a different path). In the new mixin approach, `self` **is** the SWIG object, so the rename is directly visible.

## Fix

`src/ifcwrap/IfcParseWrapper.i` — override the global rename specifically for `express::Base::get_inverse`, restoring the original name on entity instances:

```diff
+%rename("get_inverse") express::Base::get_inverse;
 %rename("get_inverses_by_declaration") get_inverse;
```

Add this line **before** the global rename (or anywhere before the `%extend express::Base` block). This scoped rename takes precedence for `express::Base`, so:
- `entity_instance.get_inverse(name)` works as the mixin expects
- `file.get_inverses_by_declaration(...)` keeps its intended name

## Python-side workaround

`entity_instance.py:106` — call the method by its SWIG-renamed name:

```diff
-            vs = self.get_inverse(name)
+            vs = self.get_inverses_by_declaration(name)
```

# Runtime fix: `entity_instance` class no longer importable from `entity_instance` module

The class rename from `entity_instance` to `entity_instance_mixin` broke external code that does `from ifcopenshell.entity_instance import entity_instance`.

## Error

```
ImportError: cannot import name 'entity_instance' from 'ifcopenshell.entity_instance'
```

Triggered at import time via `ifcopenshell.util.pset` (and likely other modules).

## Fix

`src/ifcopenshell-python/ifcopenshell/entity_instance.py` — add a backwards-compatible alias at the bottom of the module:

```python
entity_instance = entity_instance_mixin
```
