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

#ifndef IFCBASECLASS_H
#define IFCBASECLASS_H

#include "Argument.h"
#include "ifc_parse_api.h"
#include "IfcEntityInstanceData.h"
#include "IfcSchema.h"
#include "utils.h"

#include <atomic>
#include <boost/shared_ptr.hpp>

class aggregate_of_instance;

namespace IfcParse {
    class IfcFile;
}

namespace IfcUtil {

class IFC_PARSE_API IfcBaseInterface {
  protected:
    static bool is_null(const IfcBaseInterface* not_this) {
        return not_this == nullptr;
    }

    template <typename T>
    std::enable_if_t<!std::is_same<IfcBaseClass, T>::value && !std::is_same<IfcBaseEntity, T>::value && !std::is_same<IfcBaseType, T>::value> raise_error_on_concrete_class() const {
        throw IfcParse::IfcException("Instance of type " + this->declaration().name() + " cannot be cast to " + T::Class().name());
    }

    template <typename T>
    std::enable_if_t<std::is_same<IfcBaseClass, T>::value || std::is_same<IfcBaseEntity, T>::value || std::is_same<IfcBaseType, T>::value> raise_error_on_concrete_class() const {
        throw IfcParse::IfcException("Instance of type " + this->declaration().name() + " cannot be cast to base class");
    }

  public:
    virtual const IfcEntityInstanceData& data() const = 0;
    virtual IfcEntityInstanceData& data() = 0;
    virtual const IfcParse::declaration& declaration() const = 0;
    virtual ~IfcBaseInterface() {}

    template <class T>
    T* as(bool do_throw = false) {
        // @todo: do not allow this to be null in the first place
        if (is_null(this)) {
            return static_cast<T*>(0);
        }
        auto type = dynamic_cast<T*>(this);
        if (do_throw && !type) {
            raise_error_on_concrete_class<T>();
        }
        return type;
    }

    template <class T>
    const T* as(bool do_throw = false) const {
        if (is_null(this)) {
            return static_cast<const T*>(0);
        }
        auto type = dynamic_cast<const T*>(this);
        if (do_throw && !type) {
            raise_error_on_concrete_class<T>();
        }
        return type;
    }
};

class IFC_PARSE_API IfcBaseClass : public virtual IfcBaseInterface {
 protected:
    static std::atomic_uint32_t counter_;

    uint32_t identity_;
public:
    uint32_t id_;
    IfcParse::IfcFile* file_;
protected:
    IfcEntityInstanceData data_;

public:
    IfcBaseClass(IfcEntityInstanceData&& data)
        : identity_(counter_++)
        , id_(0)
        , file_(nullptr)
        , data_(std::move(data))
    {}

    const IfcEntityInstanceData& data() const { return data_; }
    IfcEntityInstanceData& data() { return data_; }

    virtual const IfcParse::declaration& declaration() const = 0;

    template <typename T>
    void set_attribute_value(size_t i, const T& t);

    template <typename T>
    void set_attribute_value(const std::string& name, const T& t);
    
    void unset_attribute_value(size_t i);

    uint32_t identity() const { return identity_; }

    uint32_t id() const { return id_; }

    void toString(std::ostream&, bool upper = false) const;
};

class IFC_PARSE_API IfcLateBoundEntity : public IfcBaseClass {
  private:
    const IfcParse::declaration* decl_;

  public:
    IfcLateBoundEntity(const IfcParse::declaration* decl, IfcEntityInstanceData&& data) : IfcBaseClass(std::move(data)),
                                                                                         decl_(decl) {}

    virtual const IfcParse::declaration& declaration() const {
        return *decl_;
    }
};

class IFC_PARSE_API IfcBaseEntity : public IfcBaseClass {
  public:
    IfcBaseEntity(IfcEntityInstanceData&& data) : IfcBaseClass(std::move(data)) {}

    IfcBaseEntity(size_t n)
        : IfcBaseClass(IfcEntityInstanceData(storage_t(n)))
    {}

    virtual const IfcParse::entity& declaration() const = 0;

    AttributeValue get(const std::string& name) const;

    template <typename T>
    T get_value(const std::string& name) const;

    template <typename T>
    T get_value(const std::string& name, const T& default_value) const;

    boost::shared_ptr<aggregate_of_instance> get_inverse(const std::string& name) const;

    unsigned set_id(const boost::optional<unsigned>& i);
};

// TODO: Investigate whether these should be template classes instead
class IFC_PARSE_API IfcBaseType : public IfcBaseClass {
  public:
    IfcBaseType(IfcEntityInstanceData&& data)\
        : IfcBaseClass(std::move(data))
    {}

    IfcBaseType()
        : IfcBaseClass(IfcEntityInstanceData(storage_t(1)))
    {}

    virtual const IfcParse::declaration& declaration() const = 0;
};

} // namespace IfcUtil

namespace IfcUtil {
template <typename T>
T IfcBaseEntity::get_value(const std::string& name) const {
    auto attr = get(name);
    return (T) attr;
}

template <typename T>
T IfcBaseEntity::get_value(const std::string& name, const T& default_value) const {
    auto attr = get(name);
    if (attr.isNull()) {
        return default_value;
    }
    return (T) attr;
}

} // namespace IfcUtil

template <class U>
typename U::list::ptr aggregate_of_instance::as() {
    typename U::list::ptr result(new typename U::list);
    for (it i = begin(); i != end(); ++i) {
        if ((*i)->template as<U>()) {
            result->push((*i)->template as<U>());
        }
    }
    return result;
}

template <class U>
typename aggregate_of_aggregate_of<U>::ptr aggregate_of_aggregate_of_instance::as() {
    typename aggregate_of_aggregate_of<U>::ptr result(new aggregate_of_aggregate_of<U>);
    for (outer_it outer = begin(); outer != end(); ++outer) {
        const std::vector<IfcUtil::IfcBaseClass*>& from = *outer;
        typename std::vector<U*> to;
        for (inner_it inner = from.begin(); inner != from.end(); ++inner) {
            if ((*inner)->template as<U>()) {
                to.push_back((*inner)->template as<U>());
            }
        }
        result->push(to);
    }
    return result;
}

#endif
