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
#include "rocksdb_map_adapter.h"
#include "rocksdb_set_view.h"
#include "map_variant.h"
#include "map_transformer.h"
#include "set_to_map_transformer.h"

#include <boost/multi_index/ordered_index.hpp>
#include <boost/multi_index/random_access_index.hpp>
#include <boost/multi_index/sequenced_index.hpp>
#include <boost/multi_index_container.hpp>
#include <boost/unordered_map.hpp>
#include <boost/variant.hpp>
#include <iterator>
#include <map>

#include "rocksdb/merge_operator.h"

namespace {
    // @todo move to a proper place
    class ConcatenateIdMergeOperator : public rocksdb::AssociativeMergeOperator {
    public:

        virtual bool FullMergeV2(const MergeOperator::MergeOperationInput& merge_in,
            MergeOperator::MergeOperationOutput* merge_out) const {
            // Log(InfoLogLevel::INFO_LEVEL, merge_in.logger, "FullMergeV2 new_value size:%ld", merge_out->new_value.size());
            if (merge_in.existing_value) {
                merge_out->new_value.append(merge_in.existing_value->data(), merge_in.existing_value->size());
            }
            for (auto& operand : merge_in.operand_list) {
                merge_out->new_value.append(operand.data(), operand.size());
            }
            return true;
        }


        virtual bool Merge(const rocksdb::Slice&,
            const rocksdb::Slice*,
            const rocksdb::Slice&,
            std::string*,
            rocksdb::Logger*) const override
        {
            return false;
        }

        virtual const char* Name() const override {
            return "ConcatenateIdMergeOperator";
        }
    };
}

namespace IfcParse {

class IFC_PARSE_API file_open_status {
  public:
    enum file_open_enum {
        SUCCESS,
        READ_ERROR,
        NO_HEADER,
        UNSUPPORTED_SCHEMA,
        INVALID_SYNTAX
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

#include <variant>
#include <iterator>
#include <type_traits>
#include <iostream>
#include <vector>
#include <list>

#ifndef SWIG

template <typename... Iterators>
class variant_iterator {
public:
    // The variant type holding one of the underlying iterators.
    using variant_type = std::variant<Iterators...>;

    // Assuming that all iterator types have the same value_type, difference_type, etc.
    using value_type = std::common_type_t<typename std::iterator_traits<Iterators>::value_type...>;
    using difference_type = std::common_type_t<typename std::iterator_traits<Iterators>::difference_type...>;
    using pointer = value_type*;
    using reference = value_type&;
    // For simplicity, we use input_iterator_tag; if all underlying iterators support more,
    // you could compute the common iterator_category.
    using iterator_category = std::input_iterator_tag;

    // Default constructor.
    variant_iterator() = default;

    // Construct from any one of the underlying iterator types.
    template <typename Iterator>
    variant_iterator(Iterator it) : it_(it) { }

    // Dereference operator.
    decltype(auto) operator*() const {
        return std::visit([](const auto& iter) -> decltype(auto) {
            return *iter;
        }, it_);
    }

    // Arrow operator.
    decltype(auto) operator->() const {
        return std::visit([](const auto& iter) -> decltype(auto) {
            return iter.operator->();
        }, it_);
    }

    // Pre-increment operator.
    variant_iterator& operator++() {
        std::visit([](auto& iter) { ++iter; }, it_);
        return *this;
    }

    // Post-increment operator.
    variant_iterator operator++(int) {
        variant_iterator temp(*this);
        ++(*this);
        return temp;
    }

    // Pre-decrement operator.
    variant_iterator& operator--() {
        std::visit([](auto& iter) { --iter; }, it_);
        return *this;
    }

    // Post-decrement operator.
    variant_iterator operator--(int) {
        variant_iterator temp(*this);
        --(*this);
        return temp;
    }

    // Equality comparison.
    friend bool operator==(const variant_iterator& lhs, const variant_iterator& rhs) {
        return lhs.it_ == rhs.it_;
    }

    // Inequality comparison.
    friend bool operator!=(const variant_iterator& lhs, const variant_iterator& rhs) {
        return !(lhs == rhs);
    }

private:
    variant_type it_;
};

#endif

namespace impl {
    struct in_memory_file_storage {
        IfcParse::IfcSpfLexer* tokens;
        IfcParse::IfcSpfStream* stream;
        IfcParse::IfcFile* file;

        unresolved_references references_to_resolve;

        typedef std::map<const IfcParse::declaration*, aggregate_of_instance::ptr> entities_by_type_t;
        typedef boost::unordered_map<uint32_t, IfcUtil::IfcBaseClass*> entity_instance_by_name_t;
        typedef boost::unordered_map<uint32_t, IfcUtil::IfcBaseClass*> type_instance_by_name_t;
        typedef std::map<std::string, IfcUtil::IfcBaseClass*> entity_instance_by_guid_t;
        typedef std::tuple<int, short, short> inverse_attr_record;
        enum INVERSE_ATTR {
            INSTANCE_ID,
            INSTANCE_TYPE,
            ATTRIBUTE_INDEX
        };
        typedef std::map<inverse_attr_record, std::vector<uint32_t>> entities_by_ref_t;
        typedef entity_instance_by_name_t::iterator iterator;

        in_memory_file_storage() : tokens(nullptr), stream(nullptr), file(nullptr) {}
        in_memory_file_storage(const in_memory_file_storage&) = delete;
        in_memory_file_storage(const in_memory_file_storage&&) = delete;

        class type_iterator : public entities_by_type_t::const_iterator {
        public:
            using iterator_category = std::forward_iterator_tag;
            using value_type = entities_by_type_t::key_type;
            using difference_type = typename entities_by_type_t::const_iterator::difference_type;
            using pointer = value_type const*;
            using reference = value_type const&;

            type_iterator() : entities_by_type_t::const_iterator() {};

            type_iterator(const entities_by_type_t::const_iterator& iter)
                : entities_by_type_t::const_iterator(iter) {};

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
        };


        static bool guid_map_;
        static bool guid_map() { return guid_map_; }
        static void guid_map(bool b) { guid_map_ = b; }

        entity_instance_by_name_t byid_;
        type_instance_by_name_t tbyid_;
        entities_by_type_t bytype_excl_;
        entities_by_ref_t byref_excl_;
        entity_instance_by_guid_t byguid_;

        void load(unsigned entity_instance_name, const IfcParse::entity* entity, parse_context&, int attribute_index = -1);
        void try_read_semicolon() const;

        void register_inverse(unsigned, const IfcParse::entity* from_entity, int inst_id, int attribute_index);
        void unregister_inverse(unsigned, const IfcParse::entity* from_entity, IfcUtil::IfcBaseClass*, int attribute_index);

        // @todo is this still used
        IfcEntityInstanceData read(unsigned int index);
        void read_from_stream(IfcParse::IfcSpfStream* stream, const IfcParse::schema_definition*& schema, unsigned int& max_id);

        file_open_status good_ = file_open_status::SUCCESS;

        IfcUtil::IfcBaseClass* instance_by_id(int id);

        void add_type_ref(IfcUtil::IfcBaseClass* new_entity) {
            auto ty = new_entity->declaration().as_entity();
            if (ty) {
                if (bytype_excl_.find(ty) == bytype_excl_.end()) {
                    bytype_excl_[ty].reset(new aggregate_of_instance());
                }
                bytype_excl_[ty]->push(new_entity);
            }
        }
        void remove_type_ref(IfcUtil::IfcBaseClass* new_entity) {
            auto ty = new_entity->declaration().as_entity();
            if (ty) {
                auto it = bytype_excl_.find(ty);
                if (it != bytype_excl_.end()) {
                    it->second->remove(new_entity);
                    if (it->second->size() == 0) {
                        bytype_excl_.erase(ty);
                    }
                }
            }
        }

        void process_deletion_inverse(IfcUtil::IfcBaseClass* inst);

        template <typename T>
        T* create();

        IfcUtil::IfcBaseClass* create(const IfcParse::declaration* decl);
    };

    class rocks_db_file_storage {
    public:
        rocksdb::DB* db;
        rocksdb::WriteOptions wopts;
        rocksdb::ReadOptions ropts;
        IfcParse::IfcFile* file;

        enum instance_ref {
            typedecl_ref,
            entityinstance_ref
        };

        // to make sure that instance pointer are constant during file lifetime
        // cache instances because we want stable pointers
        // @todo this is silly, but we cannot have the same type, this should be just a pointer then on the IfcFile side?
        typedef std::map<uint32_t, IfcUtil::IfcBaseClass*> entity_by_iden_cache_t;
        entity_by_iden_cache_t instance_cache_, type_instance_cache_;
                
        // @todo all these size_ts should probably be uint32_t for consistency with in-mem storage

        // lookup id->identity
        // typedef rocksdb_map_adapter<size_t, size_t> identity_by_id_t;
        // identity_by_id_t byid_;
        typedef rocksdb_set_view<size_t> instance_name_view_t;
        instance_name_view_t instance_ids_;
        typedef set_to_map_transformer<instance_name_view_t, std::function<IfcUtil::IfcBaseClass* (size_t)>> entity_instance_by_name_t;
        entity_instance_by_name_t instance_by_name_;

        // typedef map_transformer<rocksdb_map_adapter<size_t, size_t>, std::function<IfcUtil::IfcBaseClass*(size_t)>, std::function<size_t(IfcUtil::IfcBaseClass*)>> entity_by_id_t;
        // storage is now Instance name -> Identity -> Pointer (cached)
        // entity_by_id_t byidentity_;

        // index in schema to binary serialized ids
        typedef rocksdb_map_adapter<size_t, std::string> instance_id_str_by_type_t;
        instance_id_str_by_type_t bytype_;

        // guid -> id
        typedef rocksdb_map_adapter<std::string, size_t> instance_id_by_guid_str_t;
        instance_id_by_guid_str_t byguid_internal_;

        // guid -> id -> instance
        typedef map_transformer<rocksdb_map_adapter<std::string, size_t>, std::function<IfcUtil::IfcBaseClass* (size_t)>, std::function< size_t(IfcUtil::IfcBaseClass*)>> entity_instance_by_guid_t;
        entity_instance_by_guid_t byguid_;

        typedef std::tuple<int, int, int> inverse_attr_record;
        enum INVERSE_ATTR {
            INSTANCE_ID,
            INSTANCE_TYPE,
            ATTRIBUTE_INDEX
        };
        typedef rocksdb_map_adapter<inverse_attr_record, std::vector<uint32_t>> entities_by_ref_t;
        entities_by_ref_t byref_excl_;

        // @todo naming
        rocks_db_file_storage(const std::string& filepath, IfcParse::IfcFile* file);
        ~rocks_db_file_storage();

        bool read_schema(const IfcParse::schema_definition*& schema);

        IfcUtil::IfcBaseClass* assert_existance(size_t instanceId, instance_ref r);

        // @todo this could be another map_adapter?
        /*
        class rocksdb_instance_iterator {
        private:
            rocksdb::Iterator* state_;
            rocks_db_file_storage* storage_;

            static constexpr char prefix_[] = "i|";

            boost::optional<size_t> read_id_() const {
                auto sv = state_->key().ToStringView();
                auto ii = sv.find("|", 2);
                if (ii != decltype(sv)::npos) {
                    char* pEnd;
                    long result = strtol(sv.data() + 2, &pEnd, 10);
                    if (*pEnd == '|') {
                        return (size_t)result;
                    }
                }
                return boost::none;
            }
        public:
            rocksdb_instance_iterator()
                : state_(nullptr)
                , storage_(nullptr)
            {}
            rocksdb_instance_iterator(rocks_db_file_storage* fs) 
                : storage_(fs)
            {
                state_ = fs->db->NewIterator(rocksdb::ReadOptions());
                state_->Seek(prefix_);
                if (!state_->Valid() || !state_->key().starts_with(prefix_)) {
                    delete state_;
                    state_ = nullptr;
                }
            }
            rocksdb_instance_iterator& operator++() {
                if (!state_) {
                    return *this;
                }
                auto last_id = read_id_();
                while (state_->Valid()) {
                    state_->Next();
                    // Stop if we've left the prefix range.
                    if (!state_->Valid() || !state_->key().starts_with(prefix_)) {
                        delete state_;
                        state_ = nullptr;
                        break;
                    }
                    if (read_id_() != last_id) {
                        break;
                    }
                }
                return *this;
            }
            rocksdb_instance_iterator operator++(int) {
                rocksdb_instance_iterator temp = *this;
                ++(*this);
                return temp;
            }
            bool operator==(const rocksdb_instance_iterator& other) const {
                if (state_ == nullptr && other.state_ == nullptr) {
                    return true;
                } else {
                    return read_id_() == other.read_id_();
                }
            }

            bool operator!=(const rocksdb_instance_iterator& other) const {
                return !(*this == other);
            }

            IfcUtil::IfcBaseClass* operator*() const;
        };
        */

        // @todo merge iterators (template?)
        class rocksdb_types_iterator {
        private:
            rocksdb::Iterator* state_;
            const rocks_db_file_storage* storage_;

            static constexpr char prefix_[] = "t|";

            boost::optional<size_t> read_id_() const {
                auto sv = state_->key().ToStringView();
                auto ii = sv.find("|", 2);
                if (ii != decltype(sv)::npos) {
                    char* pEnd;
                    long result = strtol(sv.data() + 2, &pEnd, 10);
                    if (*pEnd == '|') {
                        return (size_t)result;
                    }
                }
                return boost::none;
            }
        public:
            using iterator_category = std::forward_iterator_tag;
            using value_type = const IfcParse::declaration*;
            // @todo ?
            using difference_type = ptrdiff_t;
            using pointer = value_type const*;
            using reference = value_type const&;

            rocksdb_types_iterator()
                : state_(nullptr)
                , storage_(nullptr)
            {}

            rocksdb_types_iterator(const rocks_db_file_storage* fs)
                : storage_(fs)
            {
                state_ = fs->db->NewIterator(rocksdb::ReadOptions());
                state_->Seek(prefix_);
                if (!state_->Valid() || !state_->key().starts_with(prefix_)) {
                    delete state_;
                    state_ = nullptr;
                }
            }

            rocksdb_types_iterator& operator++() {
                if (!state_) {
                    return *this;
                }
                auto last_id = read_id_();
                while (state_->Valid()) {
                    state_->Next();
                    // Stop if we've left the prefix range.
                    if (!state_->Valid() || !state_->key().starts_with(prefix_)) {
                        delete state_;
                        state_ = nullptr;
                        break;
                    }
                    if (read_id_() != last_id) {
                        break;
                    }
                }
                return *this;
            }

            rocksdb_types_iterator operator++(int) {
                rocksdb_types_iterator temp = *this;
                ++(*this);
                return temp;
            }

            bool operator==(const rocksdb_types_iterator& other) const {
                if (state_ == nullptr && other.state_ == nullptr) {
                    return true;
                } else {
                    return read_id_() == other.read_id_();
                }
            }

            bool operator!=(const rocksdb_types_iterator& other) const {
                return !(*this == other);
            }

            value_type const& operator*() const;

            value_type const* operator->() const {
                return &operator*();
            }
        };

        // @todo rocksdb_instance_iterator?
        using const_iterator = entity_instance_by_name_t::iterator;

        void register_inverse(unsigned, const IfcParse::entity* from_entity, int inst_id, int attribute_index);
        void unregister_inverse(unsigned, const IfcParse::entity* from_entity, IfcUtil::IfcBaseClass*, int attribute_index);

        // @todo a bit hard as a map because of value_type being an aggregate
        void add_type_ref(IfcUtil::IfcBaseClass* new_entity);
        void remove_type_ref(IfcUtil::IfcBaseClass* new_entity);

        IfcUtil::IfcBaseClass* instance_by_id(int id);

        void process_deletion_inverse(IfcUtil::IfcBaseClass* inst);

        template <typename T>
        T* create();

        IfcUtil::IfcBaseClass* create(const IfcParse::declaration* decl);
    };
}

enum filetype {
    FT_IFCSPF,
    FT_IFCXML,
    FT_IFCZIP,
    FT_ROCKSDB,
    FT_UNKNOWN,
    FT_AUTODETECT
};

filetype guess_file_type(const std::string& fn);

/// This class provides access to the entity instances in an IFC file
/// The file takes ownership of instances added to this file and deletes them when the file is deleted.
class IFC_PARSE_API IfcFile {
  public:

  private:
    typedef std::map<uint32_t, IfcUtil::IfcBaseClass*> entity_entity_map_t;

    // @todo determine the constness of things (probably needs to be all const, we don't want to overwrite)
    // @todo we have variant_iterator and MapVariant, we probably need to retain only one?
public:
    using const_iterator = variant_iterator<impl::in_memory_file_storage::iterator, impl::rocks_db_file_storage::const_iterator>;
    using type_iterator = variant_iterator<impl::in_memory_file_storage::type_iterator, impl::rocks_db_file_storage::rocksdb_types_iterator>;
    using storage_t = std::variant<std::monostate, impl::in_memory_file_storage, impl::rocks_db_file_storage>;

    bool check_existance_before_adding = true;
    bool calculate_unit_factors = true;
    bool instantiate_typed_instances = true;

    // @todo temporarily public for header
    storage_t storage_;
private:
    file_open_status good_ = file_open_status::SUCCESS;

    const IfcParse::schema_definition* schema_;
    const IfcParse::declaration* ifcroot_type_;

    entity_entity_map_t entity_file_map_;

    unsigned int max_id_;

    IfcSpfHeader _header;

    void setDefaultHeaderValues();

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
#ifdef USE_MMAP
    IfcFile(const std::string& path, bool mmap = false);
#else
    IfcFile(const std::string& path, filetype ty=FT_AUTODETECT);
#endif
    IfcFile(std::istream& stream, int length);
    IfcFile(void* data, int length);
    IfcFile(IfcParse::IfcSpfStream* stream);
    // @nb path is only used in rocksdb mode, for spf file is in-memory only until write() is called
    IfcFile(const IfcParse::schema_definition* schema = IfcParse::schema_by_name("IFC4"), filetype ty = FT_AUTODETECT, const std::string& path = "");

    ~IfcFile();

    file_open_status good() const { return good_; }

    /// Returns the first entity in the range of instances contained in the model,
    /// in arbitrary order
    auto begin() const {
        return byid_.begin();
    }

    /// Returns the first entity in the range of instances contained in the model,
    /// in arbitrary order
    auto end() const {
        return byid_.end();
    }

    type_iterator types_begin() const;
    type_iterator types_end() const;

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

    unsigned int FreshId() { return ++max_id_; }

    unsigned int getMaxId() const { return max_id_; }

    const IfcParse::declaration* ifcroot_type() const { return ifcroot_type_; }

    void recalculate_id_counter();

    IfcUtil::IfcBaseClass* addEntity(IfcUtil::IfcBaseClass* entity, int id = -1);
    void addEntities(aggregate_of_instance::ptr entities);

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

    const IfcParse::schema_definition* schema() const { return schema_; }

    std::pair<IfcUtil::IfcBaseClass*, double> getUnit(const std::string& unit_type);

    void build_inverses();

    void register_inverse(unsigned, const IfcParse::entity* from_entity, int inst_id, int attribute_index);
    void unregister_inverse(unsigned, const IfcParse::entity* from_entity, IfcUtil::IfcBaseClass*, int attribute_index);

    typedef VariantMap<impl::in_memory_file_storage::entity_instance_by_guid_t, impl::rocks_db_file_storage::entity_instance_by_guid_t> entity_instance_by_guid_t;
    entity_instance_by_guid_t byguid_;
    typedef VariantMap<impl::in_memory_file_storage::entity_instance_by_name_t, impl::rocks_db_file_storage::entity_instance_by_name_t> entity_by_id_t;
    entity_by_id_t byid_;
    typedef VariantMap<impl::in_memory_file_storage::entities_by_ref_t, impl::rocks_db_file_storage::entities_by_ref_t> entities_by_ref_t;
    entities_by_ref_t byref_excl_;

    entity_instance_by_guid_t internal_guid_map() { return byguid_; };

    void add_type_ref(IfcUtil::IfcBaseClass* new_entity);
    void remove_type_ref(IfcUtil::IfcBaseClass* new_entity);
    void process_deletion_inverse(IfcUtil::IfcBaseClass* inst);

    void build_inverses_(IfcUtil::IfcBaseClass*);

    template <typename T>
    T* create() {
        return std::visit([](auto& m) -> T* {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage> || 
                std::is_same_v<std::decay_t<decltype(m)>, impl::rocks_db_file_storage>)
            {
                return m.create<T>();
            } else {
                return nullptr;
            }
        }, storage_);
    }

    IfcUtil::IfcBaseClass* create(const IfcParse::declaration* decl) {
        return std::visit([decl](auto& m) -> IfcUtil::IfcBaseClass* {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage> ||
                std::is_same_v<std::decay_t<decltype(m)>, impl::rocks_db_file_storage>)
            {
                return m.create(decl);
            } else {
                return nullptr;
            }
        }, storage_);
    }
};

#ifdef WITH_IFCXML
IFC_PARSE_API IfcFile* parse_ifcxml(const std::string& filename);
#endif

} // namespace IfcParse

template <typename T>
T* IfcParse::impl::in_memory_file_storage::create() {
    IfcUtil::IfcBaseClass* inst = nullptr;
    if constexpr (std::is_same_v<std::decay_t<std::invoke_result_t<T::Class>>, IfcParse::entity>) {
        inst = new T(in_memory_attribute_storage(T::Class().attribute_count()));
    } else if constexpr (std::is_same_v<std::decay_t<std::invoke_result_t<T::Class>>, IfcParse::type_declaration>) {
        inst = new T(in_memory_attribute_storage(1));
    } else {
        static_assert(false, "Requires and entity or type declaration");
    }
    inst->file_ = file;
    return file->addEntity(inst)->as<T>();
}

IfcUtil::IfcBaseClass* IfcParse::impl::in_memory_file_storage::create(const IfcParse::declaration* decl) {
    IfcUtil::IfcBaseClass* inst = nullptr;
    if (auto* ent = decl->as_entity()) {
        inst = file->schema()->instantiate(decl, in_memory_attribute_storage(ent->attribute_count()));
    } else if (auto* typedecl = decl->as_type_declaration()) {
        inst = file->schema()->instantiate(decl, in_memory_attribute_storage(1));
    } else {
        throw std::runtime_error("Requires and entity or type declaration");
    }
    inst->file_ = file;
    return file->addEntity(inst);
}

template <typename T>
T* IfcParse::impl::rocks_db_file_storage::create() {
    if constexpr (std::is_same_v<std::decay_t<std::invoke_result_t<T::Class>>, IfcParse::entity> || std::is_same_v<std::decay_t<std::invoke_result_t<T::Class>>, IfcParse::type_declaration>) {
        auto* inst = new T(rocks_db_attribute_storage{});
        inst->file_ = file;
        return file->addEntity(inst)->as<T>();
    } else {
        static_assert(false, "Requires and entity or type declaration");
    }
}

IfcUtil::IfcBaseClass* IfcParse::impl::rocks_db_file_storage::create(const IfcParse::declaration* decl) {
    if (decl->as_entity() || decl->as_type_declaration()) {
        auto* inst = file->schema()->instantiate(decl, rocks_db_attribute_storage{});
        inst->file_ = file;
        return file->addEntity(inst);
    } else {
        throw std::runtime_error("Requires and entity or type declaration");
    }
}

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
