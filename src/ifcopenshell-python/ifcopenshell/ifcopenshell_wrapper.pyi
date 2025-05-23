# ifcopenshell_wrapper.pyi

class FileDescription:
    description: tuple[str, ...]
    implementation_level: str

class FileName:
    name: str
    time_stamp: str
    author: tuple[str, ...]
    organization: tuple[str, ...]
    preprocessor_version: str
    originating_system: str
    authorization: str

class IfcSpfHeader:
    @property
    def file_description(self) -> FileDescription: ...
    
    @property
    def file_name(self) -> FileName: ...
