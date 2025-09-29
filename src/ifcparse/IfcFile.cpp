#include "IfcFile.h"
#include "IfcLogger.h"

#ifdef IFOPSH_WITH_ROCKSDB
#include <rocksdb/table.h>
#include <rocksdb/convenience.h>
#endif

#include <fstream>
#include <sys/types.h>
#include <sys/stat.h>

IfcParse::parse_context::~parse_context() {
    for (auto& t : tokens_) {
        std::visit([](auto& v) {
            if constexpr (std::is_same_v<std::decay_t<decltype(v)>, parse_context*>) {
                delete v;
            }
        }, t);
    }
}

IfcParse::parse_context& IfcParse::parse_context::push() {
    auto* pc = new IfcParse::parse_context;
    tokens_.push_back(pc);
    return *pc;
}

void IfcParse::parse_context::push(Token t) {
    tokens_.push_back(t);
}

void IfcParse::parse_context::push(IfcUtil::IfcBaseClass* inst) {
    tokens_.push_back(inst);
}

namespace {
    template<typename Variant, typename T>
    struct is_type_in_variant;

    // Specialization when there are multiple types in the variant
    template<typename T, typename First, typename... Rest>
    struct is_type_in_variant<std::variant<First, Rest...>, T>
    {
        static constexpr bool value = std::is_same<T, First>::value || is_type_in_variant<std::variant<Rest...>, T>::value;
    };

    // Specialization when there is only one type left in the variant
    template<typename T, typename Last>
    struct is_type_in_variant<std::variant<Last>, T>
    {
        static constexpr bool value = std::is_same<T, Last>::value;
    };

    template<typename Variant, typename T>
    constexpr bool is_type_in_variant_v = is_type_in_variant<Variant, T>::value;

    template <typename Fn>
    void dispatch_token(int instance_id, int attribute_id, IfcParse::Token t, IfcParse::declaration* decl, Fn fn) {
        if (t.type == IfcParse::Token_BINARY) {
            fn(IfcParse::TokenFunc::asBinary(t));
        } else if (IfcParse::TokenFunc::isBool(t)) {
            fn(IfcParse::TokenFunc::asBool(t));
        } else if (IfcParse::TokenFunc::isLogical(t)) {
            fn(IfcParse::TokenFunc::asLogical(t));
        } else if (t.type == IfcParse::Token_ENUMERATION) {
            auto& s = IfcParse::TokenFunc::asStringRef(t);
            if (decl && decl->as_enumeration_type()) {
                try {
                    fn(EnumerationReference(decl->as_enumeration_type(), decl->as_enumeration_type()->lookup_enum_offset(s)));
                } catch (IfcParse::IfcException& e) {
                    Logger::Error("An enumeration literal '" + s + "' is not valid for type '" + decl->name() + "' at offset " + std::to_string(t.startPos));
                }
            } else {
                Logger::Error("An enumeration literal '" + s + "' is not expected at attribute index '" + std::to_string(attribute_id) + "' at offset " + std::to_string(t.startPos));
            }
        } else if (t.type == IfcParse::Token_FLOAT) {
            fn(IfcParse::TokenFunc::asFloat(t));
        } else if (t.type == IfcParse::Token_IDENTIFIER) {
            fn(IfcParse::reference_or_simple_type{ IfcParse::InstanceReference{ IfcParse::TokenFunc::asIdentifier(t), t.startPos } });
        } else if (t.type == IfcParse::Token_INT) {
            fn(IfcParse::TokenFunc::asInt(t));
        } else if (t.type == IfcParse::Token_STRING) {
            fn(IfcParse::TokenFunc::asStringRef(t));
        } else if (t.type == IfcParse::Token_OPERATOR && t.value_char == '*') {
            // This is only in place for the validator
            fn(Derived{});
        }
    }

    template <size_t Depth, typename Fn>
    void construct_(int instance_id, int attribute_id, IfcParse::parse_context& p, const IfcParse::aggregation_type* aggr, Fn fn) {
        if (p.tokens_.empty()) {
            // @todo instead of ugly if-else we could also default initialize the respective
            // variant types below.
            if (aggr) {
                auto aggr_type = IfcUtil::make_aggregate(IfcUtil::from_parameter_type(aggr->type_of_element()));
                if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_INT) {
                    fn(std::vector<int>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
                    fn(std::vector<double>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_STRING) {
                    fn(std::vector<std::string>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_BINARY) {
                    fn(std::vector<boost::dynamic_bitset<>>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
                    fn(aggregate_of_instance::ptr(new aggregate_of_instance));
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT) {
                    fn(std::vector<std::vector<int>>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE) {
                    fn(std::vector<std::vector<double>>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
                    fn(aggregate_of_aggregate_of_instance::ptr(new aggregate_of_aggregate_of_instance));
                }
            }
            return;
        }

        typedef std::variant<
            Blank,

            std::vector<int>,
            std::vector<double>,
            std::vector<std::string>,
            std::vector<boost::dynamic_bitset<>>,
            std::vector<IfcParse::reference_or_simple_type>,

            std::vector<std::vector<int>>,
            std::vector<std::vector<double>>,
            std::vector<std::vector<IfcParse::reference_or_simple_type>>
        > possible_aggregation_types_t;

        possible_aggregation_types_t aggregate_storage;

        auto append_to_aggregate_storage = [&aggregate_storage](const auto& v) {
            if constexpr (is_type_in_variant_v<possible_aggregation_types_t, std::vector<std::decay_t<decltype(v)>>>) {
                if (aggregate_storage.index() == 0) {
                    aggregate_storage = std::vector<std::decay_t<decltype(v)>>{ v };
                } else {
                    if (auto* vec_ptr = std::get_if<std::vector<std::decay_t<decltype(v)>>>(&aggregate_storage)) {
                        vec_ptr->push_back(v);
                    } else {
                        if constexpr (std::is_same_v<std::decay_t<decltype(v)>, int>) {
                            auto* vec_ptr2 = std::get_if<std::vector<double>>(&aggregate_storage);
                            if (vec_ptr2) {
                                // double[] + int
                                vec_ptr2->push_back((double) v);
                            }
                        }
                        if constexpr (std::is_same_v<std::decay_t<decltype(v)>, double>) {
                            auto* vec_ptr2 = std::get_if<std::vector<int>>(&aggregate_storage);
                            if (vec_ptr2) {
                                // int[] -> double[] + double
                                std::vector<double> ps(vec_ptr2->begin(), vec_ptr2->end());
                                ps.push_back(v);
                                aggregate_storage = ps;
                            }
                        }

                        if constexpr (std::is_same_v<std::decay_t<decltype(v)>, std::vector<int>>) {
                            auto* vec_ptr2 = std::get_if<std::vector<std::vector<double>>>(&aggregate_storage);
                            if (vec_ptr2) {
                                // double[][] + int[]
                                std::vector<double> vd(v.begin(), v.end());
                                vec_ptr2->push_back(vd);
                            }
                        }
                        if constexpr (std::is_same_v<std::decay_t<decltype(v)>, std::vector<double>>) {
                            auto* vec_ptr2 = std::get_if<std::vector<std::vector<int>>>(&aggregate_storage);
                            if (vec_ptr2) {
                                // int[][] -> double[][] + double[]
                                std::vector<std::vector<double>> vvd;
                                for (auto& vv : *vec_ptr2) {
                                    std::vector<double> vd(vv.begin(), vv.end());
                                    vvd.push_back(vd);
                                }
                                vvd.push_back(v);
                                aggregate_storage = vvd;
                            }
                        }

                        // @todo would be cool if we can trace this back to file offset
                        auto current = std::visit([](auto v) { 
                            if constexpr (!std::is_same_v<decltype(v), Blank>) {
                                return std::string(typeid(typename decltype(v)::value_type).name());
                            } else {
                                // Cannot occur as aggregate_storage.which() == 0
                                // is another branch several statements up. But is
                                // needed for consistency of return type.
                                return std::string{};
                            }
                        }, aggregate_storage);

                        Logger::Error("Inconsistent aggregate valuation while attempting to append " + std::string(typeid(decltype(v)).name()) + " to an aggregate of " + current);

                        // @todo boolean -> logical upgrade
                        // wait a second... there are no aggregate of bool / logical in the schema..
                        // 
                        // if constexpr (std::is_same_v<std::decay_t<decltype(v)>, bool>) {
                        //     auto* vec_ptr = boost::get<std::vector<boost::tribool>(&aggregate_storage);
                        //     vec_ptr->push_back(v);
                        // }
                        // if constexpr (std::is_same_v<std::decay_t<decltype(v)>, boost::tribool>) {
                        //     auto* vec_ptr = boost::get<std::vector<bool>(&aggregate_storage);
                        //     std::vector<boost::tribool> ps(vec_ptr->begin(), vec_ptr->end());
                        //     ps.push_back(v);
                        //     aggregate_storage = ps;
                        // }
                    }
                }
            } else {
                // @todo would be cool if we can trace this back to file offset
                Logger::Error(std::string("Aggregates of ") + typeid(decltype(v)).name() + " are not supported in the IfcOpenShell parser");
            }
        };

        for (auto& t : p.tokens_) {
            std::visit([&aggregate_storage, &append_to_aggregate_storage, aggr, instance_id, attribute_id](const auto& v) {
                if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::Token>) {
                    // @todo get aggregate of enumeration
                    dispatch_token(instance_id, attribute_id, v, aggr && aggr->type_of_element()->as_named_type() ? aggr->type_of_element()->as_named_type()->declared_type() : nullptr, append_to_aggregate_storage);
                } else if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::parse_context*>) {
                    // nested list
                    if constexpr (Depth < 3) {
                        construct_<Depth + 1>(instance_id, attribute_id, *v, nullptr, append_to_aggregate_storage);
                    }
                } else {
                    append_to_aggregate_storage(IfcParse::reference_or_simple_type{ v });
                }
            }, t);
        }

        std::visit(fn, aggregate_storage);
    }
}

IfcEntityInstanceData IfcParse::parse_context::construct(int name, unresolved_references& references_to_resolve, const IfcParse::declaration* decl, boost::optional<size_t> expected_size, int resolve_reference_index, bool coerce_attribute_count) {
    std::vector<const IfcParse::parameter_type*> parameter_types;
    std::unique_ptr<IfcParse::named_type> transient_named_type;

    if ((decl != nullptr) && (decl->as_type_declaration() != nullptr)) {
        parameter_types = { decl->as_type_declaration()->declared_type() };
    } else if ((decl != nullptr) && (decl->as_enumeration_type() != nullptr)) {
        transient_named_type.reset(new IfcParse::named_type(const_cast<IfcParse::declaration*>(decl)));
        parameter_types = { &*transient_named_type };
    } else if ((decl != nullptr) && (decl->as_entity() != nullptr)) {
        auto entity_attrs = decl->as_entity()->all_attributes();
        std::transform(
            entity_attrs.begin(),
            entity_attrs.end(),
            std::back_inserter(parameter_types),
            [](auto* attr) {
                return attr->type_of_attribute();
            }
        );
    }

    if (((decl != nullptr) && (tokens_.size() != parameter_types.size())) ||
        expected_size && *expected_size != tokens_.size())
    {
        size_t expected = expected_size ? *expected_size : parameter_types.size();
        Logger::Warning("Expected " + std::to_string(expected) + " attribute values, found " + std::to_string(tokens_.size()) + " for instance #" + std::to_string(name > 0 ? name : 0));
    }

    if (tokens_.empty()) {
        return IfcEntityInstanceData(in_memory_attribute_storage(0));
    }

    in_memory_attribute_storage storage(coerce_attribute_count
        ? (decl != nullptr
        ? (std::min)(parameter_types.size(), tokens_.size())
        : tokens_.size())
		: tokens_.size()
    );

    auto it = tokens_.begin();
    auto kt = parameter_types.begin();
    for (; it != tokens_.end() && ((decl == nullptr) || kt != parameter_types.end()); ++it) {
        auto& token = *it;
        // @todo coerce to expected type, e.g empty -> std::vector<int>, bool -> logical
        const IfcParse::parameter_type* param_type = nullptr;
        if (decl != nullptr) {
            param_type = *kt;
        }

        auto index = (uint8_t) std::distance(tokens_.begin(), it);

        std::visit([this, &storage, name, &references_to_resolve, index, param_type, resolve_reference_index](const auto& v) {
            if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::Token>) {
                dispatch_token(name, index, v, param_type && param_type->as_named_type() ? param_type->as_named_type()->declared_type() : nullptr, [this, &storage, name, &references_to_resolve, index, resolve_reference_index](auto v) {
                    if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::reference_or_simple_type>) {
                        if (name > 0) {
                            references_to_resolve.push_back(std::make_pair(
                                // @todo previously this was storage but apparently the 
                                // pointer is not constant with the moving and temporary nature
                                // maybe it ought to be and in that case a pointer is more direct
                                MutableAttributeValue{ name, resolve_reference_index == -1 ? index : (uint8_t) resolve_reference_index },
                                v
                            ));
                        }
                    } else {
                        storage.set(index, v);
                    }
                });
            } else if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::parse_context*>) {
                const auto *pt = param_type;
                if (pt) {
                    while (pt->as_named_type() && pt->as_named_type()->declared_type()->as_type_declaration()) {
                        pt = pt->as_named_type()->declared_type()->as_type_declaration()->declared_type();
                    }
                }
                construct_<0>(name, index, *v, pt ? pt->as_aggregation_type() : nullptr, [this, &storage, name, &references_to_resolve, index, resolve_reference_index](const auto& v) {
                    if constexpr (std::is_same_v<std::decay_t<decltype(v)>, std::vector<reference_or_simple_type>>) {
                        if (name > 0) {
                            references_to_resolve.push_back({ {name, resolve_reference_index == -1 ? index : (uint8_t)resolve_reference_index }, v });
                        }
                    } else if constexpr (std::is_same_v<std::decay_t<decltype(v)>, std::vector<std::vector<reference_or_simple_type>>>) {
                        if (name > 0) {
                            references_to_resolve.push_back({ {name, resolve_reference_index == -1 ? index : (uint8_t)resolve_reference_index }, v });
                        }
                    } else {
                        storage.set(index, v);
                    }
                });
            } else {
                storage.set(index, v);
            }
        }, token);

        if (decl != nullptr) {
            ++kt;
        }
    }

    return IfcEntityInstanceData(std::move(storage));
}

/*
IfcUtil::IfcBaseClass* IfcParse::impl::rocks_db_file_storage::rocksdb_instance_iterator::operator*() const {
    auto it = storage_->byid_.find(*read_id_());
    if (it != storage_->byid_.end()) {
        // @todo define an implicit std::to_string() in all map adapters with leading 0s
        auto jt = storage_->instance_cache_.find(it->second);
        if (jt != storage_->instance_cache_.end()) {
            return jt->second;
        } else {
            return storage_->assert_existance(it->first, by_name);
        }
    }
}
*/

IfcParse::impl::rocks_db_file_storage::rocksdb_types_iterator::value_type const& IfcParse::impl::rocks_db_file_storage::rocksdb_types_iterator::operator*() const {
    return storage_->file->schema()->declarations()[*read_id_()];
}

IfcUtil::IfcBaseClass* IfcParse::impl::rocks_db_file_storage::assert_existance(size_t number, instance_ref r) {
#ifdef IFOPSH_WITH_ROCKSDB
    if (r == IfcParse::impl::rocks_db_file_storage::entityinstance_ref) {
        auto it = instance_cache_.find(number);
        if (it != instance_cache_.end()) {
            return it->second;
        }
    } else {
        auto it = type_instance_cache_.find(number);
        if (it != type_instance_cache_.end()) {
            return it->second;
        }
    }
    
    std::string v;

    rocksdb::Status s = db->Get(rocksdb::ReadOptions{}, (r == entityinstance_ref ? "i|" : "t|") + std::to_string(number) + "|_", &v);
    if (s.ok()) {
        size_t s;
        memcpy(&s, v.data(), sizeof(size_t));
        if (s >= file->schema()->declarations().size()) {
            throw std::runtime_error("");
        }
        auto decl = file->schema()->declarations()[s];
        bool is_entity = decl->as_entity() != nullptr;
        if (is_entity != (r == entityinstance_ref)) {
            throw std::runtime_error("Incorrect reference");
        }
        IfcEntityInstanceData data(rocks_db_attribute_storage{});
        IfcUtil::IfcBaseClass* inst;
        if (file->instantiate_typed_instances) {
            inst = file->schema()->instantiate(decl, std::move(data));
        } else {
            inst = new IfcUtil::IfcLateBoundEntity(decl, std::move(data));
        }
        inst->id_ = number;
        inst->file_ = file;
        if (r == IfcParse::impl::rocks_db_file_storage::entityinstance_ref) {
            instance_cache_.insert({ number, inst });
        } else {
            type_instance_cache_.insert({ number, inst });
        }
        return inst;
    } else {
        throw IfcException("Instance #" + boost::lexical_cast<std::string>(number) + " not found");
    }
#else
	throw IfcException("RocksDB support not compiled in");
#endif
}

namespace {
    rocksdb::DB* init_db(const std::string& filepath, bool readonly) {
        rocksdb::DB* db = nullptr;
#ifdef IFOPSH_WITH_ROCKSDB
        
        rocksdb::Options options;
        // options.disable_auto_compactions = true;
        options.create_if_missing = true;
        options.merge_operator.reset(new ConcatenateIdMergeOperator());
        auto vec = rocksdb::GetSupportedCompressions();
        options.compression = std::find(vec.begin(), vec.end(), rocksdb::kZSTD) != vec.end() ? rocksdb::kZSTD : rocksdb::kNoCompression;

        rocksdb::BlockBasedTableOptions tbo;

        /*
        tbo.block_size = 16 * 1024;
        tbo.filter_policy.reset(rocksdb::NewBloomFilterPolicy(10 /*bits/key/, false));
        tbo.partition_filters = true;
        tbo.index_type = rocksdb::BlockBasedTableOptions::kHashSearch;
        tbo.cache_index_and_filter_blocks = true;
        tbo.cache_index_and_filter_blocks_with_high_priority = true;
        tbo.pin_top_level_index_and_filter = true;
        */

		// 28: 256MB
		// 29: 512MB
        // 30: 1GB

        auto block_cache = rocksdb::NewLRUCache(1ULL << 30);
        tbo.block_cache = block_cache;

        // rocksdb::CreateDBStatistics();

        options.table_factory.reset(rocksdb::NewBlockBasedTableFactory(tbo));

        rocksdb::Status status;
        if (readonly) {
            status = rocksdb::DB::OpenForReadOnly(options, filepath, &db);
        } else {
            status = rocksdb::DB::Open(options, filepath, &db);
        }
        if (!status.ok()) {
            return nullptr;
        }
#endif // IFOPSH_WITH_ROCKSDB#
        return db;
    }
}

// @todo naming
IfcParse::impl::rocks_db_file_storage::rocks_db_file_storage(const std::string& filepath, IfcParse::IfcFile* ffile, bool readonly)
    : file(ffile)
    , db(init_db(filepath, readonly))
    // @todo streaming serializer does not populate the byguid map
    , byguid_internal_(db, "g|")
    , byguid_(&byguid_internal_, [this](size_t v) { return assert_existance(v, entityinstance_ref); }, [](IfcUtil::IfcBaseClass* v) { return v->identity(); })
    , instance_ids_(db, "i|")
    , instance_by_name_(&instance_ids_, [this](size_t v) { return assert_existance(v, entityinstance_ref); })
    , bytype_(db, "t|")
    , byref_excl_(db, "v|")
    // @todo by_identity is probably not correct here, this mapping is Name -> Identity, so Fn should have access to full pair?
    // , byidentity_(&byid_, [this](size_t v) { return assert_existance(v, by_identity); }, [](IfcUtil::IfcBaseClass* v) { return v->identity(); })
{
#ifdef IFOPSH_WITH_ROCKSDB
    wopts.disableWAL = true;
#endif
}

IfcParse::impl::rocks_db_file_storage::~rocks_db_file_storage()
{
#ifdef IFOPSH_WITH_ROCKSDB
    rocksdb::FlushOptions flush_options;
    flush_options.allow_write_stall = true;
    flush_options.wait = true; // Wait until flush completes.
    rocksdb::Status s = db->Flush(flush_options);

    // compact entire db
    db->CompactRange(rocksdb::CompactRangeOptions{}, nullptr, nullptr);

    assert(s.ok());

    db->Close();
    delete db;
#endif
}


IfcUtil::IfcBaseClass* IfcParse::impl::rocks_db_file_storage::instance_by_id(int id)
{
    // @todo rename assert_existance() -> instance_by_id();
    // - no cannot be done, because it needs to differentiate between entity instances and typedecls
    return assert_existance(id, entityinstance_ref);
}

void IfcParse::impl::rocks_db_file_storage::process_deletion_inverse(IfcUtil::IfcBaseClass* inst)
{
#ifdef IFOPSH_WITH_ROCKSDB
    auto id = inst->id();

    {
        // compute next prefix that does not start with v|{id}|
        auto prefix = "v|" + std::to_string(id) + "|";
        auto it = std::unique_ptr<rocksdb::Iterator>(db->NewIterator(rocksdb::ReadOptions()));
        it->Seek(prefix);
        while (it->Valid()) {
            it->Next();
            if (!it->key().starts_with(prefix)) {
                break;
            }
        }

        rocksdb::WriteBatch batch;
        batch.DeleteRange(prefix, it->key());
        db->Write(wopts, &batch);
    }

    // This is based on traversal which needs instances to still be contained in the map.
    // another option would be to keep byid intact for the remainder of this loop
    aggregate_of_instance::ptr entity_attributes = traverse(inst, 1);
    for (aggregate_of_instance::it it = entity_attributes->begin(); it != entity_attributes->end(); ++it) {
        IfcUtil::IfcBaseClass* entity_attribute = *it;
        if (entity_attribute == inst) {
            continue;
        }
        const unsigned int name = entity_attribute->id();
        // Do not update inverses for simple types (which have id()==0 in IfcOpenShell).
        if (name != 0) {
            // Find instances entity -> other
            // and update inverses from entity into other

            {
                auto prefix = "v|" + std::to_string(name) + "|";
                auto it = std::unique_ptr<rocksdb::Iterator>(db->NewIterator(rocksdb::ReadOptions()));
                it->Seek(prefix);
                while (it->Valid() && it->key().starts_with(prefix)) {
                    std::string s = it->value().ToString();

                    // Iterator are snapshotted? So don't get invalidated?
                    std::vector<size_t> vals(s.size() / sizeof(size_t));
                    memcpy(vals.data(), s.data(), s.size());
                    vals.erase(std::find(vals.begin(), vals.end(), (size_t)id));
                    s.resize(vals.size() * sizeof(size_t));
                    memcpy(s.data(), vals.data(), s.size());
                    db->Put(wopts, it->key(), s);

                    it->Next();
                }
            }
        }
    }
#endif
}

IfcUtil::IfcBaseClass* IfcParse::impl::in_memory_file_storage::instance_by_id(int id)
{
    auto it = byid_.find(id);
    if (it == byid_.end()) {
        throw IfcException("Instance #" + boost::lexical_cast<std::string>(id) + " not found");
    }
    return it->second;
}

IfcParse::IfcFile::~IfcFile() {
    // @todo this does not make sense for rocksdb, because it would assert existance for the entire lazy model only to free the instances again
    for (const auto& p : byid_) {
        delete p.second;
    }
}

namespace {
	// Utility functions for path handling in order not to rely on C++17's std::filesystem
#ifdef _WIN32
#define stat_t struct _stat
    inline int stat_(const char* p, stat_t* s) { return ::_stat(p, s); }
#ifndef S_ISDIR
#define S_ISDIR(m) (((m) & _S_IFDIR) != 0)
#endif
#ifndef S_ISREG
#define S_ISREG(m) (((m) & _S_IFREG) != 0)
#endif
#else
    using stat_t = struct stat;
    inline int stat_(const char* p, stat_t* s) { return ::stat(p, s); }
#endif

    inline bool path_exists_(const std::string& p, stat_t* out = nullptr) {
        stat_t tmp;
        stat_t* s = out ? out : &tmp;
        return stat_(p.c_str(), s) == 0;
    }

    inline bool path_is_directory_(const stat_t& s) { return S_ISDIR(s.st_mode); }
    inline bool path_is_regular_file_(const stat_t& s) { return S_ISREG(s.st_mode); }

    inline std::string path_join_(const std::string& dir, const std::string& name) {
        if (dir.empty()) return name;
        const char last = dir.back();
        if (last == '/' || last == '\\') return dir + name;
#ifdef _WIN32
        const char sep = '\\';
#else
        const char sep = '/';
#endif
        return dir + sep + name;
    }
} // namespace

IfcParse::filetype IfcParse::guess_file_type(const std::string& fn) {
    stat_t st{};
    if (!path_exists_(fn, &st)) {
        // @todo this is just weird, but for consistency with earlier behaviour
        // for now the only intent for this function is to auto-detect RocksDB
        return FT_IFCSPF;
    }

    if (path_is_directory_(st)) {
        // Typical RocksDB file to look for
        auto currentFile = path_join_(fn, "CURRENT");
        stat_t cst{};

        if (!path_exists_(currentFile, &cst) || !path_is_regular_file_(cst)) {
            return FT_UNKNOWN;
        }

        std::ifstream infile(currentFile);
        if (!infile) {
            return FT_UNKNOWN;
        }

        std::string line;
        if (!std::getline(infile, line)) {
            return FT_UNKNOWN;
        }

        // RocksDB's CURRENT file typically contains a line like "MANIFEST-000001".
        if (line.find("MANIFEST-") == 0) {
            return FT_ROCKSDB;
        }

        return FT_UNKNOWN;
    } else {
        // @todo just return SPF for now, but ideally this will be augmented with all other options
        return FT_IFCSPF;
    }
}

std::optional<std::tuple<size_t, const IfcParse::declaration*, IfcEntityInstanceData>> IfcParse::InstanceStreamer::read_instance() {
    std::optional<std::tuple<size_t, const IfcParse::declaration*, IfcEntityInstanceData>> return_value;

    if (header_ && yielded_header_instances_ < 3) {
        if (yielded_header_instances_ == 0) {
            return_value.emplace(
                0,
                &header_->file_description()->declaration(),
                std::move(header_->file_description()->data())
             );
        } else if (yielded_header_instances_ == 1) {
            return_value.emplace(
                0,
                &header_->file_name()->declaration(),
                std::move(header_->file_name()->data())
            );
        } else if (yielded_header_instances_ == 2) {
            return_value.emplace(
                0,
                &header_->file_schema()->declaration(),
                std::move(header_->file_schema()->data())
            );
        }
        yielded_header_instances_ += 1;
        return return_value;
    }

    unsigned current_id = 0;
    while (good_ && !lexer_->stream->eof && !current_id) {
        if (token_stream_[0].type == IfcParse::Token_IDENTIFIER &&
            token_stream_[1].type == IfcParse::Token_OPERATOR &&
            token_stream_[1].value_char == '=' &&
            token_stream_[2].type == IfcParse::Token_KEYWORD) {
            current_id = (unsigned)TokenFunc::asIdentifier(token_stream_[0]);
            const IfcParse::declaration* entity_type;
            try {
                entity_type = schema_->declaration_by_name(TokenFunc::asStringRef(token_stream_[2]));
            } catch (const IfcException& ex) {
                Logger::Message(Logger::LOG_ERROR, std::string(ex.what()) + " at offset " + std::to_string(token_stream_[2].startPos));
                goto advance;
            }

            if (entity_type->as_entity() == nullptr) {
                Logger::Message(Logger::LOG_ERROR, "Non entity type " + entity_type->name() + " at offset " + std::to_string(token_stream_[2].startPos));
                goto advance;
            }

            parse_context ps;
            lexer_->Next();
            try {
                storage_.load(current_id, entity_type->as_entity(), ps, -1);
            } catch (const IfcInvalidTokenException& e) {
                good_ = file_open_status::INVALID_SYNTAX;
                Logger::Error(e);
                break;
            }

            /// @todo Printing to stdout in a library class feels weird. Maybe move the progress prints to the client code?
            // Update the status after every 1000 instances parsed
            if (((++progress_) % 1000) == 0) {
                std::stringstream ss;
                ss << "\r#" << current_id;
                Logger::Status(ss.str(), false);
            }

            auto data = ps.construct(current_id, references_to_resolve_, entity_type, boost::none, -1, coerce_attribute_count);

            return_value.emplace(
                (size_t)current_id,
                entity_type,
                std::move(data)
            );
        }
    advance:
        Token next_token;
        try {
            next_token = lexer_->Next();
        } catch (const IfcException& e) {
            Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + ". Parsing terminated");
        } catch (...) {
            Logger::Message(Logger::LOG_ERROR, "Parsing terminated");
        }

        if (!lexer_->stream->eof && next_token.type == Token_NONE) {
            good_ = file_open_status::INVALID_SYNTAX;
            break;
        }

        token_stream_.push_back(next_token);
    }

    return return_value;
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

IfcUtil::IfcBaseClass* IfcParse::impl::in_memory_file_storage::create(const IfcParse::declaration* decl) {
    IfcUtil::IfcBaseClass* inst = nullptr;
    if (auto* ent = decl->as_entity()) {
        inst = file->schema()->instantiate(decl, in_memory_attribute_storage(ent->attribute_count()));
    } else if (decl->as_type_declaration() != nullptr) {
        inst = file->schema()->instantiate(decl, in_memory_attribute_storage(1));
    } else {
        throw std::runtime_error("Requires and entity or type declaration");
    }
    inst->file_ = file;
    return file->addEntity(inst);
}
