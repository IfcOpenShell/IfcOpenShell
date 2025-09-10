import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.util.element
import ifcpatch
from logging import Logger

import typing
from typing import Union


class Patcher(ifcpatch.BasePatcher):
    def __init__(self, file: ifcopenshell.file, logger: Union[Logger, None] = None):
        """Adds a zero length segments to alignment layouts

        Example:

        .. code:: python

            model = ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "PatchStationReferentPosition"})
        """
        super().__init__(file, logger)
        self.file_patched: ifcopenshell.file

    def patch(self):
        patched_file = ifcopenshell.file.from_string(self.file.wrapped_data.to_string())

        alignments = patched_file.by_type("IfcAlignment")
        for alignment in alignments:
            basis_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)

            nests = alignment.IsNestedBy
            first_referent = nests[1].RelatedObjects[0]
            start_station = ifcopenshell.util.element.get_pset(first_referent, "Pset_Stationing", "Station")
            # start_station = first_referent.IsDefinedBy[0].RelatingPropertyDefinition.HasProperties[0].NominalValue.wrapped_data # get station from first_referent
            for referent in nests[1].RelatedObjects:
                if referent.ObjectPlacement == None:
                    # Need to get Station property from Pset_Stationing + Station property from the first referent... the DistanceAlong is the different in these values
                    station = ifcopenshell.util.element.get_pset(referent, "Pset_Stationing", "Station")
                    # station = referent.IsDefinedBy[0].RelatingPropertyDefinition.HasProperties[0].NominalValue.wrapped_data # get station from current referent
                    object_placement = patched_file.createIfcLinearPlacement(
                        RelativePlacement=patched_file.createIfcAxis2PlacementLinear(
                            Location=patched_file.createIfcPointByDistanceExpression(
                                DistanceAlong=patched_file.createIfcLengthMeasure(station - start_station),
                                OffsetLateral=None,
                                OffsetVertical=None,
                                OffsetLongitudinal=None,
                                BasisCurve=basis_curve,
                            )
                        ),
                    )

                    referent.ObjectPlacement = object_placement

        self.file_patched = patched_file
