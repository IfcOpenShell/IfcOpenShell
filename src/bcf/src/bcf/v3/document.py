"""BCF XML V3 Documents handler."""
import zipfile
from typing import Any, Optional

import bcf.v3.model as mdl
from bcf.inmemory_zipfile import ZipFileInterface
from bcf.xml_parser import AbstractXmlParserSerializer, XmlParserSerializer


class DocumentsHandler:
    """BCF documents handler."""

    def __init__(
        self,
        definition: mdl.DocumentInfo,
        documents: Optional[dict[str, bytes]] = None,
        xml_handler: Optional[AbstractXmlParserSerializer] = None,
    ) -> None:
        self.definition = definition
        self.documents = documents or {}
        self._xml_handler = xml_handler or XmlParserSerializer()

    @classmethod
    def load(
        cls,
        zip_file: zipfile.ZipFile,
        xml_handler: Optional[AbstractXmlParserSerializer] = None,
    ) -> Optional["DocumentsHandler"]:
        """
        Loads the documents from the given zip file directory.

        Args:
            zip_path: The directory path inside the zip file.
            xml_handler: The xml parser/serializer to use.

        Returns:
            The documents handler.
        """
        xml_handler = xml_handler or XmlParserSerializer()
        file_to_open = zipfile.Path(zip_file, "documents.xml")
        if not file_to_open.exists():
            return None
        definition = xml_handler.parse(file_to_open.read_bytes(), mdl.DocumentInfo)
        documents = {}
        if def_docs := definition.documents:
            for document in def_docs.document:
                document_path = zipfile.Path(zip_file, f"documents/{document.guid}")
                if document_path.exists():
                    documents[document.filename] = document_path.read_bytes()
        return cls(definition, documents=documents)

    def save(self, bcf_zip: ZipFileInterface) -> None:
        """Save the documents to the zip file."""
        bcf_zip.writestr("documents.xml", self._xml_handler.serialize(self.definition))
        if documents := self.definition.documents:
            for doc in documents.document:
                if doc.filename in self.documents:
                    bcf_zip.writestr(
                        f"documents/{doc.guid}",
                        self.documents[doc.filename],
                    )
