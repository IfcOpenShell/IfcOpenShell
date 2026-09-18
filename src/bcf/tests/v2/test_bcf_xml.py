"""BCF XML tests."""

import uuid
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import bcf.v2.model as mdl
from bcf.v2.bcfxml import BcfXml
from bcf.v2.topic import TopicHandler
from bcf.v2.visinfo import (
    VisualizationInfoHandler,
    build_camera_from_vectors,
    build_components,
)
from bcf.xml_parser import XmlParserSerializer


@pytest.fixture()
def build_sample(xml_handler: XmlParserSerializer) -> tuple[BcfXml, TopicHandler]:
    bcf = BcfXml.create_new("Test project", xml_handler=xml_handler)
    orig_th = bcf.add_topic("Test topic", "Test message", "Test author", "Test type")
    return bcf, orig_th


def test_bcf_roundtrip(xml_handler, build_sample) -> None:
    """Saving and loading a bcf xml project returns the same objects."""
    bcf, orig_th = build_sample
    with TemporaryDirectory() as tmp_dir:
        file_path = Path(tmp_dir) / "test.bcf"
        bcf.save(file_path)
        with BcfXml.load(file_path, xml_handler=xml_handler) as parsed:
            assert parsed == bcf
            parsed_th = parsed.topics[orig_th.guid]
            assert parsed_th == orig_th


def test_bcf_edit_saveas(xml_handler, build_sample) -> None:
    """Saving and loading a bcf xml project returns the same objects."""
    bcf, orig_th = build_sample
    with TemporaryDirectory() as tmp_dir:
        file_path = Path(tmp_dir) / "test.bcf"
        bcf.save(file_path)
        with BcfXml.load(file_path, xml_handler=xml_handler) as parsed:
            for th in parsed.topics.values():
                th.topic.title = "New Topic Title"
            modified_path = Path(tmp_dir) / "edited.bcf"
            parsed.save(modified_path)
            with BcfXml.load(modified_path, xml_handler=xml_handler) as modified_parsed:
                _assert_modified_parsed(modified_parsed, bcf, orig_th, parsed)


def _assert_modified_parsed(modified_parsed, bcf, orig_th, parsed):
    assert modified_parsed == bcf
    parsed_th = modified_parsed.topics[orig_th.guid]
    assert parsed_th.markup != orig_th.markup
    assert parsed_th.markup == parsed.topics[orig_th.guid].markup
    assert parsed_th.viewpoints == orig_th.viewpoints
    assert parsed_th.bim_snippet == orig_th.bim_snippet


def test_bcf_edit(xml_handler, build_sample) -> None:
    """Saving and loading a bcf xml project returns the same objects."""
    bcf, orig_th = build_sample
    with TemporaryDirectory() as tmp_dir:
        file_path = Path(tmp_dir) / "test.bcf"
        bcf.save(file_path)
        with BcfXml.load(file_path, xml_handler=xml_handler) as parsed:
            for th in parsed.topics.values():
                th.topic.title = "New Topic Title"
            parsed.save()
            with BcfXml.load(file_path, xml_handler=xml_handler) as modified_parsed:
                _assert_modified_parsed(modified_parsed, bcf, orig_th, parsed)
                assert len(modified_parsed.topics) == 1


def test_save_no_filename(build_sample) -> None:
    bcf, _ = build_sample
    with pytest.raises(ValueError):
        bcf.save()


def test_load_no_filename() -> None:
    with pytest.raises(ValueError):
        BcfXml.load("")


def test_save_keep_open(build_sample) -> None:
    bcf, _ = build_sample
    with TemporaryDirectory() as tmp_dir:
        file_path = Path(tmp_dir) / "test.bcf"
        bcf.save(file_path, keep_open=True)
        assert bcf._zip_file is not None
        bcf._zip_file.close()


def test_massive_bcf(xml_handler) -> None:
    bcf = BcfXml.create_new("Test project", xml_handler=xml_handler)
    for i in range(100):
        th = bcf.add_topic(f"Topic {i:04}", f"Message {i:04}", "Test author", "Test type")
        vi = mdl.VisualizationInfo(
            guid=str(uuid.uuid4()),
            components=build_components(str(uuid.uuid4())),
            perspective_camera=build_camera_from_vectors([i, 0, 0], [0, 1, 0], [0, 0, 1]),
        )
        vh = VisualizationInfoHandler(visualization_info=vi, xml_handler=xml_handler)
        th.add_visinfo_handler(vh)
    assert len(bcf.topics) == 100
    with TemporaryDirectory() as tmp_dir:
        file_path = Path(tmp_dir) / "test.bcf"
        bcf.save(file_path)


# 1x1 transparent PNG, used to attach a snapshot to a viewpoint.
BLANK_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT\x08\xd7c\x90\x8a"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _make_visinfo(xml_handler):
    vi = mdl.VisualizationInfo(
        guid=str(uuid.uuid4()),
        components=build_components(str(uuid.uuid4())),
        perspective_camera=build_camera_from_vectors([1, 2, 3], [0, 1, 0], [0, 0, 1]),
    )
    return VisualizationInfoHandler(visualization_info=vi, snapshot=BLANK_PNG, xml_handler=xml_handler)


def test_bcf21_viewpoint_and_snapshot_filenames(xml_handler, build_sample) -> None:
    """BCF 2.1 requires the primary viewpoint/snapshot to be named viewpoint.bcfv/snapshot.png (issue #7152)."""
    bcf, th = build_sample
    primary = th.add_visinfo_handler(_make_visinfo(xml_handler))
    assert primary.viewpoint == "viewpoint.bcfv"
    assert primary.snapshot == "snapshot.png"

    # Additional viewpoints keep guid based names so only one viewpoint.bcfv exists.
    extra_handler = _make_visinfo(xml_handler)
    extra = th.add_visinfo_handler(extra_handler)
    assert extra.viewpoint == f"{extra_handler.guid}.bcfv"
    assert extra.snapshot == f"{extra_handler.guid}.png"

    with TemporaryDirectory() as tmp_dir:
        file_path = Path(tmp_dir) / "test.bcf"
        bcf.save(file_path)
        with zipfile.ZipFile(file_path) as zf:
            names = zf.namelist()
    assert f"{th.guid}/viewpoint.bcfv" in names
    assert f"{th.guid}/snapshot.png" in names


def test_equality_with_wrong_object(build_sample) -> None:
    assert build_sample[0] != "Wrong object"


def test_topic_equality_with_wrong_object(build_sample) -> None:
    assert build_sample[1] != "Wrong object"


def test_bcf_get_set_version(build_sample) -> None:
    bcf = build_sample[0]
    assert bcf.version.version_id == "2.1"
    bcf.version.version_id = "2.0"
    assert bcf.version.version_id == "2.0"
