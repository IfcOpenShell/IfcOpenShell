from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(slots=True, kw_only=True)
class ExtensionsPriorities:
    class Meta:
        global_type = False

    priority: List[str] = field(
        default_factory=list,
        metadata={
            "name": "Priority",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )


@dataclass(slots=True, kw_only=True)
class ExtensionsSnippetTypes:
    class Meta:
        global_type = False

    snippet_type: List[str] = field(
        default_factory=list,
        metadata={
            "name": "SnippetType",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )


@dataclass(slots=True, kw_only=True)
class ExtensionsStages:
    class Meta:
        global_type = False

    stage: List[str] = field(
        default_factory=list,
        metadata={
            "name": "Stage",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )


@dataclass(slots=True, kw_only=True)
class ExtensionsTopicLabels:
    class Meta:
        global_type = False

    topic_label: List[str] = field(
        default_factory=list,
        metadata={
            "name": "TopicLabel",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )


@dataclass(slots=True, kw_only=True)
class ExtensionsTopicStatuses:
    class Meta:
        global_type = False

    topic_status: List[str] = field(
        default_factory=list,
        metadata={
            "name": "TopicStatus",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )


@dataclass(slots=True, kw_only=True)
class ExtensionsTopicTypes:
    class Meta:
        global_type = False

    topic_type: List[str] = field(
        default_factory=list,
        metadata={
            "name": "TopicType",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )


@dataclass(slots=True, kw_only=True)
class ExtensionsUsers:
    class Meta:
        global_type = False

    user: List[str] = field(
        default_factory=list,
        metadata={
            "name": "User",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )


@dataclass(slots=True, kw_only=True)
class Extensions:
    topic_types: Optional[ExtensionsTopicTypes] = field(
        default=None,
        metadata={
            "name": "TopicTypes",
            "type": "Element",
            "namespace": "",
        }
    )
    topic_statuses: Optional[ExtensionsTopicStatuses] = field(
        default=None,
        metadata={
            "name": "TopicStatuses",
            "type": "Element",
            "namespace": "",
        }
    )
    priorities: Optional[ExtensionsPriorities] = field(
        default=None,
        metadata={
            "name": "Priorities",
            "type": "Element",
            "namespace": "",
        }
    )
    topic_labels: Optional[ExtensionsTopicLabels] = field(
        default=None,
        metadata={
            "name": "TopicLabels",
            "type": "Element",
            "namespace": "",
        }
    )
    users: Optional[ExtensionsUsers] = field(
        default=None,
        metadata={
            "name": "Users",
            "type": "Element",
            "namespace": "",
        }
    )
    snippet_types: Optional[ExtensionsSnippetTypes] = field(
        default=None,
        metadata={
            "name": "SnippetTypes",
            "type": "Element",
            "namespace": "",
        }
    )
    stages: Optional[ExtensionsStages] = field(
        default=None,
        metadata={
            "name": "Stages",
            "type": "Element",
            "namespace": "",
        }
    )
