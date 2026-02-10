from typing import Union

import bcf.v2.visinfo
import bcf.v3.visinfo

VisualizationInfoHandler = Union[bcf.v2.visinfo.VisualizationInfoHandler, bcf.v3.visinfo.VisualizationInfoHandler]
