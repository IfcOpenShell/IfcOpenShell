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

    // Trait to detect contiguous containers (vector / string)
    template <typename T>
    struct is_contiguous_container : std::false_type {};
    template <typename T, typename Alloc>
    struct is_contiguous_container<std::vector<T, Alloc>> : std::true_type {};
    template <typename CharT, typename Traits, typename Alloc>
    struct is_contiguous_container<std::basic_string<CharT, Traits, Alloc>> : std::true_type {};

    template <typename T>
    bool serialize(std::string& val, const T& t) {
        return false;
    }

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value, int>::type = 0>
    bool serialize(std::string& val, const T& t) {
        auto s = sizeof(typename T::value_type) * t.size();
        val.resize(s);
        val[0] = TypeEncoder::encode_type<T>();
        memcpy(val.data() + 1, t.data(), s);
        return true;
    }

    bool serialize(std::string& val, const IfcUtil::IfcBaseClass* t) {
        auto s = sizeof(size_t);
        val.resize(s + 2);
        val[0] = TypeEncoder::encode_type<IfcUtil::IfcBaseClass*>();
        // 1 = entity - stored by id (entity name)
        // 2 = type - stored by identity (internal counter in class)
        val[1] = t->declaration().as_entity() ? 1 : 2;
        size_t iden = t->declaration().as_entity() ? t->id() : t->identity();
        memcpy(val.data() + 2, &iden, s);
        return true;
    }


    bool serialize(std::string& val, const EnumerationReference& v) {
        auto s = sizeof(size_t);
        val.resize(s * 2 + 1);
        val[0] = TypeEncoder::encode_type<EnumerationReference>();
        size_t vv = v.enumeration()->index_in_schema();
        memcpy(val.data() + 1, &vv, sizeof(size_t));
        vv = v.index();
        memcpy(val.data() + 1, &vv, sizeof(size_t));
        return true;
    }

    bool serialize(std::string& val, aggregate_of_instance::ptr& t) {
        std::vector<size_t> ids;
        // @nb this has to be identity, because needs to work for typedecls as well
        std::transform(t->begin(), t->end(), std::back_inserter(ids), [](auto& x) { return x->identity(); });
        return false;
    }

    bool serialize(std::string& val, aggregate_of_aggregate_of_instance::ptr& t) {
        return false;
    }

    /*
    template <typename T>
    bool deserialize(std::string& val, const T& t) {}
    */

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value, int>::type = 0>
    bool deserialize(std::string& val, T& t) {
        // @todo vector of vector
        if (val[0] != TypeEncoder::encode_type<T>()) {
            return false;
        }
        auto s = (val.size() - 1) / sizeof(typename T::value_type);
        t.resize(s);
        memcpy(t.data(), val.data() + 1, s * sizeof(typename T::value_type));
        return true;
    }

    template <typename T, typename std::enable_if<std::is_integral_v<T> || std::is_floating_point_v<T>, int>::type = 0>
    bool deserialize(std::string& val, T& t) {
        if (val[0] != TypeEncoder::encode_type<T>()) {
            return false;
        }
        auto s = (val.size() - 1) / sizeof(T);
        memcpy(&t, val.data() + 1, sizeof(T));
        return true;
    }

    bool deserialize(std::string& val, boost::logic::tribool& t) {
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
    }

    bool deserialize(std::string& val, boost::dynamic_bitset<>& t) {
        if (val[0] != TypeEncoder::encode_type<boost::dynamic_bitset<>>()) {
            return false;
        }
        t = boost::dynamic_bitset<>(val.substr(1));
        return true;
    }

    bool deserialize(std::string& val, aggregate_of_instance::ptr& t) {
        return false;
    }

    bool deserialize(std::string& val, aggregate_of_aggregate_of_instance::ptr& t) {
        return false;
    }
}

namespace {
    template<typename T>
    inline T dispatch_get_(AttributeValue::pointer_type array_, uint8_t storage_model_, size_t instance_name_, uint8_t index_)
    {
        if (storage_model_ == 0) {
            return array_.storage_ptr->get<T>(index_);
        } else {
            T val;
            if constexpr (
                // the following types cannot be directly deserialized from rocksdb, but need to be constructed
                !std::is_same_v<T, EnumerationReference> &&
                !std::is_same_v<std::remove_cv_t<std::remove_pointer_t<T>>, IfcUtil::IfcBaseClass>)
            {
                std::string str;
                array_.db_ptr->db->Get(rocksdb::ReadOptions{}, "a|" + std::to_string(instance_name_) + "|" + std::to_string(index_), &str);
                deserialize(str, val);
            }
            return val;
        }
    }

    template<typename T>
    inline bool dispatch_has_(AttributeValue::pointer_type array_, uint8_t storage_model_, size_t instance_name_, uint8_t index_)
    {
        if (storage_model_ == 0) {
            return array_.storage_ptr->has<T>(index_);
        } else {
            std::string str;
            array_.db_ptr->db->Get(rocksdb::ReadOptions{}, "a|" + std::to_string(instance_name_) + "|" + std::to_string(index_), &str);
            return str[0] == TypeEncoder::encode_type<T>();
        }
    }

    inline size_t dispatch_index_(AttributeValue::pointer_type array_, uint8_t storage_model_, size_t instance_name_, uint8_t index_)
    {
        if (storage_model_ == 0) {
            return array_.storage_ptr->index(index_);
        } else {
            std::string str;
            array_.db_ptr->db->Get(rocksdb::ReadOptions{}, "a|" + std::to_string(instance_name_) + "|" + std::to_string(index_), &str);
            return (size_t) str[0] - 'A';
        }
    }

}

AttributeValue::operator int() const
{
    return dispatch_get_<int>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator bool() const
{
    return dispatch_get_<bool>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator double() const
{
    return dispatch_get_<double>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator boost::logic::tribool() const
{
    if (dispatch_has_<bool>(array_, storage_model_, instance_name_, index_)) {
        return dispatch_get_<bool>(array_, storage_model_, instance_name_, index_);
    }
    return dispatch_get_<boost::logic::tribool>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator std::string() const
{
    if (dispatch_has_<EnumerationReference>(array_, storage_model_, instance_name_, index_)) {
        // @todo this is silly, but the way things currently work,
        // @todo also we don't really need to store a reference to the enumeration type, when this same type is already stored on the definition of the entity and no other value can be provided.
        if (storage_model_ == 0) {
            return dispatch_get_<EnumerationReference>(array_, storage_model_, instance_name_, index_).value();
        } else {
            std::string str;
            array_.db_ptr->db->Get(rocksdb::ReadOptions{}, "a|" + std::to_string(instance_name_) + "|" + std::to_string(index_), &str);
            size_t v;
            memcpy(&v, str.data() + 1, sizeof(size_t));
            auto decl = schema_->declarations()[v]->as_enumeration_type();
            memcpy(&v, str.data() + 5, sizeof(size_t));
            return decl->lookup_enum_value(v);
        }
    }
    return dispatch_get_<std::string>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator EnumerationReference() const
{
    if (storage_model_ == 0) {
        return dispatch_get_<EnumerationReference>(array_, storage_model_, instance_name_, index_);
    } else {
        std::string str;
        array_.db_ptr->db->Get(rocksdb::ReadOptions{}, "a|" + std::to_string(instance_name_) + "|" + std::to_string(index_), &str);
        size_t v;
        memcpy(&v, str.data() + 1, sizeof(size_t));
        auto decl = schema_->declarations()[v]->as_enumeration_type();
        memcpy(&v, str.data() + 5, sizeof(size_t));
        return EnumerationReference(decl, v);
    }
}

AttributeValue::operator boost::dynamic_bitset<>() const
{
    return dispatch_get_<boost::dynamic_bitset<>>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator IfcUtil::IfcBaseClass* () const
{
    if (storage_model_ == 0) {
        return dispatch_get_<IfcUtil::IfcBaseClass*>(array_, storage_model_, instance_name_, index_);
    } else {
        std::string str;
        array_.db_ptr->db->Get(rocksdb::ReadOptions{}, "a|" + std::to_string(instance_name_) + "|" + std::to_string(index_), &str);
        size_t v;
        memcpy(&v, str.data() + 1, sizeof(size_t));
        auto decl = schema_->declarations()[v]->as_enumeration_type();
        memcpy(&v, str.data() + 5, sizeof(size_t));
        return array_.db_ptr->assert_existance(v);
    }
}

AttributeValue::operator std::vector<int>() const
{
    return dispatch_get_<std::vector<int>>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator std::vector<double>() const
{
    return dispatch_get_<std::vector<double>>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator std::vector<std::string>() const
{
    return dispatch_get_<std::vector<std::string>>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator std::vector<boost::dynamic_bitset<>>() const
{
    return dispatch_get_<std::vector<boost::dynamic_bitset<>>>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator boost::shared_ptr<aggregate_of_instance>() const
{
    return dispatch_get_<boost::shared_ptr<aggregate_of_instance>>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator std::vector<std::vector<int>>() const
{
    return dispatch_get_<std::vector<std::vector<int>>>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator std::vector<std::vector<double>>() const
{
    return dispatch_get_<std::vector<std::vector<double>>>(array_, storage_model_, instance_name_, index_);
}

AttributeValue::operator boost::shared_ptr<aggregate_of_aggregate_of_instance>() const
{
    return dispatch_get_<boost::shared_ptr<aggregate_of_aggregate_of_instance>>(array_, storage_model_, instance_name_, index_);
}

bool AttributeValue::isNull() const
{
    return dispatch_has_<Blank>(array_, storage_model_, instance_name_, index_);
}

unsigned int AttributeValue::size() const
{
    // @todo
    return array_.storage_ptr->apply_visitor(SizeVisitor{}, index_);
}

IfcUtil::ArgumentType AttributeValue::type() const
{
    return static_cast<IfcUtil::ArgumentType>(dispatch_index_(array_, storage_model_, instance_name_, index_));
}
