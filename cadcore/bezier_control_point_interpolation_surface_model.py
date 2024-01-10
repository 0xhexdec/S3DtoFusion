# from cadcore.bezier_curve import BezierCurve
from cadcore.bezier_board import BezierBoard

class BezierControlPointInterpolationSurfaceModel():

    def get_point_at(self, board: BezierBoard, x: float, s: float):
        interpolated_slice = board.get_interpolated_slice(x)

        if interpolated_slice is None:
            return (0.0, 0.0, 0.0)

        # min_s = BezierCurve.ONE
        # max_s = BezierCurve.ZERO

        # TODO: Handle min/max angle

        current_s = s #((max_s - min_s) * s) + min_s
        p_2d = interpolated_slice.get_point_at_s(current_s)

        return (x, p_2d[0], p_2d[1] + board.get_rocker_at_pos(x))