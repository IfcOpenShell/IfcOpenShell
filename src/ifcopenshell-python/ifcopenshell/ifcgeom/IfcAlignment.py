import matplotlib.pyplot as plt
import numpy as np

import ifcopenshell
from ifcopenshell.alignment import PositioningElement
from ifcopenshell.alignment import print_structure

from .IfcAlignmentCant import AlignmentCant
from .IfcAlignmentHorizontal import AlignmentHorizontal
from .IfcAlignmentVertical import AlignmentVertical


class Alignment(PositioningElement):
    """
    IfcAlignment

    Ref: 5.4.3.1
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignment.htm
    """

    def __init__(self):
        super().__init__()
        self._horizontal = None
        self._vertical = None
        self._cant = None

    @property
    def PredefinedType(self):
        return self._elem.PredefinedType

    @property
    def horizontal(self) -> AlignmentHorizontal:
        return self._horizontal

    @property
    def vertical(self) -> AlignmentVertical:
        return self._vertical

    @property
    def cant(self) -> AlignmentCant:
        return self._cant

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem

        # extract horizontal, vertical, and cant if they exist
        for rel in self.IsNestedBy:
            for child in rel.RelatedObjects:
                if child.is_a("IfcAlignmentHorizontal"):
                    self._horizontal = AlignmentHorizontal().from_entity(child)
                elif child.is_a("IfcAlignmentVertical"):
                    self._vertical = AlignmentVertical().from_entity(child)
                elif child.is_a("IfcAlignmentCant"):
                    self._cant = AlignmentCant().from_entity(child)
        return self

    @property
    def length(self) -> float:
        """
        Total length of the alignment.
        """
        return self._horizontal.length

    def _calc_points(self, interval: float = 5.0):
        """
        Calculate all of the points on the alignment at a specific distance (interval)
        between points
        """
        x = list()
        y = list()
        z = list()
        directions = list()

        segs = self._horizontal.segments
        distances = np.arange(0, self.length, interval)
        for s in segs:
            distances = np.append(distances, s.end_distance)
        distances = np.sort(distances)

        idx = 0  # index of the segments
        for d in distances:
            if d > segs[idx].end_distance:
                idx += 1
            u = d - segs[idx].start_distance
            pt = segs[idx].calc_point(u)
            x.append(pt[0])
            y.append(pt[1])
            directions.append(segs[idx].calc_direction(u))

        if not self._vertical is None:
            z = self._vertical.calc_heights(distances)
        else:
            z = np.ones_like(distances)
            z.fill(np.nan)
        if not self._cant is None:
            clt = self._cant.calc_cant_amounts(distances)
        else:
            clt = np.ones_like(distances)
            clt.fill(np.nan)

        xar = np.array(x)
        yar = np.array(y)
        dar = np.array(directions)
        zar = np.array(z)
        cltar = np.array(clt)  # cant left
        ref_zar = zar + cltar

        self._points = np.column_stack((distances, xar, yar, dar, zar, cltar, ref_zar))

    def create_shape(
        self,
        settings: ifcopenshell.geom.settings = ifcopenshell.geom.settings(),
        use_representation: bool = True,
        point_interval: float = 5.0,
    ) -> np.ndarray:
        """
        There are two approaches to modeling IfcAlignment entities: business aspects and representation with
        IFC geometry resources.
        If a representation exists, it may be utilized.  Otherwise it will be calculated from the parameters
        of each individual segment.

        @param use_representation: Use the geometry from the IFC geometry entities, if it exists
        @param point_interval: The distance between points that will be calculated along the alignment.
        """
        if use_representation:
            try:
                if len(self.Representation) > 0:
                    return ifcopenshell.geom.create_shape(settings, self.wrapped_entity)
            except RuntimeError:
                msg = ifcopenshell.get_log()
                raise RuntimeError(msg)
            except TypeError:
                msg = (
                    f"{str(self.wrapped_entity)} does not have a representation shape."
                )
                raise LookupError(msg)
        else:
            self._calc_points(interval=point_interval)

            return self._points

    def print_structure(self, indent: int = 0):
        """
        Print alignment decomposition for debugging purposes.
        """
        print(" " * indent, str(self)[0:100])
        for rel in self.IsNestedBy:
            for child in rel.RelatedObjects:
                print_structure(child, indent + 2)

    def print_attributes(self):
        """
        Print all attributes of the IFC Entity for debugging puposes.
        """
        super().print_attributes()
        print("-----------------------------------------")
        print(f"{self.PredefinedType=}")

    def plot(self, fp: str = None, title: str = "", interactive: bool = False):
        """
        Plot the alignment and save as an image.

        @param fp: File-like structure for saving plot.
        @param title: Title to be placed at top of the plot.
        @param interactive: Set to `True` for an interactive plotting in jupyter notebooks
        """
        s = ifcopenshell.geom.settings()
        s.set(s.INCLUDE_CURVES, True)
        pts = self.create_shape(settings=s, use_representation=False)

        fig, axs = plt.subplots(3, 1)
        distances = pts[:, 0]
        x = pts[:, 1]
        y = pts[:, 2]
        elevations = pts[:, 4]
        cant = pts[:, 5]

        axs[0].plot(x, y, linewidth=1)
        axs[0].set_aspect("equal", "box")
        axs[1].plot(distances, elevations, linewidth=1)
        axs[2].plot(distances, cant, linewidth=1)

        axs[0].set_ylabel("Northing")
        axs[0].set_xlabel("Easting")
        axs[1].set_xlabel("Horizontal Distance")
        axs[2].set_xlabel("Horizontal Distance")
        axs[1].set_ylabel("Vertical Height")
        axs[2].set_ylabel("Cant")
        for ax in axs:
            ax.grid(True)
            ax.ticklabel_format(useOffset=False, style="plain")
        fig.tight_layout()
        plt.suptitle(title)
        if interactive:
            plt.show()
        else:
            plt.savefig(fp)
