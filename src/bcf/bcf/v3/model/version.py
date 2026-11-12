from dataclasses import dataclass, field


@dataclass(slots=True, kw_only=True)
class Version:
    version_id: str = field(
        metadata={
            "name": "VersionId",
            "type": "Attribute",
            "required": True,
        }
    )
