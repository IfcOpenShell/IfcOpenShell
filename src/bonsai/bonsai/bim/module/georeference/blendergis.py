# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

"""Bridge to read georeferencing data written by the BlenderGIS addon.

BlenderGIS (https://github.com/domlysz/BlenderGIS) is a separate, optional
Blender addon. It is never imported here: its scene properties are simply
documented custom ID properties, read directly off bpy.context.scene, so
this bridge degrades to a no-op when BlenderGIS is absent or has not
georeferenced the scene.

The property keys and their semantics below are taken from BlenderGIS's own
geoscene.py (class GeoScene, alias SK) and core/proj/srs.py (class SRS), as
published on the BlenderGIS repository. A scene is only considered
georeferenced by BlenderGIS itself once both a CRS and the CRS coordinates
of the scene origin are set.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

CRS_KEY = "SRID"
EASTING_KEY = "crs x"
NORTHING_KEY = "crs y"
SCALE_KEY = "scale"
LONGITUDE_KEY = "longitude"
LATITUDE_KEY = "latitude"


class SceneProperties(Protocol):
    def get(self, key: str, default: object = None) -> object: ...


@dataclass
class BlenderGISGeoreference:
    crs_name: str
    eastings: float
    northings: float
    scale: float
    longitude: Optional[float] = None
    latitude: Optional[float] = None


def normalise_crs_name(raw_srid: str) -> str:
    """Turn a BlenderGIS SRID string into an IfcProjectedCRS Name.

    BlenderGIS's SRS class accepts a bare EPSG code, an "AUTH:CODE" string,
    or a proj4 string. The first two both identify a CRS by authority and
    code, which is also the format Bonsai/IFC use for a projected CRS name
    (e.g. "EPSG:7856"). A proj4-only definition has no such identifier and
    is passed through unchanged.
    """
    raw_srid = raw_srid.strip()
    if raw_srid.isdigit():
        return f"EPSG:{raw_srid}"
    if ":" in raw_srid and not raw_srid.startswith("+"):
        auth, _, code = raw_srid.partition(":")
        return f"{auth.upper()}:{code}"
    return raw_srid


def read_blendergis_scene(scene: SceneProperties) -> Optional[BlenderGISGeoreference]:
    """Read BlenderGIS's georeferencing properties off a Blender scene.

    Returns None if BlenderGIS never wrote its georeferencing keys onto
    this scene, or wrote them only partially, matching BlenderGIS's own
    notion of GeoScene.isGeoref.
    """
    crs = scene.get(CRS_KEY)
    eastings = scene.get(EASTING_KEY)
    northings = scene.get(NORTHING_KEY)
    if not crs or eastings is None or northings is None:
        return None
    scale = scene.get(SCALE_KEY, 1) or 1
    return BlenderGISGeoreference(
        crs_name=normalise_crs_name(str(crs)),
        eastings=float(eastings),
        northings=float(northings),
        scale=float(scale),
        longitude=scene.get(LONGITUDE_KEY),
        latitude=scene.get(LATITUDE_KEY),
    )


def compute_map_conversion(
    data: BlenderGISGeoreference, blender_offset: tuple[float, float, float] = (0.0, 0.0, 0.0)
) -> dict[str, float]:
    """Compute IfcMapConversion attributes that reproduce BlenderGIS's georeferencing.

    BlenderGIS keeps its scene X/Y axes aligned with the CRS easting/northing
    axes, it never stores a grid north rotation, so the imported map
    conversion is always unrotated (XAxisAbscissa=1, XAxisOrdinate=0). Any
    existing grid north rotation in the IFC file is overwritten. True north
    is a separate, independent Bonsai setting and is left untouched.

    blender_offset is Bonsai's own "Blender session offset", the local
    engineering coordinates of Blender's (0, 0, 0) (see tool.Georeference).
    It is (0, 0, 0) when there is no such offset, in which case Eastings and
    Northings become BlenderGIS's crs x/crs y unchanged.
    """
    offset_x, offset_y, offset_z = blender_offset
    scale = data.scale
    return {
        "Eastings": data.eastings - scale * offset_x,
        "Northings": data.northings - scale * offset_y,
        "OrthogonalHeight": -scale * offset_z,
        "XAxisAbscissa": 1.0,
        "XAxisOrdinate": 0.0,
        "Scale": scale,
    }
