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
#include "parse.h"
#include "schema.h"
#include "spf_header.h"
#include "storage.h"
#include "file_open_status.h"

#include <functional>
#include <boost/multi_index/ordered_index.hpp>
#include <boost/multi_index/random_access_index.hpp>
#include <boost/multi_index/sequenced_index.hpp>
#include <boost/multi_index_container.hpp>
#include <boost/circular_buffer.hpp>
#include <iterator>
#include <map>
#include <memory>
#include <cstdint>

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

namespace ifcopenshell {

enum filetype {
    FT_IFCSPF,
    FT_IFCXML,
    FT_IFCZIP,
    FT_ROCKSDB,
    FT_UNKNOWN,
    FT_AUTODETECT
};

IFC_PARSE_API filetype guess_file_type(const std::string& path);

template <typename Reader = file_reader<full_buffer_impl>>
class IFC_PARSE_API instance_streamer {
private:
    std::unique_ptr<Reader> owned_stream_;
    Reader* stream_;
    std::unique_ptr<spf_lexer<Reader>> lexer_;
    std::unique_ptr<spf_header> owned_header_;
    ifcopenshell::file* owner_;
    boost::circular_buffer<token> token_stream_;
    const ifcopenshell::schema_definition* schema_;
    ifcopenshell::impl::in_memory_file_storage storage_;
    ifcopenshell::file_open_status good_ = ifcopenshell::file_open_status::SUCCESS;
    std::reference_wrapper<ifcopenshell::logger> logger_;
    int progress_;
    ifcopenshell::unresolved_references references_to_resolve_;
    int yielded_header_instances_ = 0;
    bool yield_header_instances_ = true;
    std::vector<const declaration*> types_to_bypass_;
    std::vector<unsigned> bypassed_instances_;
    std::vector<bool> types_to_bypass_materialized_;

    void initialize_header();
    void materialize_bypass_types();
    spf_header& ensure_header();

  public:
	bool coerce_attribute_count = true;

    operator bool() const {
        return good_ && lexer_ && !lexer_->stream->eof();
    }

    ifcopenshell::file_open_status status() const {
        return good_;
    }

    const ifcopenshell::unresolved_references& references() const {
        return references_to_resolve_;
    }

    ifcopenshell::unresolved_references& references() {
        return references_to_resolve_;
    }

    const std::vector<unsigned>& bypassed_instances() {
        std::sort(bypassed_instances_.begin(), bypassed_instances_.end());
        return bypassed_instances_;
    }

    const ifcopenshell::impl::in_memory_file_storage::entities_by_ref& inverses() const {
        return storage_.byref_excl_;
    }

    ifcopenshell::impl::in_memory_file_storage::entities_by_ref& inverses() {
        return storage_.byref_excl_;
    }

    std::vector<shared_pointer_type> steal_instances() {
        return storage_.steal_instances();
    }

    bool has_semicolon() const;

    size_t semicolon_count() const;

    void push_page(const std::string& page_data);

    instance_streamer(ifcopenshell::file* owner_file = nullptr, ifcopenshell::logger& logger = ifcopenshell::logger::root());

    instance_streamer(const std::string& path, bool use_mmap = false, ifcopenshell::file* owner_file = nullptr, ifcopenshell::logger& logger = ifcopenshell::logger::root());

    instance_streamer(void* data, int data_size, ifcopenshell::file* owner_file = nullptr, ifcopenshell::logger& logger = ifcopenshell::logger::root());

    instance_streamer(Reader* stream, ifcopenshell::file* owner_file = nullptr, ifcopenshell::logger& logger = ifcopenshell::logger::root());

    void bypass_types(const std::set<std::string>& type_names);

    void yield_header_instances(bool enabled) { yield_header_instances_ = enabled; }

    const ifcopenshell::schema_definition* schema() const { return schema_; }

    const spf_header* header() const;

    ~instance_streamer() = default;

    std::optional<std::tuple<size_t, const ifcopenshell::declaration*, shared_pointer_type>> read_instance();
};

class uninitialized_tag {};


/// This class provides access to the entity instances in an IFC file
/// The file takes ownership of instances added to this file and deletes them when the file is deleted.
class IFC_PARSE_API file {
private:
    typedef std::map<uint32_t, express::base> entity_entity_map;

    // @todo determine the constness of things (probably needs to be all const, we don't want to overwrite)
    // @todo we have variant_iterator and MapVariant, we probably need to retain only one?
public:
    using const_iterator = variant_iterator<impl::in_memory_file_storage::iterator, impl::rocks_db_file_storage::const_iterator>;
    using type_iterator = variant_iterator<impl::in_memory_file_storage::type_iterator, impl::rocks_db_file_storage::rocksdb_types_iterator>;
    using storage_type = std::variant<std::monostate, impl::in_memory_file_storage, impl::rocks_db_file_storage>;

    typedef variant_map<impl::in_memory_file_storage::entity_instance_by_guid, impl::rocks_db_file_storage::entity_instance_by_guid> entity_instance_by_guid;
    entity_instance_by_guid byguid_;
    typedef variant_map<impl::in_memory_file_storage::entity_instance_by_name, impl::rocks_db_file_storage::entity_instance_by_name> entity_by_id;
    entity_by_id byid_;
    typedef variant_map<impl::in_memory_file_storage::entities_by_ref, impl::rocks_db_file_storage::entities_by_ref> entities_by_ref;
    entities_by_ref byref_excl_;

    bool check_existance_before_adding = true;
    bool calculate_unit_factors = true;

    // @todo temporarily public for header
    storage_type storage_;

    std::set<std::string> types_to_bypass_loading_;

  private:
    file_open_status good_ = file_open_status::SUCCESS;
    std::reference_wrapper<ifcopenshell::logger> logger_;

    const ifcopenshell::schema_definition* schema_;
    const ifcopenshell::declaration* ifcroot_type_;

    entity_entity_map entity_file_map_;

    unsigned int max_id_;

    std::unique_ptr<spf_header> header_;

    void set_default_header_values();

    typedef boost::multi_index_container<
        int,
        boost::multi_index::indexed_by<
            boost::multi_index::sequenced<>,
            boost::multi_index::ordered_unique<
                boost::multi_index::identity<int>>>>
        batch_deletion_ids_t;
    batch_deletion_ids_t batch_deletion_ids_;
    bool batch_mode_ = false;
    void process_deletion_(const express::base& entity);

  public:
#ifdef USE_MMAP
    /// <summary>
	/// Constructs an file object from a file path, optionally using memory-mapped I/O, only supports IFC-SPF files.
    /// </summary>
    /// <param name="path">UTF-8 file path to an IFC-SPF file</param>
    /// <param name="mmap">Whether to use memory-mapped I/O</param>
    file(const std::string& path, bool use_mmap, ifcopenshell::logger& logger = ifcopenshell::logger::root());
#endif
    /// <summary>
	/// Constructs an file object from a file path, supports IFC-SPF and the IfcOpenShell-specific RocksDB format.
    /// </summary>
    /// <param name="path">UTF-8 file path to an IFC-SPF file or RocksDB database directory</param>
    /// <param name="type">File type of the path</param>
    /// <param name="read_only">Whether to open in read-only mode, only supported on RocksDB databases</param>
    /// <param name="logger">Logger used while opening the file</param>
    file(const std::string& path, filetype type = FT_AUTODETECT, bool read_only = false, ifcopenshell::logger& logger = ifcopenshell::logger::root());

    /// <summary>
	/// Constructs an file object from a stream containing IFC-SPF data.
    /// </summary>
    file(std::istream& stream, int data_size, ifcopenshell::logger& logger = ifcopenshell::logger::root());

    /// <summary>
	/// Constructs an file object from a memory buffer containing IFC-SPF data.
    /// </summary>
    file(void* data, int data_size, ifcopenshell::logger& logger = ifcopenshell::logger::root());

    /// <summary>
    /// Constructs an file object with the specified schema, file type, and file path.
    /// @note path is only used in RocksDB mode; an SPF file is in memory only until write() is called.
    /// </summary>
    /// <param name="schema">Pointer to the schema definition to use. Defaults to the IFC4 schema if not specified.</param>
    /// <param name="type">The file type to use for the file. Defaults to FT_AUTODETECT.</param>
    /// <param name="path">The file system path to the IFC file. Defaults to an empty string.</param>
    /// <param name="logger">Logger used while creating the file.</param>
    file(const ifcopenshell::schema_definition* schema = ifcopenshell::schema_by_name("IFC4"), filetype type = FT_AUTODETECT, const std::string& path = "", ifcopenshell::logger& logger = ifcopenshell::logger::root());

    /// <summary>
    /// Constructs an unitialized file object. Call initialize() later on. Allows to specify which types to bypass during load.
    /// </summary>
    file(const uninitialized_tag& tag, ifcopenshell::logger& logger = ifcopenshell::logger::root());

    bool initialize(const std::string& path, filetype type = FT_AUTODETECT, bool read_only = false);
#ifdef USE_MMAP
    bool initialize(const std::string& path, bool use_mmap);
#endif

    /// @brief Bypass loading of all instances of the specified type name. Only applies to parsed IFC-SPF files.
    /// @param type_name case insensitive name of the type to bypass
    void bypass_type(const std::string& type_name);

    ~file();

    ifcopenshell::file_open_status good() const { return good_; }
    ifcopenshell::logger& logger() const { return logger_.get(); }

    /// Returns the first entity in the range of instances contained in the model,
    /// in arbitrary order
    entity_by_id::iterator begin() const {
        return byid_.begin();
    }

    /// Returns the first entity in the range of instances contained in the model,
    /// in arbitrary order
    entity_by_id::iterator end() const {
        return byid_.end();
    }

    type_iterator types_begin() const;
    type_iterator types_end() const;

    /// Returns all entities in the file that match the template argument.
    /// NOTE: This also returns subtypes of the requested type, for example:
    /// IfcWall will also return IfcWallStandardCase entities
    template <class T>
    typename std::vector<T> instances_by_type() {
        std::vector<express::base> untyped_list = instances_by_type(&T::Class());
        std::vector<T> return_value;
        for (auto& untyped : untyped_list) {
            return_value.push_back(untyped.as<T>());
        }
        return return_value;
    }

    template <class T>
    typename std::vector<T> instances_by_type_excl_subtypes() {
        std::vector<express::base> untyped_list = instances_by_type_excl_subtypes(&T::Class());
        std::vector<T> return_value;
        for (auto& untyped : untyped_list) {
            return_value.push_back(untyped.as<T>());
        }
        return return_value;
    }

    /// Returns all entities in the file that match the positional argument.
    /// NOTE: This also returns subtypes of the requested type, for example:
    /// IfcWall will also return IfcWallStandardCase entities
    std::vector<express::base> instances_by_type(const ifcopenshell::declaration* declaration);

    /// Returns all entities in the file that match the positional argument.
    std::vector<express::base> instances_by_type_excl_subtypes(const ifcopenshell::declaration* declaration);

    /// Returns all entities in the file that match the positional argument.
    /// NOTE: This also returns subtypes of the requested type, for example:
    /// IfcWall will also return IfcWallStandardCase entities
    std::vector<express::base> instances_by_type(const std::string& type_name);

    /// Returns all entities in the file that match the positional argument.
    std::vector<express::base> instances_by_type_excl_subtypes(const std::string& type_name);

    /// Returns all entities in the file that reference the id
    std::vector<express::base> instances_by_reference(int reference_id);

    /// Returns the entity with the specified id
    express::base instance_by_id(int instance_id);

    /// Returns the entity with the specified GlobalId
    express::base instance_by_guid(const std::string& global_id);

    /// Performs a depth-first traversal, returning all entity instance
    /// attributes as a flat list. NB: includes the root instance specified
    /// in the first function argument.
    static std::vector<express::base> traverse(const express::base& instance, int max_depth = -1);

    /// Same as traverse() but maintains topological order by using a
    /// breadth-first search
    static std::vector<express::base> traverse_breadth_first(const express::base& instance, int max_depth = -1);

    /// Get the attribute indices corresponding to the list of entity instances
    /// returned by get_inverse().
    std::vector<int> get_inverse_indices_by_id(int instance_id);

    template <typename T>
    typename T::list::ptr get_inverse(int instance_id, int attribute_index) {
        return get_inverse(instance_id, &T::Class(), attribute_index)->template as<T>();
    }

    std::vector<express::entity> get_inverse(int instance_id, const ifcopenshell::declaration* declaration, int attribute_index);

    size_t get_total_inverses(int instance_id);

    unsigned int fresh_id() { return ++max_id_; }

    unsigned int get_max_id() const { return max_id_; }

    const ifcopenshell::declaration* ifcroot_type() const { return ifcroot_type_; }

    void recalculate_id_counter();

    express::base add_entity(const express::base& entity, int instance_id = -1);

    /// Removes entity instance from file and unsets references.
    ///
    /// Attention when running remove_entity inside a loop over a list of entities to be removed.
    /// This invalidates the iterator. A workaround is to reverse the loop:
    /// std::shared_ptr<aggregate_of_instance> entities = ...;
    /// for (auto it = entities->end() - 1; it >= entities->begin(); --it) {
    ///    ifcopenshell::IfcBaseClass *const inst = *it;
    ///    model->remove_entity(inst);
    /// }
    void remove_entity(const express::base& entity);

    const spf_header& header() const { return *header_; }
    spf_header& header() { return *header_; }

    static std::string create_timestamp();

    const ifcopenshell::schema_definition* schema() const;

    std::pair<express::base, double> get_unit(const std::string& unit_type);

    void build_inverses();

    void register_inverse(unsigned referenced_id, const ifcopenshell::entity* from_entity, int instance_id, int attribute_index);
    void unregister_inverse(unsigned referenced_id, const ifcopenshell::entity* from_entity, const express::base& entity, int attribute_index);

    entity_instance_by_guid internal_guid_map() { return byguid_; };

    void add_type_ref(const express::base& new_entity);
    void remove_type_ref(const express::base& new_entity);
    void process_deletion_inverse(const express::base& entity);

    void build_inverses_(const express::base& entity);

    template <typename T>
    T create(int instance_id = -1) {
        return create(&T::Class(), instance_id).template as<T>();
    }

    express::base create(const ifcopenshell::declaration* declaration, int instance_id = -1);

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

} // namespace ifcopenshell

template <typename T>
T ifcopenshell::impl::in_memory_file_storage::create(int id) {
    return create(&T::declaration(), id).template as<T>();
}

#ifdef IFOPSH_WITH_ROCKSDB

template <typename T>
T ifcopenshell::impl::rocks_db_file_storage::create(int id) {
    if constexpr (std::is_same_v<std::decay_t<std::invoke_result_t<typename T::Class>>, ifcopenshell::entity> || std::is_same_v<std::decay_t<std::invoke_result_t<typename T::Class>>, ifcopenshell::type_declaration>) {
        auto* inst = new T(rocks_db_attribute_storage{});
        inst->file_ = file;
        return file->add_entity(inst)->template as<T>();
    } else {
        static_assert(dependent_false_v<T>, "Requires and entity or type declaration");
    }
}

#endif

namespace std {
template <>
struct iterator_traits<ifcopenshell::file::type_iterator> {
    typedef ptrdiff_t difference_type;
    typedef const ifcopenshell::declaration* value_type;
    typedef const ifcopenshell::declaration*& reference;
    typedef const ifcopenshell::declaration** pointer;
    typedef std::forward_iterator_tag iterator_category;
};
} // namespace std

#endif
