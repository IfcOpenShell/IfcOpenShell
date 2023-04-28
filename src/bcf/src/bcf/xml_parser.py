"""XML Parser and Serializer factories."""
from typing import Optional, Protocol, Type, TypeVar

from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig


def build_xml_parser(context: Optional[XmlContext] = None) -> XmlParser:
    """Return a parser for an XML file."""
    parser = XmlParser(context=context or XmlContext())
    parser.register_namespace("xs", "http://www.w3.org/2001/XMLSchema")
    return parser


def build_serializer(context: Optional[XmlContext] = None) -> XmlSerializer:
    """Return a serializer for an XML file."""
    return XmlSerializer(
        config=SerializerConfig(pretty_print=True),
        context=context or XmlContext(),
    )


T = TypeVar("T")


class AbstractXmlParserSerializer(Protocol):
    """XML Parser and serializer wrapper."""

    def parse(self, xml: bytes, clazz: Type[T]) -> T:
        """
        Parse an XML file to an object.

        Args:
            xml: The XML file as bytes.
            clazz: The class to parse to.
        """

    def serialize(self, obj: T, ns_map: Optional[dict[str, str]] = None) -> str:
        """
        Serialize an object to XML.

        Args:
            obj: The object to serialize.
            ns_map: The namespace map to use.

        Returns:
            The XML as string.
        """


class XmlParserSerializer:
    """XML Parser and serializer wrapper."""

    def __init__(self) -> None:
        self.context = XmlContext()
        self.parser = build_xml_parser(self.context)
        self.serializer = build_serializer(self.context)

    def parse(self, xml: bytes, clazz: Type[T]) -> T:
        """
        Parse an XML file to an object.

        Args:
            xml: The XML file as bytes.
            clazz: The class to parse to.
        """
        return self.parser.from_bytes(xml, clazz)

    def serialize(self, obj: T, ns_map: Optional[dict[str, str]] = None) -> str:
        """
        Serialize an object to XML.

        Args:
            obj: The object to serialize.
            ns_map: The namespace map to use.

        Returns:
            The XML as string.
        """
        ns_map = ns_map or {"xs": "http://www.w3.org/2001/XMLSchema"}
        return self.serializer.render(obj, ns_map)
