from typing import List
import math

from cadcore.bezier_curve import BezierCurve

class BezierSlice():
    def __init__(self, bezier_curves: List[BezierCurve], position: float):
        self.curves: List[BezierCurve] = bezier_curves
        self.position: float = position

    def get_center_thickness(self):
        deck_center = self.curves[-1].ctrlpts[-1][1]
        bottom_center = self.curves[0].ctrlpts[0][1]
        return deck_center - bottom_center

    def get_width(self):
        max_x = max([crv.get_max_x() for crv in self.curves])
        return 2 * max_x

    def get_length(self):
        return sum([crv.get_length() for crv in self.curves])

    def find_matching_bezier_curve(self, pos: float):
        result = self.find_matching_bezier_curve_simple(pos)
        if result is None: 
            result = self.find_matching_bezier_curve_min_max(pos)
        return result

    def find_matching_bezier_curve_simple(self, pos: float):
        for crv in self.curves:
            lx = crv.ctrlpts[0][0]
            ux = crv.ctrlpts[-1][0]
            if lx <= pos <= ux:
                return crv

    def find_matching_bezier_curve_min_max(self, pos: float):
        # Didn't find any matching segment

		# Iterate through all segments and see if we're within max/min x value
        for crv in self.curves:
            lx = crv.get_min_x()
            ux = crv.get_max_x()
            if lx <= pos <= ux:
                return crv

    def get_value_at(self, pos: float):
        crv = self.find_matching_bezier_curve(pos)

        if crv is None:
            return 0.0
        return crv.get_y_for_x(pos)

    def get_point_by_curve_length(self, curve_length: float):
        l = curve_length
        t = -1

        # Return endpoints if input curvelength is out of range
        if curve_length <= 0.0:
            curve = self.curves[0]

            return (curve.get_x_value(BezierCurve.ZERO), curve.get_y_value(BezierCurve.ZERO))
        if curve_length >= self.get_length():
            curve = self.curves[-1]

            return (curve.get_x_value(BezierCurve.ZERO), curve.get_y_value(BezierCurve.ZERO))

        for curve in self.curves:
            current_length = curve.get_length()

            if l < current_length:
                t = curve.get_t_for_length(l)
                break

            l -= current_length

        x = curve.get_x_value(t)
        y = curve.get_y_value(t)

        return (x, y)

    def get_point_at_s(self, s: float):
        return self.get_point_by_curve_length(s * self.get_length())
    
    def get_s_by_normal_reverse(self, angle: float, use_minimum_angle_on_sharp_corners: bool = True):
        return self.get_s_by_tangent_reverse(
            angle - math.pi / 2,
            use_minimum_angle_on_sharp_corners=use_minimum_angle_on_sharp_corners
        )
    
    def get_s_by_tangent_reverse(self, angle: float, use_minimum_angle_on_sharp_corners: bool = True):
        s = self.get_length_by_tangent_reverse(
            angle,
            use_minimum_angle_on_sharp_corners=use_minimum_angle_on_sharp_corners
        ) / self.get_length()
        s = min(max(s, BezierCurve.MIN), BezierCurve.MAX)
        return s
    
    def get_length_by_control_point_index(self, start_index: int, end_index: int):
        return sum([self.curves[i].get_length() for i in range(start_index, end_index)])
    
    def get_tangent_by_curve_length(self, curve_length: float):
        l = curve_length
        t = -1

        for curve in self.curves:
            current_length = curve.get_length()

            if l < current_length:
                t = curve.get_t_for_length(l)
                break

            l -= current_length

        return curve.get_tangent(t)
    
    def get_length_by_tangent_reverse(self, target_angle: float, use_minimum_angle_on_sharp_corners: bool = True):
        length = 0
        t = 0

        min_angle_error = 10000
        min_error_t = -1
        min_angle_error_section = -1

        target_found = False

        for i in reversed(range(len(self.curves))):
            curve = self.curves[i]
            start_angle = curve.get_tangent(BezierCurve.ZERO)
            end_angle = curve.get_tangent(BezierCurve.ONE)
            # System.out.printf("getLengthByTangentReverseScaled() StartAngle:%f EndAngle:%f TargetAngle:%f\n",
            # startAngle/BezierBoard.DEG_TO_RAD +90.0,
            # endAngle/BezierBoard.DEG_TO_RAD + 90.0,
            # targetAngle/BezierBoard.DEG_TO_RAD +90.0);
            # if (startAngle >= targetAngle && endAngle <= targetAngle) {
            #     # System.out.printf("getLengthByTangentReverseScaled() Value should be in this span, StartAngle:%f EndAngle:%f TargetAngle:%f\n",
            #     # startAngle/BezierBoard.DEG_TO_RAD +90.0,
            #     # endAngle/BezierBoard.DEG_TO_RAD + 90.0,
            #     # targetAngle/BezierBoard.DEG_TO_RAD +90.0);
            # }

            # if(k1.mContinous == false)
            # {
            if end_angle > target_angle:
                # System.out.printf("getLengthByTangentReverseScaled() i:%d, endAngle > targetAngle endAngle:%f targetAngle:%f\n",i,
                # endAngle/BezierBoard.DEG_TO_RAD,
                # targetAngle/BezierBoard.DEG_TO_RAD);
                if use_minimum_angle_on_sharp_corners:
                    i += 1
                    # System.out.printf("getLengthByTangentReverseScaled() Target found by endAngle(%f) > targetAngle(%f) with use minimun angle on shape corner\n",
                    # endAngle/BezierBoard.DEG_TO_RAD+90.0,
                    # targetAngle/BezierBoard.DEG_TO_RAD+90.0);
                else:
                    length = curve.get_length(BezierCurve.ZERO, BezierCurve.ONE - .05)
                    # System.out.printf("getLengthByTangentReverseScaled() Target found by endAngle(%f) > targetAngle(%f)\n",
                    # endAngle/BezierBoard.DEG_TO_RAD+90.0,
                    # targetAngle/BezierBoard.DEG_TO_RAD+90.0);

                target_found = True
                break
            
            # }

            # t = getTForTangent(angle,ZERO,ONE, ANGLE_SPLITS);
            initial_t = (target_angle - start_angle) / (end_angle - start_angle)
            if initial_t < 0.0:
                initial_t = 0.0
            if initial_t > 1.0:
                initial_t = 1.0
            last_t = initial_t + 0.1
            if last_t > 1.0:
                last_t -= 0.2

            # System.out.printf("getLengthByTangentReverseScaled() i:%d startAngle:%f end_angle:%f initial_t:%f last_t:%f\n",i,
            # startAngle/BezierBoard.DEG_TO_RAD,
            # endAngle/BezierBoard.DEG_TO_RAD, initial_t, last_t);

            t = curve.get_t_for_tangent2(target_angle, initial_t, last_t)

            t_angle = curve.get_tangent(t)
            angle_error = abs(t_angle - target_angle)
            if min_angle_error > angle_error:
                min_angle_error = angle_error
                min_error_t = t
                min_angle_error_section = i
            
            if angle_error <= BezierCurve.ANGLE_TOLERANCE:
                length = curve._get_length(BezierCurve.ZERO, t)
                target_found = True
                # print("getLengthByTangentReverseScaled() Target found by matching angle: %f, error: %f, length: %f\n" % 
                # (t_angle/DEG_TO_RAD+90.0,
                # angle_error/DEG_TO_RAD,
                # length))
                break
            elif start_angle >= target_angle and end_angle <= target_angle:
                # System.out.printf("getLengthByTangentReverseScaled() Value should be in this span but error is too large, StartAngle:%f EndAngle:%f Target: %f Returned: %f t:%f\n",
                # startAngle/BezierBoard.DEG_TO_RAD +90.0,
                # endAngle/BezierBoard.DEG_TO_RAD +90.0,
                # targetAngle/BezierBoard.DEG_TO_RAD +90.0,
                # tAngle/BezierBoard.DEG_TO_RAD+90.0, t);
                t = curve.get_t_for_tangent2(target_angle, initial_t, last_t)

        if not target_found and min_angle_error_section != -1:
            # Use the nearest target
            curve = self.curves[min_angle_error_section]

            length = curve.get_length(BezierCurve.ZERO, min_error_t)

        length += self.get_length_by_control_point_index(0, i)

        # DEBUG sanity check
        tangent = self.get_tangent_by_curve_length(length)
        if abs(tangent - target_angle) > 0.5 and target_found:
            # System.out.printf("getLengthByTangentReverseScaled()  getTangentByCurveLength() returned different angle. Target: %f Returned: %f  length:%f curveLength:%f\n",
            # targetAngle/BezierBoard.DEG_TO_RAD +90.0,
            # tangent/BezierBoard.DEG_TO_RAD + 90.0, length,
            # lengthScaled(scaleX, scaleY));
            target_found = not target_found

        return length

    def scale(self, new_thickness: float, new_width: float):
        old_width = self.get_width()
        old_thickness = self.get_center_thickness()

        if old_width < 0.1:
            old_width = 0.1

        if old_thickness < 0.1:
            old_thickness = 0.1

        new_thickness_scale = abs(new_thickness / old_thickness)
        new_width_scale = abs(new_width / old_width)

        if (old_thickness * new_thickness_scale) <= 0.1:
            return

        if (old_width * new_width_scale) <= 0.1:
            return

        scale_y = new_thickness_scale
        scale_x = new_width_scale
        scaled_curves = [BezierCurve([[cp[0]*scale_x, cp[1]*scale_y] for cp in crv.ctrlpts]) for crv in self.curves]
        result = BezierSlice(scaled_curves, self.position)
        return result

    def interpolate(self, target: "BezierSlice", t: float):
        # Scale to same width and thickness
        interpolation_target_sandbox_copy = target.scale(self.get_center_thickness(), self.get_width())

        # TODO: Handle when number of control points doesn't match
        if len(self.curves) != len(target.curves):
            raise AttributeError("Number of control points differ - not supported")

        interpolated_bezier_curves = [] 
        for crv_a, crv_b in zip(self.curves, interpolation_target_sandbox_copy.curves):
            interpolated_curve_ctrl_pts = []
            for a_xy, b_xy in zip(crv_a.ctrlpts, crv_b.ctrlpts):
                v_x = (b_xy[0] - a_xy[0]) * t + a_xy[0]
                v_y = (b_xy[1] - a_xy[1]) * t + a_xy[1]
                interpolated_curve_ctrl_pts.append([v_x, v_y])
            interpolated_bezier_curves.append(BezierCurve(interpolated_curve_ctrl_pts))

        return BezierSlice(interpolated_bezier_curves, self.position)
