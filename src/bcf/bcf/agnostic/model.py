import bcf.v2.model
import bcf.v3.model
from typing import Union

BimSnippet = Union[bcf.v2.model.BimSnippet, bcf.v3.model.BimSnippet]
DocumentReference = Union[bcf.v2.model.TopicDocumentReference, bcf.v3.model.DocumentReference]
HeaderFile = Union[bcf.v2.model.HeaderFile, bcf.v3.model.File]
