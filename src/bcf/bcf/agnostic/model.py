import bcf.v2.model
import bcf.v3.model
from typing import Union

BimSnippet = Union[bcf.v2.model.BimSnippet, bcf.v3.model.BimSnippet]
BitMap = Union[bcf.v2.model.VisualizationInfoBitmap, bcf.v3.model.Bitmap]
DocumentReference = Union[bcf.v2.model.TopicDocumentReference, bcf.v3.model.DocumentReference]
HeaderFile = Union[bcf.v2.model.HeaderFile, bcf.v3.model.File]
Topic = Union[bcf.v2.model.Topic, bcf.v3.model.Topic]
ViewPoint = Union[bcf.v2.model.ViewPoint, bcf.v3.model.ViewPoint]
