from typing import List

import adsk.core
import adsk.fusion


def sketchPointToPoint3D(sketchPoint: adsk.fusion.SketchPoint) -> adsk.core.Point3D:
    return adsk.core.Point3D.create(sketchPoint.geometry.x, sketchPoint.geometry.y, sketchPoint.geometry.z)

def sketchPointListToPoint3DList(sketchPointList: List[adsk.fusion.SketchPoint]) -> List[adsk.core.Point3D]:
    pointList: List[adsk.core.Point3D] = []
    for sketchPoint in sketchPointList:
        pointList.append(sketchPointToPoint3D(sketchPoint))
    return pointList
