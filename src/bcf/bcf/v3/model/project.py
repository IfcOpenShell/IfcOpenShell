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
            "min_length": 1,
            "white_space": "collapse",
        },
    )
    project_id: str = field(
        metadata={
            "name": "ProjectId",
            "type": "Attribute",
            "required": True,
            "min_length": 1,
            "white_space": "collapse",
        }
    )


@dataclass(**DATACLASS_KWARGS)
class ProjectInfo:
    project: Project = field(
        metadata={
            "name": "Project",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
