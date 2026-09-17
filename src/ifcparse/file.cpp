#include "file.h"
#include "logger.h"
#include "utils.h"

#ifdef IFOPSH_WITH_ROCKSDB
#include <rocksdb/table.h>
#include <rocksdb/convenience.h>
#include <rocksdb/version.h>
#endif

#include <filesystem>
#include <fstream>
#include <memory>
#include <system_error>
#include <utility>

/*
ifcopenshell::IfcBaseClass* ifcopenshell::impl::rocks_db_file_storage::rocksdb_instance_iterator::operator*() const {
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

ifcopenshell::impl::rocks_db_file_storage::rocksdb_types_iterator::value_type const& ifcopenshell::impl::rocks_db_file_storage::rocksdb_types_iterator::operator*() const {
    return storage_->file->schema()->declarations()[*read_id_()];
}

express::base ifcopenshell::impl::rocks_db_file_storage::assert_existance(size_t number, instance_ref r) {
#ifndef IFOPSH_WITH_ROCKSDB
    (void)number;
    (void)r;
#endif
#ifdef IFOPSH_WITH_ROCKSDB
    std::lock_guard<std::mutex> lock(instance_cache_mutex_);

    if (r == ifcopenshell::impl::rocks_db_file_storage::entityinstance_ref) {
        auto it = instance_cache_.find(number);
        if (it != instance_cache_.end()) {
            return express::base(it->second);
        }
    } else {
        auto it = type_instance_cache_.find(number);
        if (it != type_instance_cache_.end()) {
            return express::base(it->second);
        }
    }

    std::string v;

    rocksdb::Status s = db->Get(rocksdb::ReadOptions{}, rocksdb_key::type_record(r == entityinstance_ref, number), &v);
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
        // @nb note that in case of type declarations we pass the identity as the number so
        // that we can read back the attributes from the db (we cannot assign to identity).
        auto data = ifcopenshell::make_pointer_type<instance_data>(file, decl, number, rocks_db_attribute_storage{});
        if (r == ifcopenshell::impl::rocks_db_file_storage::entityinstance_ref) {
            instance_cache_.insert({number, data});
        } else {
            type_instance_cache_.insert({number, data});
        }
        return express::base(data);
    } else {
        throw exception("Instance #" + boost::lexical_cast<std::string>(number) + " not found");
    }
#else
	throw exception("RocksDB support not compiled in");
#endif
}

namespace {
    std::unique_ptr<rocksdb::DB> init_db(const std::string& filepath, bool readonly) {
#ifndef IFOPSH_WITH_ROCKSDB
        (void)filepath;
        (void)readonly;
#endif
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
        tbo.filter_policy.reset(rocksdb::NewBloomFilterPolicy(10, false)); // bits/key
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
        std::unique_ptr<rocksdb::DB> db;
        if (readonly) {
#if ROCKSDB_MAJOR > 9 || (ROCKSDB_MAJOR == 9 && ROCKSDB_MINOR >= 11)
            status = rocksdb::DB::OpenForReadOnly(options, filepath, &db);
#else
            rocksdb::DB* raw = nullptr;
            status = rocksdb::DB::OpenForReadOnly(options, filepath, &raw);
            db.reset(raw);
#endif
        } else {
#if ROCKSDB_MAJOR > 9 || (ROCKSDB_MAJOR == 9 && ROCKSDB_MINOR >= 11)
            status = rocksdb::DB::Open(options, filepath, &db);
#else
            rocksdb::DB* raw = nullptr;
            status = rocksdb::DB::Open(options, filepath, &raw);
            db.reset(raw);
#endif
        }
        if (!status.ok()) {
            return nullptr;
        }
        return db;
#else
        return nullptr;
#endif
    }
}

// @todo naming
ifcopenshell::impl::rocks_db_file_storage::rocks_db_file_storage(const std::string& filepath, ifcopenshell::file* ffile, bool readonly)
    : db(init_db(filepath, readonly))
    , file(ffile)
    , instance_ids_(db.get(), "i|")
    , instance_by_name_(&instance_ids_, [this](size_t v) { return assert_existance(v, entityinstance_ref); })
    , bytype_(db.get(), "t|")
    , byguid_internal_(db.get(), "g|"),
      byguid_(&byguid_internal_, [this](size_t v) { return assert_existance(v, entityinstance_ref); }, [](const express::base& v) { return v.identity(); })
    , byref_excl_(db.get(), "v|")
    // @todo by_identity is probably not correct here, this mapping is Name -> Identity, so Fn should have access to full pair?
    // , byidentity_(&byid_, [this](size_t v) { return assert_existance(v, by_identity); }, [](ifcopenshell::IfcBaseClass* v) { return v->identity(); })
{
    read_only_ = readonly;
#ifdef IFOPSH_WITH_ROCKSDB
    wopts.disableWAL = true;
#endif
}

ifcopenshell::impl::rocks_db_file_storage::~rocks_db_file_storage()
{
#ifdef IFOPSH_WITH_ROCKSDB
    if (db != nullptr) {
        if (!read_only_) {
            rocksdb::FlushOptions flush_options;
            flush_options.allow_write_stall = true;
            flush_options.wait = true; // Wait until flush completes.
            rocksdb::Status s = db->Flush(flush_options);

            // compact entire db
            db->CompactRange(rocksdb::CompactRangeOptions{}, nullptr, nullptr);

            assert(s.ok());
        }

        db->Close();
    }
#endif
}


express::base ifcopenshell::impl::rocks_db_file_storage::instance_by_id(int id)
{
    // @todo rename assert_existance() -> instance_by_id();
    // - no cannot be done, because it needs to differentiate between entity instances and typedecls
    return assert_existance(id, entityinstance_ref);
}

void ifcopenshell::impl::rocks_db_file_storage::process_deletion_inverse(const express::base& inst)
{
#ifndef IFOPSH_WITH_ROCKSDB
    (void)inst;
#endif
#ifdef IFOPSH_WITH_ROCKSDB
    auto id = inst.id();

    {
        // Delete every record referencing inst: all keys under v|<id>|. The
        // exclusive upper bound is the same prefix with its separator
        // incremented, so no iterator is needed to find the range end.
        const auto prefix = rocksdb_key::inverse_prefix(id);
        const auto upper_bound = rocksdb_key::upper_bound(prefix);

        rocksdb::WriteBatch batch;
        batch.DeleteRange(prefix, upper_bound);
        db->Write(wopts, &batch);
    }

    // Delete the records inst contributed through its own attributes: drop
    // its id from the value lists of every instance it references. The values
    // are uint32_t ids, as written by the serializer and register_inverse().
    // This is based on traversal which needs instances to still be contained in the map.
    // another option would be to keep byid intact for the remainder of this loop
    auto entity_attributes = traverse(inst, 1);
    for (auto& entity_attribute : entity_attributes) {
        if (entity_attribute == inst) {
            continue;
        }
        const unsigned int name = entity_attribute.id();
        // Do not update inverses for simple types (which have id()==0 in IfcOpenShell).
        if (name != 0) {
            auto prefix = rocksdb_key::inverse_prefix(name);
            auto it = std::unique_ptr<rocksdb::Iterator>(db->NewIterator(rocksdb::ReadOptions()));
            it->Seek(prefix);
            while (it->Valid() && it->key().starts_with(prefix)) {
                std::string s = it->value().ToString();

                // Iterator are snapshotted? So don't get invalidated?
                std::vector<uint32_t> vals(s.size() / sizeof(uint32_t));
                memcpy(vals.data(), s.data(), s.size());
                auto removed = std::remove(vals.begin(), vals.end(), (uint32_t)id);
                if (removed != vals.end()) {
                    vals.erase(removed, vals.end());
                    s.resize(vals.size() * sizeof(uint32_t));
                    memcpy(s.data(), vals.data(), s.size());
                    db->Put(wopts, it->key(), s);
                }

                it->Next();
            }
        }
    }
#endif
}

void ifcopenshell::impl::rocks_db_file_storage::erase_instances(const std::vector<uint32_t>& ids)
{
#ifndef IFOPSH_WITH_ROCKSDB
    (void)ids;
#endif
#ifdef IFOPSH_WITH_ROCKSDB
    // One write for every instance's keys, one lock for their cached handles.
    rocksdb::WriteBatch batch;
    for (auto id : ids) {
        const auto prefix = rocksdb_key::instance(true, id);
        batch.DeleteRange(prefix, rocksdb_key::upper_bound(prefix));
    }
    db->Write(wopts, &batch);

    std::lock_guard<std::mutex> lock(instance_cache_mutex_);
    for (auto id : ids) {
        instance_cache_.erase(id);
    }
#endif
}

express::base ifcopenshell::impl::in_memory_file_storage::instance_by_id(int id)
{
    auto it = byid_.find(id);
    if (it == byid_.end()) {
        throw exception("Instance #" + boost::lexical_cast<std::string>(id) + " not found");
    }
    return express::base(it->second);
}

ifcopenshell::file::~file() {}

ifcopenshell::filetype ifcopenshell::guess_file_type(const std::string& fn) {
    namespace fs = std::filesystem;

    // The error_code overloads report inaccessible paths as "not there"
    // instead of throwing, matching the previous stat()-based behaviour.
    std::error_code ec;
    const fs::path path(ifcopenshell::path::from_utf8(fn));
    if (!fs::exists(path, ec)) {
        // @todo this is just weird, but for consistency with earlier behaviour
        // for now the only intent for this function is to auto-detect RocksDB
        return FT_IFCSPF;
    }

    if (fs::is_directory(path, ec)) {
        // Typical RocksDB file to look for
        const auto currentFile = path / "CURRENT";

        if (!fs::is_regular_file(currentFile, ec)) {
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

express::base ifcopenshell::impl::rocks_db_file_storage::create(const ifcopenshell::declaration* decl, int id) {
#ifndef IFOPSH_WITH_ROCKSDB
    (void)decl;
    (void)id;
    throw exception("RocksDB support not compiled in");
#else
    // Mirrors in_memory_file_storage::create(). The instance's attributes
    // live in the database (written by set_attribute_value(), read back on
    // access), so the cache only has to keep the identity of the handle
    // stable: assert_existance() can reload it from the type record that
    // add_type_ref() writes.
    uint32_t instance_name;
    if (decl->as_entity() != nullptr) {
        if (id == -1) {
            if (!id_counter_recalculated_) {
                file->recalculate_id_counter();
                id_counter_recalculated_ = true;
            }
            instance_name = file->fresh_id();
        } else {
            instance_name = id;
        }
    } else if (decl->as_type_declaration() != nullptr) {
        instance_name = 0;
    } else {
        throw std::runtime_error("Requires and entity or type declaration");
    }
    auto data = ifcopenshell::make_pointer_type<instance_data>(file, decl, instance_name, rocks_db_attribute_storage{});
    {
        std::lock_guard<std::mutex> lock(instance_cache_mutex_);
        if (instance_name) {
            instance_cache_.insert({instance_name, data});
        } else {
            type_instance_cache_.insert({data->identity(), data});
        }
    }

    express::base inst(data);
    add_type_ref(inst);

    return inst;
#endif
}

express::base ifcopenshell::impl::in_memory_file_storage::create(const ifcopenshell::declaration* decl, int id) {
    uint32_t instance_name;
    if (decl->as_entity() != nullptr) {
        instance_name = id == -1 ? (int)file->fresh_id() : id;
    } else if (decl->as_type_declaration() != nullptr) {
        instance_name = 0;
    } else {
        throw std::runtime_error("Requires and entity or type declaration");
    }
    auto data = ifcopenshell::make_pointer_type<instance_data>(file, decl, instance_name, decl->as_entity() ? in_memory_attribute_storage(decl->as_entity()->attribute_count()) : in_memory_attribute_storage(1));
    if (instance_name) {
        byid_.insert({instance_name, data});
    } else {
        tbyid_.insert({data->identity(), data});
    }

    express::base inst(data);
    add_type_ref(inst);

    return inst;
}

express::base ifcopenshell::file::create(const ifcopenshell::declaration* decl, int id) {
    if (id != -1) {
        if (decl->as_entity() == nullptr) {
            throw ifcopenshell::exception("Assigning instance id during creation is only valid for entity declarations");
        }
        bool id_already_exists = false;
        try {
            if (check_existance_before_adding) {
                instance_by_id(id);
                id_already_exists = true;
            }
        } catch (...) {
        }
        if (id_already_exists) {
            throw ifcopenshell::exception("An instance with id " + boost::lexical_cast<std::string>(id) + " is already part of this file");
        }
        if ((unsigned)id > max_id_) {
            max_id_ = (unsigned)id;
        }
    }

    return std::visit([&](auto& m) -> express::base {
        if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage> ||
                      std::is_same_v<std::decay_t<decltype(m)>, impl::rocks_db_file_storage>) {
            return m.create(decl, id);
        } else {
            return express::base{};
        }
    }, storage_);
}
