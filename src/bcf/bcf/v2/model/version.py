import sys
from dataclasses import dataclass, field
from typing import Optional

DATACLASS_KWARGS = {} if sys.version_info < (3, 10) else {"slots": True, "kw_only": True}


@dataclass(**DATACLASS_KWARGS)
class Version:
    detailed_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "DetailedVersion",
            "type": "Element",
            "namespace": "",
        },
    )
    version_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "VersionId",
            "type": "Attribute",
        },
    )
