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

#ifndef IFCENTITYLIST_H
#define IFCENTITYLIST_H

// #include "IfcBaseClass.h"
#include "ifc_parse_api.h"

#include <boost/shared_ptr.hpp>
#include <set>
#include <vector>

namespace IfcParse {
    class declaration;
}
namespace IfcUtil {
    class IfcBaseClass;
}

template <class T>
class aggregate_of;

class IFC_PARSE_API aggregate_of_instance {
    std::vector<IfcUtil::IfcBaseClass*> list_;

  public:
    typedef boost::shared_ptr<aggregate_of_instance> ptr;
    typedef std::vector<IfcUtil::IfcBaseClass*>::const_iterator it;
    void push(IfcUtil::IfcBaseClass* instance);
    void push(const ptr& instance);
    it begin();
    it end();
    IfcUtil::IfcBaseClass* operator[](int index);
    unsigned int size() const;
    void reserve(unsigned capacity);
    bool contains(IfcUtil::IfcBaseClass*) const;
    
    template <class U>
    typename U::list::ptr as();

    void remove(IfcUtil::IfcBaseClass*);
    aggregate_of_instance::ptr filtered(const std::set<const IfcParse::declaration*>& entities);
    aggregate_of_instance::ptr unique();
};

template <class T>
class aggregate_of {
    std::vector<T*> list_;

  public:
    typedef boost::shared_ptr<aggregate_of<T>> ptr;
    typedef typename std::vector<T*>::const_iterator it;
    void push(T* type) {
        if (type) {
            list_.push_back(type);
        }
    }
    void push(ptr instance) {
        if (instance) {
            for (typename T::list::it it = instance->begin(); it != instance->end(); ++it) {
                push(*it);
            }
        }
    }
    it begin() { return list_.begin(); }
    it end() { return list_.end(); }
    unsigned int size() const { return (unsigned int)list_.size(); }
    aggregate_of_instance::ptr generalize() {
        aggregate_of_instance::ptr result(new aggregate_of_instance());
        for (it i = begin(); i != end(); ++i) {
            result->push((*i)->template as<IfcUtil::IfcBaseClass>());
        }
        return result;
    }
    bool contains(T* type) const { return std::find(list_.begin(), list_.end(), type) != list_.end(); }
    template <class U>
    typename U::list::ptr as() {
        typename U::list::ptr result(new typename U::list);
        for (it i = begin(); i != end(); ++i) {
            if ((*i)->template as<U>()) {
                result->push((*i)->template as<U>());
            }
        }
        return result;
    }
    void remove(T* type) {
        typename std::vector<T*>::iterator iter;
        while ((iter = std::find(list_.begin(), list_.end(), type)) != list_.end()) {
            list_.erase(iter);
        }
    }
};

template <class T>
class aggregate_of_aggregate_of;

class IFC_PARSE_API aggregate_of_aggregate_of_instance {
    std::vector<std::vector<IfcUtil::IfcBaseClass*>> list_;

  public:
    typedef boost::shared_ptr<aggregate_of_aggregate_of_instance> ptr;
    typedef std::vector<std::vector<IfcUtil::IfcBaseClass*>>::const_iterator outer_it;
    typedef std::vector<IfcUtil::IfcBaseClass*>::const_iterator inner_it;
    void push(const std::vector<IfcUtil::IfcBaseClass*>& instance) {
        list_.push_back(instance);
    }
    void push(const aggregate_of_instance::ptr& instance) {
        if (instance) {
            std::vector<IfcUtil::IfcBaseClass*> list;
            for (std::vector<IfcUtil::IfcBaseClass*>::const_iterator iter = instance->begin(); iter != instance->end(); ++iter) {
                list.push_back(*iter);
            }
            push(list);
        }
    }
    outer_it begin() const { return list_.begin(); }
    outer_it end() const { return list_.end(); }
    int size() const { return (int)list_.size(); }
    int totalSize() const {
        int accum = 0;
        for (outer_it it = begin(); it != end(); ++it) {
            accum += (int)it->size();
        }
        return accum;
    }
    bool contains(IfcUtil::IfcBaseClass* instance) const {
        for (outer_it it = begin(); it != end(); ++it) {
            const std::vector<IfcUtil::IfcBaseClass*>& inner = *it;
            if (std::find(inner.begin(), inner.end(), instance) != inner.end()) {
                return true;
            }
        }
        return false;
    }

    template <class U>
    typename aggregate_of_aggregate_of<U>::ptr as();

};

template <class T>
class aggregate_of_aggregate_of {
    std::vector<std::vector<T*>> list_;

  public:
    typedef typename boost::shared_ptr<aggregate_of_aggregate_of<T>> ptr;
    typedef typename std::vector<std::vector<T*>>::const_iterator outer_it;
    typedef typename std::vector<T*>::const_iterator inner_it;
    void push(const std::vector<T*>& type) { list_.push_back(type); }
    outer_it begin() { return list_.begin(); }
    outer_it end() { return list_.end(); }
    int size() const { return (int)list_.size(); }
    int totalSize() const {
        int accum = 0;
        for (outer_it it = begin(); it != end(); ++it) {
            accum += it->size();
        }
        return accum;
    }
    bool contains(T* type) const {
        for (outer_it iter = begin(); iter != end(); ++iter) {
            const std::vector<T*>& inner = *iter;
            if (std::find(inner.begin(), inner.end(), type) != inner.end()) {
                return true;
            }
        }
        return false;
    }
    aggregate_of_aggregate_of_instance::ptr generalize() {
        aggregate_of_aggregate_of_instance::ptr result(new aggregate_of_aggregate_of_instance());
        for (outer_it outer = begin(); outer != end(); ++outer) {
            const std::vector<T*>& from = *outer;
            std::vector<IfcUtil::IfcBaseClass*> to;
            for (inner_it inner = from.begin(); inner != from.end(); ++inner) {
                to.push_back(*inner);
            }
            result->push(to);
        }
        return result;
    }
};

#endif
