#include "IfcEntityInstanceData.h"
#include "IfcBaseClass.h"
#include "IfcFile.h"

// @todo is size() still needed?
class SizeVisitor {
public:
    typedef int result_type;

    int operator()(const Blank& /*i*/) const { return -1; }
    int operator()(const Derived& /*i*/) const { return -1; }
    int operator()(const int& /*i*/) const { return -1; }
    int operator()(const bool& /*i*/) const { return -1; }
    int operator()(const boost::logic::tribool& /*i*/) const { return -1; }
    int operator()(const double& /*i*/) const { return -1; }
    int operator()(const std::string& /*i*/) const { return -1; }
    int operator()(const boost::dynamic_bitset<>& /*i*/) const { return -1; }
    int operator()(const empty_aggregate_t& /*unused*/) const { return 0; }
    int operator()(const empty_aggregate_of_aggregate_t& /*unused*/) const { return 0; }
    int operator()(const std::vector<int>& i) const { return (int)i.size(); }
    int operator()(const std::vector<double>& i) const { return (int)i.size(); }
    int operator()(const std::vector<std::vector<int>>& i) const { return (int)i.size(); }
    int operator()(const std::vector<std::vector<double>>& i) const { return (int)i.size(); }
    int operator()(const std::vector<std::string>& i) const { return (int)i.size(); }
    int operator()(const std::vector<boost::dynamic_bitset<>>& i) const { return (int)i.size(); }
    int operator()(const EnumerationReference& /*i*/) const { return -1; }
    int operator()(const IfcUtil::IfcBaseClass* const& /*i*/) const { return -1; }
    int operator()(const aggregate_of_instance::ptr& i) const { return i->size(); }
    int operator()(const aggregate_of_aggregate_of_instance::ptr& i) const { return i->size(); }
};

namespace {
    template<typename T>
    inline T dispatch_get_(AttributeValue::pointer_type array_, uint8_t storage_model_, size_t instance_name_, const IfcParse::declaration* entity_or_type, uint8_t index_)
    {
        if (storage_model_ == 0) {
            return array_.storage_ptr->get<T>(index_);
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else {
            T val = T{};
            const bool is_header = entity_or_type->schema() == &Header_section_schema::get_schema();
            if constexpr (
                // the following types cannot be directly deserialized from rocksdb, but need to be constructed
                !std::is_same_v<T, EnumerationReference> &&
                !std::is_same_v<std::remove_cv_t<std::remove_pointer_t<T>>, IfcUtil::IfcBaseClass>)
            {
                std::string str;
                array_.db_ptr->db->Get(rocksdb::ReadOptions{}, 
                    (is_header ? "h|" : (entity_or_type->as_entity() ? "i|" : "t|")) +
                    (is_header ? entity_or_type->name() : std::to_string(instance_name_)) + "|" +
                    std::to_string(index_), &str);
                impl::deserialize(array_.db_ptr, str, val);
            } else {
                static_assert(
                    std::is_same_v<T, EnumerationReference> ||
                    std::is_same_v<std::remove_cv_t<std::remove_pointer_t<T>>, IfcUtil::IfcBaseClass>,
                    "RocksDB deserialization must be specialized for this EnumerationReference and IfcBaseClass*"
                );
            }
            return val;
        }
#endif
    }

    template<typename T>
    inline bool dispatch_has_(AttributeValue::pointer_type array_, uint8_t storage_model_, size_t instance_name_, const IfcParse::declaration* entity_or_type, uint8_t index_)
    {
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
            if constexpr (std::is_same_v<T, Blank>) {
                if (str.size() == 0) {
                    return true;
                }
            }
            return str[0] == TypeEncoder::encode_type<T>();
        }
#endif
    }

    inline size_t dispatch_index_(AttributeValue::pointer_type array_, uint8_t storage_model_, size_t instance_name_, const IfcParse::declaration* entity_or_type, uint8_t index_)
    {
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
                return TypeEncoder::encode_type<Blank>() - 'A';
            }
            return (size_t) str[0] - 'A';
        }
#endif 
    }
}

AttributeValue::operator int() const
{
    return dispatch_get_<int>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator bool() const
{
    return dispatch_get_<bool>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator double() const
{
    return dispatch_get_<double>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator boost::logic::tribool() const
{
    if (dispatch_has_<bool>(array_, storage_model_, instance_name_, entity_or_type_, index_)) {
        return dispatch_get_<bool>(array_, storage_model_, instance_name_, entity_or_type_, index_);
    }
    return dispatch_get_<boost::logic::tribool>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator std::string() const
{
    if (dispatch_has_<EnumerationReference>(array_, storage_model_, instance_name_, entity_or_type_, index_)) {
        // @todo this is silly, but the way things currently work,
        // @todo also we don't really need to store a reference to the enumeration type, when this same type is already stored on the definition of the entity and no other value can be provided.
        if (storage_model_ == 0) {
            return dispatch_get_<EnumerationReference>(array_, storage_model_, instance_name_, entity_or_type_, index_).value();
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

AttributeValue::operator EnumerationReference() const
{
    if (storage_model_ == 0) {
        return dispatch_get_<EnumerationReference>(array_, storage_model_, instance_name_, entity_or_type_, index_);
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
        return EnumerationReference(decl, v);
    }
#endif
}

AttributeValue::operator boost::dynamic_bitset<>() const
{
    return dispatch_get_<boost::dynamic_bitset<>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator IfcUtil::IfcBaseClass* () const
{
    if (storage_model_ == 0) {
        return dispatch_get_<IfcUtil::IfcBaseClass*>(array_, storage_model_, instance_name_, entity_or_type_, index_);
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
            return array_.db_ptr->assert_existance(v, IfcParse::impl::rocks_db_file_storage::entityinstance_ref);
        } else if (str.size() > 1 && str[1] == 't') {
            // type reference by Identity
            return array_.db_ptr->assert_existance(v, IfcParse::impl::rocks_db_file_storage::typedecl_ref);
        } else {
            throw std::runtime_error("Invalid data encountered");
        }
    }
#endif
}

AttributeValue::operator std::vector<int>() const
{
    return dispatch_get_<std::vector<int>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator std::vector<double>() const
{
    return dispatch_get_<std::vector<double>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator std::vector<std::string>() const
{
    return dispatch_get_<std::vector<std::string>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator std::vector<boost::dynamic_bitset<>>() const
{
    return dispatch_get_<std::vector<boost::dynamic_bitset<>>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator boost::shared_ptr<aggregate_of_instance>() const
{
    return dispatch_get_<boost::shared_ptr<aggregate_of_instance>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator std::vector<std::vector<int>>() const
{
    return dispatch_get_<std::vector<std::vector<int>>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator std::vector<std::vector<double>>() const
{
    return dispatch_get_<std::vector<std::vector<double>>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

AttributeValue::operator boost::shared_ptr<aggregate_of_aggregate_of_instance>() const
{
    return dispatch_get_<boost::shared_ptr<aggregate_of_aggregate_of_instance>>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

bool AttributeValue::isNull() const
{
    return dispatch_has_<Blank>(array_, storage_model_, instance_name_, entity_or_type_, index_);
}

unsigned int AttributeValue::size() const
{
    // @todo
    return array_.storage_ptr->apply_visitor(SizeVisitor{}, index_);
}

IfcUtil::ArgumentType AttributeValue::type() const
{
    return static_cast<IfcUtil::ArgumentType>(dispatch_index_(array_, storage_model_, instance_name_, entity_or_type_, index_));
}

#ifdef IFOPSH_WITH_ROCKSDB

bool impl::serialize(std::string& val, const IfcUtil::IfcBaseClass* t)
{
    auto s = sizeof(size_t);
    val.resize(s + 2);
    val[0] = TypeEncoder::encode_type<IfcUtil::IfcBaseClass*>();
    // 1 = entity - stored by id (entity name)
    // 2 = type - stored by identity (internal counter in class)
    val[1] = t->declaration().as_entity() ? 'i' : 't';
    size_t iden = t->id() ? t->id() : t->identity();
    memcpy(val.data() + 2, &iden, s);
    return true;
}

bool impl::serialize(std::string& val, const EnumerationReference& v)
{
    auto s = sizeof(size_t);
    val.resize(s * 2 + 1);
    val[0] = TypeEncoder::encode_type<EnumerationReference>();
    size_t vv = v.enumeration()->index_in_schema();
    memcpy(val.data() + 1, &vv, sizeof(size_t));
    vv = v.index();
    memcpy(val.data() + 1 + sizeof(size_t), &vv, sizeof(size_t));
    return true;
}

bool impl::serialize(std::string& val, const aggregate_of_instance::ptr& t)
{
    // no attempt at alignment
    val.resize(t->size() * (sizeof(size_t) + 1) + 1);
    val[0] = TypeEncoder::encode_type<aggregate_of_instance::ptr>();
    char* ptr = val.data() + 1;
    for (auto it = t->begin(); it != t->end(); ++it) {
        *ptr = (*it)->declaration().as_entity() ? 'i' : 't';
        ptr++;
        size_t iden = (*it)->id() ? (*it)->id() : (*it)->identity();
        memcpy(ptr, &iden, sizeof(size_t));
        ptr += sizeof(size_t);
    }
    return true;
}

bool impl::serialize(std::string& val, const aggregate_of_aggregate_of_instance::ptr& t)
{
    std::ostringstream oss;
	oss.put(TypeEncoder::encode_type<aggregate_of_aggregate_of_instance::ptr>());
    
    auto write_size = [&oss](size_t sz) {
        std::string size_str;
        size_str.resize(sizeof(size_t));
        memcpy(size_str.data(), &sz, sizeof(size_t));
        oss.write(size_str.data(), size_str.size());
    };

	// write_size(t->size());

    for (auto it = t->begin(); it != t->end(); ++it) {
		// size of inner aggregate
        write_size(it->size() * 9);

        // values
        for (auto jt = it->begin(); jt != it->end(); ++jt) {
            char c = (*jt)->declaration().as_entity() ? 'i' : 't';
            oss.put(c);
            size_t iden = (*jt)->id() ? (*jt)->id() : (*jt)->identity();
            std::string iden_str;
            iden_str.resize(sizeof(size_t));
            memcpy(iden_str.data(), &iden, sizeof(size_t));
            oss.write(iden_str.data(), iden_str.size());
		}
    }

	val = oss.str();

    return true;
}

bool impl::serialize(std::string& val, const Blank&)
{
    val.resize(1);
    val[0] = TypeEncoder::encode_type<Blank>();
    return true;
}

bool impl::serialize(std::string& val, const Derived&)
{
    val.resize(1);
    val[0] = TypeEncoder::encode_type<Derived>();
    return true;
}

bool impl::serialize(std::string& val, const empty_aggregate_t&)
{
    val.resize(1);
    val[0] = TypeEncoder::encode_type<empty_aggregate_t>();
    return true;
}

bool impl::serialize(std::string& val, const empty_aggregate_of_aggregate_t&)
{
    val.resize(1);
    val[0] = TypeEncoder::encode_type<empty_aggregate_of_aggregate_t>();
    return true;
}

bool impl::serialize(std::string& val, const boost::logic::tribool& t)
{
    char tt = t == boost::logic::indeterminate ? 2 : t ? 1 : 0;
    val.resize(sizeof(char) + 1);
    val[0] = TypeEncoder::encode_type<boost::logic::tribool>();
    memcpy(val.data() + 1, &tt, sizeof(char));
    return true;
}

bool impl::serialize(std::string& val, const boost::dynamic_bitset<>& t)
{
    std::string tmp;
    boost::to_string(t, tmp);
	val = std::string(TypeEncoder::encode_type<boost::dynamic_bitset<>>(), 1) + tmp;
    return true;
}

bool impl::deserialize(IfcParse::impl::rocks_db_file_storage*, const std::string& val, boost::logic::tribool& t) {
    if (val[0] != TypeEncoder::encode_type<boost::logic::tribool>()) {
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

bool impl::deserialize(IfcParse::impl::rocks_db_file_storage*, const std::string& val, boost::dynamic_bitset<>& t) {
    if (val[0] != TypeEncoder::encode_type<boost::dynamic_bitset<>>()) {
        return false;
    }
    t = boost::dynamic_bitset<>(val.substr(1));
    return true;
}

bool impl::deserialize(IfcParse::impl::rocks_db_file_storage* storage, const std::string& val, aggregate_of_instance::ptr& t) {
    t.reset(new aggregate_of_instance);
    auto n = (val.size() - 1) / (sizeof(size_t) + 1);
    for (int i = 0; i < n; ++i) {
        auto ptr = val.data() + 1 + (sizeof(size_t) + 1) * i;
        auto tt = *ptr;
        ptr++;
        size_t v;
        memcpy(&v, ptr, sizeof(size_t));
        if (tt == 'i') {
            t->push(storage->assert_existance(v, IfcParse::impl::rocks_db_file_storage::entityinstance_ref));
        } else if (tt == 't') {
            t->push(storage->assert_existance(v, IfcParse::impl::rocks_db_file_storage::typedecl_ref));
        } else {
			return false;
        }
    }
    return true;
}

bool impl::deserialize(IfcParse::impl::rocks_db_file_storage* storage, const std::string& val, aggregate_of_aggregate_of_instance::ptr& t) {
	t.reset(new aggregate_of_aggregate_of_instance);
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

        std::vector<IfcUtil::IfcBaseClass*> inner;
		inner.reserve(inner_size);

        for (size_t i = 0; i < inner_size; ++i) {
            auto tt = *ptr;
            ptr++;
            size_t v;
            memcpy(&v, ptr, sizeof(size_t));
            ptr += sizeof(size_t);
            if (tt == 'i') {
                inner.push_back(storage->assert_existance(v, IfcParse::impl::rocks_db_file_storage::entityinstance_ref));
            } else if (tt == 't') {
                inner.push_back(storage->assert_existance(v, IfcParse::impl::rocks_db_file_storage::typedecl_ref));
            } else {
                return false;
            }
        }

		t->push(inner);
    }
    return true;
}

template<typename T>
bool rocks_db_attribute_storage::has(void* storage, const IfcParse::declaration* decl, std::size_t identity, std::size_t index) const
{
    // @todo unify with other implementation functions
    const bool is_header = decl->schema() == &Header_section_schema::get_schema();
    IfcParse::impl::rocks_db_file_storage* rdb_storage = (IfcParse::impl::rocks_db_file_storage*)storage;
    std::string v;
    auto success = rdb_storage->db->Get(
        rocksdb::ReadOptions{},
        (is_header ? "h|" : (decl->as_entity() ? "i|" : "t|")) +
        (is_header ? decl->name() : std::to_string(identity)) + "|" +
        std::to_string(index), &v);
    if constexpr (std::is_same_v<std::decay_t<T>, Blank>) {
        if (!success.ok()) {
            return true;
        }
    }
    return v.size() && v[0] == TypeEncoder::encode_type<T>();
}

template<typename T>
void rocks_db_attribute_storage::set(void* storage, const IfcParse::declaration* decl, std::size_t identity, std::size_t index, const T& value)
{
    const bool is_header = decl->schema() == &Header_section_schema::get_schema();
    IfcParse::impl::rocks_db_file_storage* rdb_storage = (IfcParse::impl::rocks_db_file_storage*)storage;
    std::string v;
    impl::serialize(v, value);
    rdb_storage->db->Put(
        rdb_storage->wopts,
        (is_header ? "h|" : (decl->as_entity() ? "i|" : "t|")) +
        (is_header ? decl->name() : std::to_string(identity)) + "|" + 
        std::to_string(index), v);
}

template IFC_PARSE_API void rocks_db_attribute_storage::set<Blank>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const Blank& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<int>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const int& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<bool>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const bool& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<boost::logic::tribool>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const boost::logic::tribool& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<double>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const double& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::string>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const std::string& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<boost::dynamic_bitset<>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const boost::dynamic_bitset<>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<EnumerationReference>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const EnumerationReference& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<IfcUtil::IfcBaseClass*>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, IfcUtil::IfcBaseClass* const& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<int>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const std::vector<int>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<double>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const std::vector<double>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<std::string>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const std::vector<std::string>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<boost::dynamic_bitset<>>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const std::vector<boost::dynamic_bitset<>>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<aggregate_of_instance::ptr>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const aggregate_of_instance::ptr& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<std::vector<int>>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const std::vector<std::vector<int>>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<std::vector<std::vector<double>>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const std::vector<std::vector<double>>& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<aggregate_of_aggregate_of_instance::ptr>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const aggregate_of_aggregate_of_instance::ptr& value);

// @todo why do these need to be included, but are not in BaseEntity::set()?
template IFC_PARSE_API void rocks_db_attribute_storage::set<Derived>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const Derived& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<empty_aggregate_t>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const empty_aggregate_t& value);
template IFC_PARSE_API void rocks_db_attribute_storage::set<empty_aggregate_of_aggregate_t>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index, const empty_aggregate_of_aggregate_t& value);



template IFC_PARSE_API bool rocks_db_attribute_storage::has<Blank>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<int>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<bool>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<boost::logic::tribool>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<double>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::string>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<boost::dynamic_bitset<>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<EnumerationReference>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<IfcUtil::IfcBaseClass*>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<int>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<double>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<std::string>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<boost::dynamic_bitset<>>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<aggregate_of_instance::ptr>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<std::vector<int>>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<std::vector<std::vector<double>>>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<aggregate_of_aggregate_of_instance::ptr>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;

// @todo why do these need to be included, but are not in BaseEntity::set()?
template IFC_PARSE_API bool rocks_db_attribute_storage::has<Derived>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<empty_aggregate_t>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;
template IFC_PARSE_API bool rocks_db_attribute_storage::has<empty_aggregate_of_aggregate_t>(void* storage, const IfcParse::declaration* decl, std::size_t identity, size_t index) const;

#endif