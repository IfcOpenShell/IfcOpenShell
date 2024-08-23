import json
import os
import zipfile
from pathlib import Path

from xsdata.models.datatype import XmlDateTime

import bcf.v3.model as mdl
from bcf.v3.bcfxml import BcfXml
from bcf.v3.topic import TopicHandler


def test_doc_ref_internal() -> None:
    """
    All the info in a BCF is parsed correctly.

    Uses sample file from https://github.com/buildingSMART/BCF-XML/
    """
    bcf_path = Path(__file__).parent / "Document reference internal.bcf"
    with BcfXml.load(bcf_path) as bcf:
        assert_everything_in_place(bcf)


def test_doc_ref_internal_save() -> None:
    base_dir = Path(__file__).parent
    bcf_path = base_dir / "Document reference internal.bcf"
    target_path = base_dir / "Document reference internal Saved.bcf"
    with BcfXml.load(bcf_path) as bcf:
        bcf.save(target_path)
    assert target_path.exists()
    with BcfXml.load(target_path) as bcf2:
        assert_everything_in_place(bcf2)
    assert_files_present(target_path)
    os.unlink(target_path)


def assert_everything_in_place(bcf: BcfXml):
    assert bcf.version.version_id == "3.0"
    assert bcf.project.name == "BCF 3.0 test cases"
    assert bcf.project.project_id == "de894a86-3a08-4ea0-b2d1-6c222b5602d1"

    assert bcf.extensions
    assert bcf.extensions.topic_types
    assert bcf.extensions.topic_types.topic_type == ["ERROR", "WARNING", "INFORMATION", "CLASH", "OTHER"]
    assert bcf.extensions.topic_statuses
    assert bcf.extensions.topic_statuses.topic_status == ["OPEN", "IN_PROGRESS", "SOLVED", "CLOSED"]
    assert bcf.extensions.priorities
    assert bcf.extensions.priorities.priority == ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert bcf.extensions.topic_labels
    assert bcf.extensions.topic_labels.topic_label == []
    assert bcf.extensions.users
    assert bcf.extensions.users.user == ["Architect@example.com", "Engineer@example.com", "MEPDesigner@example.com"]
    assert bcf.extensions.snippet_types
    assert bcf.extensions.snippet_types.snippet_type == []
    assert bcf.extensions.stages
    assert bcf.extensions.stages.stage == []

    assert len(bcf.topics) == 1
    topic_handler = bcf.topics["8ac9822a-761a-4deb-9f39-f61286acbf6a"]

    expected_h1 = mdl.Header(
        files=mdl.HeaderFiles(
            file=[
                mdl.File(
                    filename="BCF-ARK",
                    date=XmlDateTime(2021, 1, 4, 9, 37, 45),
                    reference="https://bimsync.com/project/f5fbb3c695274d1890036bf64f77eb71/revisions/007afab57f264d2296aae0a452486ae1",
                    is_external=True,
                ),
                mdl.File(
                    filename="BCF-MEP",
                    date=XmlDateTime(2017, 8, 7, 9, 51, 34),
                    reference="https://bimsync.com/project/f5fbb3c695274d1890036bf64f77eb71/revisions/a21ed391f9e046a2bb2bc879c48f1d48",
                    is_external=True,
                ),
            ]
        )
    )
    assert topic_handler.header == expected_h1

    expected_comments = [
        mdl.Comment(
            date=XmlDateTime(2021, 2, 17, 9, 16, 4, 160_000_000),
            author="Architect@example.com",
            comment="A comment",
            viewpoint=mdl.CommentViewpoint(guid="20ad2ff7-ceac-4d4b-b288-ad92a0f65182"),
            guid="c045ef04-324d-4c36-9ac8-831f2a15c6d6",
        ),
    ]
    assert topic_handler.comments == expected_comments

    expected_viewpoints = [
        mdl.ViewPoint(
            viewpoint="Viewpoint_20ad2ff7-ceac-4d4b-b288-ad92a0f65182.bcfv",
            snapshot="Snapshot_20ad2ff7-ceac-4d4b-b288-ad92a0f65182.png",
            guid="20ad2ff7-ceac-4d4b-b288-ad92a0f65182",
        ),
    ]

    expected_topic = mdl.Topic(
        reference_links=mdl.TopicReferenceLinks(),
        title="Document Reference Internal",
        labels=mdl.TopicLabels(),
        creation_date=XmlDateTime(2021, 2, 17, 9, 16, 4, 160_000_000),
        creation_author="Architect@example.com",
        modified_date=XmlDateTime(2021, 2, 17, 9, 16, 4, 160_000_000),
        assigned_to="OtherUser@doe.com",
        document_references=mdl.TopicDocumentReferences(
            document_reference=[
                mdl.DocumentReference(
                    document_guid="b1d1b7f0-60b9-457d-ad12-16e0fb997bc5",
                    description="ThisIsADocument.txt",
                    guid="048e898f-555f-47c3-a273-6c664fb2ef69",
                ),
            ],
        ),
        related_topics=mdl.TopicRelatedTopics(),
        comments=mdl.TopicComments(comment=expected_comments),
        viewpoints=mdl.TopicViewpoints(view_point=expected_viewpoints),
        guid="8ac9822a-761a-4deb-9f39-f61286acbf6a",
        server_assigned_id="6",
        topic_type="ERROR",
        topic_status="OPEN",
    )
    assert topic_handler.topic == expected_topic

    expected_m1 = mdl.Markup(
        header=expected_h1,
        topic=expected_topic,
    )
    assert topic_handler.markup == expected_m1

    assert topic_handler.bim_snippet is None

    assert_viewpoints(topic_handler.viewpoints)


def assert_viewpoints(viewpoints):
    assert len(viewpoints) == 1

    expected_vp = mdl.VisualizationInfo(
        components=mdl.Components(
            selection=mdl.ComponentSelection(),
            visibility=mdl.ComponentVisibility(
                view_setup_hints=mdl.ViewSetupHints(
                    spaces_visible=False,
                    space_boundaries_visible=False,
                    openings_visible=False,
                ),
                exceptions=mdl.ComponentVisibilityExceptions(
                    component=[
                        mdl.Component(ifc_guid="1m5wAJelDFdhn6qBdOGjos", originating_system="https://bimsync.com"),
                        mdl.Component(ifc_guid="1bbI761TbBCOoIa5Kt6PXt", originating_system="https://bimsync.com"),
                    ]
                ),
                default_visibility=True,
            ),
            coloring=mdl.ComponentColoring(),
        ),
        perspective_camera=mdl.PerspectiveCamera(
            camera_view_point=mdl.Point(x=23.112083480037754, y=-25.45574897560043, z=18.52519828443092),
            camera_direction=mdl.Direction(x=-0.6289237666876837, y=0.5933487270610425, z=-0.5023864884632315),
            camera_up_vector=mdl.Direction(x=-0.36542566067664123, y=0.3447553774917179, z=0.8646431727652648),
            field_of_view=60,
            aspect_ratio=1,
        ),
        lines=mdl.VisualizationInfoLines(),
        clipping_planes=mdl.VisualizationInfoClippingPlanes(),
        bitmaps=mdl.VisualizationInfoBitmaps(),
        guid="20ad2ff7-ceac-4d4b-b288-ad92a0f65182",
    )

    viewpoint = viewpoints["Viewpoint_20ad2ff7-ceac-4d4b-b288-ad92a0f65182.bcfv"]
    assert viewpoint.visualization_info == expected_vp
    assert viewpoint.snapshot is not None


def assert_second_viewpoint(viewpoint, expected_selection, expected_exception, expected_coloring) -> None:
    expected_vp = mdl.VisualizationInfo(
        components=mdl.Components(
            view_setup_hints=mdl.ViewSetupHints(
                spaces_visible=False,
                space_boundaries_visible=False,
                openings_visible=False,
            ),
            selection=expected_selection,
            visibility=mdl.ComponentVisibility(
                exceptions=expected_exception,
                default_visibility=False,
            ),
            coloring=expected_coloring,
        ),
        perspective_camera=mdl.PerspectiveCamera(
            camera_view_point=mdl.Point(x=-47.18794250488281, y=43.829200744628906, z=10.666350364685059),
            camera_direction=mdl.Direction(x=0.6745243072509766, y=-0.6599355936050415, z=-0.33091068267822266),
            camera_up_vector=mdl.Direction(x=0.2271970510482788, y=-0.24091780185699463, z=0.9435783624649048),
            field_of_view=60,
        ),
        guid="21dd4807-e9af-439e-a980-04d913a6b1ce",
    )
    assert viewpoint.visualization_info == expected_vp
    assert viewpoint.snapshot is not None


def assert_third_viewpoint(viewpoint, expected_selection, expected_exception, expected_coloring) -> None:
    expected_vp = mdl.VisualizationInfo(
        components=mdl.Components(
            view_setup_hints=mdl.ViewSetupHints(
                spaces_visible=False,
                space_boundaries_visible=False,
                openings_visible=True,
            ),
            selection=expected_selection,
            visibility=mdl.ComponentVisibility(
                exceptions=expected_exception,
                default_visibility=True,
            ),
            coloring=expected_coloring,
        ),
        perspective_camera=mdl.PerspectiveCamera(
            camera_view_point=mdl.Point(x=-48.974571228027344, y=-64.20051574707031, z=10.666350364685059),
            camera_direction=mdl.Direction(x=0.7232745289802551, y=0.5967116951942444, z=-0.3475759029388428),
            camera_up_vector=mdl.Direction(x=0.27662187814712524, y=0.21082592010498047, z=0.937567412853241),
            field_of_view=60,
        ),
        guid="81daa431-bf01-4a49-80a2-1ab07c177717",
    )
    assert viewpoint.visualization_info == expected_vp
    assert viewpoint.snapshot is not None


def assert_files_present(saved_bcf_path):
    expected_files = [
        "bcf.version",
        "project.bcfp",
        "documents.xml",
        "extensions.xml",
        "documents/b1d1b7f0-60b9-457d-ad12-16e0fb997bc5",
        "8ac9822a-761a-4deb-9f39-f61286acbf6a/markup.bcf",
        "8ac9822a-761a-4deb-9f39-f61286acbf6a/Viewpoint_20ad2ff7-ceac-4d4b-b288-ad92a0f65182.bcfv",
        "8ac9822a-761a-4deb-9f39-f61286acbf6a/Snapshot_20ad2ff7-ceac-4d4b-b288-ad92a0f65182.png",
    ]

    with zipfile.ZipFile(saved_bcf_path) as bcf_zip:
        for file_path in expected_files:
            assert zipfile.Path(bcf_zip, file_path).exists()
