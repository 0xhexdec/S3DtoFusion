from __future__ import annotations

from typing import List

import adsk
import adsk.core
import adsk.fusion
from adsk.core import Point3D

from ...s3dModel.types.bezier3d import Bezier3D
from ..converterSettings import ConverterSettings
from .utils import BezierPlane

# takes a sketch, bezier3d (the bezier3d must be a 2d bezier, all points on a plane) and a settings object
# creates the needed splines to represent the bezier


def bezier2dToSketch(sketch: adsk.fusion.Sketch, bezier: Bezier3D, bezierPlane: BezierPlane, settings: ConverterSettings):

    for i in range(bezier.controlPoints.numberOfPoints-1):
        startPoint = bezier.controlPoints.points[i]
        endPoint = bezier.controlPoints.points[i+1]
        t1 = bezier.tangents1.points[i+1]
        t2 = bezier.tangents2.points[i]
        points: List[Point3D] = []

        if bezierPlane == BezierPlane.XY:
            if settings.zUp:
                points.append(Point3D.create(startPoint.x, startPoint.y, 0))
                points.append(Point3D.create(t2.x, t2.y, 0))
                points.append(Point3D.create(t1.x, t1.y, 0))
                points.append(Point3D.create(endPoint.x, endPoint.y, 0))
            else:
                points.append(Point3D.create(startPoint.x, startPoint.y, 0))
                points.append(Point3D.create(t2.x, t2.y, 0))
                points.append(Point3D.create(t1.x, t1.y, 0))
                points.append(Point3D.create(endPoint.x, endPoint.y, 0))

        elif bezierPlane == BezierPlane.XZ:
            if settings.zUp:
                points.append(Point3D.create(startPoint.x, -startPoint.z, 0))
                points.append(Point3D.create(t2.x, -t2.z, 0))
                points.append(Point3D.create(t1.x, -t1.z, 0))
                points.append(Point3D.create(endPoint.x, -endPoint.z, 0))
            else:
                points.append(Point3D.create(startPoint.x, startPoint.z, 0))
                points.append(Point3D.create(t2.x, t2.z, 0))
                points.append(Point3D.create(t1.x, t1.z, 0))
                points.append(Point3D.create(endPoint.x, endPoint.z, 0))

        else:
            if settings.zUp:
                points.append(Point3D.create(-startPoint.z, -startPoint.y, 0))
                points.append(Point3D.create(-t2.z, -t2.y, 0))
                points.append(Point3D.create(-t1.z, -t1.y, 0))
                points.append(Point3D.create(-endPoint.z, -endPoint.y, 0))
            else:
                points.append(Point3D.create(-startPoint.y, startPoint.z, 0))
                points.append(Point3D.create(-t2.y, t2.z, 0))
                points.append(Point3D.create(-t1.y, t1.z, 0))
                points.append(Point3D.create(-endPoint.y, endPoint.z, 0))

        sketch.sketchCurves.sketchControlPointSplines.add(points, adsk.fusion.SplineDegrees.SplineDegreeThree)  # type: ignore

    adsk.doEvents()
