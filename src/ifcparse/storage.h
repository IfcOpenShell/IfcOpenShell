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

#include <boost/unordered_map.hpp>

#include <variant>
#include <iterator>
#include <type_traits>
#include <iostream>
#include <deque>
#include <vector>
#include <deque>
#include <list>
#include <mutex>
#include <set>

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

class mutable_attribute_value;

namespace ifcopenshell {

    struct IFC_PARSE_API instance_reference {
        int v;
        size_t file_offset;
        operator int() const {
            return v;
        }
    };

    typedef std::variant<instance_reference, express::Base> reference_or_simple_type;
    typedef std::list<std::pair<mutable_attribute_value, std::variant<reference_or_simple_type, std::vector<reference_or_simple_type>, std::vector<std::vector<reference_or_simple_type>>>>> unresolved_references;

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
            int value_int;       //types: INT, IDENTIFIER
            double value_double; //types: FLOAT
            const std::string* value_string;  //types: STR, ENUM, KEYWORD; lifetime managed by spf_lexer::string_pool_
        };

        token() : start_pos(0),
                  type(Token_NONE) {}
        
        token(size_t start_position, token_type token_kind, const std::string& string_value)
            : start_pos(start_position), type(token_kind), value_string(&string_value) {}

        token(size_t start_position, token_type token_kind, int integer_value)
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

        int as_int();
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

    struct IFC_PARSE_API parse_context {
        std::vector<
            std::variant<
            express::Base,
            token,
            parse_context*
            >> tokens_;

        parse_context() {}
        ~parse_context();

        parse_context(const parse_context& other) = delete;
        parse_context& operator=(const parse_context& other) = delete;

        parse_context(parse_context&& other) = default;
        parse_context& operator=(parse_context&& other) = default;

        parse_context& push();

        void push(token next_token);

        void push(const express::Base& instance);

        std::shared_ptr<instance_data> construct(ifcopenshell::file* owner_file, std::optional<size_t> instance_name, unresolved_references& references_to_resolve, const ifcopenshell::declaration* declaration, std::optional<size_t> expected_size, int resolve_reference_index, bool coerce_attribute_count = true);
    };

    namespace impl {
        struct IFC_PARSE_API in_memory_file_storage {

            std::vector<std::shared_ptr<instance_data>> read_simple_type_instances;
            std::vector<std::shared_ptr<instance_data>> steal_instances() {
                return read_simple_type_instances;
            }

            // Either one of these needs to be set
            ifcopenshell::file* file;
            const ifcopenshell::schema_definition* schema;

            unresolved_references* references_to_resolve = nullptr;

            typedef std::map<const ifcopenshell::declaration*, std::vector<express::Base>> entities_by_type_t;
            typedef boost::unordered_map<uint32_t, std::shared_ptr<instance_data>> entity_instance_by_name_storage_t;
            typedef map_transformer<entity_instance_by_name_storage_t, std::function<express::Base(std::shared_ptr<instance_data>)>> entity_instance_by_name_t;
            typedef boost::unordered_map<uint32_t, std::shared_ptr<instance_data>> type_instance_by_name_t;
            typedef std::map<std::string, express::Base> entity_instance_by_guid_t;
            typedef std::unordered_map<int, std::map<std::tuple<short, short>, std::vector<uint32_t>>> entities_by_ref_t;
            typedef entity_instance_by_name_t::iterator iterator;

            in_memory_file_storage(ifcopenshell::file* owner_file = nullptr) : file(owner_file), schema(nullptr), byid_read_(&byid_, [this](const std::shared_ptr<instance_data>& data) { return express::Base(data); }) {};
            in_memory_file_storage(const in_memory_file_storage& other) = delete;
            in_memory_file_storage(const in_memory_file_storage&& other) = delete;


            class type_iterator : public entities_by_type_t::const_iterator {
            public:
                using iterator_category = std::forward_iterator_tag;
                using value_type = entities_by_type_t::key_type;
                using difference_type = typename entities_by_type_t::const_iterator::difference_type;
                using pointer = value_type const*;
                using reference = value_type const&;

                type_iterator() : entities_by_type_t::const_iterator() {};

                type_iterator(const entities_by_type_t::const_iterator& iterator)
                    : entities_by_type_t::const_iterator(iterator) {};

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

            entity_instance_by_name_storage_t byid_;
            type_instance_by_name_t tbyid_;
            entities_by_type_t bytype_excl_;
            entities_by_ref_t byref_excl_;
            entity_instance_by_guid_t byguid_;
            entity_instance_by_name_t byid_read_;

            template <typename Reader>
            void load(ifcopenshell::spf_lexer<Reader>* tokens, std::optional<size_t> entity_instance_name, const ifcopenshell::entity* entity, parse_context& context, int attribute_index = -1);
            template <typename Reader>
            void try_read_semicolon(ifcopenshell::spf_lexer<Reader>* tokens) const;

            void register_inverse(unsigned referenced_id, const ifcopenshell::entity* from_entity, int instance_id, int attribute_index);
            void unregister_inverse(unsigned referenced_id, const ifcopenshell::entity* from_entity, const express::Base& entity, int attribute_index);

            template <typename Reader>
            void read_from_stream(Reader* stream, const ifcopenshell::schema_definition*& schema, unsigned int& max_id, const std::set<std::string>& types_to_bypass);

            file_open_status good_ = file_open_status::SUCCESS;

            express::Base instance_by_id(int instance_id);

            void add_type_ref(const express::Base& new_entity) {
                if (auto* ty = new_entity.declaration().as_entity()) {
                    bytype_excl_[ty].push_back(new_entity);
                }
            }
            void remove_type_ref(const express::Base& new_entity) {
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

            void process_deletion_inverse(const express::Base& entity);

            template <typename T>
            T create(int instance_id = -1);

            express::Base create(const ifcopenshell::declaration* declaration, int instance_id = -1);
        };

        class IFC_PARSE_API rocks_db_file_storage {
        public:
            rocksdb::DB* db;
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
            typedef std::map<uint32_t, std::shared_ptr<instance_data>> entity_by_iden_cache_t;
            entity_by_iden_cache_t instance_cache_, type_instance_cache_;
            std::mutex instance_cache_mutex_;

            // @todo all these size_ts should probably be uint32_t for consistency with in-mem storage

            // lookup id->identity
            // typedef rocksdb_map_adapter<size_t, size_t> identity_by_id_t;
            // identity_by_id_t byid_;
            typedef rocksdb_set_view<size_t> instance_name_view_t;
            instance_name_view_t instance_ids_;
            typedef set_to_map_transformer<instance_name_view_t, std::function<express::Base(size_t)>> entity_instance_by_name_t;
            entity_instance_by_name_t instance_by_name_;

            // typedef map_transformer<rocksdb_map_adapter<size_t, size_t>, std::function<ifcopenshell::IfcBaseClass*(size_t)>, std::function<size_t(ifcopenshell::IfcBaseClass*)>> entity_by_id_t;
            // storage is now Instance name -> Identity -> Pointer (cached)
            // entity_by_id_t byidentity_;

            // index in schema to binary serialized ids
            typedef rocksdb_map_adapter<size_t, std::string> instance_id_str_by_type_t;
            instance_id_str_by_type_t bytype_;

            // guid -> id
            typedef rocksdb_map_adapter<std::string, size_t> instance_id_by_guid_str_t;
            instance_id_by_guid_str_t byguid_internal_;

            // guid -> id -> instance
            typedef map_transformer<rocksdb_map_adapter<std::string, size_t>, std::function<express::Base(size_t)>, std::function<size_t(const express::Base&)>> entity_instance_by_guid_t;
            entity_instance_by_guid_t byguid_;

            typedef std::tuple<int, int, int> inverse_attr_record;
            enum INVERSE_ATTR {
                INSTANCE_ID,
                INSTANCE_TYPE,
                ATTRIBUTE_INDEX
            };
            typedef rocksdb_map_adapter<inverse_attr_record, std::vector<uint32_t>> entities_by_ref_t;
            entities_by_ref_t byref_excl_;

            bool read_only_ = false;

            // @todo naming
            rocks_db_file_storage(const std::string& path, ifcopenshell::file* owner_file, bool read_only = false);
            ~rocks_db_file_storage();

            bool read_schema(const ifcopenshell::schema_definition*& schema);

            express::Base assert_existance(size_t instance_id, instance_ref reference_type);

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
            using const_iterator = entity_instance_by_name_t::iterator;

            void register_inverse(unsigned referenced_id, const ifcopenshell::entity* from_entity, int instance_id, int attribute_index);
            void unregister_inverse(unsigned referenced_id, const ifcopenshell::entity* from_entity, const express::Base& entity, int attribute_index);

            // @todo a bit hard as a map because of value_type being an aggregate
            void add_type_ref(const express::Base& new_entity);
            void remove_type_ref(const express::Base& new_entity);

            express::Base instance_by_id(int instance_id);

            void process_deletion_inverse(const express::Base& entity);

            template <typename T>
            T create(int instance_id = -1);

            express::Base create(const ifcopenshell::declaration* declaration, int instance_id = -1);
        };
    }
}

// redefine Handle macro.
#pragma pop_macro("Handle")

#endif // STORAGE_H
