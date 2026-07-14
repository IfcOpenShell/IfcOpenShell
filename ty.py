from typing import Union, overload


class entity_instance:
    @overload
    def is_a(self) -> str: ...
    @overload
    def is_a(self, ifc_class: str, /) -> bool: ...
    @overload
    def is_a(self, with_schema: bool, /) -> str: ...
    def is_a(self, *args: Union[str, bool]) -> Union[str, bool]:
        return args[0] if args else "foo"
