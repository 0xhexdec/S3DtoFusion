from typing import List, Union

import adsk.core
import adsk.fusion
import numpy


def distance(a: adsk.core.Point3D, b: Union[adsk.fusion.SketchLine, List[adsk.core.Point3D]]) -> float:
    if isinstance(a, adsk.core.Point3D) and isinstance(b, adsk.fusion.SketchLine):
        bStartPoint = b.startSketchPoint.geometry
        bEndPoint = b.endSketchPoint.geometry
        p = numpy.array([bStartPoint.x, bStartPoint.y, bStartPoint.z])
        q = numpy.array([bEndPoint.x, bEndPoint.y, bEndPoint.z])
        r = numpy.array([a.x, a.y, a.z])

        x = p-q
        t = numpy.dot(r-q, x)/numpy.dot(x, x)

        return numpy.linalg.norm(t*(p-q)+q-r)
    elif isinstance(a, adsk.core.Point3D) and isinstance(b, list):
        bStartPoint = b[0]
        bEndPoint = b[1]
        p = numpy.array([bStartPoint.x, bStartPoint.y, bStartPoint.z])
        q = numpy.array([bEndPoint.x, bEndPoint.y, bEndPoint.z])
        r = numpy.array([a.x, a.y, a.z])

        x = p-q
        t = numpy.dot(r-q, x)/numpy.dot(x, x)

        return numpy.linalg.norm(t*(p-q)+q-r)
    else:
        return 0
        