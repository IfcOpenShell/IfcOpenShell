class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger

    def patch(self):
        # 12D can have some funky coordinates out of any sensible range. This
        # method will not work all the time, but will catch most issues.
        offset_point = None
        for point_list in self.file.by_type('IfcCartesianPointList3D'):
            coord_list = [None] * len(point_list.CoordList)
            for i, point in enumerate(point_list.CoordList):
                if len(point) == 2 or not self.is_point_far_away(point):
                    coord_list[i] = point
                    continue
                if not offset_point:
                    offset_point = (point[0], point[1], point[2])
                    self.logger.info(f'Resetting absolute coordinates by {point}')
                point = (
                    point[0] - offset_point[0],
                    point[1] - offset_point[1],
                    point[2] - offset_point[2]
                )
                coord_list[i] = point
            point_list.CoordList = coord_list
        for point in self.file.by_type('IfcCartesianPoint'):
            if len(point.Coordinates) == 2 or not self.is_point_far_away(point):
                continue
            if not offset_point:
                offset_point = (point.Coordinates[0], point.Coordinates[1], point.Coordinates[2])
                self.logger.info(f'Resetting absolute coordinates by {point}')
            point.Coordinates = (
                point.Coordinates[0] - offset_point[0],
                point.Coordinates[1] - offset_point[1],
                point.Coordinates[2] - offset_point[2]
            )

    def is_point_far_away(self, point):
        # Arbitrary threshold based on experience
        if hasattr(point, 'Coordinates'):
            return abs(point.Coordinates[0]) > 1000000 \
                or abs(point.Coordinates[1]) > 1000000 \
                or abs(point.Coordinates[2]) > 1000000
        return abs(point[0]) > 1000000 \
            or abs(point[1]) > 1000000 \
            or abs(point[2]) > 1000000
