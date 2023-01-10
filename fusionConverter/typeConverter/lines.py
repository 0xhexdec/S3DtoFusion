from math import pi
from typing import List, Optional, Union

import adsk.core
import adsk.fusion

from ...s3dModel.types.point3d import Point3d
from ..converterSettings import ConverterSettings
from .utils import BezierPlane


def pointsToLine(sketch: adsk.fusion.Sketch, pointA: Point3d, pointB: Point3d, plane: BezierPlane, settings: ConverterSettings):
    sketch.sketchCurves.sketchLines.addByTwoPoints(_toADSKPoint(pointA, plane), _toADSKPoint(pointB, plane))

# def pointsToCurve(sketch: adsk.fusion.Sketch, pointA: Point3d, pointB: Point3d, cornerRadius: float, plane: BezierPlane):
#     centerPoint = 
#     sketch.sketchCurves.sketchArcs.addByCenterStartSweep()
#     pass

def _toADSKPoint(point: Point3d, plane: BezierPlane) -> adsk.core.Point3D:
    if plane == BezierPlane.XY:
        return adsk.core.Point3D.create(point.x, point.y, 0)
    elif plane == BezierPlane.XZ:
        return adsk.core.Point3D.create(point.x, -point.z, 0)
    else:
        return adsk.core.Point3D.create(-point.z, -point.y, 0)

def rectangle(sketch: adsk.fusion.Sketch, position: Point3d, length: float, width: float, cornerRadius: Optional[float] = None):
    pos: adsk.core.Point3D = _toADSKPoint(position, BezierPlane.XY)
    pointOne: adsk.core.Point3D = pos.copy()
    pointOne.y -= width/2

    pointTwo: adsk.core.Point3D = pointOne.copy()
    pointTwo.y += width
    pointTwo.x += length
    if cornerRadius is None or cornerRadius == 0:
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(pointOne, pointTwo)
    else:
        p1 = pointOne.copy()
        p1.y += cornerRadius
        p2 = pointOne.copy()
        p2.y += width - cornerRadius
        sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)

        p1 = pointTwo.copy()
        p1.x -= length - cornerRadius
        pCenter = adsk.core.Point3D.create(p1.x, p2.y, 0)
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(pCenter, p2, -pi/2)

        p2 = pointTwo.copy()
        p2.x -= cornerRadius
        sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)

        p1 = pointTwo.copy()
        p1.y -= cornerRadius
        pCenter = adsk.core.Point3D.create(p2.x, p1.y, 0)
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(pCenter, p2, -pi/2)

        p2 = pointTwo.copy()
        p2.y -= width - cornerRadius
        sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)

        p1 = pointOne.copy()
        p1.x += length - cornerRadius
        pCenter = adsk.core.Point3D.create(p1.x, p2.y, 0)
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(pCenter, p2, -pi/2)

        p2 = pointOne.copy()
        p2.x += cornerRadius
        sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)

        p1 = pointOne.copy()
        p1.y += cornerRadius
        pCenter = adsk.core.Point3D.create(p2.x, p1.y, 0)
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(pCenter, p2, -pi/2)

def ellipse(sketch: adsk.fusion.Sketch, center: Point3d, length: float, width: float):
    if length == width:
        sketch.sketchCurves.sketchCircles.addByCenterRadius(_toADSKPoint(center, BezierPlane.XY), length)
    else:
        pCenter = _toADSKPoint(center, BezierPlane.XY)
        majorAxisPoint = pCenter.copy()
        majorAxisPoint.x += length/2
        point = pCenter.copy()
        point.y += width/2
        sketch.sketchCurves.sketchEllipses.add(pCenter, majorAxisPoint, point)

def intersectionCurve(curve1: Union[adsk.fusion.SketchEntity, adsk.fusion.SketchControlPointSplines], curve2: Union[adsk.fusion.SketchEntity, adsk.fusion.SketchControlPointSplines], sketch: adsk.fusion.Sketch, project: bool):

    app: adsk.core.Application = adsk.core.Application.get()
    ui: adsk.core.UserInterface = app.userInterface
    sels: adsk.core.Selections = ui.activeSelections
    sels.clear()

    sels.add(sketch)
    app.executeTextCommand('Commands.Start SketchActivate')
    if isinstance(curve1, adsk.fusion.SketchControlPointSplines):
        for entry in curve1:
            _intersectionCurve(entry, curve2, sketch, project)
    else:
        _intersectionCurve(curve1, curve2, sketch, project)
    app.executeTextCommand('NaFusionUI.SketchStopCmd')


def _intersectionCurve(curve1: adsk.fusion.SketchEntity, curve2: Union[adsk.fusion.SketchEntity, adsk.fusion.SketchControlPointSplines], sketch: adsk.fusion.Sketch, project: bool):
    app: adsk.core.Application = adsk.core.Application.get()
    ui: adsk.core.UserInterface = app.userInterface
    sels: adsk.core.Selections = ui.activeSelections
    app.executeTextCommand('Commands.Start IntersectionCurve')

    try:
        sels.add(curve1)

        if isinstance(curve2, adsk.fusion.SketchControlPointSplines):
            for entry in curve2:
                sels.add(entry)
        else:
            sels.add(curve2)
    except:
        print("WARNING")
        pass

    # setting the project flag
    app. executeTextCommand('Commands.SetBool infoProjectionLinkOption {value}'.format(value=1 if project else 0))


    try:
        app.executeTextCommand('NuCommands.CommitCmd')
    except:
        # app.executeTextCommand
        # could not press commit -> results in timeline error
        print("ERROR")
        pass
    finally:
        # app.executeTextCommand('NaFusionUI.SketchStopCmd')
        pass
