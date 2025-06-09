# NOTE: This file is not generated from
# https://github.com/buildingSMART/BCF-XML/blob/release_2_1/Extension%20Schemas/extensions.xsd
# because in bcf 2.1 there is no extensions.xml - I guess, the schema assumes that each .bcf
# will use their own schema patched by it's own extensions.xsd.
#
# To make things simpler we just mimic extensions structures from bcf 3, so they'll have common API,
# and parse extensions.xsd inside .bcf as .xml and fill our structures.
#
# Preferably if we could generate some kind of extensions.xml from extensions.xsd
# and leave all the handling to xsdata.
#
# We also don't add it to __init__.py not to mess with generator.
#
# Currently extensions support for v2 is only read-only.


import sys
from dataclasses import dataclass, field, fields
from typing import Optional


DATACLASS_KWARGS = {} if sys.version_info < (3, 10) else {"slots": True, "kw_only": True}


@dataclass(**DATACLASS_KWARGS)
class ExtensionsPriorities:
    class Meta:
        global_type = False

    priority: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Priority",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class ExtensionsSnippetTypes:
    class Meta:
        global_type = False

    snippet_type: list[str] = field(
        default_factory=list,
        metadata={
            "name": "SnippetType",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class ExtensionsStages:
    class Meta:
        global_type = False

    stage: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Stage",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class ExtensionsTopicLabels:
    class Meta:
        global_type = False

    topic_label: list[str] = field(
        default_factory=list,
        metadata={
            "name": "TopicLabel",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class ExtensionsTopicStatuses:
    class Meta:
        global_type = False

    topic_status: list[str] = field(
        default_factory=list,
        metadata={
            "name": "TopicStatus",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class ExtensionsTopicTypes:
    class Meta:
        global_type = False

    topic_type: list[str] = field(
        default_factory=list,
        metadata={
            "name": "TopicType",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class ExtensionsUsers:
    class Meta:
        global_type = False

    user: list[str] = field(
        default_factory=list,
        metadata={
            "name": "UserIdType",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class Extensions:
    topic_types: Optional[ExtensionsTopicTypes] = field(
        default=None,
        metadata={
            "name": "TopicTypes",
            "type": "Element",
            "namespace": "",
        },
    )
    topic_statuses: Optional[ExtensionsTopicStatuses] = field(
        default=None,
        metadata={
            "name": "TopicStatuses",
            "type": "Element",
            "namespace": "",
        },
    )
    priorities: Optional[ExtensionsPriorities] = field(
        default=None,
        metadata={
            "name": "Priorities",
            "type": "Element",
            "namespace": "",
        },
    )
    topic_labels: Optional[ExtensionsTopicLabels] = field(
        default=None,
        metadata={
            "name": "TopicLabels",
            "type": "Element",
            "namespace": "",
        },
    )
    users: Optional[ExtensionsUsers] = field(
        default=None,
        metadata={
            "name": "Users",
            "type": "Element",
            "namespace": "",
        },
    )
    snippet_types: Optional[ExtensionsSnippetTypes] = field(
        default=None,
        metadata={
            "name": "SnippetTypes",
            "type": "Element",
            "namespace": "",
        },
    )
    stages: Optional[ExtensionsStages] = field(
        default=None,
        metadata={
            "name": "Stages",
            "type": "Element",
            "namespace": "",
        },
    )
