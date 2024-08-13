import json
import os
import zipfile
from pathlib import Path

from xsdata.models.datatype import XmlDateTime

import bcf.v2.model as mdl
from bcf.v2.bcfxml import BcfXml
from bcf.v2.topic import TopicHandler


def test_maximum_information() -> None:
    """
    All the info in a BCF is parsed correctly.

    Uses sample file from https://github.com/buildingSMART/BCF-XML/
    """
    bcf_path = Path(__file__).parent / "MaximumInformation.bcf"
    with BcfXml.load(bcf_path) as bcf:
        assert_everything_in_place(bcf)


def test_save_maximum_information() -> None:
    base_dir = Path(__file__).parent
    bcf_path = base_dir / "MaximumInformation.bcf"
    target_path = base_dir / "MaximumInformationSaved.bcf"
    with BcfXml.load(bcf_path) as bcf:
        bcf.save(target_path)
    assert target_path.exists()
    with BcfXml.load(target_path) as bcf2:
        assert_everything_in_place(bcf2)

    expected_files = [
        "bcf.version",
        "project.bcfp",
        "7ddc3ef0-0ab7-43f1-918a-45e38b42369c/markup.bcf",
        "7ddc3ef0-0ab7-43f1-918a-45e38b42369c/bitmap.png",
        "7ddc3ef0-0ab7-43f1-918a-45e38b42369c/tux.png",
        "7ddc3ef0-0ab7-43f1-918a-45e38b42369c/JsonElement.json",
        "7ddc3ef0-0ab7-43f1-918a-45e38b42369c/Viewpoint_4ab7514b-b216-4d56-98d2-45cf8500ff5a.bcfv",
        "7ddc3ef0-0ab7-43f1-918a-45e38b42369c/Viewpoint_9a4a1878-ecbd-4916-83a8-dad82e560231.bcfv",
        "7ddc3ef0-0ab7-43f1-918a-45e38b42369c/Viewpoint_fc4019d7-365e-47f3-b6d0-b39fc48f15fc.bcfv",
        "7ddc3ef0-0ab7-43f1-918a-45e38b42369c/Snapshot_4ab7514b-b216-4d56-98d2-45cf8500ff5a.png",
        "7ddc3ef0-0ab7-43f1-918a-45e38b42369c/Snapshot_9a4a1878-ecbd-4916-83a8-dad82e560231.png",
        "7ddc3ef0-0ab7-43f1-918a-45e38b42369c/Snapshot_fc4019d7-365e-47f3-b6d0-b39fc48f15fc.png",
        "d1068c81-af04-4546-b63c-348810f6c716/markup.bcf",
        "extensions.xsd",
        "IfcPile_01.ifc",
        "markup.xsd",
    ]
    assert_files_present(target_path, expected_files)
    os.unlink(target_path)


def assert_everything_in_place(bcf: BcfXml):
    assert bcf.version.version_id == "2.1"
    assert bcf.project
    assert bcf.project.name == "BCF API Implementation"
    assert bcf.project_info
    assert bcf.project_info.extension_schema == "extensions.xsd"

    assert bcf.extensions
    assert bcf.extensions.topic_types
    assert bcf.extensions.topic_types.topic_type == ["Architecture", "Hidden Type", "Structural"]
    assert bcf.extensions.topic_statuses
    assert bcf.extensions.topic_statuses.topic_status == ["Finished status", "Open", "Closed"]
    assert bcf.extensions.priorities
    assert bcf.extensions.priorities.priority == ["Low", "High", "Medium"]
    assert bcf.extensions.topic_labels
    assert bcf.extensions.topic_labels.topic_label == [
        "Architecture",
        "IT Development",
        "Management",
        "Mechanical",
        "Structural",
    ]
    assert bcf.extensions.users
    assert bcf.extensions.users.user == ["dangl@iabi.eu", "linhard@iabi.eu"]
    assert bcf.extensions.snippet_types
    assert bcf.extensions.snippet_types.snippet_type == ["IFC2X3", "PDF", "XLSX"]
    assert bcf.extensions.stages is None

    assert len(bcf.topics) == 2
    assert_first_topic_handler(bcf.topics["7ddc3ef0-0ab7-43f1-918a-45e38b42369c"])
    second_th = bcf.topics["d1068c81-af04-4546-b63c-348810f6c716"]
    assert second_th.topic == mdl.Topic(
        title="Referenced topic",
        creation_date=XmlDateTime(2017, 5, 22, 7, 51, 0, 42987900),
        creation_author="dangl@iabi.eu",
        description="This is just an empty topic that acts as a referenced topic.",
        guid="d1068c81-af04-4546-b63c-348810f6c716",
    )


def assert_first_topic_handler(topic_handler: TopicHandler):
    assert topic_handler.guid == "7ddc3ef0-0ab7-43f1-918a-45e38b42369c"

    expected_bs1 = mdl.BimSnippet(
        reference="JsonElement.json", reference_schema="http://json-schema.org", snippet_type="JSON"
    )
    expected_t1 = mdl.Topic(
        reference_link=["https://bim--it.net"],
        title="Maximum Content",
        priority="High",
        index=0,
        labels=["Structural", "IT Development"],
        creation_date=XmlDateTime(2015, 6, 21, 12, 0, 0),
        creation_author="dangl@iabi.eu",
        modified_date=XmlDateTime(2015, 6, 21, 14, 22, 47),
        modified_author="dangl@iabi.eu",
        due_date=XmlDateTime(2016, 10, 2, 14, 22, 47),
        assigned_to="linhard@iabi.eu",
        stage="Construction Start",
        description="This is a topic with all informations present.",
        bim_snippet=expected_bs1,
        document_reference=[
            mdl.TopicDocumentReference(
                referenced_document="https://github.com/BuildingSMART/BCF-XML",
                description="GitHub BCF Specification",
                is_external=True,
            ),
            mdl.TopicDocumentReference(
                referenced_document="../markup.xsd",
                description="Markup.xsd Schema",
                is_external=False,
            ),
        ],
        related_topic=[mdl.TopicRelatedTopic(guid="d1068c81-af04-4546-b63c-348810f6c716")],
        guid="7ddc3ef0-0ab7-43f1-918a-45e38b42369c",
        topic_type="Structural",
        topic_status="Open",
    )
    assert topic_handler.topic == expected_t1
    expected_h1 = mdl.Header(
        file=[
            mdl.HeaderFile(
                filename="IfcPile_01.ifc",
                date=XmlDateTime(2014, 10, 27, 16, 27, 27),
                reference="../IfcPile_01.ifc",
                ifc_project="0M6o7Znnv7hxsbWgeu7oQq",
                ifc_spatial_structure_element="23B$bNeGHFQuMYJzvUX0FD",
                is_external=False,
            )
        ]
    )
    assert topic_handler.header == expected_h1

    expected_th1_comments = [
        mdl.Comment(
            date=XmlDateTime(2015, 8, 31, 12, 40, 17),
            author="dangl@iabi.eu",
            comment="This is an unmodified topic at the uppermost hierarchical level.\nAll times in the XML are marked as UTC times.",
            guid="07ccdba0-1736-47e1-807d-67dc6f3addaa",
        ),
        mdl.Comment(
            date=XmlDateTime(2015, 8, 31, 14, 0, 1),
            author="dangl@iabi.eu",
            comment="This comment was a reply to the first comment in BCF v2.0. This is a no longer supported functionality and therefore is to be treated as a regular comment in v2.1.",
            guid="a12766c2-61bc-40b4-ab19-e9f45fd0b0bf",
        ),
        mdl.Comment(
            date=XmlDateTime(2015, 8, 31, 13, 7, 11),
            author="dangl@iabi.eu",
            comment="This comment again is in the highest hierarchy level.\nIt references a viewpoint.",
            viewpoint=mdl.CommentViewpoint(guid="4ab7514b-b216-4d56-98d2-45cf8500ff5a"),
            guid="c2bb5bb0-773d-45dd-bdaa-19a216439ed3",
        ),
        mdl.Comment(
            date=XmlDateTime(2015, 8, 31, 15, 42, 58),
            author="dangl@iabi.eu",
            comment="This comment contained some spllng errs.\nHopefully, the modifier did catch them all.",
            modified_date=XmlDateTime(2015, 8, 31, 16, 7, 11),
            modified_author="dangl@iabi.eu",
            guid="0b843a5c-c3bf-41ef-be98-52a9f7bd9790",
        ),
    ]
    assert topic_handler.comments == expected_th1_comments

    expected_th1_viewpoints = [
        mdl.ViewPoint(
            viewpoint="Viewpoint_4ab7514b-b216-4d56-98d2-45cf8500ff5a.bcfv",
            snapshot="Snapshot_4ab7514b-b216-4d56-98d2-45cf8500ff5a.png",
            index=2,
            guid="4ab7514b-b216-4d56-98d2-45cf8500ff5a",
        ),
        mdl.ViewPoint(
            viewpoint="Viewpoint_fc4019d7-365e-47f3-b6d0-b39fc48f15fc.bcfv",
            snapshot="Snapshot_fc4019d7-365e-47f3-b6d0-b39fc48f15fc.png",
            index=0,
            guid="fc4019d7-365e-47f3-b6d0-b39fc48f15fc",
        ),
        mdl.ViewPoint(
            viewpoint="Viewpoint_9a4a1878-ecbd-4916-83a8-dad82e560231.bcfv",
            snapshot="Snapshot_9a4a1878-ecbd-4916-83a8-dad82e560231.png",
            index=1,
            guid="9a4a1878-ecbd-4916-83a8-dad82e560231",
        ),
    ]

    expected_m1 = mdl.Markup(
        header=expected_h1,
        topic=expected_t1,
        comment=expected_th1_comments,
        viewpoints=expected_th1_viewpoints,
    )
    assert topic_handler.markup == expected_m1

    assert json.loads(topic_handler.bim_snippet) == {"Material": "Concrete", "Temperatures": ["Cold", "Hot", "Hotter"]}

    assert topic_handler.reference_files["../IfcPile_01.ifc"] is not None

    assert_viewpoints(topic_handler.viewpoints)


def assert_viewpoints(viewpoints):
    assert len(viewpoints) == 3

    expected_selection = mdl.ComponentSelection(
        component=[
            mdl.Component(ifc_guid="0cSRUx$EX1NRjqiKcYQ$a0"),
            mdl.Component(ifc_guid="1jQQiGIAnFzxOUzrdmJYDS"),
            mdl.Component(ifc_guid="0fdpeZZEX3FwJ7x0ox5kzF"),
            mdl.Component(ifc_guid="23Zwlpd71EyvHlH6OZ77nK"),
            mdl.Component(ifc_guid="1OpjQ1Nlv4sQuTxfUC_8zS"),
        ]
    )

    expected_exception = mdl.ComponentVisibilityExceptions(
        component=[
            mdl.Component(ifc_guid="0Gl71cVurFn8bxAOox6M4X"),
            mdl.Component(ifc_guid="23Zwlpd71EyvHlH6OZ77nK"),
            mdl.Component(ifc_guid="3DvyPxGIn8qR0KDwbL_9r1"),
            mdl.Component(ifc_guid="0fdpeZZEX3FwJ7x0ox5kzF"),
            mdl.Component(ifc_guid="1OpjQ1Nlv4sQuTxfUC_8zS"),
        ]
    )

    expected_coloring = mdl.ComponentColoring(
        color=[
            mdl.ComponentColoringColor(
                component=[
                    mdl.Component(ifc_guid="0fdpeZZEX3FwJ7x0ox5kzF"),
                    mdl.Component(ifc_guid="23Zwlpd71EyvHlH6OZ77nK"),
                    mdl.Component(ifc_guid="1OpjQ1Nlv4sQuTxfUC_8zS"),
                    mdl.Component(ifc_guid="0cSRUx$EX1NRjqiKcYQ$a0"),
                ],
                color="3498DB",
            )
        ]
    )

    assert_first_viewpoint(
        viewpoints["Viewpoint_4ab7514b-b216-4d56-98d2-45cf8500ff5a.bcfv"],
        expected_selection,
        expected_exception,
        expected_coloring,
    )
    assert_second_viewpoint(
        viewpoints["Viewpoint_fc4019d7-365e-47f3-b6d0-b39fc48f15fc.bcfv"],
        expected_selection,
        expected_exception,
        expected_coloring,
    )
    assert_third_viewpoint(
        viewpoints["Viewpoint_9a4a1878-ecbd-4916-83a8-dad82e560231.bcfv"],
        expected_selection,
        expected_exception,
        expected_coloring,
    )


def assert_first_viewpoint(viewpoint, expected_selection, expected_exception, expected_coloring) -> None:
    expected_vp = mdl.VisualizationInfo(
        components=mdl.Components(
            view_setup_hints=mdl.ViewSetupHints(
                spaces_visible=True,
                space_boundaries_visible=True,
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
            camera_view_point=mdl.Point(x=0.43079984188079834, y=69.52057647705078, z=10.666350364685059),
            camera_direction=mdl.Direction(x=0.09159398823976517, y=-0.9375035166740417, z=-0.3357048034667969),
            camera_up_vector=mdl.Direction(x=0.01938679628074169, y=-0.3353792130947113, z=0.9418837428092957),
            field_of_view=60,
        ),
        lines=mdl.VisualizationInfoLines(
            line=[
                mdl.Line(start_point=mdl.Point(x=0, y=0, z=0), end_point=mdl.Point(x=0, y=0, z=1)),
                mdl.Line(start_point=mdl.Point(x=0, y=0, z=1), end_point=mdl.Point(x=0, y=1, z=1)),
                mdl.Line(start_point=mdl.Point(x=0, y=1, z=1), end_point=mdl.Point(x=1, y=1, z=1)),
            ]
        ),
        clipping_planes=mdl.VisualizationInfoClippingPlanes(
            clipping_plane=[
                mdl.ClippingPlane(location=mdl.Point(x=0, y=0, z=0), direction=mdl.Direction(x=0, y=0, z=1)),
                mdl.ClippingPlane(location=mdl.Point(x=0, y=0, z=0), direction=mdl.Direction(x=0, y=1, z=0)),
            ]
        ),
        bitmap=[
            mdl.VisualizationInfoBitmap(
                bitmap=mdl.BitmapFormat.PNG,
                reference="bitmap.png",
                location=mdl.Point(x=10, y=-10, z=7),
                normal=mdl.Direction(x=0, y=1, z=0),
                up=mdl.Direction(x=0, y=0, z=1),
                height=5.0,
            ),
            mdl.VisualizationInfoBitmap(
                bitmap=mdl.BitmapFormat.PNG,
                reference="tux.png",
                location=mdl.Point(x=20, y=-10, z=7),
                normal=mdl.Direction(x=0, y=1, z=0),
                up=mdl.Direction(x=0, y=0, z=1),
                height=5.0,
            ),
        ],
        guid="8dc86298-9737-40b4-a448-98a9e953293a",
    )
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


def assert_files_present(saved_bcf_path, expected_files):
    with zipfile.ZipFile(saved_bcf_path) as bcf_zip:
        for file_path in expected_files:
            assert zipfile.Path(bcf_zip, file_path).exists()
