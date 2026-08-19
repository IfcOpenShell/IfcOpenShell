#ifndef STORAGE_H
#define STORAGE_H

// Avoid conflicts with OpenCascade HANDLE type and RocksDB Handle
#pragma push_macro("Handle")
#undef Handle

#ifndef IFOPSH_WITH_ROCKSDB

namespace rocksdb {
    class DB {};
    class Options {};
    class WriteOptions {};
    class ReadOptions {};
    class Iterator {};
    class status {};
}

#endif

#include "rocksdb_map_adapter.h"
#include "rocksdb_set_view.h"
#include "map_variant.h"
#include "map_transformer.h"
#include "set_to_map_transformer.h"
#include "file_open_status.h"
#include "logger.h"

#include <functional>
#include <variant>
#include <algorithm>
#include <cstdint>
#include <iterator>
#include <map>
#include <memory>
#include <cstring>
#include <type_traits>
#include <iostream>
#include <deque>
#include <vector>
#include <list>
#include <mutex>
#include <set>
#include <unordered_map>

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
    variant_iterator(Iterator iterator) : it_(iterator) {}

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

namespace ifcopenshell {

    class mutable_attribute_value;

    struct IFC_PARSE_API instance_reference {
        int v;
        size_t file_offset;
        operator int() const {
            return v;
        }
    };

    typedef std::variant<instance_reference, express::base> reference_or_simple_type;
    typedef std::vector<std::pair<mutable_attribute_value, std::variant<reference_or_simple_type, std::vector<reference_or_simple_type>, std::vector<std::vector<reference_or_simple_type>>>>> unresolved_references;

    class file;
    template <typename Reader>
    class spf_lexer;

    struct IFC_PARSE_API token {
        enum token_type {
            Token_NONE,
            Token_STRING,
            Token_IDENTIFIER,
            Token_OPERATOR,
            Token_ENUMERATION,
            Token_KEYWORD,
            Token_INT,
            Token_BOOL,
            Token_FLOAT,
            Token_BINARY
        };

        size_t start_pos;
        token_type type;

        union {
            char value_char;     //types: OPERATOR
            int64_t value_int;   //types: INT, IDENTIFIER
            double value_double; //types: FLOAT
            const std::string* value_string;  //types: STR, ENUM, KEYWORD; lifetime managed by spf_lexer::string_pool_
        };

        token() : start_pos(0),
                  type(Token_NONE) {}

        token(size_t start_position, token_type token_kind, const std::string& string_value)
            : start_pos(start_position), type(token_kind), value_string(&string_value) {}

        token(size_t start_position, token_type token_kind, int64_t integer_value)
            : start_pos(start_position), type(token_kind), value_int(integer_value) {}

        token(size_t start_position, double floating_value)
            : start_pos(start_position), type(Token_FLOAT), value_double(floating_value) {}

        token(size_t start_position, char operator_character)
            : start_pos(start_position), type(Token_OPERATOR), value_char(operator_character) {}

        token(size_t start_position, token_type token_kind, char character_value)
            : start_pos(start_position), type(token_kind), value_char(character_value) {}

        bool is_string();
        bool is_identifier();
        bool is_operator();
        bool is_operator(char character);
        bool is_enumeration();
        bool is_keyword();
        bool is_int();
        bool is_bool();
        bool is_logical();
        bool is_float();
        bool is_binary();

        int64_t as_int();
        unsigned as_identifier();
        bool as_bool();
        boost::logic::tribool as_logical();
        double as_float();
        const std::string& as_string();
        boost::dynamic_bitset<> as_binary();
        std::string to_string();

        operator bool() const {
            return type != Token_NONE;
        }
    };

    namespace impl {
        struct inverse_record {
            uint32_t referenced_id;
            uint32_t source_id;
            uint16_t source_entity;
            int16_t attribute_index;
        };

        class inverse_index {
        public:
            typedef std::map<std::tuple<short, short>, std::vector<uint32_t>> legacy_bucket;
            typedef std::unordered_map<int, legacy_bucket> legacy_map;
            typedef legacy_map::key_type key_type;
            typedef legacy_map::mapped_type mapped_type;
            typedef legacy_map::value_type value_type;
            typedef legacy_map::iterator iterator;
            typedef legacy_map::const_iterator const_iterator;
            typedef std::vector<inverse_record>::const_iterator record_iterator;

        private:
            mutable std::vector<inverse_record> records_;
            mutable bool sorted_ = true;
            mutable std::unique_ptr<legacy_map> materialized_;

            static bool record_less(const inverse_record& a, const inverse_record& b) {
                if (a.referenced_id != b.referenced_id) {
                    return a.referenced_id < b.referenced_id;
                }
                if (a.source_entity != b.source_entity) {
                    return a.source_entity < b.source_entity;
                }
                if (a.attribute_index != b.attribute_index) {
                    return a.attribute_index < b.attribute_index;
                }
                return a.source_id < b.source_id;
            }

            static bool referenced_less(const inverse_record& a, uint32_t referenced_id) {
                return a.referenced_id < referenced_id;
            }

            static bool referenced_less(uint32_t referenced_id, const inverse_record& a) {
                return referenced_id < a.referenced_id;
            }

            void invalidate_materialized() const {
                materialized_.reset();
            }

            legacy_map& materialize() const {
                if (!materialized_) {
                    materialized_ = std::make_unique<legacy_map>();
                    materialized_->reserve(records_.size());
                    for (const auto& record : records_) {
                        (*materialized_)[(int)record.referenced_id][{(short)record.source_entity, (short)record.attribute_index}].push_back(record.source_id);
                    }
                }
                return *materialized_;
            }

        public:
            inverse_index() = default;

            inverse_index(const inverse_index& other)
                : records_(other.records_)
                , sorted_(other.sorted_)
            {}

            inverse_index& operator=(const inverse_index& other) {
                if (this != &other) {
                    records_ = other.records_;
                    sorted_ = other.sorted_;
                    materialized_.reset();
                }
                return *this;
            }

            inverse_index(inverse_index&&) noexcept = default;
            inverse_index& operator=(inverse_index&&) noexcept = default;

            void reserve(size_t size) {
                records_.reserve(size);
            }

            void add(uint32_t referenced_id, uint32_t source_id, uint16_t source_entity, int attribute_index) {
                records_.push_back({referenced_id, source_id, source_entity, (int16_t)attribute_index});
                sorted_ = false;
                invalidate_materialized();
            }

            bool remove(uint32_t referenced_id, uint32_t source_id, uint16_t source_entity, int attribute_index) {
                const inverse_record needle{referenced_id, source_id, source_entity, (int16_t)attribute_index};
                auto it = std::find_if(records_.begin(), records_.end(), [&needle](const inverse_record& record) {
                    return record.referenced_id == needle.referenced_id &&
                        record.source_id == needle.source_id &&
                        record.source_entity == needle.source_entity &&
                        record.attribute_index == needle.attribute_index;
                });
                if (it == records_.end()) {
                    return false;
                }
                records_.erase(it);
                invalidate_materialized();
                return true;
            }

            void remove_source(uint32_t source_id) {
                records_.erase(std::remove_if(records_.begin(), records_.end(), [source_id](const inverse_record& record) {
                    return record.source_id == source_id;
                }), records_.end());
                invalidate_materialized();
            }

            void sort() const {
                if (!sorted_) {
                    std::sort(records_.begin(), records_.end(), record_less);
                    sorted_ = true;
                    invalidate_materialized();
                }
            }

            std::pair<record_iterator, record_iterator> equal_range(uint32_t referenced_id) const {
                sort();
                return std::equal_range(records_.begin(), records_.end(), referenced_id, [](const auto& a, const auto& b) {
                    if constexpr (std::is_same_v<std::decay_t<decltype(a)>, inverse_record>) {
                        return referenced_less(a, b);
                    } else {
                        return referenced_less(a, b);
                    }
                });
            }

            const std::vector<inverse_record>& records() const {
                sort();
                return records_;
            }

            bool empty() const {
                return records_.empty();
            }

            size_t size() const {
                return records_.size();
            }

            void clear() {
                records_.clear();
                sorted_ = true;
                materialized_.reset();
            }

            iterator begin() {
                return materialize().begin();
            }

            iterator end() {
                return materialize().end();
            }

            const_iterator begin() const {
                return materialize().begin();
            }

            const_iterator end() const {
                return materialize().end();
            }

            iterator find(const key_type& key) {
                return materialize().find(key);
            }

            const_iterator find(const key_type& key) const {
                return materialize().find(key);
            }

            size_t erase(const key_type& key) {
                const auto old_size = records_.size();
                records_.erase(std::remove_if(records_.begin(), records_.end(), [key](const inverse_record& record) {
                    return record.referenced_id == (uint32_t)key;
                }), records_.end());
                invalidate_materialized();
                return old_size - records_.size();
            }

            std::pair<iterator, bool> insert(const value_type& value) {
                for (const auto& bucket : value.second) {
                    for (auto source_id : bucket.second) {
                        add((uint32_t)value.first, source_id, (uint16_t)std::get<0>(bucket.first), std::get<1>(bucket.first));
                    }
                }
                auto it = find(value.first);
                return {it, true};
            }
        };

        struct IFC_PARSE_API in_memory_file_storage {

            std::vector<shared_pointer_type> read_simple_type_instances;
            std::vector<shared_pointer_type> steal_instances() {
                return std::move(read_simple_type_instances);
            }

            std::reference_wrapper<ifcopenshell::logger> logger_;
            // IfcParse::FileReader* stream;

            // Either one of these needs to be set
            ifcopenshell::file* file;
            const ifcopenshell::schema_definition* schema;

            unresolved_references* references_to_resolve = nullptr;

            typedef std::map<const ifcopenshell::declaration*, std::vector<express::base>> entities_by_type;
            typedef std::unordered_map<uint32_t, shared_pointer_type> entity_instance_by_name_storage;
            typedef map_transformer<entity_instance_by_name_storage, std::function<express::base(shared_pointer_type)>> entity_instance_by_name;
            typedef std::unordered_map<uint32_t, shared_pointer_type> type_instance_by_name;
            typedef std::map<std::string, express::base> entity_instance_by_guid;
            typedef inverse_index entities_by_ref;
            typedef entity_instance_by_name::iterator iterator;

            in_memory_file_storage(ifcopenshell::file* owner_file = nullptr, ifcopenshell::logger& logger = ifcopenshell::logger::root()) : logger_(logger), file(owner_file), schema(nullptr), byid_read_(&byid_, [this](const shared_pointer_type& data) { return express::base(data); }) {};
            in_memory_file_storage(const in_memory_file_storage& other) = delete;
            in_memory_file_storage(const in_memory_file_storage&& other) = delete;


            class type_iterator : public entities_by_type::const_iterator {
            public:
                using iterator_category = std::forward_iterator_tag;
                using value_type = entities_by_type::key_type;
                using difference_type = typename entities_by_type::const_iterator::difference_type;
                using pointer = value_type const*;
                using reference = value_type const&;

                type_iterator() : entities_by_type::const_iterator() {};

                type_iterator(const entities_by_type::const_iterator& iterator)
                    : entities_by_type::const_iterator(iterator) {};

                entities_by_type::key_type const* operator->() const {
                    return &entities_by_type::const_iterator::operator->()->first;
                }

                entities_by_type::key_type const& operator*() const {
                    return entities_by_type::const_iterator::operator*().first;
                }

                type_iterator& operator++() {
                    entities_by_type::const_iterator::operator++();
                    return *this;
                }

                type_iterator operator++(int) {
                    type_iterator tmp(*this);
                    operator++();
                    return tmp;
                }
            };

            entity_instance_by_name_storage byid_;
            type_instance_by_name tbyid_;
            entities_by_type bytype_excl_;
            entities_by_ref byref_excl_;
            entity_instance_by_guid byguid_;
            entity_instance_by_name byid_read_;

            template <typename Reader>
            shared_pointer_type load(ifcopenshell::spf_lexer<Reader>* tokens, std::optional<size_t> entity_instance_name, const ifcopenshell::declaration* declaration, const ifcopenshell::entity* entity, int attribute_index = -1, bool coerce_attribute_count = true);
            template <typename Reader>
            void try_read_semicolon(ifcopenshell::spf_lexer<Reader>* tokens) const;

            void register_inverse(unsigned referenced_id, const ifcopenshell::entity* from_entity, int instance_id, int attribute_index);
            void unregister_inverse(unsigned referenced_id, const ifcopenshell::entity* from_entity, const express::base& entity, int attribute_index);

            template <typename Reader>
            void read_from_stream(Reader* stream, const ifcopenshell::schema_definition*& schema, unsigned int& max_id, const std::set<std::string>& types_to_bypass);

            file_open_status good_ = file_open_status::SUCCESS;

            express::base instance_by_id(int instance_id);

            void add_type_ref(const express::base& new_entity) {
                if (auto* ty = new_entity.declaration().as_entity()) {
                    bytype_excl_[ty].push_back(new_entity);
                }
            }
            void remove_type_ref(const express::base& new_entity) {
                if (auto* ty = new_entity.declaration().as_entity()) {
                    auto it = bytype_excl_.find(ty);
                    if (it != bytype_excl_.end()) {
                        it->second.erase(std::remove(it->second.begin(), it->second.end(), new_entity), it->second.end());
                        if (it->second.empty()) {
                            bytype_excl_.erase(ty);
                        }
                    }
                }
            }

            void process_deletion_inverse(const express::base& entity);

            template <typename T>
            T create(int instance_id = -1);

            express::base create(const ifcopenshell::declaration* declaration, int instance_id = -1);
        };

        class IFC_PARSE_API rocks_db_file_storage {
        public:
            std::unique_ptr<rocksdb::DB> db;
            rocksdb::WriteOptions wopts;
            rocksdb::ReadOptions ropts;
            ifcopenshell::file* file;

            enum instance_ref {
                typedecl_ref,
                entityinstance_ref
            };

            // to make sure that instance pointer are constant during file lifetime
            // cache instances because we want stable pointers
            // @todo this is silly, but we cannot have the same type, this should be just a pointer then on the file side?
            typedef std::map<uint32_t, shared_pointer_type> entity_by_iden_cache;
            entity_by_iden_cache instance_cache_, type_instance_cache_;
            std::mutex instance_cache_mutex_;

            // @todo all these size_ts should probably be uint32_t for consistency with in-mem storage

            // lookup id->identity
            // typedef rocksdb_map_adapter<size_t, size_t> identity_by_id;
            // identity_by_id byid_;
            typedef rocksdb_set_view<size_t> instance_name_view;
            instance_name_view instance_ids_;
            typedef set_to_map_transformer<instance_name_view, std::function<express::base(size_t)>> entity_instance_by_name;
            entity_instance_by_name instance_by_name_;

            // typedef map_transformer<rocksdb_map_adapter<size_t, size_t>, std::function<ifcopenshell::IfcBaseClass*(size_t)>, std::function<size_t(ifcopenshell::IfcBaseClass*)>> entity_by_id;
            // storage is now Instance name -> Identity -> Pointer (cached)
            // entity_by_id byidentity_;

            // index in schema to binary serialized ids
            typedef rocksdb_map_adapter<size_t, std::string> instance_id_str_by_type;
            instance_id_str_by_type bytype_;

            // guid -> id
            typedef rocksdb_map_adapter<std::string, size_t> instance_id_by_guid_str;
            instance_id_by_guid_str byguid_internal_;

            // guid -> id -> instance
            typedef map_transformer<rocksdb_map_adapter<std::string, size_t>, std::function<express::base(size_t)>, std::function<size_t(const express::base&)>> entity_instance_by_guid;
            entity_instance_by_guid byguid_;

            typedef std::tuple<int, int, int> inverse_attr_record;
            enum INVERSE_ATTR {
                INSTANCE_ID,
                INSTANCE_TYPE,
                ATTRIBUTE_INDEX
            };
            typedef rocksdb_map_adapter<inverse_attr_record, std::vector<uint32_t>> entities_by_ref;
            entities_by_ref byref_excl_;

            bool read_only_ = false;

            // @todo naming
            rocks_db_file_storage(const std::string& path, ifcopenshell::file* owner_file, bool read_only = false);
            ~rocks_db_file_storage();

            bool read_schema(const ifcopenshell::schema_definition*& schema);

            express::base assert_existance(size_t instance_id, instance_ref reference_type);

            // @todo merge iterators (template?)
            class IFC_PARSE_API rocksdb_types_iterator {
            private:
                rocksdb::Iterator* state_;
                const rocks_db_file_storage* storage_;

                static constexpr char prefix_[] = "t|";

                std::optional<size_t> read_id_() const {
#ifdef IFOPSH_WITH_ROCKSDB
                    auto sv = state_->key().ToStringView();
                    auto ii = sv.find("|", 2);
                    if (ii != decltype(sv)::npos) {
                        char* pEnd;
                        long result = strtol(sv.data() + 2, &pEnd, 10);
                        if (*pEnd == '|') {
                            return (size_t)result;
                        }
                    }
#endif
                    return std::nullopt;
                }
            public:
                using iterator_category = std::forward_iterator_tag;
                using value_type = const ifcopenshell::declaration*;
                // @todo ?
                using difference_type = ptrdiff_t;
                using pointer = value_type const*;
                using reference = value_type const&;

                rocksdb_types_iterator()
                    : state_(nullptr)
                    , storage_(nullptr)
                {
                }

                rocksdb_types_iterator(const rocks_db_file_storage* storage)
                    : storage_(storage)
                {
#ifdef IFOPSH_WITH_ROCKSDB
                    state_ = storage->db->NewIterator(rocksdb::ReadOptions());
                    state_->Seek(prefix_);
                    if (!state_->Valid() || !state_->key().starts_with(prefix_)) {
                        delete state_;
                        state_ = nullptr;
                    }
#endif
                }

                rocksdb_types_iterator& operator++() {
#ifdef IFOPSH_WITH_ROCKSDB
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
#endif
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
            using const_iterator = entity_instance_by_name::iterator;

            void register_inverse(unsigned referenced_id, const ifcopenshell::entity* from_entity, int instance_id, int attribute_index);
            void unregister_inverse(unsigned referenced_id, const ifcopenshell::entity* from_entity, const express::base& entity, int attribute_index);

            // @todo a bit hard as a map because of value_type being an aggregate
            void add_type_ref(const express::base& new_entity);
            void remove_type_ref(const express::base& new_entity);

            express::base instance_by_id(int instance_id);

            void process_deletion_inverse(const express::base& entity);

            template <typename T>
            T create(int instance_id = -1);

            express::base create(const ifcopenshell::declaration* declaration, int instance_id = -1);
        };
    }
}

// redefine Handle macro.
#pragma pop_macro("Handle")

#endif // STORAGE_H
