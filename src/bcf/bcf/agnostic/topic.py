import tempfile
import bcf.v2.bcfxml
import bcf.v2.model
import bcf.v2.topic
import bcf.v3.bcfxml
import bcf.v3.model
import bcf.v3.topic
import bcf.agnostic.model as mdl
from pathlib import Path
from typing import Union, Optional
from typing_extensions import assert_never

TopicHandler = Union[bcf.v2.topic.TopicHandler, bcf.v3.topic.TopicHandler]


def extract_file(
    topic: TopicHandler,
    entity: Union[mdl.HeaderFile, mdl.BimSnippet, mdl.DocumentReference, mdl.BitMap],
    bcfxml: Optional[Union[bcf.v2.bcfxml.BcfXml, bcf.v3.bcfxml.BcfXml]] = None,
    outfile: Optional[Path] = None,
) -> Union[Path, str, None]:
    """Extracts an element with a file into a temporary directory

    These include header files, bim snippets, document references, and
    viewpoint bitmaps. External reference are not downloaded. Instead, the
    URI reference is returned.

    :param entity: The entity with a file reference to extract
    :param outfile: If provided, save the header file to that location.
        Otherwise, a temporary directory is created and the filename is
        derived from the header's original filename.
    :param bcfxml: The BCF XML file to use for resolving document references files.
        Required only for BCF v3 document references (in BCF v3 internal documents
        are stored at BCF root, not in the topic).
    :return: The filepath of the extracted file. It may be a URL if the
        header file is external.
    """
    if isinstance(entity, mdl.DocumentReference):
        if isinstance(entity, bcf.v2.model.TopicDocumentReference):
            reference = entity.referenced_document
        else:
            reference = entity.document_guid
    else:
        reference = entity.reference

    if not reference:
        return None

    # For v3 document references external documents are detected by empty document_guid.
    # External bitmaps are not supported by bcf.
    if not isinstance(entity, (bcf.v3.model.DocumentReference, mdl.BitMap)) and entity.is_external:
        return reference

    if isinstance(entity, bcf.v3.model.DocumentReference):
        # Extract document reference filename and contents.
        if not bcfxml:
            raise TypeError("bcfxml is required for BCF v3 document references.")
        assert isinstance(bcfxml, bcf.v3.bcfxml.BcfXml)
        error_msg = f"BCF XML is missing document with guid '{reference}'."
        if not bcfxml.documents:
            raise Exception(error_msg)
        definition_docs = bcfxml.documents.definition.documents
        if not definition_docs:
            raise Exception(error_msg)
        docs = next((doc for doc in definition_docs.document if doc.guid == reference), None)
        if not docs:
            raise Exception(error_msg)
        filename = docs.filename
        bytes_data = bcfxml.documents.documents[filename]
    else:
        if isinstance(entity, mdl.BimSnippet):
            bytes_data = topic.bim_snippet
            assert isinstance(bytes_data, bytes)
        elif isinstance(entity, mdl.HeaderFile):
            bytes_data = topic.reference_files[reference]
        elif isinstance(entity, mdl.BitMap):
            bytes_data = next(
                byte_data
                for vp in topic.viewpoints.values()
                for data_reference, byte_data in vp.bitmaps.items()
                if data_reference == reference
            )
        elif isinstance(entity, bcf.v2.model.TopicDocumentReference):
            assert isinstance(topic, bcf.v2.topic.TopicHandler)
            bytes_data = topic.document_references[reference]
        else:
            assert_never(entity)

        # We don't really need it if 'outfile' is None, just keeping type checker happy.
        if isinstance(entity, mdl.HeaderFile) and entity.filename:
            filename = entity.filename
        else:
            filename = Path(reference).name

    if not outfile:
        outfile = Path(tempfile.mkdtemp()) / filename

    with open(outfile, "wb") as f:
        f.write(bytes_data)

    return outfile
