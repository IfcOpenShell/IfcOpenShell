from __future__ import annotations

from enum import IntEnum

import _ifcopenshell_experimental as _native

class FileType(IntEnum):
    FT_IFCSPF = _native.FT_IFCSPF
    FT_IFCXML = _native.FT_IFCXML
    FT_IFCZIP = _native.FT_IFCZIP
    FT_ROCKSDB = _native.FT_ROCKSDB
    FT_UNKNOWN = _native.FT_UNKNOWN
    FT_AUTODETECT = _native.FT_AUTODETECT

class exception:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def with_message(message: str) -> exception:
        return exception(_native.exception_new_with_message(message))

class attribute_out_of_range_exception:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def with_message(message: str) -> attribute_out_of_range_exception:
        return attribute_out_of_range_exception(_native.attribute_out_of_range_exception_new_with_message(message))

class invalid_token_exception:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def with_token_start_token_string_expected_type(token_start: int, token_string: str, expected_type: str) -> invalid_token_exception:
        return invalid_token_exception(_native.invalid_token_exception_new_with_token_start_token_string_expected_type(token_start, token_string, expected_type))

class parameter_type:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def as_named_type(self) -> named_type:
        return named_type(_native.parameter_type_as_named_type(self._handle))

    def as_simple_type(self) -> simple_type:
        return simple_type(_native.parameter_type_as_simple_type(self._handle))

    def as_aggregation_type(self) -> aggregation_type:
        return aggregation_type(_native.parameter_type_as_aggregation_type(self._handle))

    def is_(self, arg0: str) -> bool:
        return _native.parameter_type_is(self._handle, arg0)

class named_type:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def declared_type(self) -> declaration:
        return declaration(_native.named_type_declared_type(self._handle))

    def as_named_type(self) -> named_type:
        return named_type(_native.named_type_as_named_type(self._handle))

    def is_(self, name: str) -> bool:
        return _native.named_type_is(self._handle, name)

class simple_type:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def as_simple_type(self) -> simple_type:
        return simple_type(_native.simple_type_as_simple_type(self._handle))

class aggregation_type:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def bound1(self) -> int:
        return _native.aggregation_type_bound1(self._handle)

    def bound2(self) -> int:
        return _native.aggregation_type_bound2(self._handle)

    def type_of_element(self) -> parameter_type:
        return parameter_type(_native.aggregation_type_type_of_element(self._handle))

    def as_aggregation_type(self) -> aggregation_type:
        return aggregation_type(_native.aggregation_type_as_aggregation_type(self._handle))

class declaration:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def with_name_index_in_schema(name: str, index_in_schema: int) -> declaration:
        return declaration(_native.declaration_new_with_name_index_in_schema(name, index_in_schema))

    def name(self) -> str:
        return _native.declaration_name(self._handle)

    def name_uc(self) -> str:
        return _native.declaration_name_uc(self._handle)

    def as_type_declaration(self) -> type_declaration:
        return type_declaration(_native.declaration_as_type_declaration(self._handle))

    def as_select_type(self) -> select_type:
        return select_type(_native.declaration_as_select_type(self._handle))

    def as_enumeration_type(self) -> enumeration_type:
        return enumeration_type(_native.declaration_as_enumeration_type(self._handle))

    def as_entity(self) -> entity:
        return entity(_native.declaration_as_entity(self._handle))

    def is_(self, name: str) -> bool:
        return _native.declaration_is(self._handle, name)

    def index_in_schema(self) -> int:
        return _native.declaration_index_in_schema(self._handle)

    def type(self) -> int:
        return _native.declaration_type(self._handle)

    def schema(self) -> schema_definition:
        return schema_definition(_native.declaration_schema(self._handle))

class type_declaration:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def declared_type(self) -> parameter_type:
        return parameter_type(_native.type_declaration_declared_type(self._handle))

    def as_type_declaration(self) -> type_declaration:
        return type_declaration(_native.type_declaration_as_type_declaration(self._handle))

class select_type:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def select_list(self) -> list[declaration]:
        return [declaration(item) for item in _native.select_type_select_list(self._handle)]

    def as_select_type(self) -> select_type:
        return select_type(_native.select_type_as_select_type(self._handle))

class enumeration_type:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def lookup_enum_offset(self, value_name: str) -> int:
        return _native.enumeration_type_lookup_enum_offset(self._handle, value_name)

    def as_enumeration_type(self) -> enumeration_type:
        return enumeration_type(_native.enumeration_type_as_enumeration_type(self._handle))

class attribute:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def name(self) -> str:
        return _native.attribute_name(self._handle)

    def type_of_attribute(self) -> parameter_type:
        return parameter_type(_native.attribute_type_of_attribute(self._handle))

    def optional(self) -> bool:
        return _native.attribute_optional(self._handle)

class inverse_attribute:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def name(self) -> str:
        return _native.inverse_attribute_name(self._handle)

    def bound1(self) -> int:
        return _native.inverse_attribute_bound1(self._handle)

    def bound2(self) -> int:
        return _native.inverse_attribute_bound2(self._handle)

    def entity_reference(self) -> entity:
        return entity(_native.inverse_attribute_entity_reference(self._handle))

    def attribute_reference(self) -> attribute:
        return attribute(_native.inverse_attribute_attribute_reference(self._handle))

class entity:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def is_abstract(self) -> bool:
        return _native.entity_is_abstract(self._handle)

    def subtypes(self) -> list[entity]:
        return [entity(item) for item in _native.entity_subtypes(self._handle)]

    def attributes(self) -> list[attribute]:
        return [attribute(item) for item in _native.entity_attributes(self._handle)]

    def all_attributes(self) -> list[attribute]:
        return [attribute(item) for item in _native.entity_all_attributes(self._handle)]

    def all_inverse_attributes(self) -> list[inverse_attribute]:
        return [inverse_attribute(item) for item in _native.entity_all_inverse_attributes(self._handle)]

    def attribute_by_index(self, index: int) -> attribute:
        return attribute(_native.entity_attribute_by_index(self._handle, index))

    def attribute_count(self) -> int:
        return _native.entity_attribute_count(self._handle)

    def supertype(self) -> entity:
        return entity(_native.entity_supertype(self._handle))

    def as_entity(self) -> entity:
        return entity(_native.entity_as_entity(self._handle))

class schema_definition:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def declaration_by_name_with_name(self, name: str) -> declaration:
        return declaration(_native.schema_definition_declaration_by_name_with_name(self._handle, name))

    def declaration_by_name_with_declaration_index(self, declaration_index: int) -> declaration:
        return declaration(_native.schema_definition_declaration_by_name_with_declaration_index(self._handle, declaration_index))

    def declarations(self) -> list[declaration]:
        return [declaration(item) for item in _native.schema_definition_declarations(self._handle)]

    def type_declarations(self) -> list[type_declaration]:
        return [type_declaration(item) for item in _native.schema_definition_type_declarations(self._handle)]

    def select_types(self) -> list[select_type]:
        return [select_type(item) for item in _native.schema_definition_select_types(self._handle)]

    def enumeration_types(self) -> list[enumeration_type]:
        return [enumeration_type(item) for item in _native.schema_definition_enumeration_types(self._handle)]

    def entities(self) -> list[entity]:
        return [entity(item) for item in _native.schema_definition_entities(self._handle)]

    def name(self) -> str:
        return _native.schema_definition_name(self._handle)

class Base:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def create() -> Base:
        return Base(_native.base_new())

    def declaration(self) -> declaration:
        return declaration(_native.base_declaration(self._handle))

    def unset_attribute_value(self, attribute_index: int) -> None:
        _native.base_unset_attribute_value(self._handle, attribute_index)
        return None

    def identity(self) -> int:
        return _native.base_identity(self._handle)

    def id(self) -> int:
        return _native.base_id(self._handle)

class Entity:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def create() -> Entity:
        return Entity(_native.entity_new())

    def get_inverse(self, attribute_name: str) -> list[Entity]:
        return [Entity(item) for item in _native.entity_get_inverse(self._handle, attribute_name)]

class Select:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def create() -> Select:
        return Select(_native.select_new())

    def concrete(self) -> Base:
        return Base(_native.select_concrete(self._handle))

class DeclaredType:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def create() -> DeclaredType:
        return DeclaredType(_native.declared_type_new())

class full_buffer_impl:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def create() -> full_buffer_impl:
        return full_buffer_impl(_native.full_buffer_impl_new())

    @staticmethod
    def with_path(path: str) -> full_buffer_impl:
        return full_buffer_impl(_native.full_buffer_impl_new_with_path(path))

    def size(self) -> int:
        return _native.full_buffer_impl_size(self._handle)

    def get_u32(self, position: int) -> int:
        return _native.full_buffer_impl_get_u32(self._handle, position)

    def push_next_page(self, page_data: str) -> None:
        _native.full_buffer_impl_push_next_page(self._handle, page_data)
        return None

    def drop_pages(self, up_to_position: int) -> None:
        _native.full_buffer_impl_drop_pages(self._handle, up_to_position)
        return None

class paged_file_impl:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def with_path_page_size_page_capacity(path: str, page_size: int, page_capacity: int) -> paged_file_impl:
        return paged_file_impl(_native.paged_file_impl_new_with_path_page_size_page_capacity(path, page_size, page_capacity))

    def size(self) -> int:
        return _native.paged_file_impl_size(self._handle)

    def get_u32(self, position: int) -> int:
        return _native.paged_file_impl_get_u32(self._handle, position)

    def push_next_page(self, page_data: str) -> None:
        _native.paged_file_impl_push_next_page(self._handle, page_data)
        return None

    def drop_pages(self, up_to_position: int) -> None:
        _native.paged_file_impl_drop_pages(self._handle, up_to_position)
        return None

class pushed_sequential_impl:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    def size(self) -> int:
        return _native.pushed_sequential_impl_size(self._handle)

    def get_u32(self, position: int) -> int:
        return _native.pushed_sequential_impl_get_u32(self._handle, position)

    def push_next_page(self, page_data: str) -> None:
        _native.pushed_sequential_impl_push_next_page(self._handle, page_data)
        return None

    def drop_pages(self, up_to_position: int) -> None:
        _native.pushed_sequential_impl_drop_pages(self._handle, up_to_position)
        return None

class character_encoder:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def with_input(input: str) -> character_encoder:
        return character_encoder(_native.character_encoder_new_with_input(input))

class file_open_status:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    pass

class spf_header:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    pass

class file:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def with_path(path: str, filetype: FileType = FileType.FT_AUTODETECT, readonly: bool = False) -> file:
        return file(_native.file_new_with_path_with_filetype_readonly(path, int(filetype), readonly))

    def initialize(self, path: str, filetype: FileType = FileType.FT_AUTODETECT, readonly: bool = False) -> bool:
        return _native.file_initialize_with_filetype_readonly(self._handle, path, int(filetype), readonly)

    def bypass_type(self, type_name: str) -> None:
        _native.file_bypass_type(self._handle, type_name)
        return None

    def good(self) -> file_open_status:
        return file_open_status(_native.file_good(self._handle))

    def instances_by_type(self, type_name: str) -> list[Base]:
        return [Base(item) for item in _native.file_instances_by_type(self._handle, type_name)]

    def instances_by_type_excl_subtypes(self, type_name: str) -> list[Base]:
        return [Base(item) for item in _native.file_instances_by_type_excl_subtypes(self._handle, type_name)]

    def instances_by_reference(self, reference_id: int) -> list[Base]:
        return [Base(item) for item in _native.file_instances_by_reference(self._handle, reference_id)]

    def instance_by_id(self, instance_id: int) -> Base:
        return Base(_native.file_instance_by_id(self._handle, instance_id))

    def instance_by_guid(self, global_id: str) -> Base:
        return Base(_native.file_instance_by_guid(self._handle, global_id))

    def get_total_inverses(self, instance_id: int) -> int:
        return _native.file_get_total_inverses(self._handle, instance_id)

    def fresh_id(self) -> int:
        return _native.file_fresh_id(self._handle)

    def get_max_id(self) -> int:
        return _native.file_get_max_id(self._handle)

    def ifcroot_type(self) -> declaration:
        return declaration(_native.file_ifcroot_type(self._handle))

    def recalculate_id_counter(self) -> None:
        _native.file_recalculate_id_counter(self._handle)
        return None

    def header(self) -> spf_header:
        return spf_header(_native.file_header(self._handle))

    def schema(self) -> schema_definition:
        return schema_definition(_native.file_schema(self._handle))

    def build_inverses(self) -> None:
        _native.file_build_inverses(self._handle)
        return None

    def batch(self) -> None:
        _native.file_batch(self._handle)
        return None

    def unbatch(self) -> None:
        _native.file_unbatch(self._handle)
        return None

    def reset_identity_cache(self) -> None:
        _native.file_reset_identity_cache(self._handle)
        return None

class global_id:
    __slots__ = ("_handle",)

    def __init__(self, handle) -> None:
        self._handle = handle

    @staticmethod
    def create() -> global_id:
        return global_id(_native.global_id_new())

    @staticmethod
    def with_value(value: str) -> global_id:
        return global_id(_native.global_id_new_with_value(value))

    def formatted(self) -> str:
        return _native.global_id_formatted(self._handle)
