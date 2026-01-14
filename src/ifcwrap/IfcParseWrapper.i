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

%ignore IfcParse::IfcFile::register_inverse;
%ignore IfcParse::IfcFile::unregister_inverse;
%ignore IfcParse::IfcFile::schema;
%ignore IfcParse::IfcFile::begin;
%ignore IfcParse::IfcFile::end;
%ignore IfcParse::IfcFile::types_begin;
%ignore IfcParse::IfcFile::types_end;
%ignore IfcParse::IfcFile::internal_guid_map;
%ignore IfcParse::IfcFile::storage_;
%ignore IfcParse::IfcFile::byguid_;
%ignore IfcParse::IfcFile::byid_;
%ignore IfcParse::IfcFile::byref_excl_;
%ignore IfcParse::IfcFile::types_to_bypass_loading_;

%ignore IfcParse::InstanceStreamer::InstanceStreamer(const IfcParse::schema_definition* schema, IfcParse::IfcSpfLexer* lexer);

%ignore IfcParse::InstanceStreamer::readInstance;
%ignore IfcParse::InstanceStreamer::stealInstances;

%ignore express::Entity;
%ignore express::Select;
%ignore express::DeclaredType;

%ignore in_memory_file_storage;
%ignore rocks_db_file_storage;
// Available as get_inverse().
%ignore IfcParse::IfcFile::instances_by_reference;

%ignore IfcParse::parse_context;

%ignore operator<<;

%ignore IfcParse::FileDescription::FileDescription;
%ignore IfcParse::FileName::FileName;
%ignore IfcParse::FileSchema::FileSchema;
%ignore IfcParse::IfcFile::tokens;

%ignore IfcParse::IfcSpfHeader::IfcSpfHeader(IfcSpfLexer*);
%ignore IfcParse::IfcSpfHeader::lexer;
%ignore IfcParse::IfcSpfHeader::stream;
%ignore IfcParse::IfcSpfHeader::file_description;
%ignore IfcParse::IfcSpfHeader::file_name;
%ignore IfcParse::IfcSpfHeader::file_schema;

%ignore IfcParse::HeaderEntity::is;

%ignore IfcParse::IfcFile::type_iterator;

%ignore express::Base::is;

%rename("by_id") instance_by_id;
%rename("by_guid") instance_by_guid;
%rename("_by_type") instances_by_type;
%rename("_by_type_excl_subtypes") instances_by_type_excl_subtypes;
%rename("get_inverses_by_declaration") getInverse;
%rename("get_total_inverses_by_id") getTotalInverses;
%rename("entity_instance") express::Base;
%rename("file") IfcFile;
// _add() because mixin defined add which adds transaction logic
%rename("_add") addEntity;
%rename("remove") removeEntity;
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

static const std::string& helper_fn_declaration_get_name(const IfcParse::declaration* decl) {
	return decl->name();
}

static IfcUtil::ArgumentType helper_fn_attribute_type(const express::Base* instp, unsigned i) {
	const auto& inst = *instp;
	const IfcParse::parameter_type* pt = 0;
	if (inst.declaration().as_entity()) {
		pt = inst.declaration().as_entity()->attribute_by_index(i)->type_of_attribute();
		if (inst.declaration().as_entity()->derived()[i]) {
			return IfcUtil::Argument_DERIVED;
		}
	} else if (inst.declaration().as_type_declaration() && i == 0) {
		pt = inst.declaration().as_type_declaration()->declared_type();
	} else if (inst.declaration().as_enumeration_type() && i == 0) {
		// Enumeration is always from string in Python
		return IfcUtil::Argument_STRING;
	}

	if (pt == 0) {
		return IfcUtil::Argument_UNKNOWN;
	} else {
		return IfcUtil::from_parameter_type(pt);
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
    RocksDBPrefixIterator(const IfcParse::impl::rocks_db_file_storage* storage,
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

%newobject IfcParse::IfcFile::key_value_store_iter;

%extend IfcParse::IfcFile {
	/*
	// Use to correlate to entity_instance.file_pointer, so that we
	// can trace file ownership of instances on the python side.
	size_t file_pointer() const {
		return reinterpret_cast<size_t>($self);
	}
	*/

	IfcFile(const std::string& schema) {
		return new IfcParse::IfcFile(IfcParse::schema_by_name(schema));
	}

	std::vector<express::Base> _get_inverse(const express::Base& e) {
		if (auto e_ = e.as<express::Entity>()) {
			return cast_vector<express::Base>($self->getInverse(e_.id(), 0, -1));
		}
		throw IfcParse::IfcException("Only entities with ids are supported for get_inverse. Provided entity: '" + e.declaration().name() + "'.");
	}

	std::vector<int> _get_inverse_indices(const express::Base& e) {
		if (auto e_ = e.as<express::Entity>()) {
			return $self->get_inverse_indices(e_.id());
		}
		throw IfcParse::IfcException("Only entities with ids are supported for get_inverse_indices. Provided entity: '" + e.declaration().name() + "'.");
	}

	int get_total_inverses(const express::Base& e) {
		if (auto e_ = e.as<express::Entity>()) {
			return $self->getTotalInverses(e_.id());
		}
		throw IfcParse::IfcException("Only entities with ids are supported for get_total_inverses. Provided entity: '" + e.declaration().name() + "'.");
	}

	void _write(const std::string& fn) {
		std::ofstream f(IfcUtil::path::from_utf8(fn).c_str());
		if (!f.good()) {
			throw std::runtime_error("Failed to write to path: '" + fn + "', check folder and file permissions.");
		}
		f << (*$self);
	}

	std::string to_string() {
		std::stringstream s;
		s << (*$self);
		return s.str();
	}

	express::Base create(const std::string& entity_name) {
		const IfcParse::declaration* decl = $self->schema()->declaration_by_name(entity_name);
		if (!decl || !(decl->as_entity() || decl->as_type_declaration())) {
			throw IfcParse::IfcException("No such entity or type declaration: '" + entity_name + "' in schema '" + $self->schema()->name());
		}
		return $self->create(decl);
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

	std::string schema_name() const {
		if ($self->schema() == 0) return "";
		return $self->schema()->name();
	}

	int storage_mode() const {
		return std::visit([](auto& m) -> int {
			if constexpr (std::is_same_v<std::decay_t<decltype(m)>, IfcParse::impl::in_memory_file_storage>) {
				return 0;
			} else if constexpr (std::is_same_v<std::decay_t<decltype(m)>, IfcParse::impl::rocks_db_file_storage>) {
				return 1;
			}
			return -1;
		}, $self->storage_);
	}

#ifdef IFOPSH_WITH_ROCKSDB
	RocksDBPrefixIterator* key_value_store_iter(const std::string& prefix) const {
        auto* storage = std::visit([](auto& m) -> IfcParse::impl::rocks_db_file_storage const * {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, IfcParse::impl::rocks_db_file_storage>) {
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
        auto* storage = std::visit([](auto& m) -> IfcParse::impl::rocks_db_file_storage const * {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, IfcParse::impl::rocks_db_file_storage>) {
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
		schema = property(schema_name)
		header = property(header)
		_registry = {}

		_old_init = __init__
		def __init__(self, schema=None, schema_version=None):
			self._old_init(*filter(None, (schema, schema_version)))
    
		def __setattr__(self, k, v):
			object.__setattr__(self, k, v)
			if k == 'this':
				# only now we know the identity of the object and we set our python-side attributes based on a python-side map
				self.post_init(int(v))
	%}
}

%extend express::Base {

	// 0 = not found
	// 1 = regular forward attribute
	// 2 = inverse attribute
	// 3 = derived attribute (redeclared in subtype as derived)
	int get_attribute_category(const std::string& name) const {
		if (!$self->declaration().as_entity()) {
			return name == "wrappedValue" ? 1 : 0;
		}
		
		{
		const std::vector<const IfcParse::attribute*> attrs = $self->declaration().as_entity()->all_attributes();
		std::vector<const IfcParse::attribute*>::const_iterator it = attrs.begin();
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
		const std::vector<const IfcParse::inverse_attribute*> attrs = $self->declaration().as_entity()->all_inverse_attributes();
		std::vector<const IfcParse::inverse_attribute*>::const_iterator it = attrs.begin();
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
		return $self->as<express::Base>() != nullptr
			? $self->as<express::Base>()->id()
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
		
		const std::vector<const IfcParse::attribute*> attrs = $self->declaration().as_entity()->all_attributes();
		
		std::vector<std::string> attr_names;
		attr_names.reserve(attrs.size());		
		
		std::vector<const IfcParse::attribute*>::const_iterator it = attrs.begin();
		for (; it != attrs.end(); ++it) {
			attr_names.push_back((*it)->name());
		}

		return attr_names;
	}

	std::vector<std::string> get_inverse_attribute_names() const {
		if (!$self->declaration().as_entity()) {
			return std::vector<std::string>(0);
		}

		const std::vector<const IfcParse::inverse_attribute*> attrs = $self->declaration().as_entity()->all_inverse_attributes();
		
		std::vector<std::string> attr_names;
		attr_names.reserve(attrs.size());		
		
		std::vector<const IfcParse::inverse_attribute*>::const_iterator it = attrs.begin();
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

	AttributeValue get_argument(unsigned i) {
		return $self->get_attribute_value(i);
	}

	AttributeValue get_argument(const std::string& a) {
		auto i = $self->declaration().as_entity()->attribute_index(a);
		if (i == -1) {
			throw std::runtime_error("Attribute '" + a + "' not found on entity named " + $self->declaration().name());
		}
		return $self->get_attribute_value((unsigned)i);
	}

	bool __eq__(const express::Base& other) const {
		return $self->identity() == other.identity();
	}

	size_t __hash__() const {
	    if (!self->declaration().as_entity()) {
            return boost::hash<std::tuple<uint32_t, void*>>{}({self->identity(), self->file()});
		} else {
            return self->get_attribute_value(0).apply_visitor([&](const auto& val){
                using U = std::decay_t<decltype(val)>;
                if constexpr (std::is_same_v<U, Blank> || std::is_same_v<U, Derived> || std::is_same_v<U, boost::logic::tribool> || std::is_same_v<U, EnumerationReference> || std::is_same_v<U, empty_aggregate_t> || std::is_same_v<U, empty_aggregate_of_aggregate_t>) {
					// @todo
                    return boost::hash<std::tuple<size_t, size_t, void*>>{}({self->declaration().index_in_schema(), 0, self->file()});
                } else {
                    return boost::hash<std::tuple<size_t, decltype(val), void*>>{}({self->declaration().index_in_schema(), val, self->file()});
                }
			});			
		}
	}

	std::string __repr__() const {
	    std::ostringstream oss;
		$self->toString(oss);
        return oss.str();
	}

	std::string to_string(bool valid_spf = true) const {
		std::ostringstream oss;
		$self->toString(oss, valid_spf);
        return oss.str();
	}

	/*
	// Just something to have a somewhat sensible value to hash
	size_t file_pointer() const {
		return reinterpret_cast<size_t>($self->file_);
	}
	*/

	unsigned get_argument_index(const std::string& a) const {
		if ($self->declaration().as_entity()) {
			return $self->declaration().as_entity()->attribute_index(a);
		} else if (a == "wrappedValue") {
			return 0;
		} else {
			throw IfcParse::IfcException(a + " not found on " + $self->declaration().name());
		}
	}

	std::vector<express::Base> get_inverse(const std::string& a) {
		if ($self->declaration().as_entity()) {
			return cast_vector<express::Base>($self->as<express::Entity>().get_inverse(a));
		} else {
			throw IfcParse::IfcException(a + " not found on " + $self->declaration().name());
		}
	}

	const char* const attribute_type(unsigned int i) const {
		return IfcUtil::ArgumentTypeToString(helper_fn_attribute_type($self, i));
	}

	const char* const attribute_type(const std::string& name) const {
		return IfcUtil::ArgumentTypeToString(helper_fn_attribute_type($self, express_Base_get_argument_index($self, name)));
	}

	const std::string& attribute_name(unsigned int i) const {
		if ($self->declaration().as_entity()) {
			return $self->declaration().as_entity()->attribute_by_index(i)->name();
		} else if (i == 0) {
			static std::string WRAPPED = "wrappedValue";
			return WRAPPED;
		} else {
			throw IfcParse::IfcException(boost::lexical_cast<std::string>(i) + " out of bounds on " + $self->declaration().name());
		}
	}

	void set_attribute_value_py(unsigned int i, PyObject* value) {
		if (value == Py_None) {
			// @nb we don't check anymore if the attribute is optional here, because it should be
			// possible to go back to the state at construction time.
			// bool is_optional = $self->declaration().as_entity()->attribute_by_index(i)->optional();
			self->set_attribute_value(i, Blank{});
			return;
		}

		auto to_index_long = [&](PyObject* o) -> long {
			PyObject* idx = PyNumber_Index(o);  // accepts numpy ints, bools, etc.
			if (!idx) {
				PyErr_Clear();
				throw IfcParse::IfcException("Attribute not set");
			}
			long v = PyLong_AsLong(idx);
			Py_DECREF(idx);
			if (PyErr_Occurred()) {
				PyErr_Clear();
				throw IfcParse::IfcException("Attribute not set");
			}
			return v;
		};

		auto to_double = [&](PyObject* o) -> double {
			double v = PyFloat_AsDouble(o); // accepts ints and float-like objects
			if (PyErr_Occurred()) {
				PyErr_Clear();
				throw IfcParse::IfcException("Attribute not set");
			}
			return v;
		};

		auto to_string = [&](PyObject* o) -> std::string {
			if (PyUnicode_Check(o)) {
				Py_ssize_t n = 0;
				const char* s = PyUnicode_AsUTF8AndSize(o, &n);
				if (!s) {
					PyErr_Clear();
					throw IfcParse::IfcException("Attribute not set");
				}
				return std::string(s, static_cast<size_t>(n));
			}
			if (PyBytes_Check(o)) {
				char* s = nullptr;
				Py_ssize_t n = 0;
				if (PyBytes_AsStringAndSize(o, &s, &n) == -1) {
					PyErr_Clear();
					throw IfcParse::IfcException("Attribute not set");
				}
				return std::string(s, static_cast<size_t>(n));
			}
			throw IfcParse::IfcException("Attribute not set");
		};

		auto seq_fast = [&](PyObject* o) -> PyObject* {
			PyObject* fast = PySequence_Fast(o, "expected a sequence");
			if (!fast) {
				PyErr_Clear();
				throw IfcParse::IfcException("Attribute not set");
			}
			return fast; // new ref
		};

		auto to_vec_int = [&](PyObject* o) -> std::vector<int> {
			PyObject* fast = seq_fast(o);
			Py_ssize_t n = PySequence_Fast_GET_SIZE(fast);
			PyObject** items = PySequence_Fast_ITEMS(fast);

			std::vector<int> out;
			out.reserve(static_cast<size_t>(n));
			for (Py_ssize_t k = 0; k < n; ++k) {
				out.push_back(static_cast<int>(to_index_long(items[k])));
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

		auto to_base = [&](PyObject* o) -> express::Base {
			void* vp = nullptr;

			// Try non-const pointer first
			if (swig_type_info* ti = SWIG_TypeQuery("express::Base *")) {
				int res = SWIG_ConvertPtr(o, &vp, ti, 0);
				if (res >= 0 && vp) {
					return *static_cast<express::Base*>(vp);
				}
			}

			// Then try const pointer
			vp = nullptr;
			if (swig_type_info* ti = SWIG_TypeQuery("express::Base const *")) {
				int res = SWIG_ConvertPtr(o, &vp, ti, 0);
				if (res >= 0 && vp) {
					return *static_cast<const express::Base*>(vp);
				}
			}

			throw IfcParse::IfcException("Attribute not set");
		};

		auto to_vec_base = [&](PyObject* o) -> std::vector<express::Base> {
			PyObject* fast = seq_fast(o);
			Py_ssize_t n = PySequence_Fast_GET_SIZE(fast);
			PyObject** items = PySequence_Fast_ITEMS(fast);

			std::vector<express::Base> out;
			out.reserve(static_cast<size_t>(n));
			for (Py_ssize_t k = 0; k < n; ++k) {
				out.push_back(to_base(items[k]));
			}

			Py_DECREF(fast);
			return out;
		};

		auto to_vec_vec_int = [&](PyObject* o) -> std::vector<std::vector<int>> {
			PyObject* fast = seq_fast(o);
			Py_ssize_t n = PySequence_Fast_GET_SIZE(fast);
			PyObject** items = PySequence_Fast_ITEMS(fast);

			std::vector<std::vector<int>> out;
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

		auto to_vec_vec_base = [&](PyObject* o) -> std::vector<std::vector<express::Base>> {
			PyObject* fast = seq_fast(o);
			Py_ssize_t n = PySequence_Fast_GET_SIZE(fast);
			PyObject** items = PySequence_Fast_ITEMS(fast);

			std::vector<std::vector<express::Base>> out;
			out.reserve(static_cast<size_t>(n));
			for (Py_ssize_t k = 0; k < n; ++k) {
				out.push_back(to_vec_base(items[k]));
			}

			Py_DECREF(fast);
			return out;
		};

		// Dispatch based on the IFC argument type (same decision Python was making before)
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);

		switch (arg_type) {
			case IfcUtil::Argument_INT: {
				self->set_attribute_value(i, static_cast<int>(to_index_long(value)));
				return;
			}
			case IfcUtil::Argument_BOOL: {
				if (PyBool_Check(value)) {
					self->set_attribute_value(i, value == Py_True);
				}
				return;
			}
			case IfcUtil::Argument_LOGICAL: {
				boost::logic::tribool t(boost::logic::indeterminate);
				if (PyBool_Check(value)) {
					t = (value == Py_True);
				} else {
					long v = to_index_long(value);
					if (v == 0) t = false;
					else if (v == 1) t = true;
					else if (v == -1 || v == 2) t = boost::logic::tribool(boost::logic::indeterminate);
					else throw IfcParse::IfcException("Attribute not set");
				}
				self->set_attribute_value(i, t);
				return;
			}
			case IfcUtil::Argument_DOUBLE: {
				self->set_attribute_value(i, to_double(value));
				return;
			}
			case IfcUtil::Argument_STRING:
				self->set_attribute_value(i, to_string(value));
				return;
			case IfcUtil::Argument_ENUMERATION: {
				const IfcParse::enumeration_type* enum_type = $self->declaration().schema()->declaration_by_name($self->declaration().type())->as_entity()->
				attribute_by_index(i)->type_of_attribute()->as_named_type()->declared_type()->as_enumeration_type();
				self->set_attribute_value(i, EnumerationReference(enum_type, enum_type->lookup_enum_offset(to_string(value))));
				return;
			} case IfcUtil::Argument_BINARY: {
				std::string s = to_string(value);
				if (IfcUtil::valid_binary_string(s)) {
					boost::dynamic_bitset<> bits(s);
					self->set_attribute_value(i, bits);
				}
				return;
			}
			case IfcUtil::Argument_AGGREGATE_OF_INT: {
				self->set_attribute_value(i, to_vec_int(value));
				return;
			}
			case IfcUtil::Argument_AGGREGATE_OF_DOUBLE: {
				self->set_attribute_value(i, to_vec_double(value));
				return;
			}
			case IfcUtil::Argument_AGGREGATE_OF_STRING:
				self->set_attribute_value(i, to_vec_string(value));
				return;
			case IfcUtil::Argument_AGGREGATE_OF_BINARY: {
				auto vs = to_vec_string(value);
				std::vector< boost::dynamic_bitset<> > bits;
				bits.reserve(vs.size());
				for (auto& v : vs) {
					if (IfcUtil::valid_binary_string(v)) {
						bits.push_back(boost::dynamic_bitset<>(v));
					} else {
						throw IfcParse::IfcException("String not a valid binary representation");
					}			
				}
				self->set_attribute_value(i, bits);
				return;
			}
			case IfcUtil::Argument_ENTITY_INSTANCE: {
				self->set_attribute_value(i, to_base(value));
				return;
			}
			case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
				self->set_attribute_value(i, to_vec_base(value));
				return;
			}
			case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT: {
				self->set_attribute_value(i, to_vec_vec_int(value));
				return;
			}
			case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE: {
				self->set_attribute_value(i, to_vec_vec_double(value));
				return;
			}
			case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
				self->set_attribute_value(i, to_vec_vec_base(value));
				return;
			}
			default:
				throw IfcParse::IfcException("Attribute not set");
		}
	}

	IfcParse::IfcFile* file_py() const {
		return $self->file();
	}

	%pythoncode %{
		file = property(file_py)
	%}
}

%extend IfcParse::IfcSpfHeader {
	// Upcast to header instances for SWIG, because
	// it has no idea about the schema definitions.
	express::Base file_description_py() {
		return $self->file_description();
	}
	express::Base file_name_py() {
		return $self->file_name();
	}
	express::Base file_schema_py() {
		return $self->file_schema();
	}

	%pythoncode %{
		file_description = property(file_description_py)
		file_name = property(file_name_py)
		file_schema = property(file_schema_py)
	%}
};

%include "../ifcparse/ifc_parse_api.h"
%include "../ifcparse/IfcSpfHeader.h"

%pythoncode %{
### hack hack hack
### we trick swig into inheriting from our own extension class
### that way we do not constantly need to decorate/undecorate
# @todo is there no official way to do this?
_old_object = object
from .file import file_mixin as custom_base
object = custom_base
%}

%include "../ifcparse/IfcFile.h"

%pythoncode %{
### hack hack hack
### restore
object = _old_object
%}

%include "../ifcparse/file_open_status.h"

%pythoncode %{
### hack hack hack
### we trick swig into inheriting from our own extension class
### that way we do not constantly need to decorate/undecorate
# @todo is there no official way to do this?
_old_object = object
from .entity_instance import entity_instance_mixin as custom_base
object = custom_base
%}

%include "../ifcparse/express.h"

%pythoncode %{
### hack hack hack
### restore
object = _old_object
%}

%include "../ifcparse/IfcSchema.h"
%include "../serializers/RocksDbSerializer.h"

// The IfcFile* returned by open() is to be freed by SWIG/Python
%newobject open;
%newobject read;
%newobject parse_ifcxml;
%newobject stream_from_string;

%inline %{
	IfcParse::IfcFile* open(const std::string& fn, bool readonly=false) {
		IfcParse::IfcFile* f;
		Py_BEGIN_ALLOW_THREADS;
		f = new IfcParse::IfcFile(fn, IfcParse::FT_AUTODETECT, readonly);
		Py_END_ALLOW_THREADS;
		return f;
	}

    IfcParse::IfcFile* read(const std::string& data) {
		char* copiedData = new char[data.length()];
		memcpy(copiedData, data.c_str(), data.length());
		IfcParse::IfcFile* f;
		Py_BEGIN_ALLOW_THREADS;
		f = new IfcParse::IfcFile((void *)copiedData, data.length());
		Py_END_ALLOW_THREADS;
		return f;
	}

	IfcParse::InstanceStreamer* stream_from_string(const std::string& data) {
		char* copiedData = new char[data.length()];
		memcpy(copiedData, data.c_str(), data.length());
		return new IfcParse::InstanceStreamer((void *)copiedData, data.length());
	}

	const char* version() {
		return IFCOPENSHELL_VERSION;
	}

	express::Base new_IfcBaseClass(IfcParse::IfcFile* file, const std::string& name) {
        return file->create(file->schema()->declaration_by_name(name));
	}
%}

%extend IfcParse::named_type {
	%pythoncode %{
		def __repr__(self):
			return repr(self.declared_type())
	%}
}

%extend IfcParse::simple_type {
	%pythoncode %{
		def __repr__(self):
			return "<%s>" % self.declared_type()
	%}
}

%extend IfcParse::aggregation_type {
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

%extend IfcParse::type_declaration {
	%pythoncode %{
		def __repr__(self):
			return "<type %s: %r>" % (self.name(), self.declared_type())
	%}
	std::vector<std::string> argument_types() {
		std::vector<std::string> r;
		auto at = IfcUtil::Argument_UNKNOWN;
		auto pt = $self->declared_type();
		if (pt) {
			at = IfcUtil::from_parameter_type(pt);
		}
		r.push_back(IfcUtil::ArgumentTypeToString(at));
		return r;
	}
}

%extend IfcParse::select_type {
	%pythoncode %{
		def __repr__(self):
			return "<select %s: (%s)>" % (self.name(), " | ".join(map(repr, self.select_list())))
	%}
}

%extend IfcParse::enumeration_type {
	%pythoncode %{
		def __repr__(self):
			return "<enumeration %s: (%s)>" % (self.name(), ", ".join(self.enumeration_items()))
	%}
	std::vector<std::string> argument_types() {
		std::vector<std::string> r;
		r.push_back(IfcUtil::ArgumentTypeToString(IfcUtil::Argument_STRING));
		return r;
	}
}

%extend IfcParse::attribute {
	%pythoncode %{
		def __repr__(self):
			return "<attribute %s%s: %s>" % (self.name(), "?" if self.optional() else "", self.type_of_attribute())
	%}
}

%extend IfcParse::inverse_attribute {
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

%extend IfcParse::entity {
	%pythoncode %{
		def __repr__(self):
			return "<entity %s>" % (self.name())
	%}
	std::vector<std::string> argument_types() {
		size_t i = 0;
		std::vector<std::string> r;
		for (auto& attr : $self->all_attributes()) {
			auto at = IfcUtil::Argument_UNKNOWN;
			auto pt = attr->type_of_attribute();
			if ($self->derived()[i++]) {
				at = IfcUtil::Argument_DERIVED;
			} else if (!pt) {
				at = IfcUtil::Argument_UNKNOWN;
			} else {
				at = IfcUtil::from_parameter_type(pt);
			}
			r.push_back(IfcUtil::ArgumentTypeToString(at));
		}
		return r;
	}
}

%extend IfcParse::schema_definition {
	%pythoncode %{
		def __repr__(self):
			return "<schema %s>" % (self.name())
	%}
}

%{
	static std::stringstream ifcopenshell_log_stream;
%}
%init %{
	Logger::SetOutput(0, &ifcopenshell_log_stream);
%}
%inline %{
	std::string get_log() {
		std::string log = ifcopenshell_log_stream.str();
		ifcopenshell_log_stream.str("");
		return log;
	}
	void turn_on_detailed_logging() {
		Logger::SetOutput(&std::cout, &std::cout);
		Logger::Verbosity(Logger::LOG_DEBUG);
	}
	void turn_off_detailed_logging() {
		Logger::SetOutput(0, &ifcopenshell_log_stream);
		Logger::Verbosity(Logger::LOG_WARNING);
	}
	void set_log_format_json() {
		ifcopenshell_log_stream.str("");
		Logger::OutputFormat(Logger::FMT_JSON);
	}
	void set_log_format_text() {
		ifcopenshell_log_stream.str("");
		Logger::OutputFormat(Logger::FMT_PLAIN);
	}
%}

%{
	PyObject* get_info_cpp(const express::Base& v, bool include_identifier);

	// @todo refactor this to remove duplication with the typemap. 
	// except this is calls the above function in case of instances.
	PyObject* convert_cpp_attribute_to_python(const express::Base& instance, size_t attribute_index, bool include_identifier = true) {
		return instance.get_attribute_value(attribute_index).apply_visitor([include_identifier](const auto& v){
			using U = std::decay_t<decltype(v)>;
            if constexpr (is_std_vector_v<U>) {
				return pythonize_vector(v);
            } else if constexpr (std::is_same_v<U, EnumerationReference>) {
                return pythonize(std::string(v.value()));
			} else if constexpr (std::is_same_v<U, Derived>) {
				if (feature_use_attribute_value_derived) {
					return SWIG_NewPointerObj(new attribute_value_derived, SWIGTYPE_p_attribute_value_derived, SWIG_POINTER_OWN);
				} else {
					Py_INCREF(Py_None);
					return static_cast<PyObject*>(Py_None); 
				}
			} else if constexpr (std::is_same_v<U, express::Base>) {
				return get_info_cpp(v, include_identifier);
            } else if constexpr (std::is_same_v<U, empty_aggregate_t> || std::is_same_v<U, empty_aggregate_of_aggregate_t> || std::is_same_v<U, Blank>) {
                Py_INCREF(Py_None);
				return static_cast<PyObject*>(Py_None); 
            } else {
				return pythonize(v);
			}
		});
	}
%}
%inline %{
	PyObject* get_info_cpp(const express::Base& v, bool include_identifier = true) {
		PyObject *d = PyDict_New();

		if (v.declaration().as_entity()) {
			const std::vector<const IfcParse::attribute*> attrs = v.declaration().as_entity()->all_attributes();
			std::vector<const IfcParse::attribute*>::const_iterator it = attrs.begin();
			auto dit = v.declaration().as_entity()->derived().begin();
			for (; it != attrs.end(); ++it, ++dit) {
				const std::string& name_cpp = (*it)->name();
				auto name_py = pythonize(name_cpp);
				auto attr_type = *dit
					? IfcUtil::Argument_DERIVED
					: IfcUtil::from_parameter_type((*it)->type_of_attribute());
				auto value_py = convert_cpp_attribute_to_python(v, std::distance(attrs.begin(), it), include_identifier);
				PyDict_SetItem(d, name_py, value_py);
				Py_DECREF(name_py);
				Py_DECREF(value_py);
			}
			if (include_identifier) {
				const std::string& id_cpp = "id";
				auto id_py = pythonize(id_cpp);
				auto id_v_py = pythonize(v.id());
				PyDict_SetItem(d, id_py, id_v_py);
				Py_DECREF(id_py);
				Py_DECREF(id_v_py);
			}
		} else {
			const std::string& name_cpp = "wrappedValue";
			auto name_py = pythonize(name_cpp);
			auto value_py = convert_cpp_attribute_to_python(v, 0, include_identifier);
			PyDict_SetItem(d, name_py, value_py);
			Py_DECREF(name_py);
			Py_DECREF(value_py);
		}

		// @todo type and id can be static?
		const std::string& type_cpp = "type";
		auto type_py = pythonize(type_cpp);
		const std::string& type_v_cpp = v.declaration().name();
		auto type_v_py = pythonize(type_v_cpp);
		PyDict_SetItem(d, type_py, type_v_py);
		Py_DECREF(type_py);
		Py_DECREF(type_v_py);

		return d;
	}
%}

%extend IfcParse::InstanceStreamer {
	PyObject* readInstancePy(bool type_as_declaration_instance=false) {
		auto simply_type_to_dictionary = [&](const express::Base& t) -> PyObject* {
			const auto& nm = t.declaration().name();
			auto ifc_val = t.get_attribute_value(0);
			auto attribute_val_py = ifc_val.apply_visitor([&](const auto& t) {
                using U = std::decay_t<decltype(t)>;

                if constexpr (is_std_vector_v<U>) {
                    return pythonize_vector(t);
                } else if constexpr (std::is_same_v<U, EnumerationReference>) {
                    return pythonize(std::string(t.value()));
                } else if constexpr (std::is_same_v<U, Derived>) {
                    if (feature_use_attribute_value_derived) {
                        return SWIG_NewPointerObj(new attribute_value_derived, SWIGTYPE_p_attribute_value_derived, SWIG_POINTER_OWN);
                    } else {
                        Py_INCREF(Py_None);
                        return static_cast<PyObject*>(Py_None);
                    }
                } else if constexpr (std::is_same_v<U, empty_aggregate_t> || std::is_same_v<U, empty_aggregate_of_aggregate_t> || std::is_same_v<U, Blank>) {
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
		auto inst = self->readInstance();
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
					using T = std::decay_t<decltype(t)>;
					PyObject* attribute_val_py;
					if constexpr (std::is_same_v<T, express::Base>) {
						attribute_val_py = simply_type_to_dictionary(t);
					} else {
                        using U = std::decay_t<decltype(t)>;

                        if constexpr (is_std_vector_v<U>) {
                            attribute_val_py = pythonize_vector(t);
                        } else if constexpr (std::is_same_v<U, EnumerationReference>) {
                            attribute_val_py = pythonize(std::string(t.value()));
                        } else if constexpr (std::is_same_v<U, Derived>) {
                            if (feature_use_attribute_value_derived) {
                                attribute_val_py = SWIG_NewPointerObj(new attribute_value_derived, SWIGTYPE_p_attribute_value_derived, SWIG_POINTER_OWN);
                            } else {
                                Py_INCREF(Py_None);
                                attribute_val_py = static_cast<PyObject*>(Py_None);
                            }
                        } else if constexpr (std::is_same_v<U, empty_aggregate_t> || std::is_same_v<U, empty_aggregate_of_aggregate_t> || std::is_same_v<U, Blank>) {
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
					using T = std::decay_t<decltype(v)>;
					
					if constexpr (std::is_same_v<T, IfcParse::reference_or_simple_type>) {
						if (auto* inst = std::get_if<express::Base>(&v)) {
							// So this never happens?
						} else if (auto* name = std::get_if<IfcParse::InstanceReference>(&v)) {
							attribute_val_py = instance_reference_to_dict(*name);
						}
					} else if constexpr (std::is_same_v<T, std::vector<IfcParse::reference_or_simple_type>>) {
						attribute_val_py = PyTuple_New(v.size());
						size_t idx = 0;
						for (auto const& inner : v) {
							if (auto* inst = std::get_if<express::Base>(&inner)) {
								PyTuple_SetItem(attribute_val_py, idx++, simply_type_to_dictionary(*inst));
							} else if (auto* name = std::get_if<IfcParse::InstanceReference>(&inner)) {
								PyTuple_SetItem(attribute_val_py, idx++, instance_reference_to_dict(*name));
							}
						}
					} else if constexpr (std::is_same_v<T, std::vector<std::vector<IfcParse::reference_or_simple_type>>>) {
						attribute_val_py = PyTuple_New(v.size());
						size_t outer_idx = 0;
						for (auto const& inner : v) {
							PyObject* inner_py = PyTuple_New(inner.size());
							size_t idx = 0;
							for (auto const& innermost : inner) {
								if (auto* inst = std::get_if<express::Base>(&innermost)) {
									PyTuple_SetItem(inner_py, idx++, simply_type_to_dictionary(*inst));
								} else if (auto* name = std::get_if<IfcParse::InstanceReference>(&innermost)) {
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
	