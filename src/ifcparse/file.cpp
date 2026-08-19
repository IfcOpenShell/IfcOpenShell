#include "file.h"
#include "logger.h"

#ifdef IFOPSH_WITH_ROCKSDB
#include <rocksdb/table.h>
#include <rocksdb/convenience.h>
#include <rocksdb/version.h>
#endif

#include <fstream>
#include <memory>
#include <sys/types.h>
#include <sys/stat.h>
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
    auto entity_attributes = traverse(inst, 1);
    for (auto& entity_attribute : entity_attributes) {
        if (entity_attribute == inst) {
            continue;
        }
        const unsigned int name = entity_attribute.id();
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

express::base ifcopenshell::impl::in_memory_file_storage::instance_by_id(int id)
{
    auto it = byid_.find(id);
    if (it == byid_.end()) {
        throw exception("Instance #" + boost::lexical_cast<std::string>(id) + " not found");
    }
    return express::base(it->second);
}

ifcopenshell::file::~file() {}

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

ifcopenshell::filetype ifcopenshell::guess_file_type(const std::string& fn) {
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

express::base ifcopenshell::impl::rocks_db_file_storage::create(const ifcopenshell::declaration* decl, int id) {
    (void)decl;
    (void)id;
    return express::base{};
    /*
    if (decl->as_entity() || decl->as_type_declaration()) {
        auto* inst = file->schema()->instantiate(decl, rocks_db_attribute_storage{});
		// @todo maybe this needs to be set to file? In order to have a context (ie. rocksdb::db*) to write to?
        inst->file_ = nullptr;
        return file->add_entity(inst);
    } else {
        throw std::runtime_error("Requires and entity or type declaration");
    }
    */
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
