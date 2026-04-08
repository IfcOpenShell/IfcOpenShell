import pytest

from bcf.xml_parser import XmlParserSerializer


@pytest.fixture(scope="session")
def xml_handler() -> XmlParserSerializer:
    return XmlParserSerializer()
