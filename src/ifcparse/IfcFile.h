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

#ifndef IFCFILE_H
#define IFCFILE_H

#include "ifc_parse_api.h"
#include "IfcParse.h"
#include "IfcSchema.h"
#include "IfcSpfHeader.h"

#include <boost/multi_index/ordered_index.hpp>
#include <boost/multi_index/random_access_index.hpp>
#include <boost/multi_index/sequenced_index.hpp>
#include <boost/multi_index_container.hpp>
#include <boost/unordered_map.hpp>
#include <boost/variant.hpp>
#include <iterator>
#include <map>

namespace IfcParse {

class IFC_PARSE_API file_open_status {
  public:
    enum file_open_enum {
        SUCCESS,
        READ_ERROR,
        NO_HEADER,
        UNSUPPORTED_SCHEMA
    };

  private:
    file_open_enum error_;

  public:
    file_open_status(file_open_enum error)
        : error_(error) {}

    operator file_open_enum() const {
        return error_;
    }

    file_open_enum value() const {
        return error_;
    }

    operator bool() const {
        return error_ == SUCCESS;
    }
};

typedef boost::variant<int, IfcUtil::IfcBaseClass*> reference_or_simple_type;
typedef std::list<std::pair<MutableAttributeValue, boost::variant<reference_or_simple_type, std::vector<reference_or_simple_type>, std::vector<std::vector<reference_or_simple_type>>>>> unresolved_references;

struct parse_context {
    std::list<
        boost::variant<
        IfcUtil::IfcBaseClass*,
        Token,
        parse_context*
        >> tokens_;

    parse_context() {};
    ~parse_context();

    parse_context(const parse_context&) = delete;
    parse_context& operator=(const parse_context&) = delete;

    parse_context(parse_context&&) = default;
    parse_context& operator=(parse_context&&) = default;

    parse_context& push();

    void push(Token t);

    void push(IfcUtil::IfcBaseClass* inst);

    IfcEntityInstanceData construct(int name, unresolved_references& references_to_resolve, const IfcParse::declaration* decl, boost::optional<size_t> expected_size);
};

/// This class provides several static convenience functions and variables
/// and provide access to the entities in an IFC file
class IFC_PARSE_API IfcFile {
  public:
      unresolved_references references_to_resolve;

    typedef std::map<const IfcParse::declaration*, aggregate_of_instance::ptr> entities_by_type_t;
    typedef boost::unordered_map<unsigned int, IfcUtil::IfcBaseClass*> entity_by_id_t;
    typedef boost::unordered_map<uint32_t, IfcUtil::IfcBaseClass*> entity_by_iden_t;
    typedef std::map<std::string, IfcUtil::IfcBaseClass*> entity_by_guid_t;
    typedef std::tuple<int, short, short> inverse_attr_record;
    enum INVERSE_ATTR {
        INSTANCE_ID,
        INSTANCE_TYPE,
        ATTRIBUTE_INDEX
    };
    typedef std::map<inverse_attr_record, std::vector<int>> entities_by_ref_t;
    typedef std::map<int, std::vector<int>> entities_by_ref_excl_t;
    typedef std::map<unsigned int, aggregate_of_instance::ptr> ref_map_t;
    typedef entity_by_id_t::const_iterator const_iterator;

    class type_iterator : private entities_by_type_t::const_iterator {
      public:
        type_iterator() : entities_by_type_t::const_iterator(){};

        type_iterator(const entities_by_type_t::const_iterator& iter)
            : entities_by_type_t::const_iterator(iter){};

        entities_by_type_t::key_type const* operator->() const {
            return &entities_by_type_t::const_iterator::operator->()->first;
        }

        entities_by_type_t::key_type const& operator*() const {
            return entities_by_type_t::const_iterator::operator*().first;
        }

        type_iterator& operator++() {
            entities_by_type_t::const_iterator::operator++();
            return *this;
        }

        type_iterator operator++(int) {
            type_iterator tmp(*this);
            operator++();
            return tmp;
        }

        bool operator!=(const type_iterator& other) const {
            const entities_by_type_t::const_iterator& self_ = *this;
            const entities_by_type_t::const_iterator& other_ = other;
            return self_ != other_;
        }
    };

    static bool guid_map_;
    static bool guid_map() { return guid_map_; }
    static void guid_map(bool b) { guid_map_ = b; }

  private:
    typedef std::map<uint32_t, IfcUtil::IfcBaseClass*> entity_entity_map_t;

    file_open_status good_ = file_open_status::SUCCESS;

    const IfcParse::schema_definition* schema_;
    const IfcParse::declaration* ifcroot_type_;

    // std::vector<Argument*> internal_attribute_vector_, internal_attribute_vector_simple_type_;

    entity_by_id_t byid_;
    // this is for simple types
    entity_by_iden_t byidentity_;
    // entities_by_type_t bytype_;
    entities_by_type_t bytype_excl_;
    // entities_by_ref_t byref_;
    entities_by_ref_t byref_excl_;
    entity_by_guid_t byguid_;
    entity_entity_map_t entity_file_map_;

    unsigned int MaxId;

    IfcSpfHeader _header;

    void setDefaultHeaderValues();

    void initialize_(IfcParse::IfcSpfStream* stream);

    void build_inverses_(IfcUtil::IfcBaseClass*);

    typedef boost::multi_index_container<
        int,
        boost::multi_index::indexed_by<
            boost::multi_index::sequenced<>,
            boost::multi_index::ordered_unique<
                boost::multi_index::identity<int>>>>
        batch_deletion_ids_t;
    batch_deletion_ids_t batch_deletion_ids_;
    bool batch_mode_ = false;
    void process_deletion_();

  public:
    IfcParse::IfcSpfLexer* tokens;
    IfcParse::IfcSpfStream* stream;

#ifdef USE_MMAP
    IfcFile(const std::string& path, bool mmap = false);
#else
    IfcFile(const std::string& path);
#endif
    IfcFile(std::istream& stream, int length);
    IfcFile(void* data, int length);
    IfcFile(IfcParse::IfcSpfStream* stream);
    IfcFile(const IfcParse::schema_definition* schema = IfcParse::schema_by_name("IFC4"));

    /// Deleting the file will also delete all new instances that were added to the file (via memory allocation)
    virtual ~IfcFile();

    file_open_status good() const { return good_; }

    /// Returns the first entity in the file, this probably is the entity
    /// with the lowest id (EXPRESS ENTITY_INSTANCE_NAME)
    const_iterator begin() const;
    /// Returns the last entity in the file, this probably is the entity
    /// with the highest id (EXPRESS ENTITY_INSTANCE_NAME)
    const_iterator end() const;

    type_iterator types_begin() const;
    type_iterator types_end() const;

    // type_iterator types_incl_super_begin() const;
    // type_iterator types_incl_super_end() const;

    /// Returns all entities in the file that match the template argument.
    /// NOTE: This also returns subtypes of the requested type, for example:
    /// IfcWall will also return IfcWallStandardCase entities
    template <class T>
    typename T::list::ptr instances_by_type() {
        aggregate_of_instance::ptr untyped_list = instances_by_type(&T::Class());
        if (untyped_list) {
            return untyped_list->as<T>();
        }
        return typename T::list::ptr(new typename T::list);
    }

    template <class T>
    typename T::list::ptr instances_by_type_excl_subtypes() {
        aggregate_of_instance::ptr untyped_list = instances_by_type_excl_subtypes(&T::Class());
        if (untyped_list) {
            return untyped_list->as<T>();
        }
        return typename T::list::ptr(new typename T::list);
    }

    /// Returns all entities in the file that match the positional argument.
    /// NOTE: This also returns subtypes of the requested type, for example:
    /// IfcWall will also return IfcWallStandardCase entities
    aggregate_of_instance::ptr instances_by_type(const IfcParse::declaration*);

    /// Returns all entities in the file that match the positional argument.
    aggregate_of_instance::ptr instances_by_type_excl_subtypes(const IfcParse::declaration*);

    /// Returns all entities in the file that match the positional argument.
    /// NOTE: This also returns subtypes of the requested type, for example:
    /// IfcWall will also return IfcWallStandardCase entities
    aggregate_of_instance::ptr instances_by_type(const std::string& type);

    /// Returns all entities in the file that match the positional argument.
    aggregate_of_instance::ptr instances_by_type_excl_subtypes(const std::string& type);

    /// Returns all entities in the file that reference the id
    aggregate_of_instance::ptr instances_by_reference(int id);

    /// Returns the entity with the specified id
    IfcUtil::IfcBaseClass* instance_by_id(int id);

    /// Returns the entity with the specified GlobalId
    IfcUtil::IfcBaseClass* instance_by_guid(const std::string& guid);

    /// Performs a depth-first traversal, returning all entity instance
    /// attributes as a flat list. NB: includes the root instance specified
    /// in the first function argument.
    static aggregate_of_instance::ptr traverse(IfcUtil::IfcBaseClass* instance, int max_level = -1);

    /// Same as traverse() but maintains topological order by using a
    /// breadth-first search
    static aggregate_of_instance::ptr traverse_breadth_first(IfcUtil::IfcBaseClass* instance, int max_level = -1);

    /// Get the attribute indices corresponding to the list of entity instances
    /// returned by getInverse().
    std::vector<int> get_inverse_indices(int instance_id);

    template <typename T>
    typename T::list::ptr getInverse(int instance_id, int attribute_index) {
        return getInverse(instance_id, &T::Class(), attribute_index)->template as<T>();
    }

    aggregate_of_instance::ptr getInverse(int instance_id, const IfcParse::declaration* type, int attribute_index);

    size_t getTotalInverses(int instance_id);

    unsigned int FreshId() { return ++MaxId; }

    unsigned int getMaxId() const { return MaxId; }

    const IfcParse::declaration* ifcroot_type() const { return ifcroot_type_; }

    void recalculate_id_counter();

    IfcUtil::IfcBaseClass* addEntity(IfcUtil::IfcBaseClass* entity, int id = -1);
    void addEntities(aggregate_of_instance::ptr entities);

    void batch() { batch_mode_ = true; }
    void unbatch() {
        process_deletion_();
        batch_mode_ = false;
    }

    /// Removes entity instance from file and unsets references.
    ///
    /// Attention when running removeEntity inside a loop over a list of entities to be removed.
    /// This invalidates the iterator. A workaround is to reverse the loop:
    /// boost::shared_ptr<aggregate_of_instance> entities = ...;
    /// for (auto it = entities->end() - 1; it >= entities->begin(); --it) {
    ///    IfcUtil::IfcBaseClass *const inst = *it;
    ///    model->removeEntity(inst);
    /// }
    void removeEntity(IfcUtil::IfcBaseClass* entity);

    const IfcSpfHeader& header() const { return _header; }
    IfcSpfHeader& header() { return _header; }

    static std::string createTimestamp() ;

    void load(unsigned entity_instance_name, const IfcParse::entity* entity, parse_context&, int attribute_index = -1);
    void try_read_semicolon() const;

    void register_inverse(unsigned, const IfcParse::entity* from_entity, Token, int attribute_index);
    void register_inverse(unsigned, const IfcParse::entity* from_entity, IfcUtil::IfcBaseClass*, int attribute_index);
    void unregister_inverse(unsigned, const IfcParse::entity* from_entity, IfcUtil::IfcBaseClass*, int attribute_index);

    const IfcParse::schema_definition* schema() const { return schema_; }

    std::pair<IfcUtil::IfcBaseClass*, double> getUnit(const std::string& unit_type);

    void build_inverses();

    entity_by_guid_t& internal_guid_map() { return byguid_; };
};

#ifdef WITH_IFCXML
IFC_PARSE_API IfcFile* parse_ifcxml(const std::string& filename);
#endif

} // namespace IfcParse

namespace std {
template <>
struct iterator_traits<IfcParse::IfcFile::type_iterator> {
    typedef ptrdiff_t difference_type;
    typedef const IfcParse::declaration* value_type;
    typedef const IfcParse::declaration*& reference;
    typedef const IfcParse::declaration** pointer;
    typedef std::forward_iterator_tag iterator_category;
};
} // namespace std

#endif
