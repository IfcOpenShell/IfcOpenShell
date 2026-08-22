/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

%ignore ifcopenshell::file::register_inverse;
%ignore ifcopenshell::file::unregister_inverse;
%ignore ifcopenshell::file::schema;
%ignore ifcopenshell::file::logger;
%ignore ifcopenshell::file::process_deletion_inverse;
%ignore ifcopenshell::file::build_inverses_;
%ignore ifcopenshell::file::get_unit;
%ignore ifcopenshell::file::build_inverses;
%ignore ifcopenshell::file::check_existance_before_adding;
%ignore ifcopenshell::file::calculate_unit_factors;
%ignore ifcopenshell::file::begin;
%ignore ifcopenshell::file::end;
%ignore ifcopenshell::file::types_begin;
%ignore ifcopenshell::file::types_end;
%ignore ifcopenshell::file::internal_guid_map;
%ignore ifcopenshell::file::storage_;
%ignore ifcopenshell::file::byguid_;
%ignore ifcopenshell::file::byid_;
%ignore ifcopenshell::file::byref_excl_;
%ignore ifcopenshell::file::types_to_bypass_loading_;

// Replaces the raw multi-overload ctor with a friendlier keyword-based signature.
%feature("shadow") ifcopenshell::file::file %{
	def __init__(self, schema=None, schema_identifier=None, schema_version=None):
		if schema_identifier is not None:
			identifier = schema_identifier
		else:
			identifier = self._determine_schema_identifier(schema=schema, schema_version=schema_version)
		_ifcopenshell_wrapper.file_swiginit(self, $action(identifier))
%}

%ignore ifcopenshell::instance_streamer<ifcopenshell::file_reader<ifcopenshell::full_buffer_impl>>::read_instance;
%ignore ifcopenshell::instance_streamer<ifcopenshell::file_reader<ifcopenshell::full_buffer_impl>>::steal_instances;

%ignore express::entity;
%ignore express::select;
%ignore express::declared_type;

// operator< takes a reference, so SWIG's auto __lt__ crashes on None.
// entity_instance_mixin already has a safe __lt__; let it inherit through.
%ignore express::base::operator<;

%ignore in_memory_file_storage;
%ignore rocks_db_file_storage;
// Available as get_inverse().
%ignore ifcopenshell::file::instances_by_reference;

%ignore ifcopenshell::parse_context;

%ignore operator<<;

%ignore ifcopenshell::FileDescription::FileDescription;
%ignore ifcopenshell::FileName::FileName;
%ignore ifcopenshell::FileSchema::FileSchema;
%ignore ifcopenshell::file::tokens;

%ignore ifcopenshell::spf_header::file_description;
%ignore ifcopenshell::spf_header::file_name;
%ignore ifcopenshell::spf_header::file_schema;
// The setters take a raw shared_pointer_type (an internal instance_data*
// storage handle), not a Python-facing type. SWIG would emit the alias
// unqualified into the global-scope wrapper (C2065 on MSVC), and these
// aren't a usable Python API anyway — ignore them like the getters above.
%ignore ifcopenshell::spf_header::set_file_description;
%ignore ifcopenshell::spf_header::set_file_name;
%ignore ifcopenshell::spf_header::set_file_schema;

%ignore ifcopenshell::spf_header::logger;
%ignore ifcopenshell::spf_header::owner_file;
%ignore ifcopenshell::spf_header::write;
%ignore ifcopenshell::spf_header::assign;

%ignore ifcopenshell::HeaderEntity::is;

%ignore ifcopenshell::file::type_iterator;

%ignore express::base::is;
%ignore express::base::operator==;
%ignore express::base::operator!=;
%ignore express::base::base(std::nullopt_t);

%rename("by_id") instance_by_id;
%rename("by_guid") instance_by_guid;
%rename("_by_type") instances_by_type;
%rename("_by_type_excl_subtypes") instances_by_type_excl_subtypes;
%rename("get_inverses_by_declaration") get_inverse;
%rename("entity_instance") express::base;
%rename("file") file;
// _add() because mixin defined add which adds transaction logic
%rename("_add") add_entity;
%rename("_remove") remove_entity;
%rename("_traverse") traverse;
%rename("_traverse_breadth_first") traverse_breadth_first;

class attribute_value_derived {};
%{
class attribute_value_derived {};
%}

%extend attribute_value_derived {
	%pythoncode %{
		def __bool__(self): return False
		def __repr__(self): return '*'
	%}
}

%inline %{
static bool feature_use_attribute_value_derived = false;

void set_feature(const std::string& x, PyObject* v) {
	if (PyBool_Check(v) && x == "use_attribute_value_derived") {
		feature_use_attribute_value_derived = v == Py_True;
	} else {
		throw std::runtime_error("Invalid feature specification");
	}
}

PyObject* get_feature(const std::string& x) {
	if (x == "use_attribute_value_derived") {
		return PyBool_FromLong(feature_use_attribute_value_derived);
	} else {
		throw std::runtime_error("Invalid feature specification");
	}
}

%}

%{

#include <fstream>
#include <random>

// Atomic IFC/STEP write (issue #4797): serialize to a temporary file next to
// the destination, then atomically rename it onto the destination. If the
// process is interrupted mid-write, the destination is never truncated or
// left with dangling STEP references; at most a stray temp file remains, which
// the caller can safely ignore. Keeping the temp in the same directory means
// the rename stays on a single filesystem and is therefore atomic. The temp
// path never leaks into the FILE_NAME header, which is derived from the model
// header, not the output path.
template <typename T>
static void helper_fn_atomic_write(T& file_obj, const std::string& fn) {
	std::random_device rd;
	const std::string temp_fn = fn + "." + std::to_string(rd()) + ".tmp";
	{
		// Same open mode as a plain write so the bytes are identical.
		std::ofstream f(ifcopenshell::path::from_utf8(temp_fn).c_str());
		if (!f.good()) {
			// The temp file could not be created (e.g. directory not
			// writable). Nothing was touched; report as a normal write error.
			throw std::runtime_error("Failed to write to path: '" + fn + "', check folder and file permissions.");
		}
		f << file_obj;
		f.flush();
		if (!f.good()) {
			// Serialization failed (e.g. disk full). Clean up the partial temp
			// and abort. The existing destination is left intact.
			f.close();
			ifcopenshell::path::delete_file(temp_fn);
			throw std::runtime_error("Failed to write to path: '" + fn + "', the file may be incomplete.");
		}
		// The ofstream destructor at the end of this scope closes the stream.
		// On Windows the file must be closed before it can be renamed.
	}
	if (!ifcopenshell::path::atomic_rename_file(temp_fn, fn)) {
		ifcopenshell::path::delete_file(temp_fn);
		throw std::runtime_error("Failed to write to path: '" + fn + "', could not replace the existing file.");
	}
}

static const std::string& helper_fn_declaration_get_name(const ifcopenshell::declaration* decl) {
	return decl->name();
}

static ifcopenshell::argument_type helper_fn_attribute_type(const express::base* instp, unsigned i) {
	const auto& inst = *instp;
	const ifcopenshell::parameter_type* pt = 0;
	if (inst.declaration().as_entity()) {
		pt = inst.declaration().as_entity()->attribute_by_index(i)->type_of_attribute();
		if (inst.declaration().as_entity()->derived()[i]) {
			return ifcopenshell::Argument_DERIVED;
		}
	} else if (inst.declaration().as_type_declaration() && i == 0) {
		pt = inst.declaration().as_type_declaration()->declared_type();
	} else if (inst.declaration().as_enumeration_type() && i == 0) {
		// Enumeration is always from string in Python
		return ifcopenshell::Argument_STRING;
	}

	if (pt == 0) {
		return ifcopenshell::Argument_UNKNOWN;
	} else {
		return ifcopenshell::from_parameter_type(pt);
	}
}
%}

%inline %{
#include <memory>
#include <string>
#ifdef IFOPSH_WITH_ROCKSDB
#include <rocksdb/db.h>
#include <rocksdb/slice.h>

class RocksDBPrefixIterator {
public:
    RocksDBPrefixIterator(const ifcopenshell::impl::rocks_db_file_storage* storage,
                          const std::string& prefix)
        : it_(storage->db->NewIterator(storage->ropts)), prefix_(prefix)
    {
        it_->Seek(prefix_);
    }

    bool valid() const {
        if (!it_ || !it_->Valid()) return false;
        const rocksdb::Slice k = it_->key();
        const rocksdb::Slice p(prefix_);
        return k.starts_with(p);
    }

    void next() {
        if (it_) it_->Next();
    }

    PyObject* key() const {
        if (!valid()) { Py_RETURN_NONE; }
        const rocksdb::Slice k = it_->key();
        return PyBytes_FromStringAndSize(k.data(), static_cast<Py_ssize_t>(k.size()));
    }

    PyObject* value() const {
        if (!valid()) { Py_RETURN_NONE; }
        const rocksdb::Slice v = it_->value();
        return PyBytes_FromStringAndSize(v.data(), static_cast<Py_ssize_t>(v.size()));
    }
private:
    std::unique_ptr<rocksdb::Iterator> it_;
    std::string prefix_;
};
#endif
%}

%newobject ifcopenshell::file::key_value_store_iter;
%newobject ifcopenshell::file::create_uninitialized;

%extend ifcopenshell::file {
	// Use to correlate to entity_instance.file_pointer, so that we
	// can trace file ownership of instances on the python side.
	size_t file_pointer() const {
		return reinterpret_cast<size_t>($self);
	}

	%pythoncode %{
		def __eq__(self, other):
			# Attribute access hands out a new wrapper every time, so identity
			# of the wrapper says nothing about the file it refers to.
			if self is other:
				return True
			if not isinstance(other, file):
				return NotImplemented
			return self.file_pointer() == other.file_pointer()

		def __ne__(self, other):
			result = self.__eq__(other)
			return result if result is NotImplemented else not result

		def __hash__(self):
			return self.file_pointer()
	%}

	file(const std::string& schema) {
		return new ifcopenshell::file(ifcopenshell::schema_by_name(schema));
	}

	static ifcopenshell::file* create_uninitialized(ifcopenshell::logger* logger=nullptr) {
		return new ifcopenshell::file(ifcopenshell::uninitialized_tag{}, ifcopenshell::logger_or_root(logger));
	}

	std::vector<express::base> _get_inverse(const express::base& e) {
		if (auto e_ = e.as<express::entity>()) {
			return cast_vector<express::base>($self->get_inverse(e_.id(), 0, -1));
		}
		throw ifcopenshell::exception("Only entities with ids are supported for get_inverse. Provided entity: '" + e.declaration().name() + "'.");
	}

	std::vector<int> _get_inverse_indices(const express::base& e) {
		if (auto e_ = e.as<express::entity>()) {
			return $self->get_inverse_indices_by_id(e_.id());
		}
		throw ifcopenshell::exception("Only entities with ids are supported for get_inverse_indices. Provided entity: '" + e.declaration().name() + "'.");
	}

	int get_total_inverses(const express::base& e) {
		if (auto e_ = e.as<express::entity>()) {
			return $self->get_inverse_indices_by_id(e_.id()).size();
		}
		throw ifcopenshell::exception("Only entities with ids are supported for get_total_inverses. Provided entity: '" + e.declaration().name() + "'.");
	}

	void _write(const std::string& fn) {
		// Atomic write: serialize to a temp file next to the target, then
		// atomically rename it into place, so an interrupted write can never
		// corrupt the destination (issue #4797).
		helper_fn_atomic_write(*$self, fn);
	}

	std::string to_string() {
		std::stringstream s;
		s << (*$self);
		return s.str();
	}

	express::base create(const std::string& entity_name, int id=-1) {
		const ifcopenshell::declaration* decl = $self->schema()->declaration_by_name(entity_name);
		if (!decl || !(decl->as_entity() || decl->as_type_declaration())) {
			throw ifcopenshell::exception("No such entity or type declaration: '" + entity_name + "' in schema '" + $self->schema()->name());
		}
		return $self->create(decl, id);
	}

	std::vector<unsigned> entity_names() const {
		std::vector<unsigned> keys;
		keys.reserve(std::distance($self->begin(), $self->end()));
		for (auto it = $self->begin(); it != $self->end(); ++ it) {
			keys.push_back(it->first);
		}
		return keys;
	}

	std::vector<std::string> types() const {
		const size_t n = std::distance($self->types_begin(), $self->types_end());
		std::vector<std::string> ts;
		ts.reserve(n);
		std::transform($self->types_begin(), $self->types_end(), std::back_inserter(ts), helper_fn_declaration_get_name);
		return ts;
	}

	/*
	std::vector<std::string> types_with_super() const {
		const size_t n = std::distance($self->types_incl_super_begin(), $self->types_incl_super_end());
		std::vector<std::string> ts;
		ts.reserve(n);
		std::transform($self->types_incl_super_begin(), $self->types_incl_super_end(), std::back_inserter(ts), helper_fn_declaration_get_name);
		return ts;
	}
	*/

	std::string schema_identifier() const {
		if ($self->schema() == 0) return "";
		return $self->schema()->name();
	}

	int storage_mode() const {
		return std::visit([](auto& m) -> int {
			if constexpr (std::is_same_v<std::decay_t<decltype(m)>, ifcopenshell::impl::in_memory_file_storage>) {
				return 0;
			} else if constexpr (std::is_same_v<std::decay_t<decltype(m)>, ifcopenshell::impl::rocks_db_file_storage>) {
				return 1;
			}
			return -1;
		}, $self->storage_);
	}

#ifdef IFOPSH_WITH_ROCKSDB
	RocksDBPrefixIterator* key_value_store_iter(const std::string& prefix) const {
        auto* storage = std::visit([](auto& m) -> ifcopenshell::impl::rocks_db_file_storage const * {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, ifcopenshell::impl::rocks_db_file_storage>) {
                return &m;
            }
            return nullptr;
        }, $self->storage_);
		if (!storage) {
			nullptr;
		}
		return new RocksDBPrefixIterator(storage, prefix);
	}
#endif

	PyObject* key_value_store_query(const std::string& key) const {
        auto* storage = std::visit([](auto& m) -> ifcopenshell::impl::rocks_db_file_storage const * {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, ifcopenshell::impl::rocks_db_file_storage>) {
                return &m;
            }
            return nullptr;
        }, $self->storage_);
		if (!storage) {
			Py_RETURN_NONE;
		}
#ifdef IFOPSH_WITH_ROCKSDB
		std::string value;
		if (storage->db->Get(storage->ropts, key, &value) != rocksdb::Status::OK()) {
			Py_RETURN_NONE;
		}
		return PyBytes_FromStringAndSize(value.data(), value.size());
#else
		Py_RETURN_NONE;
#endif
	}

	%pythoncode %{
		@staticmethod
		def from_string(s: str) -> 'file':
			return read(s)

		schema_identifier = property(schema_identifier)
		header = property(header)
		_registry = {}

		def __setattr__(self, k, v):
			object.__setattr__(self, k, v)
			if k == 'this':
				# only now we know the identity of the object and we set our python-side attributes based on a python-side map
				self.post_init(int(v))
	%}
}

%extend express::base {

	// 0 = not found
	// 1 = regular forward attribute
	// 2 = inverse attribute
	// 3 = derived attribute (redeclared in subtype as derived)
	int get_attribute_category(const std::string& name) const {
		if (!$self->declaration().as_entity()) {
			return name == "wrappedValue" ? 1 : 0;
		}

		{
		const std::vector<const ifcopenshell::attribute*> attrs = $self->declaration().as_entity()->all_attributes();
		std::vector<const ifcopenshell::attribute*>::const_iterator it = attrs.begin();
		for (; it != attrs.end(); ++it) {
			if ((*it)->name() == name) {
				if ($self->declaration().as_entity()->derived()[std::distance(attrs.begin(), it)]) {
					return 3;
				} else {
					return 1;
				}
			}
		}
		}

		{
		const std::vector<const ifcopenshell::inverse_attribute*> attrs = $self->declaration().as_entity()->all_inverse_attributes();
		std::vector<const ifcopenshell::inverse_attribute*>::const_iterator it = attrs.begin();
		for (; it != attrs.end(); ++it) {
			if ((*it)->name() == name) {
				return 2;
			}
		}
		}

		return 0;
	}

	/*
	@todo determine if we want to reinstante id() availability only on Entity instances.

	// id() is defined on IfcBaseEntity and not on IfcBaseClass, in order
	// to expose it to the Python wrapper it is simply duplicated here.
	// Same applies to the two methods reimplemented below.
	int id() const {
		return $self->as<express::base>() != nullptr
			? $self->as<express::base>()->id()
			: 0;
	}
	*/

	int __len__() const {
		if ($self->declaration().as_entity()) {
			return $self->declaration().as_entity()->attribute_count();
		} else {
			return 1;
		}
	}

	std::vector<std::string> get_attribute_names() const {
		if (!$self->declaration().as_entity()) {
			return std::vector<std::string>(1, "wrappedValue");
		}

		const std::vector<const ifcopenshell::attribute*> attrs = $self->declaration().as_entity()->all_attributes();

		std::vector<std::string> attr_names;
		attr_names.reserve(attrs.size());

		std::vector<const ifcopenshell::attribute*>::const_iterator it = attrs.begin();
		for (; it != attrs.end(); ++it) {
			attr_names.push_back((*it)->name());
		}

		return attr_names;
	}

	std::vector<std::string> get_inverse_attribute_names() const {
		if (!$self->declaration().as_entity()) {
			return std::vector<std::string>(0);
		}

		const std::vector<const ifcopenshell::inverse_attribute*> attrs = $self->declaration().as_entity()->all_inverse_attributes();

		std::vector<std::string> attr_names;
		attr_names.reserve(attrs.size());

		std::vector<const ifcopenshell::inverse_attribute*>::const_iterator it = attrs.begin();
		for (; it != attrs.end(); ++it) {
			attr_names.push_back((*it)->name());
		}

		return attr_names;
	}

	bool is_a(const std::string& s) {
		return self->declaration().is(s);
	}

	std::string is_a(bool with_schema=false) const {
		auto t = self->declaration().name();
		if (with_schema) {
			t = self->declaration().schema()->name() + "." + t;
		}
		return t;
	}

	attribute_value get_argument(unsigned i) {
		return $self->get_attribute_value(i);
	}

	attribute_value get_argument(const std::string& a) {
		auto i = $self->declaration().as_entity()->attribute_index(a);
		if (i == -1) {
			throw std::runtime_error("Attribute '" + a + "' not found on entity named " + $self->declaration().name());
		}
		return $self->get_attribute_value((unsigned)i);
	}

	size_t __hash__() const {
		return std::hash<uint32_t>{}(self->identity());
	}

	std::string __repr__() const {
	    std::ostringstream oss;
		$self->to_string(oss);
        return oss.str();
	}

	std::string to_string(bool valid_spf = true) const {
		std::ostringstream oss;
		$self->to_string(oss, valid_spf);
        return oss.str();
	}

	// Identifies the file owning this instance, zero when it has no owner.
	size_t file_pointer() const {
		return reinterpret_cast<size_t>($self->file());
	}

	unsigned get_argument_index(const std::string& a) const {
		if ($self->declaration().as_entity()) {
			return $self->declaration().as_entity()->attribute_index(a);
		} else if (a == "wrappedValue") {
			return 0;
		} else {
			throw ifcopenshell::exception(a + " not found on " + $self->declaration().name());
		}
	}

	std::vector<express::base> _get_inverse(const std::string& a) {
		if ($self->declaration().as_entity()) {
			return cast_vector<express::base>($self->as<express::entity>().get_inverse(a));
		} else {
			throw ifcopenshell::exception(a + " not found on " + $self->declaration().name());
		}
	}

	const char* const attribute_type(unsigned int i) const {
		return ifcopenshell::argument_type_to_string(helper_fn_attribute_type($self, i));
	}

	const char* const attribute_type(const std::string& name) const {
		unsigned int index;
		if ($self->declaration().as_entity()) {
			index = $self->declaration().as_entity()->attribute_index(name);
		} else if (name == "wrappedValue") {
			index = 0;
		} else {
			throw ifcopenshell::exception(name + " not found on " + $self->declaration().name());
		}
		return ifcopenshell::argument_type_to_string(helper_fn_attribute_type($self, index));
	}

	const std::string& attribute_name(unsigned int i) const {
		if ($self->declaration().as_entity()) {
			return $self->declaration().as_entity()->attribute_by_index(i)->name();
		} else if (i == 0) {
			static std::string WRAPPED = "wrappedValue";
			return WRAPPED;
		} else {
			throw ifcopenshell::exception(boost::lexical_cast<std::string>(i) + " out of bounds on " + $self->declaration().name());
		}
	}

	void set_attribute_value_py(unsigned int i, PyObject* value) {
		if (value == Py_None) {
			// @nb we don't check anymore if the attribute is optional here, because it should be
			// possible to go back to the state at construction time.
			// bool is_optional = $self->declaration().as_entity()->attribute_by_index(i)->optional();
			self->set_attribute_value(i, blank{});
			return;
		}

		auto to_index_long = [&](PyObject* o) -> long {
			PyObject* idx = PyNumber_Index(o);  // accepts numpy ints, bools, etc.
			if (!idx) {
				PyErr_Clear();
				throw ifcopenshell::exception("Attribute not set");
			}
			long v = PyLong_AsLong(idx);
			Py_DECREF(idx);
			if (PyErr_Occurred()) {
				PyErr_Clear();
				throw ifcopenshell::exception("Attribute not set");
			}
			return v;
		};

		auto to_index_i64 = [&](PyObject* o) -> long long {
			PyObject* idx = PyNumber_Index(o);  // accepts numpy ints, bools, etc.
			if (!idx) {
				PyErr_Clear();
				throw ifcopenshell::exception("Attribute not set");
			}
			long long v = PyLong_AsLongLong(idx);
			Py_DECREF(idx);
			if (PyErr_Occurred()) {
				PyErr_Clear();
				throw ifcopenshell::exception("Attribute not set");
			}
			return v;
		};

		auto to_double = [&](PyObject* o) -> double {
			double v = PyFloat_AsDouble(o); // accepts ints and float-like objects
			if (PyErr_Occurred()) {
				PyErr_Clear();
				throw ifcopenshell::exception("Attribute not set");
			}
			return v;
		};

		auto to_string = [&](PyObject* o) -> std::string {
			if (PyUnicode_Check(o)) {
				Py_ssize_t n = 0;
				const char* s = PyUnicode_AsUTF8AndSize(o, &n);
				if (!s) {
					PyErr_Clear();
					throw ifcopenshell::exception("Attribute not set");
				}
				return std::string(s, static_cast<size_t>(n));
			}
			if (PyBytes_Check(o)) {
				char* s = nullptr;
				Py_ssize_t n = 0;
				if (PyBytes_AsStringAndSize(o, &s, &n) == -1) {
					PyErr_Clear();
					throw ifcopenshell::exception("Attribute not set");
				}
				return std::string(s, static_cast<size_t>(n));
			}
			throw ifcopenshell::exception("Attribute not set");
		};

		auto seq_fast = [&](PyObject* o) -> PyObject* {
			PyObject* fast = PySequence_Fast(o, "expected a sequence");
			if (!fast) {
				PyErr_Clear();
				throw ifcopenshell::exception("Attribute not set");
			}
			return fast; // new ref
		};

		auto to_vec_int = [&](PyObject* o) -> std::vector<int64_t> {
			PyObject* fast = seq_fast(o);
			Py_ssize_t n = PySequence_Fast_GET_SIZE(fast);
			PyObject** items = PySequence_Fast_ITEMS(fast);

			std::vector<int64_t> out;
			out.reserve(static_cast<size_t>(n));
			for (Py_ssize_t k = 0; k < n; ++k) {
				out.push_back(static_cast<int64_t>(to_index_i64(items[k])));
			}

			Py_DECREF(fast);
			return out;
		};

		auto to_vec_double = [&](PyObject* o) -> std::vector<double> {
			PyObject* fast = seq_fast(o);
			Py_ssize_t n = PySequence_Fast_GET_SIZE(fast);
			PyObject** items = PySequence_Fast_ITEMS(fast);

			std::vector<double> out;
			out.reserve(static_cast<size_t>(n));
			for (Py_ssize_t k = 0; k < n; ++k) {
				out.push_back(to_double(items[k]));
			}

			Py_DECREF(fast);
			return out;
		};

		auto to_vec_string = [&](PyObject* o) -> std::vector<std::string> {
			PyObject* fast = seq_fast(o);
			Py_ssize_t n = PySequence_Fast_GET_SIZE(fast);
			PyObject** items = PySequence_Fast_ITEMS(fast);

			std::vector<std::string> out;
			out.reserve(static_cast<size_t>(n));
			for (Py_ssize_t k = 0; k < n; ++k) {
				out.push_back(to_string(items[k]));
			}

			Py_DECREF(fast);
			return out;
		};

		auto to_base = [&](PyObject* o) -> express::base {
			void* vp = nullptr;

			// Try non-const pointer first
			if (swig_type_info* ti = SWIG_TypeQuery("express::base *")) {
				int res = SWIG_ConvertPtr(o, &vp, ti, 0);
				if (res >= 0 && vp) {
					return *static_cast<express::base*>(vp);
				}
			}

			// Then try const pointer
			vp = nullptr;
			if (swig_type_info* ti = SWIG_TypeQuery("express::base const *")) {
				int res = SWIG_ConvertPtr(o, &vp, ti, 0);
				if (res >= 0 && vp) {
					return *static_cast<const express::base*>(vp);
				}
			}

			throw ifcopenshell::exception("Attribute not set");
		};

		auto to_vec_base = [&](PyObject* o) -> std::vector<express::base> {
			PyObject* fast = seq_fast(o);
			Py_ssize_t n = PySequence_Fast_GET_SIZE(fast);
			PyObject** items = PySequence_Fast_ITEMS(fast);

			std::vector<express::base> out;
			out.reserve(static_cast<size_t>(n));
			for (Py_ssize_t k = 0; k < n; ++k) {
				out.push_back(to_base(items[k]));
			}

			Py_DECREF(fast);
			return out;
		};

		auto to_vec_vec_int = [&](PyObject* o) -> std::vector<std::vector<int64_t>> {
			PyObject* fast = seq_fast(o);
			Py_ssize_t n = PySequence_Fast_GET_SIZE(fast);
			PyObject** items = PySequence_Fast_ITEMS(fast);

			std::vector<std::vector<int64_t>> out;
			out.reserve(static_cast<size_t>(n));
			for (Py_ssize_t k = 0; k < n; ++k) {
				out.push_back(to_vec_int(items[k]));
			}

			Py_DECREF(fast);
			return out;
		};

		auto to_vec_vec_double = [&](PyObject* o) -> std::vector<std::vector<double>> {
			PyObject* fast = seq_fast(o);
			Py_ssize_t n = PySequence_Fast_GET_SIZE(fast);
			PyObject** items = PySequence_Fast_ITEMS(fast);

			std::vector<std::vector<double>> out;
			out.reserve(static_cast<size_t>(n));
			for (Py_ssize_t k = 0; k < n; ++k) {
				out.push_back(to_vec_double(items[k]));
			}

			Py_DECREF(fast);
			return out;
		};

		auto to_vec_vec_base = [&](PyObject* o) -> std::vector<std::vector<express::base>> {
			PyObject* fast = seq_fast(o);
			Py_ssize_t n = PySequence_Fast_GET_SIZE(fast);
			PyObject** items = PySequence_Fast_ITEMS(fast);

			std::vector<std::vector<express::base>> out;
			out.reserve(static_cast<size_t>(n));
			for (Py_ssize_t k = 0; k < n; ++k) {
				out.push_back(to_vec_base(items[k]));
			}

			Py_DECREF(fast);
			return out;
		};

		// Dispatch based on the IFC argument type (same decision Python was making before)
		ifcopenshell::argument_type arg_type = helper_fn_attribute_type($self, i);

		switch (arg_type) {
			case ifcopenshell::Argument_INT: {
				self->set_attribute_value(i, static_cast<int64_t>(to_index_i64(value)));
				return;
			}
			case ifcopenshell::Argument_BOOL: {
				if (PyBool_Check(value)) {
					self->set_attribute_value(i, value == Py_True);
				}
				return;
			}
			case ifcopenshell::Argument_LOGICAL: {
				boost::logic::tribool t(boost::logic::indeterminate);
				if (PyBool_Check(value)) {
					t = (value == Py_True);
				} else if (PyUnicode_Check(value)) {
					if (PyObject* ascii = PyUnicode_AsEncodedString(value, "UTF-8", "strict")) {
						// value is kept as indeterminate
						if (strcmp(PyBytes_AS_STRING(ascii), "UNKNOWN") != 0) {
							throw ifcopenshell::exception("Attribute not set");
						}
						Py_DECREF(ascii);
					}
				} else {
					long v = to_index_long(value);
					if (v == 0) t = false;
					else if (v == 1) t = true;
					else if (v == -1 || v == 2) t = boost::logic::tribool(boost::logic::indeterminate);
					else throw ifcopenshell::exception("Attribute not set");
				}
				self->set_attribute_value(i, t);
				return;
			}
			case ifcopenshell::Argument_DOUBLE: {
				self->set_attribute_value(i, to_double(value));
				return;
			}
			case ifcopenshell::Argument_STRING:
				self->set_attribute_value(i, to_string(value));
				return;
			case ifcopenshell::Argument_ENUMERATION: {
				const ifcopenshell::enumeration_type* enum_type = $self->declaration().schema()->declaration_by_name($self->declaration().type())->as_entity()->
				attribute_by_index(i)->type_of_attribute()->as_named_type()->declared_type()->as_enumeration_type();
				self->set_attribute_value(i, enumeration_reference(enum_type, enum_type->lookup_enum_offset(to_string(value))));
				return;
			} case ifcopenshell::Argument_BINARY: {
				std::string s = to_string(value);
				if (ifcopenshell::valid_binary_string(s)) {
					boost::dynamic_bitset<> bits(s);
					self->set_attribute_value(i, bits);
				}
				return;
			}
			case ifcopenshell::Argument_AGGREGATE_OF_INT: {
				self->set_attribute_value(i, to_vec_int(value));
				return;
			}
			case ifcopenshell::Argument_AGGREGATE_OF_DOUBLE: {
				self->set_attribute_value(i, to_vec_double(value));
				return;
			}
			case ifcopenshell::Argument_AGGREGATE_OF_STRING:
				self->set_attribute_value(i, to_vec_string(value));
				return;
			case ifcopenshell::Argument_AGGREGATE_OF_BINARY: {
				auto vs = to_vec_string(value);
				std::vector< boost::dynamic_bitset<> > bits;
				bits.reserve(vs.size());
				for (auto& v : vs) {
					if (ifcopenshell::valid_binary_string(v)) {
						bits.push_back(boost::dynamic_bitset<>(v));
					} else {
						throw ifcopenshell::exception("String not a valid binary representation");
					}
				}
				self->set_attribute_value(i, bits);
				return;
			}
			case ifcopenshell::Argument_ENTITY_INSTANCE: {
				self->set_attribute_value(i, to_base(value));
				return;
			}
			case ifcopenshell::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
				self->set_attribute_value(i, to_vec_base(value));
				return;
			}
			case ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_INT: {
				self->set_attribute_value(i, to_vec_vec_int(value));
				return;
			}
			case ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE: {
				self->set_attribute_value(i, to_vec_vec_double(value));
				return;
			}
			case ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
				self->set_attribute_value(i, to_vec_vec_base(value));
				return;
			}
			default:
				throw ifcopenshell::exception("Attribute not set");
		}
	}

	ifcopenshell::file* file_py() const {
		return $self->file();
	}

	%pythoncode %{
		file = property(file_py)
		declaration = property(declaration)
	%}
}

%extend ifcopenshell::spf_header {
	// Upcast to header instances for SWIG, because
	// it has no idea about the schema definitions.
	express::base file_description_py() {
		return $self->file_description();
	}
	express::base file_name_py() {
		return $self->file_name();
	}
	express::base file_schema_py() {
		return $self->file_schema();
	}

	%pythoncode %{
		file_description = property(file_description_py)
		file_name = property(file_name_py)
		file_schema = property(file_schema_py)
	%}
};

%include "../ifcparse/ifc_parse_api.h"

namespace ifcopenshell {
std::string encode_spf_string(const std::string& value);
std::string decode_spf_string(const std::string& value);
}

%include "../ifcparse/spf_header.h"

%pythoncode %{
from .file import file_mixin as file_mixin
%}
%feature("python:abc", "file_mixin") ifcopenshell::file;

%include "../ifcparse/file.h"
%template(instance_streamer) ifcopenshell::instance_streamer<ifcopenshell::file_reader<ifcopenshell::full_buffer_impl>>;

%include "../ifcparse/file_open_status.h"

%pythoncode %{
from .entity_instance import entity_instance_mixin
%}
%feature("python:abc", "entity_instance_mixin") express::base;

%include "../ifcparse/express.h"

%include "../ifcparse/schema.h"
%include "../serializers/rocks_db_serializer.h"
%include "../ifcparse/logger.h"

// The file* returned by open() is to be freed by SWIG/Python
%newobject open;
%newobject read;
%newobject stream_from_string;

%inline %{
	ifcopenshell::file* open(const std::string& fn, bool readonly=false, ifcopenshell::logger* logger=nullptr) {
		ifcopenshell::file* f;
		Py_BEGIN_ALLOW_THREADS;
		f = new ifcopenshell::file(fn, ifcopenshell::FT_AUTODETECT, readonly, ifcopenshell::logger_or_root(logger));
		Py_END_ALLOW_THREADS;
		return f;
	}

    ifcopenshell::file* read(const std::string& data) {
		char* copiedData = new char[data.length()];
		memcpy(copiedData, data.c_str(), data.length());
		ifcopenshell::file* f;
		Py_BEGIN_ALLOW_THREADS;
		f = new ifcopenshell::file((void *)copiedData, data.length());
		Py_END_ALLOW_THREADS;
		return f;
	}

	ifcopenshell::instance_streamer<ifcopenshell::file_reader<ifcopenshell::full_buffer_impl>>* stream_from_string(const std::string& data) {
		char* copiedData = new char[data.length()];
		memcpy(copiedData, data.c_str(), data.length());
		return new ifcopenshell::instance_streamer<ifcopenshell::file_reader<ifcopenshell::full_buffer_impl>>((void *)copiedData, data.length());
	}

	const char* version() {
		return IFCOPENSHELL_VERSION;
	}

	express::base new_IfcBaseClass(ifcopenshell::file& file, const std::string& name) {
        return file.create(file.schema()->declaration_by_name(name));
	}
%}

%extend ifcopenshell::named_type {
	%pythoncode %{
		def __repr__(self):
			return repr(self.declared_type())
	%}
}

%extend ifcopenshell::simple_type {
	%pythoncode %{
		def __repr__(self):
			return "<%s>" % self.declared_type()
	%}
}

%extend ifcopenshell::aggregation_type {
	std::string type_of_aggregation_string() const {
		static const char* const aggr_strings[] = {"array", "bag", "list", "set"};
		return aggr_strings[(int) $self->type_of_aggregation()];
	}
	%pythoncode %{
		def __repr__(self):
			format_bound = lambda i: "?" if i == -1 else str(i)
			return "<%s [%s:%s] of %r>" % (
				self.type_of_aggregation_string(),
				format_bound(self.bound1()),
				format_bound(self.bound2()),
				self.type_of_element()
			)
	%}
}

%extend ifcopenshell::type_declaration {
	%pythoncode %{
		def __repr__(self):
			return "<type %s: %r>" % (self.name(), self.declared_type())
	%}
	std::vector<std::string> argument_types() {
		std::vector<std::string> r;
		auto at = ifcopenshell::Argument_UNKNOWN;
		auto pt = $self->declared_type();
		if (pt) {
			at = ifcopenshell::from_parameter_type(pt);
		}
		r.push_back(ifcopenshell::argument_type_to_string(at));
		return r;
	}
}

%extend ifcopenshell::select_type {
	%pythoncode %{
		def __repr__(self):
			return "<select %s: (%s)>" % (self.name(), " | ".join(map(repr, self.select_list())))
	%}
}

%extend ifcopenshell::enumeration_type {
	%pythoncode %{
		def __repr__(self):
			return "<enumeration %s: (%s)>" % (self.name(), ", ".join(self.enumeration_items()))
	%}
	std::vector<std::string> argument_types() {
		std::vector<std::string> r;
		r.push_back(ifcopenshell::argument_type_to_string(ifcopenshell::Argument_STRING));
		return r;
	}
}

%extend ifcopenshell::attribute {
	%pythoncode %{
		def __repr__(self):
			return "<attribute %s%s: %s>" % (self.name(), "?" if self.optional() else "", self.type_of_attribute())
	%}
}

%extend ifcopenshell::inverse_attribute {
	std::string type_of_aggregation_string() const {
		static const char* const aggr_strings[] = {"bag", "set", ""};
		return aggr_strings[(int) $self->type_of_aggregation()];
	}
	%pythoncode %{
		def __repr__(self):
			format_bound = lambda i: "?" if i == -1 else str(i)
			return "<inverse %s: %s [%s:%s] of %r for %r>" % (
				self.name(),
				self.type_of_aggregation_string(),
				format_bound(self.bound1()),
				format_bound(self.bound2()),
				self.entity_reference(),
				self.attribute_reference()
			)
	%}
}

%extend ifcopenshell::entity {
	%pythoncode %{
		def __repr__(self):
			return "<entity %s>" % (self.name())
	%}
	std::vector<std::string> argument_types() {
		size_t i = 0;
		std::vector<std::string> r;
		for (auto& attr : $self->all_attributes()) {
			auto at = ifcopenshell::Argument_UNKNOWN;
			auto pt = attr->type_of_attribute();
			if ($self->derived()[i++]) {
				at = ifcopenshell::Argument_DERIVED;
			} else if (!pt) {
				at = ifcopenshell::Argument_UNKNOWN;
			} else {
				at = ifcopenshell::from_parameter_type(pt);
			}
			r.push_back(ifcopenshell::argument_type_to_string(at));
		}
		return r;
	}
}

%extend ifcopenshell::schema_definition {
	%pythoncode %{
		def __repr__(self):
			return "<schema %s>" % (self.name())
	%}
}

%{
	static std::stringstream ifcopenshell_log_stream;
%}
%init %{
	ifcopenshell::logger::root().set_output(0, &ifcopenshell_log_stream);
%}
%inline %{
	std::string get_log() {
		std::string log = ifcopenshell_log_stream.str();
		ifcopenshell_log_stream.str("");
		return log;
	}
	void turn_on_detailed_logging() {
		ifcopenshell::logger::root().set_output(&std::cout, &std::cout);
		ifcopenshell::logger::root().verbosity(ifcopenshell::logger::LOG_DEBUG);
	}
	void turn_off_detailed_logging() {
		ifcopenshell::logger::root().set_output(0, &ifcopenshell_log_stream);
		ifcopenshell::logger::root().verbosity(ifcopenshell::logger::LOG_WARNING);
	}
	void set_log_format_json() {
		ifcopenshell_log_stream.str("");
		ifcopenshell::logger::root().output_format(ifcopenshell::logger::FMT_JSON);
	}
	void set_log_format_text() {
		ifcopenshell_log_stream.str("");
		ifcopenshell::logger::root().output_format(ifcopenshell::logger::FMT_PLAIN);
	}
%}

%{
	PyObject* get_info_cpp(const express::base& v, bool recursive, bool include_identifier);

	// @todo refactor this to remove duplication with the typemap.
	// except this is calls the above function in case of instances.
	PyObject* convert_cpp_attribute_to_python(const express::base& instance, size_t attribute_index, bool recursive, bool include_identifier) {
		return instance.get_attribute_value(attribute_index).apply_visitor([recursive, include_identifier](const auto& v){
			using u = std::decay_t<decltype(v)>;
            if constexpr (std::is_same_v<u, ifcopenshell::enumeration_reference>) {
                return pythonize(std::string(v.value()));
			} else if constexpr (std::is_same_v<u, ifcopenshell::derived>) {
				if (feature_use_attribute_value_derived) {
					return SWIG_NewPointerObj(new attribute_value_derived, SWIGTYPE_p_attribute_value_derived, SWIG_POINTER_OWN);
				} else {
					Py_INCREF(Py_None);
					return static_cast<PyObject*>(Py_None);
				}
			} else if constexpr (std::is_same_v<u, express::base>) {
				if (recursive) {
					return get_info_cpp(v, recursive, include_identifier);
				} else {
					return pythonize(v);
				}
            } else if constexpr (std::is_same_v<u, std::vector<express::base>>) {
				if (recursive) {
					PyObject* t = PyTuple_New(v.size());
                    for (size_t i = 0; i < v.size(); ++i) {
                        PyObject* item = get_info_cpp(v[i], recursive, include_identifier);
                        PyTuple_SET_ITEM(t, i, item);
                    }
                    return t;
				} else {
					return pythonize_vector(v);
				}
            } else if constexpr (std::is_same_v<u, std::vector<std::vector<express::base>>>) {
				if (recursive) {
					PyObject* outer = PyTuple_New(v.size());
                    for (size_t i = 0; i < v.size(); ++i) {
                        const auto& inner_vec = v[i];
                        PyObject* inner = PyTuple_New(inner_vec.size());
                        for (size_t j = 0; j < inner_vec.size(); ++j) {
                            PyObject* item = get_info_cpp(inner_vec[j], recursive, include_identifier);
                            PyTuple_SET_ITEM(inner, j, item);
                        }
                        PyTuple_SET_ITEM(outer, i, inner);
                    }
                    return outer;
				} else {
					return pythonize_vector(v);
				}
            } else if constexpr (std::is_same_v<u, ifcopenshell::empty_aggregate> || std::is_same_v<u, ifcopenshell::empty_aggregate_of_aggregate> || std::is_same_v<u, ifcopenshell::blank>) {
                Py_INCREF(Py_None);
				return static_cast<PyObject*>(Py_None);
            } else if constexpr (is_std_vector_v<u>) {
				// only for non-entity-instance vectors
				return pythonize_vector(v);
            } else {
				return pythonize(v);
			}
		});
	}
%}
%inline %{
	PyObject* get_info_cpp(const express::base& v, bool recursive, bool include_identifier) {
		PyObject *d = PyDict_New();

		if (v.declaration().as_entity()) {
			const std::vector<const ifcopenshell::attribute*> attrs = v.declaration().as_entity()->all_attributes();
			std::vector<const ifcopenshell::attribute*>::const_iterator it = attrs.begin();
			auto dit = v.declaration().as_entity()->derived().begin();
			for (; it != attrs.end(); ++it, ++dit) {
				const std::string& name_cpp = (*it)->name();
				auto name_py = pythonize(name_cpp);
				auto attr_type = *dit
					? ifcopenshell::Argument_DERIVED
					: ifcopenshell::from_parameter_type((*it)->type_of_attribute());
				auto value_py = convert_cpp_attribute_to_python(v, std::distance(attrs.begin(), it), recursive, include_identifier);
				PyDict_SetItem(d, name_py, value_py);
				Py_DECREF(name_py);
				Py_DECREF(value_py);
			}
			if (include_identifier) {
				auto id_v_py = pythonize(v.id());
				PyDict_SetItemString(d, "id", id_v_py);
				Py_DECREF(id_v_py);
			}
		} else {
			auto value_py = convert_cpp_attribute_to_python(v, 0, recursive, include_identifier);
			PyDict_SetItemString(d, "wrappedValue", value_py);
			Py_DECREF(value_py);
		}

		const std::string& type_v_cpp = v.declaration().name();
		auto type_v_py = pythonize(type_v_cpp);
		PyDict_SetItemString(d, "type", type_v_py);
		Py_DECREF(type_v_py);

		return d;
	}
%}

%extend ifcopenshell::instance_streamer<ifcopenshell::file_reader<ifcopenshell::full_buffer_impl>> {
	PyObject* read_instance_py(bool type_as_declaration_instance=false) {
		auto simply_type_to_dictionary = [&](const express::base& t) -> PyObject* {
			const auto& nm = t.declaration().name();
			auto ifc_val = t.get_attribute_value(0);
			auto attribute_val_py = ifc_val.apply_visitor([&](const auto& t) {
                using u = std::decay_t<decltype(t)>;

                if constexpr (is_std_vector_v<u>) {
                    return pythonize_vector(t);
                } else if constexpr (std::is_same_v<u, ifcopenshell::enumeration_reference>) {
                    return pythonize(std::string(t.value()));
                } else if constexpr (std::is_same_v<u, ifcopenshell::derived>) {
                    if (feature_use_attribute_value_derived) {
                        return SWIG_NewPointerObj(new attribute_value_derived, SWIGTYPE_p_attribute_value_derived, SWIG_POINTER_OWN);
                    } else {
                        Py_INCREF(Py_None);
                        return static_cast<PyObject*>(Py_None);
                    }
                } else if constexpr (std::is_same_v<u, ifcopenshell::empty_aggregate> || std::is_same_v<u, ifcopenshell::empty_aggregate_of_aggregate> || std::is_same_v<u, ifcopenshell::blank>) {
                    Py_INCREF(Py_None);
                    return static_cast<PyObject*>(Py_None);
                } else {
                    return pythonize(t);
                }
			});

			PyObject* val = PyDict_New();
			{
				const std::string& key_cpp = "type";
				auto name_py = pythonize(key_cpp);
				auto value_py = pythonize(nm);
				PyDict_SetItem(val, name_py, value_py);
				Py_DECREF(name_py);
				Py_DECREF(value_py);
			}
			{
				const std::string& key_cpp = "value";
				auto name_py = pythonize(key_cpp);
				PyDict_SetItem(val, name_py, attribute_val_py);
				Py_DECREF(name_py);
				Py_DECREF(attribute_val_py);
			}
			return val;
		};

		auto instance_reference_to_dict = [&](int i) -> PyObject* {
			PyObject* val = PyDict_New();
			const std::string& key_cpp = "ref";
			auto name_py = pythonize(key_cpp);
			auto value_py = pythonize(i);
			PyDict_SetItem(val, name_py, value_py);
			Py_DECREF(name_py);
			Py_DECREF(value_py);
			return val;
		};

		if (!*self) {
			Py_INCREF(Py_None);
			return Py_None;
		}
		auto inst = self->read_instance();
		if (!inst) {
			Py_INCREF(Py_None);
			return Py_None;
		}
		PyObject* d = PyDict_New();

		{
			const std::string& key_cpp = "id";
			auto name_py = pythonize(key_cpp);
			auto value_py = pythonize((int) std::get<0>(*inst));
			PyDict_SetItem(d, name_py, value_py);
			Py_DECREF(name_py);
			Py_DECREF(value_py);
		}
		{
			const std::string& key_cpp = "type";
			auto name_py = pythonize(key_cpp);
			PyObject* value_py;
			if (type_as_declaration_instance) {
				// @todo should this just be the default behavior?
				value_py = pythonize(std::get<1>(*inst));
			} else {
				value_py = pythonize(std::get<1>(*inst)->name());
			}
			PyDict_SetItem(d, name_py, value_py);
			Py_DECREF(name_py);
			Py_DECREF(value_py);
		}
		{
			const auto* decl = std::get<1>(*inst);
			const auto& data = std::get<2>(*inst);

			for (size_t i = 0; i < decl->as_entity()->attribute_count(); i++) {
				auto val = data->get_attribute_value(i);

                // sets dict member, returns void
				val.apply_visitor([&](const auto& t) -> void {
					using value_type = std::decay_t<decltype(t)>;
					PyObject* attribute_val_py;
					if constexpr (std::is_same_v<value_type, express::base>) {
						attribute_val_py = simply_type_to_dictionary(t);
					} else {
                        if constexpr (is_std_vector_v<value_type>) {
                            attribute_val_py = pythonize_vector(t);
                        } else if constexpr (std::is_same_v<value_type, ifcopenshell::enumeration_reference>) {
                            attribute_val_py = pythonize(std::string(t.value()));
                        } else if constexpr (std::is_same_v<value_type, ifcopenshell::derived>) {
                            if (feature_use_attribute_value_derived) {
                                attribute_val_py = SWIG_NewPointerObj(new attribute_value_derived, SWIGTYPE_p_attribute_value_derived, SWIG_POINTER_OWN);
                            } else {
                                Py_INCREF(Py_None);
                                attribute_val_py = static_cast<PyObject*>(Py_None);
                            }
                        } else if constexpr (std::is_same_v<value_type, ifcopenshell::empty_aggregate> || std::is_same_v<value_type, ifcopenshell::empty_aggregate_of_aggregate> || std::is_same_v<value_type, ifcopenshell::blank>) {
                            Py_INCREF(Py_None);
                            attribute_val_py = static_cast<PyObject*>(Py_None);
                        } else {
                            attribute_val_py = pythonize(t);
                        }
					}

					{
						auto name_py = pythonize(decl->as_entity()->attribute_by_index(i)->name());
						PyDict_SetItem(d, name_py, attribute_val_py);
						Py_DECREF(name_py);
						Py_DECREF(attribute_val_py);
					}
				});
			}

			for (auto& p : self->references()) {
				int index = p.first.index_;
				auto name_py = pythonize(decl->as_entity()->attribute_by_index(index)->name());

				std::visit([&](const auto& v) -> void {
                    PyObject* attribute_val_py = nullptr;
					using t = std::decay_t<decltype(v)>;

					if constexpr (std::is_same_v<t, ifcopenshell::reference_or_simple_type>) {
						if (auto* inst = std::get_if<express::base>(&v)) {
							// So this never happens?
						} else if (auto* name = std::get_if<ifcopenshell::instance_reference>(&v)) {
							attribute_val_py = instance_reference_to_dict(*name);
						}
					} else if constexpr (std::is_same_v<t, std::vector<ifcopenshell::reference_or_simple_type>>) {
						attribute_val_py = PyTuple_New(v.size());
						size_t idx = 0;
						for (auto const& inner : v) {
							if (auto* inst = std::get_if<express::base>(&inner)) {
								PyTuple_SetItem(attribute_val_py, idx++, simply_type_to_dictionary(*inst));
							} else if (auto* name = std::get_if<ifcopenshell::instance_reference>(&inner)) {
								PyTuple_SetItem(attribute_val_py, idx++, instance_reference_to_dict(*name));
							}
						}
					} else if constexpr (std::is_same_v<t, std::vector<std::vector<ifcopenshell::reference_or_simple_type>>>) {
						attribute_val_py = PyTuple_New(v.size());
						size_t outer_idx = 0;
						for (auto const& inner : v) {
							PyObject* inner_py = PyTuple_New(inner.size());
							size_t idx = 0;
							for (auto const& innermost : inner) {
								if (auto* inst = std::get_if<express::base>(&innermost)) {
									PyTuple_SetItem(inner_py, idx++, simply_type_to_dictionary(*inst));
								} else if (auto* name = std::get_if<ifcopenshell::instance_reference>(&innermost)) {
									PyTuple_SetItem(inner_py, idx++, instance_reference_to_dict(*name));
								}
							}
							PyTuple_SetItem(attribute_val_py, outer_idx++, inner_py);
						}
					}

                    if (attribute_val_py) {
                        // This is for IfcPropertySetDefinitionSet where the references need to be written
                        // into a simple type.
                        PyObject* existing = PyDict_GetItemWithError(d, name_py);
                        bool set_in_dict = false;
                        if (existing && PyDict_Check(existing) && PyDict_GetItemString(existing, "type")) {
                            PyObject* val = PyDict_GetItemString(existing, "value");
                            if (val && val == Py_None) {
                                PyDict_SetItemString(existing, "value", attribute_val_py);
                                set_in_dict = true;
                            }
                        }

                        if (!set_in_dict) {
                            PyDict_SetItem(d, name_py, attribute_val_py);
                            Py_DECREF(name_py);
                            Py_DECREF(attribute_val_py);
                        }
                    }

				}, p.second);
			}
		}

		$self->references().clear();
		$self->inverses().clear();

		return d;
	}
}

%extend ifcopenshell::logger {
	%pythoncode %{
		def __iter__(self):
			return iter(self.log_messages())
	%}
}

%extend ifcopenshell::log_message {
	std::string severity_string() const {
		static const char* const severity_strings[] = {"PERF", "DEBUG", "NOTICE", "WARNING", "ERROR"};
		return severity_strings[(int)$self->severity];
	}
	%pythoncode %{
		severity_string = property(severity_string)
		def to_dict(self):
			keys = ("timestamp", "severity", "code", "message", "instance", "product")
			return dict(zip(keys, self.to_tuple()))
		def to_tuple(self):
			return self.timestamp, self.severity_string, self.code, self.message, self.instance, self.product
		def __eq__(self, other):
			return type(self) == type(other) and self.to_tuple() == other.to_tuple()
		def __hash__(self):
			return hash(self.to_tuple())
		def __repr__(self):
			return "<log_message '[%s] [%s] %s'>" % (self.severity_string, self.code, self.message)
	%}
}
