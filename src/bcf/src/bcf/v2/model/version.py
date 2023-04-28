from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True, kw_only=True)
class Version:
    detailed_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "DetailedVersion",
            "type": "Element",
            "namespace": "",
        }
    )
    version_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "VersionId",
            "type": "Attribute",
        }
    )
