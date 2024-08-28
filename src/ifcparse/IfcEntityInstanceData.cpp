#include "IfcEntityInstanceData.h"
#include "IfcBaseClass.h"

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

AttributeValue::operator int() const
{
    return array_->get<int>(index_);
}

AttributeValue::operator bool() const
{
    return array_->get<bool>(index_);
}

AttributeValue::operator double() const
{
    return array_->get<double>(index_);
}

AttributeValue::operator boost::logic::tribool() const
{
    if (array_->has<bool>(index_)) {
        return array_->get<bool>(index_);
    }
    return array_->get<boost::logic::tribool>(index_);
}

AttributeValue::operator std::string() const
{
    if (array_->has<EnumerationReference>(index_)) {
        // @todo this is silly, but the way things currently work,
        // @todo also we don't really need to store a reference to the enumeration type, when this same type is already stored on the definition of the entity and no other value can be provided.
        return array_->get<EnumerationReference>(index_).value();
    }
    return array_->get<std::string>(index_);
}

AttributeValue::operator boost::dynamic_bitset<>() const
{
    return array_->get<boost::dynamic_bitset<>>(index_);
}

AttributeValue::operator IfcUtil::IfcBaseClass* () const
{
    return array_->get<IfcUtil::IfcBaseClass*>(index_);
}

AttributeValue::operator std::vector<int>() const
{
    return array_->get<std::vector<int>>(index_);
}

AttributeValue::operator std::vector<double>() const
{
    return array_->get<std::vector<double>>(index_);
}

AttributeValue::operator std::vector<std::string>() const
{
    return array_->get<std::vector<std::string>>(index_);
}

AttributeValue::operator std::vector<boost::dynamic_bitset<>>() const
{
    return array_->get<std::vector<boost::dynamic_bitset<>>>(index_);
}

AttributeValue::operator boost::shared_ptr<aggregate_of_instance>() const
{
    return array_->get<boost::shared_ptr<aggregate_of_instance>>(index_);
}

AttributeValue::operator std::vector<std::vector<int>>() const
{
    return array_->get<std::vector<std::vector<int>>>(index_);
}

AttributeValue::operator std::vector<std::vector<double>>() const
{
    return array_->get<std::vector<std::vector<double>>>(index_);
}

AttributeValue::operator boost::shared_ptr<aggregate_of_aggregate_of_instance>() const
{
    return array_->get<boost::shared_ptr<aggregate_of_aggregate_of_instance>>(index_);
}

bool AttributeValue::isNull() const
{
    return array_->has<Blank>(index_);
}

unsigned int AttributeValue::size() const
{
    return array_->apply_visitor(SizeVisitor{}, index_);
}

IfcUtil::ArgumentType AttributeValue::type() const
{
    return static_cast<IfcUtil::ArgumentType>(array_->index(index_));
}
