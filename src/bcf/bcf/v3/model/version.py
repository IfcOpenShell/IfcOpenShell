import sys
from dataclasses import dataclass, field

DATACLASS_KWARGS = {} if sys.version_info < (3, 10) else {"slots": True, "kw_only": True}


@dataclass(**DATACLASS_KWARGS)
class Version:
    version_id: str = field(
        metadata={
            "name": "VersionId",
            "type": "Attribute",
            "required": True,
        }
    )
