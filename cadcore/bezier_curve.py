from geomdl import BSpline
from geomdl import utilities
import math
from typing import List, Optional
import sys
import traceback

DEG_TO_RAD = math.pi / 180

class BezierCurve():
    MIN: int = 0
    MAX: int = 1
    X: int = 0
    Y: int = 1
    MIN_MAX_TOLERANCE: float = 0.0001
    MIN_MAX_SPLITS: int = 96
    POS_TOLERANCE: float = 0.003
    POS_MAX_ITERATIONS: int = 30
    ZERO: float = 0.0000000001
    ONE: float = 0.9999999999
    LENGTH_TOLERANCE: float = 0.001
    ANGLE_TOLERANCE: float = 0.05 * DEG_TO_RAD
    ANGLE_MAX_ITERATIONS: int = 50
    BEZIER_KNOT_VECTOR = utilities.generate_knot_vector(3, 4)

    def __init__(self, ctrl_pts: List[List[float]]):
        self.curve: BSpline.Curve = BSpline.Curve()
        self.curve.degree = 3
        self.curve.ctrlpts = ctrl_pts
        self.curve.knotvector = BezierCurve.BEZIER_KNOT_VECTOR

        self.coeff0: float = 0.0
        self.coeff1: float = 0.0
        self.coeff2: float = 0.0
        self.coeff3: float = 0.0
        self.coeff4: float = 0.0
        self.coeff5: float = 0.0
        self.coeff6: float = 0.0
        self.coeff7: float = 0.0
        self.coeff_dirty: bool = True
        self.length = 0.0
        self.length_dirty: bool = True

    @property
    def ctrlpts(self):
        return self.curve.ctrlpts

    @ctrlpts.setter
    def ctrlpts(self, value: List[float]):
        self.curve.ctrlpts = value
        self.coeff_dirty = True
        self.length_dirty = True

    def calculate_coeff(self):
        if not self.coeff_dirty:
            return
        
        # MORE ON CUBIC SPLINE MATH
		# =========================
		# by Don Lancaster

		# In graph space, the cubic spline is defined by eight points. A pair
		# of
		# initial points x0 and y0. A pair of end points x3 and y3. A pair of
		# first influence points x1 and y1. And a pair of second influence
		# points
		# x2 and y2.

		# A cubic spline consists of two parametric equations in t (or time)
		# space...

		# x = At^3 + Bt^2 + Ct + D
		# y = Dt^3 + Et^2 + Ft + G

		# Cubing can be a real pain, so the above equations can be rewritten in
		# a
		# "cubeless" form that calculates quickly...

		# x = ((At + B)t + C)t + D
		# y = ((Dt + E)t + F)t + G
		
		## double A = p3.x - (3*t2.x) + (3*t1.x) - p0.x; //A = x3 - 3x2 + 3x1 -
		## x0 double B = (3*t2.x) - (6*t1.x) + (3*p0.x); //B = 3x2 - 6x1 + 3x0
		## double C = (3*t1.x) - (3*p0.x); //C = 3x1 - 3x0 double D = p0.x; //D
		## = x0
		## 
		## double E = p3.y - (3*t2.y) + (3*t1.y) - p0.y; //E = y3 - 3y2 + 3y1 -
		## y0 double F = (3*t2.y) - (6*t1.y) + (3*p0.y); //F = 3y2 - 6y1 + 3y0
		## double G = (3*t1.y) - (3*p0.y); //G = 3y1 - 3y0 double H = p0.y; //H
		## = y0
		## 
		## coeff0 = A; coeff1 = B; coeff2 = C; coeff3 = D; coeff4 = E; coeff5 =
		## F; coeff6 = G; coeff7 = H;
		
        p0 = self.ctrlpts[0]
        t1 = self.ctrlpts[1]
        t2 = self.ctrlpts[2]
        p3 = self.ctrlpts[3]

        self.coeff0 = p3[0] + (3 * (-t2[0] + t1[0])) - p0[0] # A = x3 - 3x2 + 3x1 - x0
        self.coeff1 = 3 * (t2[0] - (2 * t1[0]) + p0[0]) # B = 3x2 - 6x1 + 3x0
        self.coeff2 = 3 * (t1[0] - p0[0]) # C = 3x1 - 3x0
        self.coeff3 = p0[0] # D = x0

        self.coeff4 = p3[1] + (3 * (-t2[1] + t1[1])) - p0[1] # E = y3 - 3y2 + 3y1 - y0
        self.coeff5 = 3 * (t2[1] - (2 * t1[1]) + p0[1]) # F = 3y2 - 6y1 + 3y0
        self.coeff6 = 3 * (t1[1] - p0[1]) # G = 3y1 - 3y0
        self.coeff7 = p0[1] # H = y0

        self.mCoeffDirty = False

    def get_x_value(self, t: float):
        self.calculate_coeff()

        # compareCoeff();
        # A cubic spline consists of two parametric equations in t (or time)
        # space...

        # x = At^3 + Bt^2 + Ct + D
        # y = Dt^3 + Et^2 + Ft + G

        # Cubing can be a real pain, so the above equations can be rewritten in
        # a
        # "cubeless" form that calculates quickly...

        # x = ((At + B)t + C)t + D
        value = (((((self.coeff0 * t) + self.coeff1) * t) + self.coeff2) * t) + self.coeff3

        # compareCoeff();

        return value
    
    def get_y_value(self, t: float):
        self.calculate_coeff()

        # compareCoeff();
        # A cubic spline consists of two parametric equations in t (or time)
        # space...

        # x = At^3 + Bt^2 + Ct + D
        # y = Dt^3 + Et^2 + Ft + G

        # Cubing can be a real pain, so the above equations can be rewritten in
        # a
        # "cubeless" form that calculates quickly...

        # y = ((Dt + E)t + F)t + G
        value = (((((self.coeff4 * t) + self.coeff5) * t) + self.coeff6) * t) + self.coeff7

        # compareCoeff();
        return value

    def get_length(self):
        if self.length_dirty:
            self.length = self._get_length(BezierCurve.ZERO, BezierCurve.ONE)
            self.length_dirty = False
        return self.length
            
    def _get_length(self, t0: float, t1: float):
        self.calculate_coeff()

        # Get endpoints
        x0 = self.get_x_value(t0)
        y0 = self.get_y_value(t0)
        x1 = self.get_x_value(t1)
        y1 = self.get_y_value(t1)

        # Get t split point
        ts = (t1 - t0) / 2 + t0
        sx = self.get_x_value(ts)
        sy = self.get_y_value(ts)

        # Distance between centerpoint and real split curvepoint
        length = math.sqrt((x0-sx)**2+(y0-sy)**2) + math.sqrt((sx-x1)**2+(sy-y1)**2)
        chord = math.sqrt((x0-x1)**2+(y0-y1)**2)

        if length - chord > BezierCurve.LENGTH_TOLERANCE and t1 - t0 > 0.001:
            return self._get_length(t0, ts) + self._get_length(ts, t1)
        else:
            return length

    def get_min_max_numerical(self, x_or_y: int, min_or_max: int, t0: float = 0, t1: float = 1,
                              nr_of_splits: Optional[int] = None):
        if nr_of_splits is None:
            nr_of_splits = BezierCurve.MIN_MAX_SPLITS

        self.calculate_coeff()

        best_t = 0
        best_value = -10000000 if min_or_max == BezierCurve.MAX else 10000000

        seg = ((t1 - t0) / nr_of_splits)
        for i in range(nr_of_splits):
            current_t = seg * i + t0
            if current_t < 0 or current_t > 1:
                continue

            current_value = self.get_x_value(current_t) if x_or_y == BezierCurve.X else self.get_y_value(current_t)

            if min_or_max == BezierCurve.MAX:
                if current_value >= best_value:
                    best_value = current_value
                    best_t = current_t
            else:
                if current_value <= best_value:
                    best_value = current_value
                    best_t = current_t

        if (best_t - ((t1 - t0) / 2)) < BezierCurve.MIN_MAX_TOLERANCE:
            return best_value
        elif nr_of_splits <= 2:
            return best_value
        else:
            return self.get_min_max_numerical(x_or_y, min_or_max, t0=best_t - seg, t1=best_t + seg, nr_of_splits=int(nr_of_splits / 2))

    def get_min_x(self):
        return self.get_min_max_numerical(BezierCurve.X, BezierCurve.MIN)

    def get_min_y(self):
        return self.get_min_max_numerical(BezierCurve.Y, BezierCurve.MIN)

    def get_max_x(self):
        return self.get_min_max_numerical(BezierCurve.X, BezierCurve.MAX)

    def get_max_y(self):
        return self.get_min_max_numerical(BezierCurve.Y, BezierCurve.MAX)

    def get_t_for_x_internal(self, x: float, start_t: float):
        # I don't know how to find an exact and closed solution to finding y
        # given
        # x. You first have to use x to solve for t and then you solve t for y.

        # One useful way to do this is to take a guess for a t value. See what
        # x you get. Note the error. Reduce the error and try again. Keep this up
        # till you have a root to acceptable accuracy.
        #
        # A good first guess is to normalize x so it ranges from 0 to 1 and
        # then simply guess that x = t. This will be fairly close for curves that
        # aren't bent very much. And a useful guess for ALL spline curves.

        # Guess initial t
        tn = start_t

        # Now, on any triangle...
        #
        # rise = run x (rise/run)
        #
        # This gives us a very good improvement for our next approximation. It
        # turns out that the "adjust for slope" method converges very rapidly.
        # Three passes are usually good enough.
        #
        # If our curve has an equation of...
        #
        # x = At^3 + Bt^2 + Ct + D
        #
        # ...its slope will be...
        #
        # x' = 3At^2 +2Bt + C
        #
        # And the dt/dx slope will be its inverse or 1/(3At^2 + 2Bt +C)
        # This is easily calculated. 
        #
        # The next guess will be
        # nextguess = currentt + (curentx - x)(currentslope)
        xn = self.get_x_value(tn)

        error = x - xn
        # double lasterror = error;

        for n in range(BezierCurve.POS_MAX_ITERATIONS):
            if abs(error) <= BezierCurve.POS_TOLERANCE:
                break

            currentSlope = 1 / self.get_x_derivative(tn)

            tn = tn + error * currentSlope

            xn = self.get_x_value(tn)

            error = x - xn

        # Sanity check
        if tn < 0 or tn > 1 or math.isnan(tn) or n >= BezierCurve.POS_MAX_ITERATIONS or abs(error) > BezierCurve.POS_TOLERANCE:
            tn = self.get_t_for_x(x, 0, 1, BezierCurve.MIN_MAX_SPLITS)
            xn = self.get_x_value(tn)

        return tn

    def get_y_for_x(self, x: float):
        self.calculate_coeff()

        # I don't know how to find an exact and closed solution to finding y
        # given
        # x. You first have to use x to solve for t and then you solve t for y.

        # One useful way to do this is to take a guess for a t value. See what
        # x
        # you get. Note the error. Reduce the error and try again. Keep this up
        # till you have a root to acceptable accuracy.
        #
        # A good first guess is to normalize x so it ranges from 0 to 1 and
        # then
        # simply guess that x = t. This will be fairly close for curves that
        # aren't
        # bent very much. And a useful guess for ALL spline curves.

        # Guess initial t
        t = (x - self.ctrlpts[0][0]) / (self.ctrlpts[-1][0] - self.ctrlpts[0][0])

        t = self.get_t_for_x_internal(x, t)

        return self.get_y_value(t)

    def get_t_for_length(self, length_left: float, t0: Optional[float] = None, t1: Optional[float] = None):
        if t0 is None:
            t0 = BezierCurve.ZERO
        if t1 is None:
            t1 = BezierCurve.ONE

        self.calculate_coeff()

        # Get t split point
        ts = (t1 - t0) / 2 + t0
        sl = self._get_length(t0, ts)

        try:
            if abs(t0 - t1) < 0.00001:
                return t0
            if abs(sl - length_left) > BezierCurve.LENGTH_TOLERANCE:
                if sl > length_left:
                    return self.get_t_for_length(length_left, t0=t0, t1=ts)
                else:
                    return self.get_t_for_length(length_left - sl, t0=ts, t1=t1)
            else:
                return ts
        except Exception:
            print("Exception in BezierSpline::get_t_for_length():")
            traceback.print_exc(file=sys.stdout)
            return 0.0
        
    def get_x_derivative(self, t: float):
        # compareCoeff();
        # If our curve has an equation of...
        #
        # x = At^3 + Bt^2 + Ct + D
        #
        # ...its slope will be...
        #
        # x' = 3At^2 + 2Bt + C
        # x' = (3At + 2B)t + C
        value = ((((3 * self.coeff0) * t) + (2 * self.coeff1)) * t) + self.coeff2
        # compareCoeff();
        return value
    
    def get_y_derivative(self, t: float):
        # If our curve has an equation of...
        #
        # y = At^3 + Bt^2 + Ct + D
        #
        # ...its slope will be...
        #
        # y' = 3Et^2 +2Ft + G
        # y' = (3Et + 2F)t + G
        value = ((((3 * self.coeff4) * t) + (2 * self.coeff5)) * t) + self.coeff6
        return value
        
    def get_tangent(self, t: float):
        self.calculate_coeff()

        dx = self.get_x_derivative(t)
        dy = self.get_y_derivative(t)

        angle = math.atan2(dx, dy)
        return angle
    
    def get_t_for_tangent2(self, target_angle: float, current_t: float, last_t: float):
        # Search for the angle using secant method
        current_angle = self.get_tangent(current_t)
        last_angle = self.get_tangent(last_t)

        current_error = target_angle - current_angle

        # System.out.printf("getTForTangent2(): target_angle:%f, current_t:%f, last_t:%f\n",
        # target_angle/BezierBoard.DEG_TO_RAD, current_t, last_t);

        n = 0
        while (abs(current_error) > BezierCurve.ANGLE_TOLERANCE
                and n < BezierCurve.ANGLE_MAX_ITERATIONS
                and current_t > BezierCurve.ZERO
                and current_t < BezierCurve.ONE):
            n += 1
            current_slope = (current_angle - last_angle) / (current_t - last_t)

            last_t = current_t
            current_t = current_t + (current_error * current_slope)

            last_angle = current_angle
            current_angle = self.get_tangent(current_t)

            current_error = target_angle - current_angle

            # System.out.printf("getTForTangent2(): current_slope:%f, current_error:%f, current_t:%f last_angle:%f current_angle:%f target_angle:%f\n",
            # current_slope, current_error/BezierBoard.DEG_TO_RAD, current_t,
            # last_angle/BezierBoard.DEG_TO_RAD,
            # current_angle/BezierBoard.DEG_TO_RAD,
            # target_angle/BezierBoard.DEG_TO_RAD);

        # Sanity check
        if (abs(self.get_tangent(current_t) - target_angle) > BezierCurve.ANGLE_TOLERANCE or
           (current_t < BezierCurve.ZERO or current_t > BezierCurve.ONE)):
            # System.out.printf("getTForTangent(): converge failed, error: %f\n",
            # current_error/BezierBoard.DEG_TO_RAD);

            n = 0
            lt = 0.0
            ht = 1.0
            while (abs(current_error) > BezierCurve.ANGLE_TOLERANCE and
                   n < BezierCurve.ANGLE_MAX_ITERATIONS and
                   ht - lt > 0.00001):
                n += 1
                current_t = lt + ((ht - lt) / 2.0)

                current_angle = self.get_tangent(current_t)
                current_error = target_angle - current_angle

                if current_error < 0.0:
                    lt = current_t
                else:
                    ht = current_t

                # print("getTForTangent2(): current_error:%f, current_t:%f lt:%f ht:%f current_angle:%f target_angle:%f \n",
                # current_error, current_t, lt, ht, current_angle,
                # target_angle)

        return current_t