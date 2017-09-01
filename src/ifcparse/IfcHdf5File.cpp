#include "../ifcparse/IfcHdf5File.h"

#include <limits>
#include <H5pubconf.h>
#include <boost/lexical_cast.hpp>

#ifndef H5_HAVE_FILTER_DEFLATE
#pragma message("warning: HDF5 compression support is recommended")
#endif

class type_mapper {
public:
	type_mapper(IfcParse::IfcFile& ifc_file, H5::H5File* hdf5_file);

	H5::DataType* commit(H5::DataType* dt, const std::string& name);

	H5::DataType* operator()(const IfcParse::parameter_type* pt);
	H5::DataType* operator()(const IfcParse::select_type* pt);
	H5::CompType* operator()(const IfcParse::entity* e);
	H5::EnumType* operator()(const IfcParse::enumeration_type* en);
	
	void operator()();

	std::pair<std::string, const H5::DataType*> make_select_leaf(const IfcParse::declaration* decl);

private:
	bool padded_;
	bool referenced_;
	IfcParse::Hdf5Settings settings_;

	IfcParse::IfcFile& ifc_file_;
	H5::H5File* hdf5_file_;
	H5::Group schema_group_;
	H5::CompType* instance_reference_;
	std::vector<const H5::DataType*> default_types_;
	std::vector<std::string> default_type_names_;
	std::vector<std::string> default_cpp_type_names_;
	std::vector<H5::DataType*> declared_types_;

	std::string flatten_aggregate_name(const IfcParse::parameter_type* at) const;
};

class enumeration_reference {
private:
	size_t index_;
public:
	explicit enumeration_reference(size_t index)
		: index_(index)
	{}

	operator size_t() const {
		return index_;
	}
};

class select_item {
private:
	IfcUtil::IfcBaseClass* data_;
public:
	explicit select_item(IfcUtil::IfcBaseClass* data)
		: data_(data)
	{}

	operator IfcUtil::IfcBaseClass*() const {
		return data_;
	}
};

template <typename T> struct is_hdf5_integral { static const bool value = false; };
template <> struct is_hdf5_integral <int>     { static const bool value =  true; };
template <> struct is_hdf5_integral <bool>    { static const bool value =  true; };
template <> struct is_hdf5_integral <float>   { static const bool value =  true; };
template <> struct is_hdf5_integral <double>  { static const bool value =  true; };
template <> struct is_hdf5_integral <enumeration_reference> { static const bool value = true; };

template <typename T> struct hdf5_datatype_for{};
template <> struct hdf5_datatype_for <int>    { static const H5T_class_t value = H5T_INTEGER; };
// Booleans are enumerations in HDF5 as well!
template <> struct hdf5_datatype_for <bool>   { static const H5T_class_t value = H5T_ENUM; };
template <> struct hdf5_datatype_for <float>  { static const H5T_class_t value = H5T_FLOAT; };
template <> struct hdf5_datatype_for <double> { static const H5T_class_t value = H5T_FLOAT; };
template <> struct hdf5_datatype_for <enumeration_reference> { static const H5T_class_t value = H5T_ENUM; };

template <unsigned int T> struct uint_of_size {};
template <>               struct uint_of_size <1> { typedef  uint8_t type; };
template <>               struct uint_of_size <2> { typedef uint16_t type; };
template <>               struct uint_of_size <4> { typedef uint32_t type; };
template <>               struct uint_of_size <8> { typedef uint64_t type; };

template <unsigned int T> struct int_of_size {};
template <>               struct int_of_size <1> { typedef  int8_t type; };
template <>               struct int_of_size <2> { typedef int16_t type; };
template <>               struct int_of_size <4> { typedef int32_t type; };
template <>               struct int_of_size <8> { typedef int64_t type; };

template <unsigned int T> struct float_of_size {};
template <>               struct float_of_size <4> { typedef  float type; };
template <>               struct float_of_size <8> { typedef double type; };

template <typename T, unsigned int N> struct number_of_size {};
template <unsigned int N> struct number_of_size <int, N>    { typedef typename   int_of_size<N>::type type; };
template <unsigned int N> struct number_of_size <float, N>  { typedef typename float_of_size<N>::type type; };
template <unsigned int N> struct number_of_size <double, N> { typedef typename float_of_size<N>::type type; };

std::pair<H5T_class_t, H5T_class_t> compound_member_types_as_pair(H5::DataType& datatype) {
	if (datatype.getClass() != H5T_COMPOUND) {
		throw std::runtime_error("Expected a compound");
	}

	H5::CompType* compound = (H5::CompType*) &datatype;

	if (compound->getNmembers() != 2) {
		throw std::runtime_error("Expected a compound with two members");
	}

	return std::make_pair(
		compound->getMemberDataType(0).getClass(),
		compound->getMemberDataType(1).getClass());
}

bool is_select(H5::DataType& datatype) {
	if (datatype.getClass() != H5T_COMPOUND) {
		return false;
	}

	H5::CompType* compound = (H5::CompType*) &datatype;

	if (compound->getNmembers() < 1) {
		return false;
	}

	return compound->getMemberName(0) == "type_code";
}

void advance(void*& ptr, size_t n) {
	ptr = (uint8_t*)ptr + n;
}

template <typename T>
void write(void*& ptr, const T& t) {
	*((T*)ptr) = t;
	advance(ptr, sizeof(T));
}

template <>
void write(void*& ptr, const std::string& s) {
	// TFK: So we assume this is freed by h5 vlen reclaim?
	char* c = new char[s.size() + 1];
	strcpy(c, s.c_str());
	write(ptr, c);
}

template <typename T>
void write_number_of_size(void*& ptr, size_t n, T i) {
	void* old_ptr = ptr;
	if (std::is_floating_point<T>::value) {
		if (n == 4) {
			write(ptr, static_cast< float_of_size<4>::type > (i));
		} else if (n == 8) {
			write(ptr, static_cast< float_of_size<8>::type > (i));
		}
	} else if (std::numeric_limits<T>::is_signed) {
		if (n == 1) {
			write(ptr, static_cast< int_of_size<1>::type > (i));
		} else if (n == 2) {
			write(ptr, static_cast< int_of_size<2>::type > (i));
		} else if (n == 4) {
			write(ptr, static_cast< int_of_size<4>::type > (i));
		} else if (n == 8) {
			write(ptr, static_cast< int_of_size<8>::type > (i));
		}
	} else {
		// NB: enumeration_reference also ends up here
		if (n == 1) {
			write(ptr, static_cast< uint_of_size<1>::type > (i));
		} else if (n == 2) {
			write(ptr, static_cast< uint_of_size<2>::type > (i));
		} else if (n == 4) {
			write(ptr, static_cast< uint_of_size<4>::type > (i));
		} else if (n == 8) {
			write(ptr, static_cast< uint_of_size<8>::type > (i));
		}
	}
	if (old_ptr == ptr) {
		throw std::runtime_error("No value written");
	}
}

void write_string_of_size(void*& ptr, size_t n, const std::string& s) {
	memset(ptr, 0, n);
	memcpy(ptr, s.c_str(), s.size());
	advance(ptr, n);
}

void write_vlen_t(void*& ptr, size_t n_elements, void* vlen_data) {
	advance(ptr, HOFFSET(hvl_t, len));
	void* temp_ptr;
	write_number_of_size(temp_ptr = ptr, sizeof(size_t), n_elements);
	advance(ptr, HOFFSET(hvl_t, p));
	write(ptr, vlen_data);
}

#define CAST_AND_CALL(attr, type, fn) {IfcUtil::attr_type_to_cpp_type<type>::cpp_type v = *attr; fn(v);}
#define CHECK_CAST_AND_CALL(ty) else if (attr_->type() == ty) CAST_AND_CALL(attr_, ty, t)

class apply_attribute_visitor {
private:
	Argument* attr_;
	const IfcParse::entity::attribute* schema_attr_;
public:
	apply_attribute_visitor(Argument* attr, const IfcParse::entity::attribute* schema_attr)
		: attr_(attr)
		, schema_attr_(schema_attr)
	{}

	template <typename T>
	typename T::return_type apply(T& t) const {
		if (attr_->type() == IfcUtil::Argument_NULL) {
			t(boost::none);
		} else if (attr_->type() == IfcUtil::Argument_DERIVED) {
			throw std::runtime_error("Derived attributes should not be written to the file");
			// IfcWrite::IfcWriteArgument::Derived d;
			// t(d);
		}
		CHECK_CAST_AND_CALL(IfcUtil::Argument_INT)
		CHECK_CAST_AND_CALL(IfcUtil::Argument_BOOL)
		CHECK_CAST_AND_CALL(IfcUtil::Argument_DOUBLE)
		CHECK_CAST_AND_CALL(IfcUtil::Argument_STRING)
		else if (attr_->type() == IfcUtil::Argument_BINARY) {
			throw std::runtime_error("Binary not supported at the moment");
		}
		else if (attr_->type() == IfcUtil::Argument_ENUMERATION) {
			std::string v = *attr_;
			const std::vector<std::string>& enum_values = schema_attr_->type_of_attribute()->as_named_type()->declared_type()->as_enumeration_type()->enumeration_items();
			size_t d = std::distance(enum_values.begin(), std::find(enum_values.begin(), enum_values.end(), v));
			enumeration_reference enum_ref(d);
			t(enum_ref);
		}
		CHECK_CAST_AND_CALL(IfcUtil::Argument_ENTITY_INSTANCE)

		CHECK_CAST_AND_CALL(IfcUtil::Argument_AGGREGATE_OF_INT)
		CHECK_CAST_AND_CALL(IfcUtil::Argument_AGGREGATE_OF_BOOL)
		CHECK_CAST_AND_CALL(IfcUtil::Argument_AGGREGATE_OF_DOUBLE)
		CHECK_CAST_AND_CALL(IfcUtil::Argument_AGGREGATE_OF_STRING)
		else if (attr_->type() == IfcUtil::Argument_AGGREGATE_OF_BINARY) {
			throw std::runtime_error("Not supported currently");
		}
		else if (attr_->type() == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
			IfcUtil::attr_type_to_cpp_type<IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE>::cpp_type v = *attr_;
			std::vector<IfcUtil::IfcBaseClass*> vec(v->begin(), v->end());
			t(vec);
		}

		CHECK_CAST_AND_CALL(IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT)
		CHECK_CAST_AND_CALL(IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_BOOL)
		CHECK_CAST_AND_CALL(IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE)
		else if (attr_->type() == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
			IfcUtil::attr_type_to_cpp_type<IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE>::cpp_type v = *attr_;
			std::vector< std::vector<IfcUtil::IfcBaseClass*> > vec(v->begin(), v->end());
			t(vec);
		}

		else if (attr_->type() == IfcUtil::Argument_UNKNOWN) {
			auto aggregation = schema_attr_->type_of_attribute()->as_aggregation_type();
			if (aggregation == nullptr) {
				throw std::exception("Attribute of unknown type encountered, expected empty aggregate");
			}
			auto elem_type = aggregation->type_of_element();
			if (elem_type->as_named_type()) {
				auto entity = elem_type->as_named_type()->declared_type()->as_entity();
				if (entity == nullptr) {
					throw std::exception("Not implemented");
				}
				std::vector<IfcUtil::IfcBaseClass*> empty;
				t(empty);
			} else if (elem_type->as_simple_type()) {
				auto dt = elem_type->as_simple_type()->declared_type();
				if (dt == IfcParse::simple_type::integer_type) {
					std::vector<int> empty;
					t(empty);
				} else {
					throw std::exception("Not implemented");
				}
			} else {
				throw std::exception("Not implemented");
			}
		}		
	}
};

class sorted_instance_locator {
private:
	IfcParse::IfcFile& file_;
	std::vector< IfcSchema::Type::Enum > dataset_names_;
	std::vector< std::vector<IfcUtil::IfcBaseEntity*>* > cache_;

public:
	sorted_instance_locator(IfcParse::IfcFile& file)
		: file_(file)
	{
		std::set<IfcSchema::Type::Enum> dataset_names_temp;
		for (auto it = file_.begin(); it != file_.end(); ++it) {
			dataset_names_temp.insert(it->second->declaration().type());
		}
		dataset_names_.assign(dataset_names_temp.begin(), dataset_names_temp.end());
		std::sort(dataset_names_.begin(), dataset_names_.end());

		cache_.resize(IfcSchema::Type::UNDEFINED);
	}

	std::pair<int, int> operator()(IfcUtil::IfcBaseClass* v) {
		if (IfcSchema::Type::IsSimple(v->declaration().type())) {
			throw std::exception("Simple type not expected here");
		}

		IfcSchema::Type::Enum t = v->declaration().type();
		auto tt = std::lower_bound(dataset_names_.begin(), dataset_names_.end(), t);
		int a = std::distance(dataset_names_.begin(), tt);
		int b;

		if (cache_[t] == nullptr) {
			auto li = file_.entitiesByType(t);
			std::vector<IfcUtil::IfcBaseEntity*>* vs = cache_[t] = new std::vector<IfcUtil::IfcBaseEntity*>();
			vs->reserve(li->size());

			for (auto jt = li->begin(); jt != li->end(); ++jt) {
				if ((*jt)->declaration().type() == t) {
					vs->push_back(static_cast<IfcUtil::IfcBaseEntity*>(*jt));
				}
			}

			std::sort(vs->begin(), vs->end(), [](IfcUtil::IfcBaseEntity* i1, IfcUtil::IfcBaseEntity* i2) {
				return i1->data().id() < i2->data().id();
			});
		}

		auto it = std::lower_bound(cache_[t]->begin(), cache_[t]->end(), v);
		b = std::distance(cache_[t]->begin(), it);
		
		return std::make_pair(a, b);
	}
};

class pointer_increment_assert {
	void*& ptr_reference_;
	uint8_t* ptr_initial_;
	size_t datatype_size_;
public:
	pointer_increment_assert(void*& ptr_reference, size_t datatype_size)
		: ptr_reference_(ptr_reference)
		, ptr_initial_(static_cast<uint8_t*>(ptr_reference))
		, datatype_size_(datatype_size)
	{}

	~pointer_increment_assert() noexcept(false) {
		if (ptr_initial_ + datatype_size_ != ptr_reference_) {
			throw std::runtime_error("Incorrect amount of bytes written");
		}
	}
};

// template <typename LocatorT>
class write_visit {
private:
	bool padded_;
	bool referenced_;
	type_mapper& type_mapper_;

public:
	typedef sorted_instance_locator locator_type;

	locator_type& instance_locator_;

	write_visit(bool padded, bool referenced, locator_type& instance_locator, type_mapper& type_mapper)
		: padded_(padded)
		, referenced_(referenced)
		, instance_locator_(instance_locator)
		, type_mapper_(type_mapper)
	{}

	template <typename T, typename std::enable_if<is_hdf5_integral<T>::value, T>::type* = nullptr>
	void visit(void*& ptr, H5::DataType& datatype, T& v) {
		if (datatype.getClass() != hdf5_datatype_for<T>::value) {
			throw std::runtime_error("Datatype and value do not match");
		}
		write_number_of_size(ptr, datatype.getSize(), v);
	}

	void visit(void*& ptr, H5::DataType& datatype, const boost::none_t&) {
		// TODO: Do we need to do sth based on datatype here, eg. allocate vlen/char* if necessary?
		memset(ptr, 0, datatype.getSize());
		advance(ptr, datatype.getSize());
	}
	
	// template <>
	void visit(void*& ptr, H5::DataType& datatype, std::string& v) {
		pointer_increment_assert _(ptr, datatype.getSize());
		if (padded_) {
			if (compound_member_types_as_pair(datatype) != std::make_pair(H5T_INTEGER, H5T_STRING)) {
				throw std::runtime_error("Datatype and value do not match");
			}

			H5::CompType* compound = (H5::CompType*) &datatype;
			H5::IntType int_type = compound->getMemberIntType(0);
			H5::StrType string_type = compound->getMemberStrType(1);

			if (string_type.getSize() < v.size()) {
				throw std::runtime_error("Not enough space reserved for string");
			}

			write_number_of_size(ptr, int_type.getSize(), v.size());
			write_string_of_size(ptr, string_type.getSize(), v);
		} else {
			if (datatype.getClass() != H5T_STRING) {
				throw std::runtime_error("Datatype and value do not match");
			}

			H5::StrType* string_type = (H5::StrType*) &datatype;

			// TFK: Check whether this does not leak resources
			if (*string_type == H5::StrType(H5::PredType::C_S1, H5T_VARIABLE)) {
				write(ptr, v);
			} else {
				if (string_type->getSize() < v.size()) {
					throw std::runtime_error("Not enough space reserved for string");
				}
				write_string_of_size(ptr, string_type->getSize(), v);
			}
		}		
	}

	void visit(void*& ptr, H5::DataType& datatype, select_item& v);

	void visit(void*& ptr, H5::DataType& datatype, IfcUtil::IfcBaseClass*& v) {
		
		// This does not seem to help
		// if (datatype.committed()) {
		//	std::cout << datatype.getObjName();
		// }

		if (is_select(datatype)) {
			select_item si(v);
			return visit(ptr, datatype, si);
		}

		pointer_increment_assert _(ptr, datatype.getSize());

		if (referenced_) {
			if (datatype.getClass() != H5T_REFERENCE) {
				throw std::runtime_error("Datatype and value do not match");
			}
		} else {
			if (datatype.getClass() != H5T_COMPOUND) {
				throw std::runtime_error("Datatype and value do not match");
			}

			if (compound_member_types_as_pair(datatype) != std::make_pair(H5T_INTEGER, H5T_INTEGER)) {
				throw std::runtime_error("Datatype and value do not match");
			}

			H5::CompType* compound = (H5::CompType*) &datatype;
			H5::IntType ds_idx = compound->getMemberIntType(0);
			H5::IntType ds_row = compound->getMemberIntType(1);

			std::pair<int, int> ref = instance_locator_(v);

			write_number_of_size(ptr, ds_idx.getSize(), ref.first);
			write_number_of_size(ptr, ds_row.getSize(), ref.second);
		}
	}

	template <typename T>
	void visit(void*& ptr, H5::DataType& datatype, std::vector<T>& v) {
		pointer_increment_assert _(ptr, datatype.getSize());
		if (padded_) {
			if (datatype.getClass() != H5T_COMPOUND) {
				throw std::runtime_error("Datatype and value do not match");
			}

			if (compound_member_types_as_pair(datatype) != std::make_pair(H5T_INTEGER, H5T_ARRAY)) {
				throw std::runtime_error("Datatype and value do not match");
			}

			H5::CompType* compound = (H5::CompType*) &datatype;
			H5::IntType size_dt = compound->getMemberIntType(0);
			H5::ArrayType array_dt = compound->getMemberArrayType(1);

			write_number_of_size(ptr, size_dt.getSize(), v.size());
			
			// TFK: Enable multi-dimensional arrays for LISTS of LISTS as well.
			if (array_dt.getArrayNDims() != 1) {
				throw std::runtime_error("Unexpected array dimensions");
			}

			hsize_t n;
			array_dt.getArrayDims(&n);
			H5::DataType elem_dt = array_dt.getSuper();

			for (size_t i = 0; i < n; ++i) {
				if (i < v.size()) {
					// I only get this to work if I make a copy.
					// cannot convert from 'std::_Vb_reference<std::_Wrap_alloc<std::allocator<_Other>>>' to 'const boost::none_t' :(
					T t = v[i];
					visit(ptr, elem_dt, t);
				} else {
					// TODO: Figure this out.
					// visit(ptr, elem_dt, T());
				}
			}
		} else {
			if (datatype.getClass() != H5T_VLEN) {
				throw std::runtime_error("Datatype and value do not match");
			}

			H5::VarLenType* vlen = (H5::VarLenType*) &datatype;
			H5::DataType elem_dt = vlen->getSuper();

			void* vlen_data = new uint8_t[elem_dt.getSize() * v.size()];
			void* temp = vlen_data;
			for (size_t i = 0; i < v.size(); ++i) {
				T t = v[i];
				visit(temp, elem_dt, t);
			}
			
			write_vlen_t(ptr, v.size(), vlen_data);
		}
	}

};

// template <typename LocatorT>
class write_visit_instance_attribute {
private:
	void*& ptr_;
	write_visit& fn_;
	H5::DataType& dt_;

public:
	typedef void return_type;

	write_visit_instance_attribute(void*& ptr, write_visit& fn, H5::DataType& dt)
		: ptr_(ptr)
		, fn_(fn)
		, dt_(dt)
	{}

	template <typename T>
	void operator()(T& t) {
		fn_.visit(ptr_, dt_, t);
	}
};

static const std::string Entity_Instance_Identifier = "Entity-Instance-Identifier";
static const std::string set_unset_bitmap = "set_unset_bitmap";

template <typename T>
void IfcParse::IfcHdf5File::write_instance(void*& ptr, T& visitor, H5::DataType& datatype, IfcUtil::IfcBaseEntity* v) {
	pointer_increment_assert _(ptr, datatype.getSize());

	if (datatype.getClass() != H5T_COMPOUND) {
		throw std::runtime_error("Datatype and value do not match");
	}

	H5::CompType* compound = (H5::CompType*) &datatype;

	auto attributes = v->declaration().all_attributes();
	// TFK: Creating copies
	// TFK: Do this once for every entity
	std::vector<std::string> attribute_names;
	attribute_names.reserve(attributes.size());

	std::transform(attributes.begin(), attributes.end(),
		std::back_inserter(attribute_names),
		[](const IfcParse::entity::attribute* attr) {
		return attr->name();
	});

	void* set_unset_bitmap_location = 0;
	uint32_t set_unset_bitmap_value = 0;
	size_t set_unset_bitmap_size = 0;

	for (int i = 0; i < compound->getNmembers(); ++i) {
		const std::string name = compound->getMemberName(i);
		H5::DataType attr_type = compound->getMemberDataType(i);

		if (name == Entity_Instance_Identifier) {
			write_number_of_size(ptr, attr_type.getSize(), v->data().id());
			continue;
		} else if (name == set_unset_bitmap) {
			set_unset_bitmap_location = ptr;
			set_unset_bitmap_size = attr_type.getSize();
			advance(ptr, set_unset_bitmap_size);
			continue;
		}

		auto it = std::find(attribute_names.begin(), attribute_names.end(), name);
		if (it == attribute_names.end()) {
			throw std::runtime_error("Unexpected compound member");
		}
		int idx = std::distance(attribute_names.begin(), it);
		
		Argument* attr = v->data().getArgument(idx);
		if (!attr->isNull()) {
			// TODO: This is now index in IFC-attributes list, specify
			set_unset_bitmap_value |= (1 << idx);
		}
		write_visit_instance_attribute/*<typename T::locator_type>*/ attribute_visitor(ptr, visitor, attr_type);
		apply_attribute_visitor(attr, attributes[idx]).apply(attribute_visitor);
	}

	if (set_unset_bitmap_size && set_unset_bitmap_location) {
		write_number_of_size(set_unset_bitmap_location, set_unset_bitmap_size, set_unset_bitmap_value);
	}
}

class default_value_visitor {
private:
	H5::DataType& datatype_;

public:
	default_value_visitor(H5::DataType& datatype)
		: datatype_(datatype)
	{}

	void operator()(void*& ptr) {
		switch (datatype_.getClass()) {
		case H5T_INTEGER:
			write_number_of_size(ptr, datatype_.getSize(), 0);
			break;
		case H5T_FLOAT:
			write_number_of_size(ptr, datatype_.getSize(), 0.);
			break;
		case H5T_STRING:
			if (datatype_ == H5::StrType(H5::PredType::C_S1, H5T_VARIABLE)) {
				write(ptr, new char(0));
			} else {
				write_string_of_size(ptr, datatype_.getSize(), "");
			}
			break;
		case H5T_COMPOUND:
		{
			H5::CompType* compound = (H5::CompType*) &datatype_;
			for (int i = 0; i < compound->getNmembers(); ++i) {
				H5::DataType attr_type = compound->getMemberDataType(i);
				default_value_visitor visitor(attr_type);
				visitor(ptr);
			}
			break;
		}			
		case H5T_REFERENCE:
			throw std::runtime_error("Not implemented");
			break;
		case H5T_ENUM:
			write_number_of_size(ptr, datatype_.getSize(), 0);
			break;
		case H5T_VLEN:
		{
			// H5::VarLenType* vlen = (H5::VarLenType*) &datatype_;
			// Does this work?
			write_vlen_t(ptr, 0, nullptr);
			break;
		}
		case H5T_ARRAY:
		{
			H5::ArrayType* arr = (H5::ArrayType*) &datatype_;
			size_t ndims = arr->getArrayNDims();
			hsize_t* array_dims = new hsize_t[ndims];
			arr->getArrayDims(array_dims);
			if (ndims != 1) {
				throw std::runtime_error("Not implemented");
			}
			H5::DataType super = arr->getSuper();
			default_value_visitor visitor(super);
			for (hsize_t i = 0; i < array_dims[0]; ++i) {
				visitor(ptr);
			}
			break;
		}
		default:
			throw std::runtime_error("Unexpected type encountered");
		}
	}
};

void write_visit::visit(void*& ptr, H5::DataType& datatype, select_item& v) {
	pointer_increment_assert _(ptr, datatype.getSize());

	IfcUtil::IfcBaseClass* data = v;

	H5::CompType* compound = (H5::CompType*) &datatype;
	const bool data_is_entity = !!data->declaration().as_entity();

	for (int i = 0; i < compound->getNmembers(); ++i) {
		const std::string name = compound->getMemberName(i);
		H5::DataType attr_type = compound->getMemberDataType(i);

		if (name == "type_code") {
			write_number_of_size(ptr, attr_type.getSize(), data->declaration().type());
		} else if (data_is_entity && name == "instance-value") {
			visit(ptr, attr_type, data);
		} else if (type_mapper_.make_select_leaf(&data->declaration()).first == name) {
			write_visit_instance_attribute/*<typename T::locator_type>*/ attribute_visitor(ptr, *this, attr_type);
			apply_attribute_visitor(data->data().getArgument(0), 0).apply(attribute_visitor);
		} else {
			default_value_visitor visitor(attr_type);
			visitor(ptr);
		}
	}
}

H5::CompType* create_compound(const std::vector< IfcParse::IfcHdf5File::compound_member >& members) {
	size_t s = 0, o = 0;
	for (auto it = members.begin(); it != members.end(); ++it) {
		s += it->second->getSize();
	}

	H5::CompType* h5_dt = new H5::CompType(s);
	for (auto it = members.begin(); it != members.end(); ++it) {
		h5_dt->insertMember(it->first, o, *it->second);
		o += it->second->getSize();
	}

	return h5_dt;
}

H5::EnumType* create_enumeration(const std::vector<std::string>& items, int offset = 0) {
	size_t numbytes = 0;
	size_t size = items.size();
	while (size != 0) {
		size >>= 8;
		numbytes++;
	}

	int i = offset;
	H5::EnumType* h5_enum = new H5::EnumType(numbytes);
	for (auto it = items.begin(); it != items.end(); ++it, ++i) {
		h5_enum->insert(it->c_str(), &i);
	}

	return h5_enum;
}

void visit_select(const IfcParse::select_type* pt, std::set<const IfcParse::declaration*>& leafs) {
	for (auto it = pt->select_list().begin(); it != pt->select_list().end(); ++it) {
		if ((*it)->as_select_type()) {
			visit_select((*it)->as_select_type(), leafs);
		} else {
			leafs.insert(*it);
		}
	}
}

class UnmetDependencyException : public std::exception {};

std::string type_mapper::flatten_aggregate_name(const IfcParse::parameter_type* at) const {
	if (at->as_aggregation_type()) {
		return std::string("aggregate-of-") + flatten_aggregate_name(at->as_aggregation_type()->type_of_element());
	} else if (at->as_simple_type()) {
		return default_type_names_[at->as_simple_type()->declared_type()];
	} else if (at->as_named_type()) {
		// TODO: Unwind type name
		return at->as_named_type()->declared_type()->name();
	} else {
		throw;
	}
}

type_mapper::type_mapper(IfcParse::IfcFile& ifc_file, H5::H5File* hdf5_file)
	: ifc_file_(ifc_file)
	, hdf5_file_(hdf5_file)
	// TODO: Configure
	, padded_(false)
	, referenced_(false)
{
	schema_group_ = hdf5_file_->openGroup(ifc_file_.schema()->name() + "_encoding");

	default_types_.resize(IfcParse::simple_type::datatype_COUNT);
	default_type_names_.resize(IfcParse::simple_type::datatype_COUNT);
	default_cpp_type_names_.resize(IfcUtil::Argument_UNKNOWN);
	declared_types_.resize(IfcSchema::Type::UNDEFINED);

	{
		std::vector< IfcParse::IfcHdf5File::compound_member > members;
		members.push_back(std::make_pair(std::string("_HDF5_dataset_index_"), new H5::PredType(H5::PredType::NATIVE_INT16)));
		members.push_back(std::make_pair(std::string("_HDF5_instance_index_"), new H5::PredType(H5::PredType::NATIVE_INT32)));
		instance_reference_ = static_cast<H5::CompType*>(commit(create_compound(members), "_HDF_INSTANCE_REFERENCE_HANDLE_"));
	}

	{
		std::vector<std::string> names;
		names.push_back("BOOLEAN-FALSE");
		names.push_back("BOOLEAN-TRUE");
		default_types_[IfcParse::simple_type::boolean_type] = create_enumeration(names);
	}

	{
		std::vector<std::string> names;
		names.push_back("LOGICAL-UNKNOWN");
		names.push_back("LOGICAL-FALSE");
		names.push_back("LOGICAL-TRUE");
		default_types_[IfcParse::simple_type::logical_type] = create_enumeration(names, -1);
	}

	default_types_[IfcParse::simple_type::binary_type] = &H5::PredType::NATIVE_OPAQUE; // vlen?
	default_types_[IfcParse::simple_type::real_type] = &H5::PredType::NATIVE_DOUBLE;
	default_types_[IfcParse::simple_type::number_type] = &H5::PredType::NATIVE_DOUBLE;
	default_types_[IfcParse::simple_type::string_type] = new H5::StrType(H5::PredType::C_S1, H5T_VARIABLE);
	default_types_[IfcParse::simple_type::integer_type] = &H5::PredType::NATIVE_INT;

	default_type_names_[IfcParse::simple_type::logical_type] = "logical";
	default_type_names_[IfcParse::simple_type::boolean_type] = "boolean";
	default_type_names_[IfcParse::simple_type::binary_type] = "binary";
	default_type_names_[IfcParse::simple_type::real_type] = "real";
	default_type_names_[IfcParse::simple_type::number_type] = "number";
	default_type_names_[IfcParse::simple_type::string_type] = "string";
	default_type_names_[IfcParse::simple_type::integer_type] = "integer";

	default_cpp_type_names_[IfcUtil::Argument_BOOL] = "boolean";
	default_cpp_type_names_[IfcUtil::Argument_DOUBLE] = "real";
	default_cpp_type_names_[IfcUtil::Argument_STRING] = "string";
	default_cpp_type_names_[IfcUtil::Argument_INT] = "integer";
}

H5::DataType* type_mapper::commit(H5::DataType* dt, const std::string& name) {
	dt->commit(schema_group_, name);
	return dt;
}

H5::DataType* type_mapper::operator()(const IfcParse::parameter_type* pt) {
	H5::DataType* h5_dt;
	if (pt->as_aggregation_type()) {
		if (padded_) {
			// TODO: Determine dimensions
			// TODO: Check whether these pointers can safely be dereferenced
			hsize_t dims = 1;
			h5_dt = new H5::ArrayType(*(*this)(pt->as_aggregation_type()->type_of_element()), 1, &dims);
		} else {
			h5_dt = new H5::VarLenType((*this)(pt->as_aggregation_type()->type_of_element()));
		}
	} else if (pt->as_named_type()) {
		if (pt->as_named_type()->declared_type()->as_entity()) {
			return instance_reference_;
			// TFK: Do not copy, we want to retain path to simplify datatype identify checks later on
			// h5_dt = new H5::DataType();
			// h5_dt->copy(*instance_reference_);
		} else {
			IfcSchema::Type::Enum ty = pt->as_named_type()->declared_type()->type();
			if (!declared_types_[ty]) {
				throw UnmetDependencyException();
			} else {
				// TFK: Copy, as well be committed under different name?
				h5_dt = new H5::DataType();
				h5_dt->copy(*declared_types_[ty]);
			}
		}
	} else if (pt->as_simple_type()) {
		const H5::DataType* orig = default_types_[pt->as_simple_type()->declared_type()];
		h5_dt = new H5::DataType();
		h5_dt->copy(*orig);
	} else {
		throw UnmetDependencyException();
	}

	return h5_dt;
}

std::pair<std::string, const H5::DataType*> type_mapper::make_select_leaf(const IfcParse::declaration* decl) {
	std::string name;
	const H5::DataType* dt = 0;

	if (decl) {
		while (decl->as_type_declaration()) {
			const IfcParse::parameter_type* leaf_pt = decl->as_type_declaration()->declared_type();
			const IfcParse::named_type* nt = leaf_pt->as_named_type();
			const IfcParse::simple_type* st = leaf_pt->as_simple_type();
			const IfcParse::aggregation_type* at = leaf_pt->as_aggregation_type();
			if (nt) {
				decl = nt->declared_type();
			} else if (st) {
				name = default_type_names_[st->declared_type()];
				dt = default_types_[st->declared_type()];
				break;
			} else if (at) {
				name = flatten_aggregate_name(at);
				dt = (*this)(at);
				break;
			}
		}
	}

	if (!dt) {
		if (decl->as_entity()) {
			name = "instance";
			dt = instance_reference_;
		} else if (decl->as_enumeration_type()) {
			name = decl->name();
			dt = declared_types_[decl->type()];
		} else {
			throw;
		}
	}

	name += "-value";

	return std::make_pair(name, dt);
}

H5::DataType* type_mapper::operator()(const IfcParse::select_type* pt) {
	std::set<const IfcParse::declaration*> leafs;
	visit_select(pt, leafs);

	bool all_entity_instance_refs = true;
	for (auto it = leafs.begin(); it != leafs.end(); ++it) {
		if (!(*it)->as_entity()) {
			all_entity_instance_refs = false;
			break;
		}
	}

	if (all_entity_instance_refs) {
		return 0;
	} else {
		std::set<std::string> member_names;
		std::vector<IfcParse::IfcHdf5File::compound_member> h5_attributes;

		h5_attributes.push_back(std::make_pair(std::string("type_code"), &H5::PredType::NATIVE_INT16));

		for (auto it = leafs.begin(); it != leafs.end(); ++it) {
			const IfcParse::declaration* decl = (*it);
			auto leaf_type = make_select_leaf(decl);

			if (member_names.find(leaf_type.first) != member_names.end()) {
				continue;
			}
			member_names.insert(leaf_type.first);

			h5_attributes.push_back(leaf_type);
		}

		return create_compound(h5_attributes);
	}
}

H5::CompType* type_mapper::operator()(const IfcParse::entity* e) {

	// List of entity instances of this type, no subtypes
	IfcEntityList::ptr incl_subtypes = ifc_file_.entitiesByType(e->name());
	IfcEntityList::ptr instances(new IfcEntityList);
	if (incl_subtypes) {
		for (auto it = incl_subtypes->begin(); it != incl_subtypes->end(); ++it) {
			if ((**it).declaration().type() == e->type()) {
				instances->push(*it);
			}
		}
	}

	if (instances->size() == 0) {
		return 0;
	}

	std::vector<const IfcParse::entity::attribute*> attributes = e->all_attributes();
	std::vector<const IfcParse::entity::inverse_attribute*> inverse_attributes;
	if (settings_.instantiate_inverse()) {
		inverse_attributes = e->all_inverse_attributes();
	}

	const std::vector<bool>& attributes_derived_in_subtype = e->derived();

	bool has_optional_attributes = false;
	const size_t num_extra = has_optional_attributes ? 2 : 1;
	// size_t num_all_null = 0;
	std::vector<bool> attributes_all_null(attributes.size(), false);

	auto jt = attributes_derived_in_subtype.begin();
	for (auto it = attributes.begin(); it != attributes.end(); ++it, ++jt) {
		if (*jt) {
			continue;
		}
		if ((**it).optional()) {
			const int idx = std::distance(attributes.begin(), it);

			has_optional_attributes = true;

			/*
			apply_attribute_visitor_instance_list dispatch(instances, idx);
			all_null_visitor visitor;
			dispatch.apply(visitor);
			if (visitor.all_null()) {
				num_all_null += 1;
				attributes_all_null[idx] = true;
				attributes_omitted.insert(std::make_pair(e->name(), idx));
			}
			*/
		}
	}

	/*
	if (has_optional_attributes) {
		entities_with_optional_attrs.insert(e->name());
	}
	*/

	std::vector< IfcParse::IfcHdf5File::compound_member > h5_attributes;
	h5_attributes.reserve(attributes.size() + inverse_attributes.size() + num_extra);

	if (has_optional_attributes) {
		h5_attributes.push_back(std::make_pair(std::string("set_unset_bitmap"), &H5::PredType::NATIVE_INT16));
	}
	h5_attributes.push_back(std::make_pair(std::string("Entity-Instance-Identifier"), &H5::PredType::NATIVE_INT32));

	jt = attributes_derived_in_subtype.begin();
	for (auto it = attributes.begin(); it != attributes.end(); ++it, ++jt) {
		if (*jt) {
			continue;
		}

		const int idx = std::distance(attributes.begin(), it);

		if (attributes_all_null[idx]) {
			continue;
		}

		const std::string& name = (*it)->name();
		if (name == "InnerCurves") {
			std::cerr << 1;
		}
		const bool is_optional = (*it)->optional();
		const H5::DataType* type;
		const std::string qualified_attr_name = e->name() + "." + name;
		if (std::binary_search(settings_.ref_attributes().begin(), settings_.ref_attributes().end(), qualified_attr_name)) {
			type = new H5::PredType(H5::PredType::STD_REF_OBJ);
		// } else if (overridden_types.find(qualified_attr_name) != overridden_types.end()) {
		// 	type = overridden_types.find(qualified_attr_name)->second;
		// } else if (overridden_types.find("*." + name) != overridden_types.end()) {
		// 	type = overridden_types.find("*." + name)->second;
		} else {
			type = (*this)((*it)->type_of_attribute());
		}

		/*
		apply_attribute_visitor_instance_list dispatch(instances, idx);
		max_length_visitor visitor;
		dispatch.apply(visitor);
		if (visitor) {
			type = specify_length(type, visitor.max_length());
		}
		*/

		// TODO: Re-evaluate
		// if (false && visitor && visitor.max_length()[0] == 0) {
		//	attributes_omitted.insert(std::make_pair(e->name(), idx));
		// } else {
			h5_attributes.push_back(std::make_pair(name, type));
		// }
	}

	if (settings_.instantiate_inverse()) {
		for (auto it = inverse_attributes.begin(); it != inverse_attributes.end(); ++it) {
			const std::string& name = (*it)->name();
			// H5::DataType* ir_copy = new H5::DataType();
			// ir_copy->copy(*instance_reference_);
			const H5::DataType* type = new H5::VarLenType(instance_reference_);
			h5_attributes.push_back(std::make_pair(name, type));
		}
	}

	return create_compound(h5_attributes);
}

H5::EnumType* type_mapper::operator()(const IfcParse::enumeration_type* en) {
	return create_enumeration(en->enumeration_items());
}

void type_mapper::operator()() {
	const IfcParse::schema_definition& schema = *ifc_file_.schema();

	for (auto it = schema.enumeration_types().begin(); it != schema.enumeration_types().end(); ++it) {
		declared_types_[(*it)->type()] = commit((*this)(*it), (*it)->name());
	}

	const std::vector<const IfcParse::type_declaration*>& ts = schema.type_declarations();
	std::set<const IfcParse::type_declaration*> processed;
	while (processed.size() < ts.size()) {
		for (auto it = ts.begin(); it != ts.end(); ++it) {
			auto pt = (*it)->declared_type();
			const std::string& name = (*it)->name();
			if (processed.find(*it) != processed.end()) continue;
			try {
				declared_types_[(*it)->type()] = commit((*this)(pt), name);
				processed.insert(*it);
			} catch (const UnmetDependencyException&) {}
		}
	}

	for (auto it = schema.select_types().begin(); it != schema.select_types().end(); ++it) {
		H5::DataType* dt = (*this)(*it);
		if (dt) {
			declared_types_[(*it)->type()] = commit(dt, (*it)->name());
		} else {
			declared_types_[(*it)->type()] = instance_reference_;
		}
	}

	for (auto it = schema.entities().begin(); it != schema.entities().end(); ++it) {
		auto dt = (*this)(*it);
		if (dt) {
			declared_types_[(*it)->type()] = commit(dt, (*it)->name());
		}
	}

	H5::StrType schema_name_t;
	schema_name_t.copy(H5::PredType::C_S1);
	schema_name_t.setSize(schema.name().size());

	hsize_t schema_name_length = 1;
	H5::DataSpace schema_name_s(1, &schema_name_length);

	H5::Attribute attr = schema_group_.createAttribute("iso_10303_26_data", schema_name_t, schema_name_s);
	attr.write(schema_name_t, schema.name());
	attr.close();
}

void visit(void* buffer, H5::DataType* dt) {
	if (dt->getClass() == H5T_COMPOUND) {
		H5::CompType* ct = (H5::CompType*) dt;
		for (int i = 0; i < ct->getNmembers(); ++i) {
			std::cerr << ct->getMemberName(i) << " ";
			size_t offs = ct->getMemberOffset(i);
			H5::DataType dt2 = ct->getMemberDataType(i);
			visit((uint8_t*)buffer + offs, &dt2);
			dt2.close();
		}
	} else if (dt->getClass() == H5T_VLEN) {
		hvl_t* ht = (hvl_t*)buffer;
		H5::VarLenType* vt = (H5::VarLenType*) dt;
		H5::DataType dt2 = vt->getSuper();
		for (size_t i = 0; i < ht->len; ++i) {
			std::cerr << i << " ";
			visit((uint8_t*)ht->p + i * vt->getSize(), &dt2);
		}
		dt2.close();
	} else if (dt->getClass() == H5T_STRING) {
		char* c = *(char**)buffer;
		std::cerr << "'" << c << "'" << " ";
	}
}

/*
const H5::DataType* IfcParse::IfcHdf5File::specify_length(const H5::DataType* dt, const size_t * n) {
	const hsize_t N = *n;

	H5::DataType* dt3 = 0;
	if (dt->getClass() == H5T_VLEN) {
		H5::VarLenType* vt = (H5::VarLenType*) dt;
		H5::DataType dt2 = vt->getSuper();
		if (dt2.getClass() == H5T_VLEN) {
			throw IfcParse::IfcException("Not supported");
		}

		if (dt2.getClass() == H5T_STRING) {
			dt2.close();
			dt2 = H5::StrType(H5::PredType::C_S1, n[1] + 1);
		}

		dt3 = new H5::ArrayType(dt2, 1, &N);

		if (dt2.getClass() != H5T_STRING) {
			dt2.close();
		}
	} else if (dt->getClass() == H5T_STRING) {
		// + 1? 0-sized strings not allowed.
		dt3 = new H5::StrType(H5::PredType::C_S1, *n + 1);
	}

	if (dt3) {
		if (dt->committed()) {
			std::string nm = dt->getObjName() + "_" + boost::lexical_cast<std::string>(*n);
			dt3->commit(schema_group, nm);
		}
		return dt3;
	} else {
		return dt;
	}
}
*/

size_t get_alignment() {
	return 0;
}

H5::EnumType* map_enumeration(const IfcParse::enumeration_type* en) {
	return create_enumeration(en->enumeration_items());
}

H5::DataType* IfcParse::IfcHdf5File::commit(H5::DataType* dt, const std::string& name) {
	dt->commit(schema_group, name);
	return dt;
}

class all_null_visitor {
private:
	bool all_null_;
public:
	typedef void return_type;

	all_null_visitor()
		: all_null_(true)
	{}

	void operator()(const boost::none_t&) {
		// Empty on purpose
	}

	template <typename T>
	void operator()(const T& other) {
		all_null_ = false;
	}

	bool all_null() const {
		return all_null_;
	}
};

class max_length_visitor {
private:
	std::vector<size_t> max_length_;
	void contain(size_t dim, size_t count) {
		if (dim == max_length_.size()) {
			max_length_.push_back(count);
		} else if (count > max_length_[dim]) {
			max_length_[dim] = count;
		}
	}

public:
	typedef void return_type;

	void operator()(const IfcEntityList::ptr& aggregate) {
		contain(0, aggregate->size());
	}

	void operator()(const IfcEntityListList::ptr& aggregate) {
		contain(0, aggregate->size());
		for (auto it = aggregate->begin(); it != aggregate->end(); ++it) {
			contain(1, it->size());
		}
	}

	void operator()(const std::string& str) {
		contain(0, str.size());
	}

	void operator()(const std::vector<std::string>& aggregate) {
		contain(0, aggregate.size());
		for (auto it = aggregate.begin(); it != aggregate.end(); ++it) {
			contain(1, it->size());
		}
	}

	template <typename T>
	void operator()(const std::vector< std::vector<T> >& aggregate) {
		contain(0, aggregate.size());
		for (auto it = aggregate.begin(); it != aggregate.end(); ++it) {
			contain(1, it->size());
		}
	}

	template <typename T>
	void operator()(const std::vector<T>& aggregate) {
		contain(0, aggregate.size());
	}

	template <typename T>
	void operator()(const T& other) {
	}

	operator bool() const {
		return !max_length_.empty();
	}

	const size_t* max_length() const {
		return max_length_.data();
	}
};

class apply_attribute_visitor_instance_list {
private:
	const IfcEntityList::ptr& instances_;
	int attribute_idx_;
public:
	apply_attribute_visitor_instance_list(const IfcEntityList::ptr& instances, int attribute_idx)
		: instances_(instances)
		, attribute_idx_(attribute_idx)
	{}

	template <typename T>
	typename T::return_type apply(T& t) const {
		for (auto it = instances_->begin(); it != instances_->end(); ++it) {
			apply_attribute_visitor((**it).data().getArgument(attribute_idx_)).apply(t);
		}
	}
};

std::set< std::pair<std::string, int> > attributes_omitted;
std::set< std::string > entities_with_optional_attrs;

/*
template <>
void IfcParse::IfcHdf5File::write(void*& ptr, const std::string& s) const {
	char* c = new(allocator.allocate(s.size()+1)) char [s.size()+1];
	strcpy(c, s.c_str());
	write(ptr, c);
}

void IfcParse::IfcHdf5File::write_string_of_size(void*& ptr, const std::string& s, size_t n) const {
	memset(ptr, 0, n);
	memcpy(ptr, s.c_str(), s.size());
	advance(ptr, n);
}

void IfcParse::IfcHdf5File::write_vlen_t(void*& ptr, size_t n_elements, void* vlen_data) const {
	advance(ptr, HOFFSET(hvl_t, len));
	void* temp_ptr;
	write_number_of_size(temp_ptr = ptr, sizeof(size_t), n_elements);
	advance(ptr, HOFFSET(hvl_t, p));
	write(ptr, vlen_data);
}

template <typename T>
void IfcParse::IfcHdf5File::write_aggregate(void*& ptr, const T& ts) const {
	size_t elem_size = get_datatype<typename T::value_type>()->getSize();
	size_t n_elements = ts.size();
	size_t size_in_bytes = elem_size * n_elements;
	void* aggr_data = allocator.allocate(size_in_bytes);
	void* aggr_ptr = aggr_data;
	for (T::const_iterator it = ts.begin(); it != ts.end(); ++it) {
		write_number_of_size(aggr_ptr, elem_size, *it);
	}
	write_vlen_t(ptr, n_elements, aggr_data);
}

template <typename T>
void IfcParse::IfcHdf5File::write_consecutive(void*& ptr, const std::vector<T>& ts, hsize_t* num, size_t* elem_size) const {
	size_t sz = get_datatype<T>()->getSize();
	hsize_t n = 0;
	for (typename std::vector<T>::const_iterator it = ts.begin(); it != ts.end(); ++it, ++n) {
		write_number_of_size(ptr, sz, *it);
	}
	while (n++ < num[0]) {
		write_number_of_size(ptr, sz, T());
	}
}

template <>
void IfcParse::IfcHdf5File::write_consecutive(void*& ptr, const std::vector<IfcUtil::IfcBaseClass*>& ts, hsize_t* num, size_t*) const {
	hsize_t n = 0;
	for (std::vector<IfcUtil::IfcBaseClass*>::const_iterator it = ts.begin(); it != ts.end(); ++it, ++n) {
		auto ref = make_instance_reference(*it);
		write_number_of_size(ptr, 2, ref.first);
		write_number_of_size(ptr, 4, ref.second);
	}
	while (n++ < num[0]) {
		write_number_of_size(ptr, 2, 0);
		write_number_of_size(ptr, 4, 0);
	}
}

template <>
void IfcParse::IfcHdf5File::write_consecutive(void*& ptr, const std::vector<std::string>& ts, hsize_t* num, size_t* elem_size) const {
	hsize_t n = 0;
	for (std::vector<std::string>::const_iterator it = ts.begin(); it != ts.end(); ++it, ++n) {
		write_string_of_size(ptr, *it, elem_size[0]);
	}
	while (n++ < num[0]) {
		write_string_of_size(ptr, "", elem_size[0]);
	}
}

template <>
void IfcParse::IfcHdf5File::write_aggregate(void*& ptr, const std::vector<std::string>& ts) const {
	size_t elem_size = sizeof(char*);
	size_t n_elements = ts.size();
	size_t size_in_bytes = elem_size * n_elements;
	void* aggr_data = allocator.allocate(size_in_bytes);
	void* aggr_ptr = aggr_data;
	for (std::vector<std::string>::const_iterator it = ts.begin(); it != ts.end(); ++it) {
		write(aggr_ptr, *it);
	}
	write_vlen_t(ptr, n_elements, aggr_data);
}

template <>
void IfcParse::IfcHdf5File::write_aggregate(void*& ptr, const IfcEntityList::ptr& ts) const {
	size_t elem_size = instance_reference->getSize();
	size_t n_elements = ts->size();
	size_t size_in_bytes = elem_size * n_elements;
	void* aggr_data = allocator.allocate(size_in_bytes);
	void* aggr_ptr = aggr_data;
	for (IfcEntityList::it it = ts->begin(); it != ts->end(); ++it) {
		auto ref = make_instance_reference(*it);
		// write_number_of_size(aggr_ptr, instance_reference->getMemberDataType(0).getSize(), ref.first);
		// write_number_of_size(aggr_ptr, instance_reference->getMemberDataType(1).getSize(), ref.second);
		// Hard-coded for efficiency
		write_number_of_size(aggr_ptr, 2, ref.first);
		write_number_of_size(aggr_ptr, 4, ref.second);
	}
	write_vlen_t(ptr, n_elements, aggr_data);
}

template <typename T>
void IfcParse::IfcHdf5File::write_aggregate2(void*& ptr, const std::vector< std::vector<T> >& ts) const {
	size_t elem_size = sizeof(hvl_t);
	size_t n_elements = ts.size();
	size_t size_in_bytes = elem_size * n_elements;
	void* aggr_data = allocator.allocate(size_in_bytes);
	void* aggr_ptr = aggr_data;
	for (std::vector< std::vector<T> >::const_iterator it = ts.begin(); it != ts.end(); ++it) {
		write_aggregate(aggr_ptr, *it);
	}
	write_vlen_t(ptr, n_elements, aggr_data);
}

template <typename T>
void IfcParse::IfcHdf5File::write_reference_attribute(void*& ptr, const std::string& dsn, const std::vector<T>& vs) {
	const std::string dsn_path = "/population/" + dsn;
	const hsize_t s = vs.size();
	const H5::DataType& dt = *get_datatype<T>();
	const size_t size_in_bytes = dt.getSize() * vs.size();

	H5::DataSpace space(1, &s);
	
	void* buffer = allocator.allocate(size_in_bytes);
	void* ds_ptr = buffer;
	for (auto it = vs.begin(); it != vs.end(); ++it) {
		write_number_of_size(ds_ptr, dt.getSize(), *it);
	}

	// TODO: Refactor
	hsize_t chunk;
	if (settings_.chunk_size() > 0 && settings_.chunk_size() < s) {
		chunk = static_cast<hsize_t>(settings_.chunk_size());
	} else {
		chunk = s;
	}

	const H5::DSetCreatPropList* plist;
	// H5O_MESG_MAX_SIZE = 65536
	const bool compact = size_in_bytes < (1 << 15);
	if (settings_.compress() && !compact) { 
		H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
		plist_->setChunk(1, &chunk);
		// D'oh. Order is significant, according to h5ex_d_shuffle.c
		plist_->setShuffle();
		plist_->setDeflate(9);
		plist = plist_;
	} else if (compact) {
		H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
		// Set compact according to h5ex_d_compact.c
		plist_->setLayout(H5D_COMPACT);
		plist = plist_;
	} else if (chunk != s){
		H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
		plist_->setChunk(1, &chunk);
		plist = plist_;
	} else {
		plist = &H5::DSetCreatPropList::DEFAULT;
	}
	
	H5::DataSet ds = population_group.createDataSet(dsn, dt, space, *plist);
	ds.write(buffer, dt);
	space.close();

	ds.reference(ptr, dsn_path.c_str());
	advance(ptr, sizeof(hobj_ref_t));

	if (plist != &H5::DSetCreatPropList::DEFAULT) {
		// ->close() doesn't work due to const, hack hack hack
		H5Pclose(plist->getId());
	}
	
	delete[] buffer;
	ds.close();
}

template <typename T>
void IfcParse::IfcHdf5File::write_reference_attribute2(void*& ptr, const std::string& dsn, const std::vector< std::vector<T> >& vs) {
	
	// See if the attribute is a 'jagged' array in which case a single row of
	// vlens is written. Otherwise a two dimensional dataset is created.
	bool is_rectangular = true;
	size_t w = 0;
	for (auto it = vs.begin(); it != vs.end(); ++it) {
		if (it == vs.begin()) {
			w = it->size();
		} else {
			if (w != it->size()) {
				is_rectangular = false;
				break;
			}
		}
	}
	
	// TODO: Please use smart pointers next time
	hsize_t* s;
	hsize_t* chunk;
	const H5::DataType* dt;
	H5::DataType* dt2;
	bool scaled_type = false;
	
	if (is_rectangular) {
		s = new hsize_t[2];
		s[0] = vs.size();
		s[1] = w;

		// Try to find the narrowest integer that can represent values in the dataset
		dt = dt2 = 0;
		if (std::numeric_limits<T>::is_integer) {
			T min_value = std::numeric_limits<T>::max();
			T max_value = std::numeric_limits<T>::min();
			for (auto it = vs.begin(); it != vs.end(); ++it) {
				for (auto jt = it->begin(); jt != it->end(); ++jt) {
					if ((*jt) > max_value) {
						max_value = *jt;
					}
					if ((*jt) < min_value) {
						min_value = *jt;
					}
				}
			}

			scaled_type = true;
			if (min_value >= std::numeric_limits<uint8_t>::min() && max_value <= std::numeric_limits<uint8_t>::max()) {
				dt = dt2 = new H5::PredType(H5::PredType::NATIVE_UINT8);
			} else if (min_value >= std::numeric_limits<int8_t>::min() && max_value <= std::numeric_limits<int8_t>::max()) {
				dt = dt2 = new H5::PredType(H5::PredType::NATIVE_INT8);
			} else if (min_value >= std::numeric_limits<uint16_t>::min() && max_value <= std::numeric_limits<uint16_t>::max()) {
				dt = dt2 = new H5::PredType(H5::PredType::NATIVE_UINT16);
			} else if (min_value >= std::numeric_limits<int16_t>::min() && max_value <= std::numeric_limits<int16_t>::max()) {
				dt = dt2 = new H5::PredType(H5::PredType::NATIVE_INT16);
			} else if (min_value >= std::numeric_limits<uint32_t>::min() && max_value <= std::numeric_limits<uint32_t>::max()) {
				dt = dt2 = new H5::PredType(H5::PredType::NATIVE_UINT32);
			} else if (min_value >= std::numeric_limits<int32_t>::min() && max_value <= std::numeric_limits<int32_t>::max()) {
				dt = dt2 = new H5::PredType(H5::PredType::NATIVE_INT32);
			} else {
				scaled_type = false;
			}

		}
		
		if (dt == 0) {
			dt = get_datatype<T>();
		}
		
	} else {
		s = new hsize_t(vs.size());
		dt = dt2 = new H5::VarLenType(get_datatype<T>());
	}

	const std::string dsn_path = "/population/" + dsn;
	const size_t size_in_bytes = is_rectangular
		? sizeof(T) * vs.size() * w
		: sizeof(hvl_t) * vs.size();

	// TODO: Refactor
	const bool is_chunked = settings_.chunk_size() > 0 && settings_.chunk_size() < s[0];
	if (is_chunked) {
		if (is_rectangular) {
			chunk = new hsize_t[2];
			chunk[0] = settings_.chunk_size();
			chunk[1] = s[1];
		} else {
			chunk = new hsize_t(vs.size());
		}
	} else {
		chunk = s;
	}

	const H5::DSetCreatPropList* plist;
	// H5O_MESG_MAX_SIZE = 65536
	const bool compact = size_in_bytes < (1 << 15);
	if (settings_.compress() && !compact) { 
		H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
		plist_->setChunk(is_rectangular ? 2 : 1, chunk);
		// D'oh. Order is significant, according to h5ex_d_shuffle.c
		plist_->setShuffle();
		plist_->setDeflate(9);
		plist = plist_;
	} else if (compact) {
		H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
		// Set compact according to h5ex_d_compact.c
		plist_->setLayout(H5D_COMPACT);
		plist = plist_;
	} else if (chunk != s){
		H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
		plist_->setChunk(is_rectangular ? 2 : 1, chunk);
		plist = plist_;
	} else {
		plist = &H5::DSetCreatPropList::DEFAULT;
	}

	H5::DataSpace space(is_rectangular ? 2 : 1, s);
	H5::DataSet ds = population_group.createDataSet(dsn, *dt, space, *plist);
	
	void* buffer = allocator.allocate(size_in_bytes);
	void* ds_ptr = buffer;
	for (auto it = vs.begin(); it != vs.end(); ++it) {
		if (is_rectangular) {
			for (auto jt = it->begin(); jt != it->end(); ++jt) {
				write_number_of_size(ds_ptr, dt->getSize(), *jt);
			}
		} else {
			write_aggregate(ds_ptr, *it);
		}
	}						
	ds.write(buffer, *dt);
	space.close();

	ds.reference(ptr, dsn_path.c_str());
	advance(ptr, sizeof(hobj_ref_t));
	
	delete[] buffer;
	ds.close();

	if (plist != &H5::DSetCreatPropList::DEFAULT) {
		// ->close() doesn't work due to const, hack hack hack
		H5Pclose(plist->getId());
	}
	
	if (is_rectangular) {
		delete[] s;
		if (is_chunked) {
			delete[] chunk;
		}
		if (scaled_type) {
			dt2->close();
			delete dt;
		}
	} else {
		dt2->close();
		delete dt;
		delete s;
		if (is_chunked) {
			delete chunk;
		}
	}
}
*/

void IfcParse::IfcHdf5File::write_schema(const IfcParse::schema_definition& schema, IfcParse::IfcFile& ifc_file) {

	// From h5ex_g_compact.c
	// Compact groups?
	H5::FileAccPropList* plist = new H5::FileAccPropList();
	plist->setLibverBounds(H5F_LIBVER_LATEST, H5F_LIBVER_LATEST);

	// H5::FileCreatPropList* plist2 = new H5::FileCreatPropList();
	// H5Pset_file_space(plist2->getId(), H5F_FILE_SPACE_VFD, (hsize_t)0);
	
	file = new H5::H5File(name_, H5F_ACC_TRUNC, H5::FileCreatPropList::DEFAULT, *plist);

	schema_group = file->createGroup(schema.name() + "_encoding");
	population_group = file->createGroup("population");
	
	// init_default_types();

	mapper_ = new type_mapper(ifc_file, file);
	(*(type_mapper*)mapper_)();
};

std::pair<size_t, size_t> IfcParse::IfcHdf5File::make_instance_reference(const IfcUtil::IfcBaseClass* instance) const {
#ifdef SORT_ON_NAME
	const std::vector<uint32_t>& es = sorted_entities.find(instance->declaration().type())->second;
#else
	const std::vector<IfcUtil::IfcBaseClass*>& es = sorted_entities.find(instance->declaration().type())->second;
#endif
	
	auto dataset_id = std::lower_bound(dataset_names.begin(), dataset_names.end(), instance->declaration().type());
#ifdef SORT_ON_NAME
	auto instance_id = std::lower_bound(es.begin(), es.end(), instance->data().id());
#else
	auto instance_id = std::lower_bound(es.begin(), es.end(), instance);
#endif
	
	size_t dataset_offset = std::distance(dataset_names.begin(), dataset_id);
	size_t instance_offset = std::distance(es.begin(), instance_id);

	return std::make_pair(dataset_offset, instance_offset);
}

/*
void IfcParse::IfcHdf5File::write_select(void*& ptr, IfcUtil::IfcBaseClass* instance, const H5::CompType* datatype) const {
	int member_index = -1;

	if (instance->declaration().as_entity()) {
		member_index = datatype->getMemberIndex("instance-value");
		size_t offset = datatype->getMemberOffset(member_index);
		auto ref = make_instance_reference(instance);
		void* ptr_member = (uint8_t*) ptr + offset;
		// write_number_of_size(ptr_member, instance_reference->getMemberDataType(0).getSize(), ref.first);
		// write_number_of_size(ptr_member, instance_reference->getMemberDataType(1).getSize(), ref.second);
		write_number_of_size(ptr_member, 2, ref.first);
		write_number_of_size(ptr_member, 4, ref.second);
	} else {
		Argument& wrapped_data = *instance->data().getArgument(0);
		IfcUtil::ArgumentType ty = wrapped_data.type();
		if (default_cpp_type_names.find(ty) == default_cpp_type_names.end()) {
			Logger::Message(Logger::LOG_ERROR, "Unsupported select valuation encountered", instance);
		} else {
			std::string member_name = default_cpp_type_names.find(ty)->second + "-value";
			member_index = datatype->getMemberIndex(member_name);
			size_t offset = datatype->getMemberOffset(member_index);
			H5::DataType memberdt = datatype->getMemberDataType(member_index);
			size_t member_size = memberdt.getSize();
			memberdt.close();
			void* ptr_member = (uint8_t*) ptr + offset;
			switch(wrapped_data.type()) {
				case IfcUtil::Argument_BOOL: {
					bool v = wrapped_data;
					write_number_of_size(ptr_member, member_size, static_cast<uint8_t>(v ? 1 : 0));
					break; }
				case IfcUtil::Argument_DOUBLE: {
					double d = wrapped_data;
					write_number_of_size(ptr_member, member_size, d);
					break; }
				case IfcUtil::Argument_STRING: {
					std::string s = wrapped_data;
					write(ptr_member, s);
					break; }
				case IfcUtil::Argument_INT: {
					int i = wrapped_data;
					write_number_of_size(ptr_member, member_size, i);
					break; }
				default:
					Logger::Message(Logger::LOG_ERROR, "Unsupported select valuation encountered", instance);
					break;
			}
		}							
	}

	if (member_index == -1) {
		member_index = 0;
	} else {
		member_index -= 2; // select_bitmap, type_path
	}

	void* temp_ptr = ptr;
	write_number_of_size(temp_ptr, H5::PredType::NATIVE_INT8.getSize(), member_index);
	write(temp_ptr, instance->declaration().name());

	// TODO: Should string be set to "", or keep as null?
	// std::cout << datatype->getMemberIndex("string-value") << std::endl;

	advance(ptr, datatype->getSize());
}
*/

H5::DataSet IfcParse::IfcHdf5File::create_dataset(const std::string& path, H5::DataType datatype, int rank, hsize_t* dimensions) {
	if (rank != 1) {
		throw std::runtime_error("Expected rank 1");
	}

	const size_t datatype_size = datatype.getSize();	

	hsize_t chunk;
	if (settings_.chunk_size() > 0 && settings_.chunk_size() < dimensions[0]) {
		chunk = static_cast<hsize_t>(settings_.chunk_size());
	} else {
		chunk = dimensions[0];
	}

	const H5::DSetCreatPropList* plist;
	// H5O_MESG_MAX_SIZE = 65536
	const bool compact = dimensions[0] * datatype_size < (1 << 15);
	if (settings_.compress() && !compact) {
		H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
		plist_->setChunk(1, &chunk);
		// D'oh. Order is significant, according to h5ex_d_shuffle.c
		plist_->setShuffle();
		plist_->setDeflate(9);
		plist = plist_;
	} else if (compact) {
		H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
		// Set compact according to h5ex_d_compact.c
		plist_->setLayout(H5D_COMPACT);
		plist = plist_;
	} else if (chunk != dimensions[0]) {
		H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
		plist_->setChunk(1, &chunk);
		plist = plist_;
	} else {
		plist = &H5::DSetCreatPropList::DEFAULT;
	}

	H5::DataSpace space(1, dimensions);
	H5::DataSet ds = population_group.createDataSet(path, datatype, space, *plist);

	if (plist != &H5::DSetCreatPropList::DEFAULT) {
		// ->close() doesn't work due to const, hack hack hack
		H5Pclose(plist->getId());
	}

	return ds;
}

void IfcParse::IfcHdf5File::write_population(IfcFile& f) {
	std::set<IfcSchema::Type::Enum> tys;

	// Wth was this?
	// this->file->close();

	std::set<IfcSchema::Type::Enum> types_with_instiated_selected;

	for (auto it = f.begin(); it != f.end(); ++it) {
		IfcSchema::Type::Enum ty = it->second->declaration().type();
		tys.insert(ty);
		// This already is sorted on entity instance name
#ifdef SORT_ON_NAME
		sorted_entities[ty].push_back(static_cast<uint32_t>(it->first));
#else
		sorted_entities[ty].push_back(it->second);
#endif
	}

	dataset_names.assign(tys.begin(), tys.end());
	std::sort(dataset_names.begin(), dataset_names.end());

	{
		hsize_t dataset_names_length = dataset_names.size();
		H5::DataSpace dataset_names_s(1, &dataset_names_length);

		H5::Attribute attr = schema_group.createAttribute("iso_10303_26_data_set_names", H5::PredType::C_S1, dataset_names_s);
		char** attr_data = (char**)allocator.allocate(static_cast<size_t>(sizeof(char*) * dataset_names_length));
		size_t i = 0;
		for (auto it = dataset_names.begin(); it != dataset_names.end(); ++it, ++i) {
			std::string nm = IfcSchema::Type::ToString(*it);
			attr_data[i] = (char*)allocator.allocate(nm.size() + 1);
			strcpy(attr_data[i], nm.c_str());
		}
		attr.write(H5::PredType::C_S1, attr_data);
		attr.close();
	}

#ifdef SORT_ON_NAME
	for (auto it = sorted_entities.begin(); it != sorted_entities.end(); ++it) {
		std::sort(it->second.begin(), it->second.end());
	}
#endif

	sorted_instance_locator locator(this->ifcfile_);
	write_visit/*<sorted_instance_locator>*/ visitor(false, false, locator, *((type_mapper*)mapper_));

	for (auto dsn_it = dataset_names.begin(); dsn_it != dataset_names.end(); ++dsn_it) {
		
		const std::string current_entity_name = IfcSchema::Type::ToString(*dsn_it);
		std::cerr << current_entity_name << std::endl;

#ifdef SORT_ON_NAME
		std::vector<IfcUtil::IfcBaseClass*> instances;
		const auto& idxs = sorted_entities.find(*dsn_it)->second;
		std::transform(idxs.begin(), idxs.end(), std::back_inserter(instances), [&f](uint32_t idx) {
			return f.entityById(idx);
		});
#else
		const std::vector<IfcUtil::IfcBaseClass*>& instances = sorted_entities.find(*it)->second;
#endif
		hsize_t num_instances = instances.size();
		H5::DataType entity_datatype = schema_group.openDataType(current_entity_name);
		H5::DataSet dataset = create_dataset(current_entity_name + "_instances", entity_datatype, 1, &num_instances);
		
		size_t dataset_size = entity_datatype.getSize() * static_cast<size_t>(num_instances);
		void* data = allocator.allocate(dataset_size);
		void* ptr = data;
		std::cerr << dataset_size << std::endl;

		for (auto inst_it = instances.begin(); inst_it != instances.end(); ++inst_it) {
			write_instance(ptr, visitor, entity_datatype, (IfcUtil::IfcBaseEntity*)*inst_it);
		}

		dataset.write(data, entity_datatype);
		H5::DataSpace space(1, &num_instances);
		H5Dvlen_reclaim(entity_datatype.getId(), space.getId(), H5P_DEFAULT, data);

		dataset.close();
		space.close();

		// allocator.free();
		delete[] data;
	}
}

/*
void IfcParse::IfcHdf5File::write_population(IfcFile& f) {
	std::set<IfcSchema::Type::Enum> tys;

	// Wth was this?
	// this->file->close();
	
	std::set<IfcSchema::Type::Enum> types_with_instiated_selected;

	for (auto it = f.begin(); it != f.end(); ++it) {
		IfcSchema::Type::Enum ty = it->second->declaration().type();
		tys.insert(ty);
		// This already is sorted on entity instance name
#ifdef SORT_ON_NAME
		sorted_entities[ty].push_back(static_cast<uint32_t>(it->first));
#else
		sorted_entities[ty].push_back(it->second);
#endif

#ifndef SORT_ON_NAME
		if (settings_.instantiate_select()) {
			bool has=false;
			for (unsigned i = 0; i < it->second->data().getArgumentCount(); ++i) {
				Argument* attr = it->second->data().getArgument(i);
				if (attr->type() == IfcUtil::Argument_ENTITY_INSTANCE) {
					IfcUtil::IfcBaseClass* inst = *attr;
					if (!inst->declaration().as_entity()) {
						IfcSchema::Type::Enum ty2 = inst->declaration().type();
						tys.insert(ty2);
						sorted_entities[ty2].push_back(inst);
						has = true;
					}
				} else if (attr->type() == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
					IfcEntityList::ptr insts = *attr;
					for (auto it = insts->begin(); it != insts->end(); ++it) {
						if (!(*it)->declaration().as_entity()) {
							IfcSchema::Type::Enum ty2 = (*it)->declaration().type();
							tys.insert(ty2);
							sorted_entities[ty2].push_back(*it);
							has = true;
						}
					}
				}
			}
			if (has) {
				types_with_instiated_selected.insert(ty);
			} else {
				static_cast<IfcParse::Entity*>(&it->second->data())->Unload();
			}
		}
#endif
	}

	dataset_names.assign(tys.begin(), tys.end());
	std::sort(dataset_names.begin(), dataset_names.end());
	
	// dataset_names.push_back(IfcSchema::Type::IfcPostalAddress);

	{
		hsize_t dataset_names_length = dataset_names.size();
		H5::DataSpace dataset_names_s(1, &dataset_names_length);

		H5::Attribute attr = schema_group.createAttribute("iso_10303_26_data_set_names", *default_types[simple_type::string_type], dataset_names_s);
		char** attr_data = (char**) allocator.allocate(static_cast<size_t>(sizeof(char*) * dataset_names_length));
		size_t i = 0;
		for (auto it = dataset_names.begin(); it != dataset_names.end(); ++it, ++i) {
			std::string nm = IfcSchema::Type::ToString(*it);
			attr_data[i] = (char*) allocator.allocate(nm.size() + 1);
			strcpy(attr_data[i], nm.c_str());
		}
		attr.write(*default_types[simple_type::string_type], attr_data);
		attr.close();
	}

#ifdef SORT_ON_NAME
	for (auto it = sorted_entities.begin(); it != sorted_entities.end(); ++it) {
		std::sort(it->second.begin(), it->second.end());
	}
#endif
	
	for (auto it = dataset_names.begin(); it != dataset_names.end(); ++it) {

		// std::cout << "begin inner loop" << std::endl;
		// std::cin.get();

		// if (*it != IfcSchema::Type::IfcUnitAssignment) continue;

		const std::string current_entity_name = IfcSchema::Type::ToString(*it);
		std::cerr << current_entity_name << std::endl;

#ifdef SORT_ON_NAME
		std::vector<IfcUtil::IfcBaseClass*> es;
		es.reserve(sorted_entities.find(*it)->second.size());
		for (auto jt = sorted_entities.find(*it)->second.begin(); jt != sorted_entities.find(*it)->second.end(); ++jt) {
			es.push_back(f.entityById(*jt));
		}
#else
		const std::vector<IfcUtil::IfcBaseClass*>& es = sorted_entities.find(*it)->second;
#endif
		size_t datatype_size = declared_types[*it]->getSize();
		hsize_t dims = es.size();
		
		hsize_t chunk;
		if (settings_.chunk_size() > 0 && settings_.chunk_size() < dims) {
			chunk = static_cast<hsize_t>(settings_.chunk_size());
		} else {
			chunk = dims;
		}

		const H5::DSetCreatPropList* plist;
		// H5O_MESG_MAX_SIZE = 65536
		const bool compact = es.size() * datatype_size < (1 << 15);
		if (settings_.compress() && !compact) { 
			H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
			plist_->setChunk(1, &chunk);
			// D'oh. Order is significant, according to h5ex_d_shuffle.c
			plist_->setShuffle();
			plist_->setDeflate(9);
			plist = plist_;
		} else if (compact) {
			H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
			// Set compact according to h5ex_d_compact.c
			plist_->setLayout(H5D_COMPACT);
			plist = plist_;
		} else if (chunk != dims){
			H5::DSetCreatPropList* plist_ = new H5::DSetCreatPropList;
			plist_->setChunk(1, &chunk);
			plist = plist_;
		} else {
			plist = &H5::DSetCreatPropList::DEFAULT;
		}

		H5::DataSpace space(1, &dims);
		H5::DataSet ds = population_group.createDataSet(IfcSchema::Type::ToString(*it) + "_instances", *declared_types[*it], space, *plist);
		
		size_t dataset_size = declared_types[*it]->getSize() * static_cast<size_t>(dims);
		void* data = allocator.allocate(dataset_size);

		std::cerr << dataset_size << std::endl;
		
		void* ptr = data;
		const H5::CompType* dt = (H5::CompType*) declared_types[*it];
		int ind = 0;

		for (auto jt = es.begin(); jt != es.end(); ++jt, ++ind) {
			void* start = ptr;

			int member_idx = 0;

			H5::DataType member_type;

			IfcAbstractEntity& dat = (*jt)->data();
			const declaration& decl = (*jt)->declaration();			

			if (!decl.as_entity()) {
				if (!settings_.instantiate_select()) throw;
				// This is a type
				// auto q = dt->getClass();
				auto size = dt->getSize();
				const Argument& attr_value = *dat.getArgument(0);
				if (*dt == *default_types[simple_type::real_type]) {
					double d = attr_value;
					write_number_of_size(ptr, size, d);
				} else if (*dt == *default_types[simple_type::string_type]) {
					std::string s = attr_value;
					write(ptr, s);
				} else if (*dt == *default_types[simple_type::integer_type]) {
					int i = attr_value;
					write_number_of_size(ptr, size, i);
				} else if (*dt == *default_types[simple_type::boolean_type] ||
					        *dt == *default_types[simple_type::logical_type]) 
				{
					bool b = attr_value;
					write_number_of_size(ptr, size, static_cast<uint8_t>(b ? 1 : 0));
				} else {
					throw;
				}
				continue;
			}

			std::vector<const IfcParse::entity::attribute*> attributes = decl.as_entity()->all_attributes();
			std::vector<const IfcParse::entity::inverse_attribute*> inverse_attributes;
			if (settings_.instantiate_inverse()) {
				inverse_attributes = decl.as_entity()->all_inverse_attributes();
			}
			const std::vector<bool>& attributes_derived_in_subtype = decl.as_entity()->derived();
			std::vector<bool>::const_iterator is_derived = attributes_derived_in_subtype.begin();

			//for (auto qt = attributes_derived_in_subtype.begin(); qt != attributes_derived_in_subtype.end(); ++qt) {
			//	std::cout << int(*qt);
			//}
			//std::cout << std::endl;

			const bool has_optional = entities_with_optional_attrs.find(current_entity_name) != entities_with_optional_attrs.end();

			uint32_t set_unset_mask;
			size_t set_unset_size;
			void* set_unset_ptr;

			if (has_optional) {
				member_type = dt->getMemberDataType(member_idx++);
				set_unset_mask = 0;
				set_unset_ptr = ptr;
				set_unset_size = member_type.getSize();
				// skip for now write later
				advance(ptr, set_unset_size);
				member_type.close();
			}
			
			member_type = dt->getMemberDataType(member_idx++);
			const unsigned int inst_name = static_cast<unsigned int>(dat.id());
			write_number_of_size(ptr, member_type.getSize(), inst_name);
			member_type.close();

			//                        ----v-----   In some IFC files there are extra superfluous attributes in the instantiation. For example FJK haus.
			const size_t attr_count = (std::min)(attributes.size(), (size_t) dat.getArgumentCount());
			for (unsigned i = 0; i < attr_count; ++i, ++is_derived) {

				//std::cout << i << std::endl;

				if (*is_derived) {
					continue;
				}

				if (attributes_omitted.find(std::make_pair(current_entity_name, i)) != attributes_omitted.end()) {
					continue;
				}

				const IfcParse::entity::attribute* schema_attr = attributes[i];
				const std::string& attribute_name = schema_attr->name();
				//std::cout << "ifc " << attribute_name << std::endl;
				Argument& attr_value = *dat.getArgument(i);

				member_type = dt->getMemberDataType(member_idx++);

				//std::cout << "hdf5 " << dt->getMemberName(member_idx - 1) << ": " << member_type.getClass() << std::endl;

				if (attr_value.isNull()) {
					if (member_type == *default_types[simple_type::string_type]) {
						// HDF5 otherwise crashes on derefencing a zero pointer for the string type
						write(ptr, new(allocator.allocate(1)) char(0));
					} else {
						memset(ptr, 0, member_type.getSize());
						advance(ptr, member_type.getSize());
					}
				} else {
					set_unset_mask |= 1 << i;
					if (member_type.getClass() == H5T_REFERENCE) {
						// Something that comes from the ref_attributes settings
						const std::string dsn = current_entity_name + "." + attribute_name + "_" + boost::lexical_cast<std::string>(dat.id());
						switch(attr_value.type()) {
						case IfcUtil::Argument_AGGREGATE_OF_INT: {
							std::vector<int> vs = attr_value;
							write_reference_attribute(ptr, dsn, vs);
							break; }
						case IfcUtil::Argument_AGGREGATE_OF_BOOL: {
							std::vector<bool> vs = attr_value;
							write_reference_attribute(ptr, dsn, vs);
							break; }
						case IfcUtil::Argument_AGGREGATE_OF_DOUBLE: {
							std::vector<double> vs = attr_value;
							write_reference_attribute(ptr, dsn, vs);
							break; }
						case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT: {
							std::vector< std::vector<int> > vs = attr_value;
							write_reference_attribute2(ptr, dsn, vs);
							break; }
						case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_BOOL: {
							std::vector< std::vector<int> > vs = attr_value;
							write_reference_attribute2(ptr, dsn, vs);
							break; }
						case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE: {
							std::vector< std::vector<double> > vs = attr_value;
							write_reference_attribute2(ptr, dsn, vs);
							break; }
						default:
							throw IfcException(dsn + " is not a supported aggregate");
						}
					} if (settings_.fix_global_id() && attribute_name == "GlobalId") {
						std::string s = attr_value;
						memcpy(static_cast<char*>(ptr), s.c_str(), s.size());
						advance(ptr, s.length());
					} else if (settings_.fix_cartesian_point() && ((attribute_name == "Coordinates" && current_entity_name == "IfcCartesianPoint") || (attribute_name == "DirectionRatios" && current_entity_name == "IfcDirection"))) {
						std::vector<double> vs = attr_value;
						for (auto vs_it = vs.begin(); vs_it != vs.end(); ++vs_it) {
							write_number_of_size(ptr, default_types[simple_type::real_type]->getSize(), *vs_it);
						}
						if (vs.size() == 2) {
							write_number_of_size(ptr, default_types[simple_type::real_type]->getSize(), std::numeric_limits<double>::quiet_NaN());
						}
					} else if (member_type == *instance_reference) {
						IfcUtil::IfcBaseClass* v = attr_value;
						auto ref = make_instance_reference(v);
						// write_number_of_size(ptr, instance_reference->getMemberDataType(0).getSize(), ref.first);
						// write_number_of_size(ptr, instance_reference->getMemberDataType(1).getSize(), ref.second);
						write_number_of_size(ptr, 2, ref.first);
						write_number_of_size(ptr, 4, ref.second);
					} else if (member_type == *default_types[simple_type::real_type]) {
						double d = attr_value;
						write_number_of_size(ptr, member_type.getSize(), d);
					} else if (member_type == *default_types[simple_type::string_type] || member_type.getClass() == H5T_STRING) {
						std::string s = attr_value;
						if (member_type == *default_types[simple_type::string_type]) {
							write(ptr, s);
						} else {
							write_string_of_size(ptr, s, member_type.getSize());
						}
					} else if (member_type == *default_types[simple_type::integer_type]) {
						int v = attr_value;
						write_number_of_size(ptr, member_type.getSize(), v);
					} else if (member_type == *default_types[simple_type::boolean_type] ||
					           member_type == *default_types[simple_type::logical_type]) 
					{
						bool b = attr_value;
						write_number_of_size(ptr, member_type.getSize(), static_cast<uint8_t>(b ? 1 : 0));
					} else if (member_type.getClass() == H5T_ENUM) {
						// NB: Note that boolean and logical are also enums
						// NB2: In IfcOpenShell an enum value can be read as a string
						std::string s = attr_value;
						const std::vector<std::string>& enum_values = schema_attr->type_of_attribute()->as_named_type()->declared_type()->as_enumeration_type()->enumeration_items();
						size_t d = std::distance(enum_values.begin(), std::find(enum_values.begin(), enum_values.end(), s));
						write_number_of_size(ptr, member_type.getSize(), d);
					} else if (member_type.getClass() == H5T_VLEN || member_type.getClass() == H5T_ARRAY) {
						const parameter_type* pt = schema_attr->type_of_attribute();
						while (pt->as_named_type()) {
							pt = pt->as_named_type()->declared_type()->as_type_declaration()->declared_type();
						}
						const named_type* nt = pt->as_aggregation_type()->type_of_element()->as_named_type();
						if (nt && nt->declared_type()->as_select_type()) {
							const H5::DataType* datatype = declared_types[nt->declared_type()->type()];
							IfcEntityList::ptr vs = attr_value;
							if (datatype == instance_reference) {
								// For a SELECTs with only ENTITY leaves, a blind instance reference type is used
								// TK: Is this actually correct?
								if (member_type.getClass() == H5T_VLEN) {
									write_aggregate(ptr, vs);
								} else {
									H5::ArrayType* adt = (H5::ArrayType*) &member_type;
									size_t ndims = adt->getArrayNDims();
									size_t element_size = adt->getSuper().getSize();
									hsize_t* array_dims = new hsize_t[ndims];
									adt->getArrayDims(array_dims);

									std::vector<IfcUtil::IfcBaseClass*> es2(vs->begin(), vs->end());
									write_consecutive(ptr, es2, array_dims, &element_size);
								}
							} else {
								if (member_type.getClass() == H5T_VLEN) {
									size_t size_in_bytes = datatype->getSize();
									size_t num_elements = vs->size();
									void* buffer_ptr;
									// void* buffer = buffer_ptr = new uint8_t[size_in_bytes * num_elements];
									void* buffer = buffer_ptr = allocator.allocate(size_in_bytes * num_elements);
									memset(buffer, 0, size_in_bytes * num_elements);
									for (auto vs_it = vs->begin(); vs_it != vs->end(); ++vs_it) {
										write_select(buffer_ptr, *vs_it, static_cast<const H5::CompType*>(datatype));
									}
									write_vlen_t(ptr, num_elements, buffer);
								} else {
									// Set to zero in case of different size
									memset(ptr, 0, member_type.getSize());
									void* ptr_ = ptr;
									for (auto vs_it = vs->begin(); vs_it != vs->end(); ++vs_it) {
										write_select(ptr_, *vs_it, static_cast<const H5::CompType*>(datatype));
									}
									// This is cheating, let's hope the sizes align.
									advance(ptr, member_type.getSize());
								}
							}
						} else {
							if (member_type.getClass() == H5T_VLEN) {
								switch (attr_value.type()) {
								case IfcUtil::Argument_AGGREGATE_OF_INT: {
									std::vector<int> vs = attr_value;
									write_aggregate(ptr, vs);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_BOOL: {
									std::vector<bool> vs = attr_value;
									write_aggregate(ptr, vs);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_DOUBLE: {
									std::vector<double> vs = attr_value;
									write_aggregate(ptr, vs);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
									IfcEntityList::ptr vs = attr_value;
									write_aggregate(ptr, vs);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_STRING: {
									std::vector<std::string> ss = attr_value;
									write_aggregate(ptr, ss);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT: {
									std::vector< std::vector<int> > vs = attr_value;
									write_aggregate2(ptr, vs);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_BOOL: {
									std::vector< std::vector<bool> > vs = attr_value;
									write_aggregate2(ptr, vs);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE: {
									std::vector< std::vector<double> > vs = attr_value;
									write_aggregate2(ptr, vs);
									break; }
								default:
									// Can be an empty list in which case parser does not know type
									if (attr_value.size() > 0) {
										Logger::Message(Logger::LOG_ERROR, "Unsupported aggregate encountered", *jt);
									}
									memset(ptr, 0, member_type.getSize());
									ptr = (uint8_t*)ptr + member_type.getSize();
								}
							} else {
								if (member_type.getClass() != H5T_ARRAY) throw;
								H5::ArrayType* adt = (H5::ArrayType*) &member_type;
								size_t ndims = adt->getArrayNDims();
								size_t element_size = adt->getSuper().getSize();
								hsize_t* array_dims = new hsize_t[ndims];
								adt->getArrayDims(array_dims);

								size_t ifcdims = 0;

								switch (attr_value.type()) {
								case IfcUtil::Argument_AGGREGATE_OF_INT:
								case IfcUtil::Argument_AGGREGATE_OF_BOOL:
								case IfcUtil::Argument_AGGREGATE_OF_DOUBLE:
								case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE:
								case IfcUtil::Argument_AGGREGATE_OF_STRING:
									ifcdims = 1;
									break;
								case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT:
								case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_BOOL:
								case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE:
									ifcdims = 2;
									break;
								}

								// Caught in default block below and memset() to zero.
								// if (false && ifcdims != ndims) {
								// 	std::cerr << "Expected dim " << ndims << " got " << ifcdims << std::endl;
								// 	std::cin.get();
								// 	abort();
								// }
								
								switch (attr_value.type()) {
								case IfcUtil::Argument_AGGREGATE_OF_INT: {
									std::vector<int> vs = attr_value;
									write_consecutive(ptr, vs, array_dims, &element_size);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_BOOL: {
									std::vector<bool> vs = attr_value;
									write_consecutive(ptr, vs, array_dims, &element_size);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_DOUBLE: {
									std::vector<double> vs = attr_value;
									write_consecutive(ptr, vs, array_dims, &element_size);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
									IfcEntityList::ptr vs = attr_value;
									std::vector<IfcUtil::IfcBaseClass*> vs2(vs->begin(), vs->end());
									write_consecutive(ptr, vs2, array_dims, &element_size);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_STRING: {
									std::vector<std::string> vs = attr_value;
									write_consecutive(ptr, vs, array_dims, &element_size);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT: {
									// std::vector< std::vector<int> > ds = attr_value;
									// write_consecutive2(ptr, ds);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_BOOL: {
									// std::vector< std::vector<bool> > ds = attr_value;
									// write_consecutive2(ptr, ds);
									break; }
								case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE: {
									// std::vector< std::vector<double> > ds = attr_value;
									// write_consecutive2(ptr, ds);
									break; }
								default:
									// Can be an empty list in which case parser does not know type
									if (attr_value.size() > 0) {
										Logger::Message(Logger::LOG_ERROR, "Unsupported aggregate encountered", *jt);
									}
									memset(ptr, 0, member_type.getSize());
									advance(ptr, member_type.getSize());
								}




								
								delete[] array_dims;
							}
						}
					} else if (member_type.getClass() == H5T_COMPOUND) {
						memset(ptr, 0, member_type.getSize());
						
						IfcUtil::ArgumentType ty = attr_value.type();
						if (ty != IfcUtil::Argument_ENTITY_INSTANCE) throw;
						//                    v impl. cast
						write_select(ptr, attr_value, static_cast<H5::CompType*>(&member_type));
					}
				}

				member_type.close();
			}

			for (auto inv_it = inverse_attributes.begin(); inv_it != inverse_attributes.end(); ++inv_it) {
				member_type = dt->getMemberDataType(member_idx++);

				if (member_type.getClass() != H5T_VLEN) {
					std::cerr << dt->getMemberName(member_idx - 1) << " ";
					std::cerr << "Inverse attribute must be vlen" << std::endl;
				}
				const IfcParse::entity* entity_ref = (*inv_it)->entity_reference();
				const IfcParse::entity::attribute* attribute_ref = (*inv_it)->attribute_reference();
				IfcEntityList::ptr instances = f.getInverse(dat.id(), entity_ref->type(), entity_ref->attribute_index(attribute_ref));
				if (instances->size() == 0) {
					memset(ptr, 0, member_type.getSize());
					advance(ptr, member_type.getSize());
				} else {
					write_aggregate(ptr, instances);
				}

				member_type.close();
			}

			if (has_optional) {
				write_number_of_size(set_unset_ptr, set_unset_size, set_unset_mask);
			}
			const size_t written_length = (uint8_t*) ptr - (uint8_t*) start;
			
			if (written_length != datatype_size) {
				std::cerr << "Written " << written_length << " bytes, but expected " << datatype_size << std::endl;
				std::cin.get();
				abort();
			}
		}

		// for (size_t i = 0; i < dataset_size; ++i) {
		// 	std::cout << std::hex << (int)((uint8_t*)data)[i] << " ";
		// }

		// visit(data, declared_types[*it]);
		ds.write(data, *declared_types[*it]);
		H5Dvlen_reclaim(declared_types[*it]->getId(), space.getId(), H5P_DEFAULT, data);

		ds.close();
		space.close();

		if (plist != &H5::DSetCreatPropList::DEFAULT) {
			// ->close() doesn't work due to const, hack hack hack
			H5Pclose(plist->getId());
		}

		// allocator.free();
		delete[] data;
		
		for (auto es_it = es.begin(); es_it != es.end(); ++es_it) {
			if (types_with_instiated_selected.find((**es_it).declaration().type()) == types_with_instiated_selected.end()) {
				// Instances possibly refering to embedded simple type instantiations are not freed
				static_cast<IfcParse::Entity*>(&(**es_it).data())->Unload();
			}
		}

	}
}
*/