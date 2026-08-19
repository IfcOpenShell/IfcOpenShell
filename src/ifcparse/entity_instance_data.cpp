#include "instance_data.h"
#include "express.h"
#include "exception.h"
#include "file.h"

using namespace ifcopenshell;

// @todo is size() still needed?
class size_visitor {
public:
    typedef int result_type;

    int operator()(const blank& /*i*/) const { return -1; }
    int operator()(const derived& /*i*/) const { return -1; }
    int operator()(const int64_t& /*i*/) const { return -1; }
    int operator()(const bool& /*i*/) const { return -1; }
    int operator()(const boost::logic::tribool& /*i*/) const { return -1; }
    int operator()(const double& /*i*/) const { return -1; }
    int operator()(const std::string& /*i*/) const { return -1; }
    int operator()(const boost::dynamic_bitset<>& /*i*/) const { return -1; }
    int operator()(const empty_aggregate& /*unused*/) const { return 0; }
    int operator()(const empty_aggregate_of_aggregate& /*unused*/) const { return 0; }
    int operator()(const std::vector<int64_t>& i) const { return (int)i.size(); }
    int operator()(const std::vector<double>& i) const { return (int)i.size(); }
    int operator()(const std::vector<std::vector<int64_t>>& i) const { return (int)i.size(); }
    int operator()(const std::vector<std::vector<double>>& i) const { return (int)i.size(); }
    int operator()(const std::vector<std::string>& i) const { return (int)i.size(); }
    int operator()(const std::vector<boost::dynamic_bitset<>>& i) const { return (int)i.size(); }
    int operator()(const enumeration_reference& /*i*/) const { return -1; }
    int operator()(const express::base& /*i*/) const { return -1; }
    int operator()(const std::vector<express::base>& i) const { return (int)i.size(); }
    int operator()(const std::vector<std::vector<express::base>>& i) const { return (int)i.size(); }
};

namespace {
    template<typename T>
    inline T dispatch_get_(attribute_value::pointer_type array_, uint8_t storage_model_, size_t instance_name_, const ifcopenshell::declaration* entity_or_type, uint8_t index_)
    {
        if (storage_model_ == 0) {
            try {
                return array_.storage_ptr->get<T>(index_);
            } catch (const ::impl::storage_type_mismatch& e) {
                throw ifcopenshell::exception(
                    // entity_or_type not passed, but in v0.9 this is beginning to make sense
                    (entity_or_type
                    ? std::string("On instance #" + std::to_string(instance_name_) + " of " + entity_or_type->name() + ": ")
                    : std::string("")) +
                    "Requested type <" + e.requested() + "> does not match actual type <" + e.actual() + "> at index " + std::to_string(index_));
            } catch (const std::out_of_range& e) {
                throw ifcopenshell::exception(
                    (entity_or_type
                    ? std::string("On instance #" + std::to_string(instance_name_) + " of " + entity_or_type->name() + ": ")
                    : std::string("")) +
                    e.what());
            }
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else {
            T val = T{};
            const bool is_header = entity_or_type->schema() == &Header_section_schema::get_schema();
            if constexpr (
                // the following types cannot be directly deserialized from rocksdb, but need to be constructed
                !std::is_same_v<T, enumeration_reference> &&
                !std::is_same_v<std::remove_cv_t<T>, express::base>)
            {
                std::string str;
                array_.db_ptr->db->Get(rocksdb::ReadOptions{},
                    (is_header ? "h|" : (entity_or_type->as_entity() ? "i|" : "t|")) +
                    (is_header ? entity_or_type->name() : std::to_string(instance_name_)) + "|" +
                    std::to_string(index_), &str);
                ::impl::deserialize(array_.db_ptr, str, val);
            } else {
                static_assert(
                    std::is_same_v<T, enumeration_reference> ||
                     std::is_same_v<std::remove_cv_t<T>, express::base>,
                    "RocksDB deserialization must be specialized for this enumeration_reference and express::base"
                );
            }
            return val;
        }
#endif
        throw std::logic_error("RocksDB storage is unavailable");
    }

    template<typename T>
    inline bool dispatch_has_(attribute_value::pointer_type array_, uint8_t storage_model_, size_t instance_name_, const ifcopenshell::declaration* entity_or_type, uint8_t index_)
    {
#ifndef IFOPSH_WITH_ROCKSDB
        (void)instance_name_;
        (void)entity_or_type;
#endif
        if (storage_model_ == 0) {
            return array_.storage_ptr->has<T>(index_);
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else {
            std::string str;
            const bool is_header = entity_or_type->schema() == &Header_section_schema::get_schema();
            array_.db_ptr->db->Get(rocksdb::ReadOptions{},
                (is_header ? "h|" : (entity_or_type->as_entity() ? "i|" : "t|")) +
                (is_header ? entity_or_type->name() : std::to_string(instance_name_)) + "|" +
                std::to_string(index_), &str);
            if constexpr (std::is_same_v<T, blank>) {
                if (str.size() == 0) {
                    return true;
                }
            }
            return str[0] == type_encoder::encode_type<T>();
        }
#endif
        throw std::logic_error("RocksDB storage is unavailable");
    }

    inline size_t dispatch_index_(attribute_value::pointer_type array_, uint8_t storage_model_, size_t instance_name_, const ifcopenshell::declaration* entity_or_type, uint8_t index_)
    {
#ifndef IFOPSH_WITH_ROCKSDB
        (void)instance_name_;
        (void)entity_or_type;
#endif
        if (storage_model_ == 0) {
            return array_.storage_ptr->index(index_);
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else {
            std::string str;
            const bool is_header = entity_or_type->schema() == &Header_section_schema::get_schema();
            if (!array_.db_ptr->db->Get(rocksdb::ReadOptions{},
                (is_header ? "h|" : (entity_or_type->as_entity() ? "i|" : "t|")) +
                (is_header ? entity_or_type->name() : std::to_string(instance_name_)) + "|" +
                std::to_string(index_), &str).ok()) {
                return type_encoder::encode_type<blank>() - 'A';
            }
            return (size_t) str[0] - 'A';
        }
#endif
        throw std::logic_error("RocksDB storage is unavailable");
    }
}

attribute_value::operator int64_t() const
{
    return dispatch_get_<int64_t>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator bool() const
{
    return dispatch_get_<bool>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator double() const
{
    return dispatch_get_<double>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator boost::logic::tribool() const
{
    if (dispatch_has_<bool>(array_, storage_model_, instance_name_, entity_or_type_, index_)) {
        return dispatch_get_<bool>(array_, storage_model_, instance_name_, entity_or_type_, index_);
    }
    return dispatch_get_<boost::logic::tribool>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator std::string() const
{
    if (dispatch_has_<enumeration_reference>(array_, storage_model_, instance_name_, entity_or_type_, index_)) {
        // @todo this is silly, but the way things currently work,
        // @todo also we don't really need to store a reference to the enumeration type, when this same type is already stored on the definition of the entity and no other value can be provided.
        if (storage_model_ == 0) {
            return dispatch_get_<enumeration_reference>(array_, storage_model_, instance_name_, entity_or_type_, index_).value();
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else {
            std::string str;
            const bool is_header = entity_or_type_->schema() == &Header_section_schema::get_schema();
            array_.db_ptr->db->Get(rocksdb::ReadOptions{},
                (is_header ? "h|" : (entity_or_type_->as_entity() ? "i|" : "t|")) +
                (is_header ? entity_or_type_->name() : std::to_string(instance_name_)) + "|" +
                std::to_string(index_), &str);
            size_t v;
            memcpy(&v, str.data() + 1, sizeof(size_t));
            auto decl = array_.db_ptr->file->schema()->declarations()[v]->as_enumeration_type();
            memcpy(&v, str.data() + 1 + sizeof(size_t), sizeof(size_t));
            return decl->lookup_enum_value(v);
        }
#endif
    }
    return dispatch_get_<std::string>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator enumeration_reference() const
{
    if (storage_model_ == 0) {
        return dispatch_get_<enumeration_reference>(array_, storage_model_, instance_name_, entity_or_type_, index_);
    }
#ifdef IFOPSH_WITH_ROCKSDB
    else {
        std::string str;
        const bool is_header = entity_or_type_->schema() == &Header_section_schema::get_schema();
        array_.db_ptr->db->Get(rocksdb::ReadOptions{},
            (is_header ? "h|" : (entity_or_type_->as_entity() ? "i|" : "t|")) +
            (is_header ? entity_or_type_->name() : std::to_string(instance_name_)) + "|" +
            std::to_string(index_), &str);
        size_t v;
        memcpy(&v, str.data() + 1, sizeof(size_t));
        auto decl = array_.db_ptr->file->schema()->declarations()[v]->as_enumeration_type();
        memcpy(&v, str.data() + 1 + sizeof(size_t), sizeof(size_t));
        return enumeration_reference(decl, v);
    }
#endif
    throw std::logic_error("RocksDB storage is unavailable");
}

attribute_value::operator boost::dynamic_bitset<>() const
{
    return dispatch_get_<boost::dynamic_bitset<>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator express::base () const
{
    if (storage_model_ == 0) {
        return dispatch_get_<express::base>(array_, storage_model_, instance_name_, entity_or_type_, index_);
    }
#ifdef IFOPSH_WITH_ROCKSDB
    else {
        std::string str;
        const bool is_header = entity_or_type_->schema() == &Header_section_schema::get_schema();
        array_.db_ptr->db->Get(rocksdb::ReadOptions{},
            (is_header ? "h|" : (entity_or_type_->as_entity() ? "i|" : "t|")) +
            (is_header ? entity_or_type_->name() : std::to_string(instance_name_)) + "|" +
            std::to_string(index_), &str);
        size_t v;
        memcpy(&v, str.data() + 2, sizeof(size_t));
        if (str.size() > 1 && str[1] == 'i') {
            // entity reference, by #Name
            return array_.db_ptr->assert_existance(v, ifcopenshell::impl::rocks_db_file_storage::entityinstance_ref);
        } else if (str.size() > 1 && str[1] == 't') {
            // type reference by Identity
            return array_.db_ptr->assert_existance(v, ifcopenshell::impl::rocks_db_file_storage::typedecl_ref);
        } else {
            throw std::runtime_error("Invalid data encountered");
        }
    }
#endif
    throw std::logic_error("RocksDB storage is unavailable");
}

attribute_value::operator std::vector<int64_t>() const
{
    return dispatch_get_<std::vector<int64_t>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator std::vector<double>() const
{
    return dispatch_get_<std::vector<double>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator std::vector<std::string>() const
{
    return dispatch_get_<std::vector<std::string>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator std::vector<boost::dynamic_bitset<>>() const
{
    return dispatch_get_<std::vector<boost::dynamic_bitset<>>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator std::vector<express::base>() const
{
    return dispatch_get_<std::vector<express::base>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator std::vector<std::vector<int64_t>>() const
{
    return dispatch_get_<std::vector<std::vector<int64_t>>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator std::vector<std::vector<double>>() const
{
    return dispatch_get_<std::vector<std::vector<double>>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

attribute_value::operator std::vector<std::vector<express::base>>() const
{
    return dispatch_get_<std::vector<std::vector<express::base>>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

bool attribute_value::isNull() const
{
    return dispatch_has_<blank>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

unsigned int attribute_value::size() const
{
    // @todo
    return array_.storage_ptr->apply_visitor(size_visitor{}, index_);
}

ifcopenshell::argument_type attribute_value::type() const
{
    return static_cast<ifcopenshell::argument_type>(dispatch_index_(array_, storage_model_, instance_name_, entity_or_type_, index_));
}

#ifdef IFOPSH_WITH_ROCKSDB

bool ::impl::serialize(std::string& val, const express::base& t)
{
    auto s = sizeof(size_t);
    val.resize(s + 2);
    val[0] = type_encoder::encode_type<express::base>();
    // 1 = entity - stored by id (entity name)
    // 2 = type - stored by identity (internal counter in class)
    val[1] = t.declaration().as_entity() ? 'i' : 't';
    size_t iden = t.id() ? t.id() : t.identity();
    memcpy(val.data() + 2, &iden, s);
    return true;
}

bool ::impl::serialize(std::string& val, const enumeration_reference& v)
{
    auto s = sizeof(size_t);
    val.resize(s * 2 + 1);
    val[0] = type_encoder::encode_type<enumeration_reference>();
    size_t vv = v.enumeration()->index_in_schema();
    memcpy(val.data() + 1, &vv, sizeof(size_t));
    vv = v.index();
    memcpy(val.data() + 1 + sizeof(size_t), &vv, sizeof(size_t));
    return true;
}

bool ::impl::serialize(std::string& val, const std::vector<express::base>& t)
{
    // no attempt at alignment
    val.resize(t.size() * (sizeof(size_t) + 1) + 1);
    val[0] = type_encoder::encode_type<std::vector<express::base>>();
    char* ptr = val.data() + 1;
    for (auto& inst : t) {
        *ptr = inst.declaration().as_entity() ? 'i' : 't';
        ptr++;
        size_t iden = inst.id() ? inst.id() : inst.identity();
        memcpy(ptr, &iden, sizeof(size_t));
        ptr += sizeof(size_t);
    }
    return true;
}

bool ::impl::serialize(std::string& val, const std::vector<std::vector<express::base>>& t)
{
    std::ostringstream oss;
	oss.put(type_encoder::encode_type<std::vector<std::vector<express::base>>>());

    auto write_size = [&oss](size_t sz) {
        std::string size_str;
        size_str.resize(sizeof(size_t));
        memcpy(size_str.data(), &sz, sizeof(size_t));
        oss.write(size_str.data(), size_str.size());
    };

	// write_size(t->size());

    for (auto& inner : t) {
		// size of inner aggregate
        write_size(inner.size() * 9);

        // values
        for (auto& inst : inner) {
            char c = inst.declaration().as_entity() ? 'i' : 't';
            oss.put(c);
            size_t iden = inst.id() ? inst.id() : inst.identity();
            std::string iden_str;
            iden_str.resize(sizeof(size_t));
            memcpy(iden_str.data(), &iden, sizeof(size_t));
            oss.write(iden_str.data(), iden_str.size());
		}
    }

	val = oss.str();

    return true;
}

bool ::impl::serialize(std::string& val, const blank&)
{
    val.resize(1);
    val[0] = type_encoder::encode_type<blank>();
    return true;
}

bool ::impl::serialize(std::string& val, const derived&)
{
    val.resize(1);
    val[0] = type_encoder::encode_type<derived>();
    return true;
}

bool ::impl::serialize(std::string& val, const empty_aggregate&)
{
    val.resize(1);
    val[0] = type_encoder::encode_type<empty_aggregate>();
    return true;
}

bool ::impl::serialize(std::string& val, const empty_aggregate_of_aggregate&)
{
    val.resize(1);
    val[0] = type_encoder::encode_type<empty_aggregate_of_aggregate>();
    return true;
}

bool ::impl::serialize(std::string& val, const boost::logic::tribool& t)
{
    char tt = t == boost::logic::indeterminate ? 2 : t ? 1 : 0;
    val.resize(sizeof(char) + 1);
    val[0] = type_encoder::encode_type<boost::logic::tribool>();
    memcpy(val.data() + 1, &tt, sizeof(char));
    return true;
}

bool ::impl::serialize(std::string& val, const boost::dynamic_bitset<>& t)
{
    std::string tmp;
    boost::to_string(t, tmp);
	val = std::string(type_encoder::encode_type<boost::dynamic_bitset<>>(), 1) + tmp;
    return true;
}

bool ::impl::deserialize(ifcopenshell::impl::rocks_db_file_storage*, const std::string& val, boost::logic::tribool& t) {
    if (val[0] != type_encoder::encode_type<boost::logic::tribool>()) {
        return false;
    }
    if (val[1] == 0) {
        t = false;
    } else if (val[1] == 1) {
        t = true;
    } else if (val[1] == 2) {
        t = boost::logic::indeterminate;
    } else {
        return false;
    }
    return true;
}

bool ::impl::deserialize(ifcopenshell::impl::rocks_db_file_storage*, const std::string& val, boost::dynamic_bitset<>& t) {
    if (val[0] != type_encoder::encode_type<boost::dynamic_bitset<>>()) {
        return false;
    }
    t = boost::dynamic_bitset<>(val.substr(1));
    return true;
}

bool ::impl::deserialize(ifcopenshell::impl::rocks_db_file_storage* storage, const std::string& val, std::vector<express::base>& t) {
    auto n = (val.size() - 1) / (sizeof(size_t) + 1);
    for (int i = 0; i < n; ++i) {
        auto ptr = val.data() + 1 + (sizeof(size_t) + 1) * i;
        auto tt = *ptr;
        ptr++;
        size_t v;
        memcpy(&v, ptr, sizeof(size_t));
        if (tt == 'i') {
            t.push_back(storage->assert_existance(v, ifcopenshell::impl::rocks_db_file_storage::entityinstance_ref));
        } else if (tt == 't') {
            t.push_back(storage->assert_existance(v, ifcopenshell::impl::rocks_db_file_storage::typedecl_ref));
        } else {
			return false;
        }
    }
    return true;
}

bool ::impl::deserialize(ifcopenshell::impl::rocks_db_file_storage* storage, const std::string& val, std::vector<std::vector<express::base>>& t) {
	char const* ptr = val.data() + 1;

	// size_t outer_size;
	// memcpy(&outer_size, ptr, sizeof(size_t));
	// ptr += sizeof(size_t);

    while (ptr < val.data() + val.size()) {
		size_t inner_size;
		memcpy(&inner_size, ptr, sizeof(size_t));
		ptr += sizeof(size_t);

        if (ptr + inner_size * (sizeof(size_t) + 1) > val.data() + val.size()) {
			return false;
		}

        auto& inner = t.emplace_back();
		inner.reserve(inner_size);

        for (size_t i = 0; i < inner_size; ++i) {
            auto tt = *ptr;
            ptr++;
            size_t v;
            memcpy(&v, ptr, sizeof(size_t));
            ptr += sizeof(size_t);
            if (tt == 'i') {
                inner.push_back(storage->assert_existance(v, ifcopenshell::impl::rocks_db_file_storage::entityinstance_ref));
            } else if (tt == 't') {
                inner.push_back(storage->assert_existance(v, ifcopenshell::impl::rocks_db_file_storage::typedecl_ref));
            } else {
                return false;
            }
        }
    }
    return true;
}

template<typename T>
bool rocks_db_attribute_storage::has(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, std::size_t index) const
{
    // @todo unify with other implementation functions
    const bool is_header = decl->schema() == &Header_section_schema::get_schema();
    ifcopenshell::impl::rocks_db_file_storage* rdb_storage = (ifcopenshell::impl::rocks_db_file_storage*)storage;
    std::string v;
    auto success = rdb_storage->db->Get(
        rocksdb::ReadOptions{},
        (is_header ? "h|" : (decl->as_entity() ? "i|" : "t|")) +
        (is_header ? decl->name() : std::to_string(identity)) + "|" +
        std::to_string(index), &v);
    if constexpr (std::is_same_v<std::decay_t<T>, blank>) {
        if (!success.ok()) {
            return true;
        }
    }
    return v.size() && v[0] == type_encoder::encode_type<T>();
}

template<typename T>
void rocks_db_attribute_storage::set(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, std::size_t index, const T& value)
{
    const bool is_header = decl->schema() == &Header_section_schema::get_schema();
    ifcopenshell::impl::rocks_db_file_storage* rdb_storage = (ifcopenshell::impl::rocks_db_file_storage*)storage;
    std::string v;
    ::impl::serialize(v, value);
    rdb_storage->db->Put(
        rdb_storage->wopts,
        (is_header ? "h|" : (decl->as_entity() ? "i|" : "t|")) +
        (is_header ? decl->name() : std::to_string(identity)) + "|" +
        std::to_string(index), v);
}

template IFC_PARSE_API void rocks_db_attribute_storage::set<blank>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const blank& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<int64_t>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const int64_t& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<bool>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const bool& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<boost::logic::tribool>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const boost::logic::tribool& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<double>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const double& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::string>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const std::string& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<boost::dynamic_bitset<>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const boost::dynamic_bitset<>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<enumeration_reference>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const enumeration_reference& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<express::base>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, express::base const& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<int64_t>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const std::vector<int64_t>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<double>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const std::vector<double>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<std::string>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const std::vector<std::string>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<boost::dynamic_bitset<>>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const std::vector<boost::dynamic_bitset<>>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<express::base>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const std::vector<express::base>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<std::vector<int64_t>>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const std::vector<std::vector<int64_t>>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<std::vector<double>>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const std::vector<std::vector<double>>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<std::vector<express::base>>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const std::vector<std::vector<express::base>>& value);

// @todo why do these need to be included, but are not in BaseEntity::set()?
template IFC_PARSE_API void rocks_db_attribute_storage::set<derived>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const derived& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<empty_aggregate>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const empty_aggregate& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<empty_aggregate_of_aggregate>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index, const empty_aggregate_of_aggregate& value);

template IFC_PARSE_API bool rocks_db_attribute_storage::has<blank>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<int64_t>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<bool>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<boost::logic::tribool>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<double>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::string>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<boost::dynamic_bitset<>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<enumeration_reference>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<express::base>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<int64_t>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<double>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<std::string>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<boost::dynamic_bitset<>>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<express::base>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<std::vector<int64_t>>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<std::vector<double>>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<std::vector<express::base>>>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;

// @todo why do these need to be included, but are not in BaseEntity::set()?
template IFC_PARSE_API bool rocks_db_attribute_storage::has<derived>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<empty_aggregate>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<empty_aggregate_of_aggregate>(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, size_t index) const;

template <typename T>
T* instance_data::get_storage_of_type() const {
    return std::visit([this](auto& m) -> T* {
        if constexpr (std::is_same_v<std::decay_t<decltype(m)>, T>) {
            return &m;
        }
        return nullptr;
    }, file()->storage_);
}

template IFC_PARSE_API ifcopenshell::impl::in_memory_file_storage* instance_data::get_storage_of_type<ifcopenshell::impl::in_memory_file_storage>() const;
template IFC_PARSE_API ifcopenshell::impl::rocks_db_file_storage* instance_data::get_storage_of_type<ifcopenshell::impl::rocks_db_file_storage>() const;

#endif
