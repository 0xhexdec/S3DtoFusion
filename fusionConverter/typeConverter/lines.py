from math import pi
from typing import List, Optional, Union

import adsk.core
import adsk.fusion

from ... import config
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

def intersection_curve_via_text_command(curve1: Union[adsk.fusion.SketchEntity, adsk.fusion.SketchControlPointSplines], curve2: Union[adsk.fusion.SketchEntity, adsk.fusion.SketchControlPointSplines], sketch: adsk.fusion.Sketch, project: bool):

    app: adsk.core.Application = adsk.core.Application.get()
    ui: adsk.core.UserInterface = app.userInterface
    sels: adsk.core.Selections = ui.activeSelections
    sels.clear()

    sels.add(sketch)
    app.executeTextCommand('Commands.Start SketchActivate')
    if isinstance(curve1, adsk.fusion.SketchControlPointSplines):
        for entry in curve1:
            _intersection_curve_via_text_command(entry, curve2, sketch, project)
    else:
        _intersection_curve_via_text_command(curve1, curve2, sketch, project)
    app.executeTextCommand('NaFusionUI.SketchStopCmd')


def _intersection_curve_via_text_command(curve1: adsk.fusion.SketchEntity, curve2: Union[adsk.fusion.SketchEntity, adsk.fusion.SketchControlPointSplines], sketch: adsk.fusion.Sketch, project: bool):
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
    app.executeTextCommand('Commands.SetBool infoProjectionLinkOption {value}'.format(value=1 if project else 0))
    try:
        app.executeTextCommand('NuCommands.CommitCmd')
    except:
        print("ERROR")
    finally:
        # app.executeTextCommand('NaFusionUI.SketchStopCmd')
        pass

def intersection_curve_via_surface_project(curve1: Union[adsk.fusion.SketchEntity, adsk.fusion.SketchControlPointSplines], curve2: Union[adsk.fusion.SketchEntity, adsk.fusion.SketchControlPointSplines], sketchName: str):
    app: adsk.core.Application = adsk.core.Application.get()
    rootComponent = adsk.fusion.Design.cast(app.activeProduct).rootComponent

    extrudes = rootComponent.features.extrudeFeatures

    collection: adsk.core.ObjectCollection = adsk.core.ObjectCollection.create()
    if isinstance(curve1,adsk.fusion.SketchControlPointSplines ):
        for spline in curve1:
            collection.add(spline)
    else:
        collection.add(curve1)

    # define a path from the sketch curves
    path = rootComponent.features.createPath(collection, True)

    # set parameters to extrude surfaces according to the profileCollection
    extrudeInput = extrudes.createInput(path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # TODO 50 needs to be based on some value from the board to make sure it always fits
    extrudeInput.setSymmetricExtent(adsk.core.ValueInput.createByReal(50), False, adsk.core.ValueInput.createByReal(0))

    # indiciate that the extrude should be a surface, not a solid
    extrudeInput.isSolid = False

    # extrude and get the created body
    body = extrudes.add(extrudeInput).bodies.item(0)

    newSketch: adsk.fusion.Sketch = rootComponent.sketches.add(rootComponent.xYConstructionPlane)
    newSketch.name = sketchName
    curveList = []
    if isinstance(curve2, adsk.fusion.SketchControlPointSplines):
        for curve in curve2:
            curveList.append(curve)
    else:
        curveList.append(curve2)

    faceList = []
    for face in body.faces:
        faceList.append(face)
    newSketch.projectToSurface(faceList, curveList, adsk.fusion.SurfaceProjectTypes.AlongVectorSurfaceProjectType, rootComponent.zConstructionAxis)
    body.isLightBulbOn = False
    return newSketch


def copySpline(spline: adsk.fusion.SketchControlPointSpline, sketch: adsk.fusion.Sketch):
    pointlist: list = []
    for point in spline.controlPoints:
        pointlist.append(point)
    # duplicated_sketch = rootComponent.sketches.add(rootComponent.yZConstructionPlane, None)
    return sketch.sketchCurves.sketchControlPointSplines.add(pointlist, adsk.fusion.SplineDegrees.SplineDegreeFive)

def vector2List(vector: List[adsk.core.Point3D]):
    lst = []
    for entry in vector:
        lst.append(entry)
    return lst

def intersection_curve_via_surface_split():
    # finding Top Spline
    rootComponent = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    # Step one create surface from spline
    top_spline_sketch = rootComponent.sketches.itemByName("Top_Spline")
    spline = top_spline_sketch.sketchCurves.sketchControlPointSplines.item(0)
    # finding Side Spline
    side_spline_sketch = rootComponent.sketches.itemByName("Side_Spline")
    spline2 = side_spline_sketch.sketchCurves.sketchControlPointSplines.item(0)
    copyOfSpline = copySpline(spline2, side_spline_sketch)

    # print(side_spline_sketch.sketchCurves.sketchControlPointSplines)
    # return
    extrudes = rootComponent.features.extrudeFeatures

    # set extrude distance to 10mm
    mm10 = adsk.core.ValueInput.createByString("150 mm")
    distance = adsk.fusion.DistanceExtentDefinition.create(mm10)

    # define a path from the sketch curves
    path = rootComponent.features.createPath(spline, False)

    # set parameters to extrude surfaces according to the profileCollection
    extrudeInput = extrudes.createInput(path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extrudeInput.setOneSideExtent(distance, adsk.fusion.ExtentDirections.PositiveExtentDirection)

    # indiciate that the extrude should be a surface, not a solid
    extrudeInput.isSolid = False

    # extrude and get the created body
    body = extrudes.add(extrudeInput).bodies.item(0)
    # body = rootComponent.bRepBodies.item(0)

    splitFaceFeatures = rootComponent.features.splitFaceFeatures

    # Set faces to split
    faces = adsk.core.ObjectCollection.create()
    faces.add(body.faces.item(0))

    # Create a split face feature of surface intersection split type
    splitFaceInput = splitFaceFeatures.createInput(faces, spline2, True)
    split = splitFaceFeatures.add(splitFaceInput)
    for edge in split.faces.item(0).edges:
        print(edge.length)
    curve = split.faces.item(0).edges.item(0).geometry
    if curve.curveType == adsk.core.Curve3DTypes.NurbsCurve3DCurveType:
        nurbs = adsk.core.NurbsCurve3D.cast(curve)
        print(nurbs.controlPointCount)
        pointList = vector2List(nurbs.controlPoints)
        newSketch = rootComponent.sketches.add(rootComponent.xYConstructionPlane)
        newSketch.sketchCurves.sketchControlPointSplines.add(pointList, nurbs.degree)
