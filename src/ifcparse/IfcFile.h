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
#include "storage.h"
#include "file_open_status.h"

#include <boost/multi_index/ordered_index.hpp>
#include <boost/multi_index/random_access_index.hpp>
#include <boost/multi_index/sequenced_index.hpp>
#include <boost/multi_index_container.hpp>
#include <boost/circular_buffer.hpp>
#include <iterator>
#include <map>

#ifdef IFOPSH_WITH_ROCKSDB

#include <rocksdb/merge_operator.h>

namespace {
    // @todo move to a proper place
    class ConcatenateIdMergeOperator : public rocksdb::AssociativeMergeOperator {
    public:

        virtual bool FullMergeV2(const MergeOperator::MergeOperationInput& merge_in,
            MergeOperator::MergeOperationOutput* merge_out) const {
            // Log(InfoLogLevel::INFO_LEVEL, merge_in.logger, "FullMergeV2 new_value size:%ld", merge_out->new_value.size());
            merge_out->new_value.clear();
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
#endif

namespace IfcParse {

enum filetype {
    FT_IFCSPF,
    FT_IFCXML,
    FT_IFCZIP,
    FT_ROCKSDB,
    FT_UNKNOWN,
    FT_AUTODETECT
};

IFC_PARSE_API filetype guess_file_type(const std::string& fn);

class IFC_PARSE_API InstanceStreamer {
private:
    FileReader* stream_;
    IfcSpfLexer* lexer_;
    IfcSpfHeader* header_;
    IfcParse::IfcFile* owner_;
    boost::circular_buffer<Token> token_stream_;
    const IfcParse::schema_definition* schema_;
    IfcParse::impl::in_memory_file_storage storage_;
    IfcParse::file_open_status good_ = IfcParse::file_open_status::SUCCESS;
    int progress_;
    IfcParse::unresolved_references references_to_resolve_;
    int yielded_header_instances_ = 0;
    std::vector<const declaration*> types_to_bypass_;
    std::vector<unsigned> bypassed_instances_;

  public:
	bool coerce_attribute_count = true;

    operator bool() const {
        return good_ && !lexer_->stream->eof();
    }

    IfcParse::file_open_status status() const {
        return good_;
    }

    const IfcParse::unresolved_references& references() const {
        return references_to_resolve_;
    }

    IfcParse::unresolved_references& references() {
        return references_to_resolve_;
    }

    const std::vector<unsigned>& bypassed_instances() {
        std::sort(bypassed_instances_.begin(), bypassed_instances_.end());
        return bypassed_instances_;
    }

    const IfcParse::impl::in_memory_file_storage::entities_by_ref_t& inverses() const {
        return storage_.byref_excl_;
    }

    IfcParse::impl::in_memory_file_storage::entities_by_ref_t& inverses() {
        return storage_.byref_excl_;
    }

    std::vector<std::shared_ptr<InstanceData>> stealInstances() {
        return storage_.steal_instances();
    }

    bool hasSemicolon() const;

    size_t semicolonCount() const;

    void pushPage(const std::string& page);

    InstanceStreamer(IfcParse::IfcFile* f = nullptr);

    InstanceStreamer(const std::string& fn, bool mmap = false, IfcParse::IfcFile* f = nullptr);

    InstanceStreamer(void* data, int length, IfcParse::IfcFile* f = nullptr);

    InstanceStreamer(const IfcParse::schema_definition* schema, IfcParse::IfcSpfLexer* lexer, IfcParse::IfcFile* f = nullptr);

    void bypassTypes(const std::set<std::string>& type_names);

    ~InstanceStreamer() {
        delete stream_;
        if (stream_) {
            delete lexer_;
        }
        delete header_;
    }

    std::optional<std::tuple<size_t, const IfcParse::declaration*, std::shared_ptr<InstanceData>>> readInstance();
};

class uninitialized_tag {};


/// This class provides access to the entity instances in an IFC file
/// The file takes ownership of instances added to this file and deletes them when the file is deleted.
class IFC_PARSE_API IfcFile {
private:
    typedef std::map<uint32_t, express::Base> entity_entity_map_t;

    // @todo determine the constness of things (probably needs to be all const, we don't want to overwrite)
    // @todo we have variant_iterator and MapVariant, we probably need to retain only one?
public:
    using const_iterator = variant_iterator<impl::in_memory_file_storage::iterator, impl::rocks_db_file_storage::const_iterator>;
    using type_iterator = variant_iterator<impl::in_memory_file_storage::type_iterator, impl::rocks_db_file_storage::rocksdb_types_iterator>;
    using storage_t = std::variant<std::monostate, impl::in_memory_file_storage, impl::rocks_db_file_storage>;

    typedef VariantMap<impl::in_memory_file_storage::entity_instance_by_guid_t, impl::rocks_db_file_storage::entity_instance_by_guid_t> entity_instance_by_guid_t;
    entity_instance_by_guid_t byguid_;
    typedef VariantMap<impl::in_memory_file_storage::entity_instance_by_name_t, impl::rocks_db_file_storage::entity_instance_by_name_t> entity_by_id_t;
    entity_by_id_t byid_;
    typedef VariantMap<impl::in_memory_file_storage::entities_by_ref_t, impl::rocks_db_file_storage::entities_by_ref_t> entities_by_ref_t;
    entities_by_ref_t byref_excl_;

    bool check_existance_before_adding = true;
    bool calculate_unit_factors = true;

    // @todo temporarily public for header
    storage_t storage_;

    std::set<std::string> types_to_bypass_loading_;

  private:
    file_open_status good_ = file_open_status::SUCCESS;

    const IfcParse::schema_definition* schema_;
    const IfcParse::declaration* ifcroot_type_;

    entity_entity_map_t entity_file_map_;

    unsigned int max_id_;

    std::unique_ptr<IfcSpfHeader> header_;

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
    void process_deletion_(const express::Base& entity);

  public:
#ifdef USE_MMAP
    /// <summary>
	/// Constructs an IfcFile object from a file path, optionally using memory-mapped I/O, only supports IFC-SPF files.
    /// </summary>
    /// <param name="path">UTF-8 file path to an IFC-SPF file</param>
    /// <param name="mmap">Whether to use memory-mapped I/O</param>
    IfcFile(const std::string& path, bool mmap);
#endif
    /// <summary>
	/// Constructs an IfcFile object from a file path, supports IFC-SPF and the IfcOpenShell-specific RocksDB format.
    /// </summary>
    /// <param name="path">UTF-8 file path to an IFC-SPF file or RocksDB database directory</param>
    /// <param name="ty">File type of the path</param>
    /// <param name="readonly">Whether to open in read-only mode, only supported on RocksDB databases</param>
    IfcFile(const std::string& path, filetype ty=FT_AUTODETECT, bool readonly=false);

    /// <summary>
	/// Constructs an IfcFile object from a stream containing IFC-SPF data.
    /// </summary>
    IfcFile(std::istream& stream, int length);

    /// <summary>
	/// Constructs an IfcFile object from a memory buffer containing IFC-SPF data.
    /// </summary>
    IfcFile(void* data, int length);

    /// <summary>
    /// Constructs an IfcFile object from a given IFC SPF stream.
    /// </summary>
    /// <param name="stream">A pointer to an IfcParse::FileReader object representing the input IFC SPF data stream.</param>
    IfcFile(IfcParse::FileReader* stream);

    /// <summary>
    /// Constructs an IfcFile object with the specified schema, file type, and file path.
    /// @nb path is only used in rocksdb mode, for spf file is in-memory only until write() is called
    /// </summary>
    /// <param name="schema">Pointer to the schema definition to use. Defaults to the IFC4 schema if not specified.</param>
    /// <param name="ty">The file type to use for the file. Defaults to FT_AUTODETECT.</param>
    /// <param name="path">The file system path to the IFC file. Defaults to an empty string.</param>
    IfcFile(const IfcParse::schema_definition* schema = IfcParse::schema_by_name("IFC4"), filetype ty = FT_AUTODETECT, const std::string& path = "");

    /// <summary>
    /// Constructs an unitialized IfcFile object. Call initialize() later on. Allows to specify which types to bypass during load.
    /// </summary>
    IfcFile(const uninitialized_tag&);

    bool initialize(const std::string& path, filetype ty = FT_AUTODETECT, bool readonly = false);
#ifdef USE_MMAP
    bool initialize(const std::string& path, bool mmap);
#endif

    /// @brief Bypass loading of all instances of the specified type name. Only applies to parsed IFC-SPF files.
    /// @param type_name case insensitive name of the type to bypass
    void bypass_type(const std::string& type_name);

    ~IfcFile();

    IfcParse::file_open_status good() const { return good_; }

    /// Returns the first entity in the range of instances contained in the model,
    /// in arbitrary order
    entity_by_id_t::iterator begin() const {
        return byid_.begin();
    }

    /// Returns the first entity in the range of instances contained in the model,
    /// in arbitrary order
    entity_by_id_t::iterator end() const {
        return byid_.end();
    }

    type_iterator types_begin() const;
    type_iterator types_end() const;

    /// Returns all entities in the file that match the template argument.
    /// NOTE: This also returns subtypes of the requested type, for example:
    /// IfcWall will also return IfcWallStandardCase entities
    template <class T>
    typename std::vector<T> instances_by_type() {
        std::vector<express::Base> untyped_list = instances_by_type(&T::Class());
        std::vector<T> return_value;
        for (auto& untyped : untyped_list) {
            return_value.push_back(untyped.as<T>());
        }
        return return_value;
    }

    template <class T>
    typename std::vector<T> instances_by_type_excl_subtypes() {
        std::vector<express::Base> untyped_list = instances_by_type_excl_subtypes(&T::Class());
        std::vector<T> return_value;
        for (auto& untyped : untyped_list) {
            return_value.push_back(untyped.as<T>());
        }
        return return_value;
    }

    /// Returns all entities in the file that match the positional argument.
    /// NOTE: This also returns subtypes of the requested type, for example:
    /// IfcWall will also return IfcWallStandardCase entities
    std::vector<express::Base> instances_by_type(const IfcParse::declaration*);

    /// Returns all entities in the file that match the positional argument.
    std::vector<express::Base> instances_by_type_excl_subtypes(const IfcParse::declaration*);

    /// Returns all entities in the file that match the positional argument.
    /// NOTE: This also returns subtypes of the requested type, for example:
    /// IfcWall will also return IfcWallStandardCase entities
    std::vector<express::Base> instances_by_type(const std::string& type);

    /// Returns all entities in the file that match the positional argument.
    std::vector<express::Base> instances_by_type_excl_subtypes(const std::string& type);

    /// Returns all entities in the file that reference the id
    std::vector<express::Base> instances_by_reference(int id);

    /// Returns the entity with the specified id
    express::Base instance_by_id(int id);

    /// Returns the entity with the specified GlobalId
    express::Base instance_by_guid(const std::string& guid);

    /// Performs a depth-first traversal, returning all entity instance
    /// attributes as a flat list. NB: includes the root instance specified
    /// in the first function argument.
    static std::vector<express::Base> traverse(const express::Base& instance, int max_level = -1);

    /// Same as traverse() but maintains topological order by using a
    /// breadth-first search
    static std::vector<express::Base> traverse_breadth_first(const express::Base& instance, int max_level = -1);

    /// Get the attribute indices corresponding to the list of entity instances
    /// returned by getInverse().
    std::vector<int> get_inverse_indices(int instance_id);

    template <typename T>
    typename T::list::ptr getInverse(int instance_id, int attribute_index) {
        return getInverse(instance_id, &T::Class(), attribute_index)->template as<T>();
    }

    std::vector<express::Entity> getInverse(int instance_id, const IfcParse::declaration* type, int attribute_index);

    size_t getTotalInverses(int instance_id);

    unsigned int FreshId() { return ++max_id_; }

    unsigned int getMaxId() const { return max_id_; }

    const IfcParse::declaration* ifcroot_type() const { return ifcroot_type_; }

    void recalculate_id_counter();

    express::Base addEntity(const express::Base& entity, int id = -1);

    /// Removes entity instance from file and unsets references.
    ///
    /// Attention when running removeEntity inside a loop over a list of entities to be removed.
    /// This invalidates the iterator. A workaround is to reverse the loop:
    /// boost::shared_ptr<aggregate_of_instance> entities = ...;
    /// for (auto it = entities->end() - 1; it >= entities->begin(); --it) {
    ///    IfcUtil::IfcBaseClass *const inst = *it;
    ///    model->removeEntity(inst);
    /// }
    void removeEntity(const express::Base& entity);

    const IfcSpfHeader& header() const { return *header_; }
    IfcSpfHeader& header() { return *header_; }

    static std::string createTimestamp();

    const IfcParse::schema_definition* schema() const;

    std::pair<express::Base, double> getUnit(const std::string& unit_type);

    void build_inverses();

    void register_inverse(unsigned, const IfcParse::entity* from_entity, int inst_id, int attribute_index);
    void unregister_inverse(unsigned, const IfcParse::entity* from_entity, const express::Base&, int attribute_index);

    entity_instance_by_guid_t internal_guid_map() { return byguid_; };

    void add_type_ref(const express::Base& new_entity);
    void remove_type_ref(const express::Base& new_entity);
    void process_deletion_inverse(const express::Base& inst);

    void build_inverses_(const express::Base&);

    // @nb this does not support id assignment
    template <typename T, typename... Ts>
    T create(Ts&&... args) {
        T t = create(&T::Class()).template as<T>();
        if constexpr (sizeof...(Ts) > 0) {
            t.initialize(std::forward<Ts>(args)...);
        }
        return t;
    }

    template <typename T>
    T create(int id = -1) {
        return create(&T::Class(), id).template as<T>();
    }

    express::Base create(const IfcParse::declaration* decl, int id = -1);

    void batch() {
        batch_mode_ = true; 
    }
    void unbatch();

    void reset_identity_cache();
};

namespace impl {
    // Trick to have a dependent static assertion
    template <class> inline constexpr bool dependent_false_v = false;
}

} // namespace IfcParse

template <typename T>
T IfcParse::impl::in_memory_file_storage::create(int id) {
    return create(&T::declaration(), id).template as<T>();
}

#ifdef IFOPSH_WITH_ROCKSDB

template <typename T>
T IfcParse::impl::rocks_db_file_storage::create(int id) {
    if constexpr (std::is_same_v<std::decay_t<std::invoke_result_t<typename T::Class>>, IfcParse::entity> || std::is_same_v<std::decay_t<std::invoke_result_t<typename T::Class>>, IfcParse::type_declaration>) {
        auto* inst = new T(rocks_db_attribute_storage{});
        inst->file_ = file;
        return file->addEntity(inst)->template as<T>();
    } else {
        static_assert(dependent_false_v<T>, "Requires and entity or type declaration");
    }
}

#endif

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
