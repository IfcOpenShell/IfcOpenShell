import sys
from dataclasses import dataclass, field
from typing import Optional

DATACLASS_KWARGS = {} if sys.version_info < (3, 10) else {"slots": True, "kw_only": True}


@dataclass(**DATACLASS_KWARGS)
class Project:
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "",
        },
    )
    project_id: str = field(
        metadata={
            "name": "ProjectId",
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass(**DATACLASS_KWARGS)
class ProjectExtension:
    project: Optional[Project] = field(
        default=None,
        metadata={
            "name": "Project",
            "type": "Element",
            "namespace": "",
        },
    )
    extension_schema: str = field(
        metadata={
            "name": "ExtensionSchema",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
