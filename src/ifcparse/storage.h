#ifndef STORAGE_H
#define STORAGE_H

#ifndef IFOPSH_WITH_ROCKSDB

namespace rocksdb {
    class DB {};
    class Options {};
    class WriteOptions {};
    class ReadOptions {};
    class Iterator {};
    class Status {};
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
    variant_iterator(Iterator it) : it_(it) {}

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

namespace IfcParse {

    struct InstanceReference {
        int v;
        size_t file_offset;
        operator int() const {
            return v;
        }
    };

    typedef std::variant<InstanceReference, IfcUtil::IfcBaseClass*> reference_or_simple_type;
    typedef std::list<std::pair<MutableAttributeValue, std::variant<reference_or_simple_type, std::vector<reference_or_simple_type>, std::vector<std::vector<reference_or_simple_type>>>>> unresolved_references;

    class IfcFile;
    class IfcSpfLexer;
    class IfcSpfStream;

    enum TokenType {
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

    struct Token {
        IfcSpfLexer* lexer; //TODO: remove it from here
        unsigned startPos;
        TokenType type;
        union {
            char value_char;     //types: OPERATOR
            int value_int;       //types: INT, IDENTIFIER
            double value_double; //types: FLOAT
        };

        Token() : lexer(0),
            startPos(0),
            type(Token_NONE) {
        }
        Token(IfcSpfLexer* _lexer, unsigned _startPos, unsigned /*_endPos*/, TokenType _type)
            : lexer(_lexer),
            startPos(_startPos),
            type(_type) {
        }
    };

    struct parse_context {
        std::list<
            std::variant<
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

        IfcEntityInstanceData construct(int name, unresolved_references& references_to_resolve, const IfcParse::declaration* decl, boost::optional<size_t> expected_size, int resolve_reference_index, bool coerce_attribute_count=true);
    };

    namespace impl {
        struct IFC_PARSE_API in_memory_file_storage {
            std::vector<std::unique_ptr<IfcUtil::IfcBaseClass>> read_simple_type_instances;
            std::vector<std::unique_ptr<IfcUtil::IfcBaseClass>> steal_instances() {
                return std::move(read_simple_type_instances);
            }

            IfcParse::IfcSpfLexer* tokens;
            // IfcParse::IfcSpfStream* stream;

            // Either one of these needs to be set
            IfcParse::IfcFile* file;
            const IfcParse::schema_definition* schema;

            unresolved_references* references_to_resolve = nullptr;

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

            in_memory_file_storage(IfcParse::IfcFile* f = nullptr) : tokens(nullptr), file(f), schema(nullptr) {}
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

        class IFC_PARSE_API rocks_db_file_storage {
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
            rocks_db_file_storage(const std::string& filepath, IfcParse::IfcFile* file, bool readonly=false);
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
            class IFC_PARSE_API rocksdb_types_iterator {
            private:
                rocksdb::Iterator* state_;
                const rocks_db_file_storage* storage_;

                static constexpr char prefix_[] = "t|";

                boost::optional<size_t> read_id_() const {
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
                {
                }

                rocksdb_types_iterator(const rocks_db_file_storage* fs)
                    : storage_(fs)
                {
#ifdef IFOPSH_WITH_ROCKSDB
                    state_ = fs->db->NewIterator(rocksdb::ReadOptions());
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
}

#endif // STORAGE_H
