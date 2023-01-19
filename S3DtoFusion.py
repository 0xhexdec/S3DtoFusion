# Assuming you have not changed the general structure of the template no modification is needed in this file.
from typing import List

import adsk.core
import adsk.fusion

from . import commands, config, utils
from .fusionConverter.converter import Converter
from .fusionConverter.converterSettings import ConverterSettings
from .lib import fusion360utils as futil
from .s3dModel.s3dx import S3DModel, fromFile
from .s3dModel.types.enums import TangentType
from .utils import timer
from .utils.test import test

app = adsk.core.Application.get()


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


def surface_split():
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

def surface_project():
    # finding Top Spline
    rootComponent = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    # Step one create surface from spline
    top_spline_sketch = rootComponent.sketches.itemByName("Top_Spline")
    spline = top_spline_sketch.sketchCurves.sketchControlPointSplines.item(0)
    # finding Side Spline
    side_spline_sketch = rootComponent.sketches.itemByName("Side_Spline")
    spline2 = side_spline_sketch.sketchCurves.sketchControlPointSplines.item(0)
    copyOfSpline = copySpline(spline2, side_spline_sketch)

    extrudes = rootComponent.features.extrudeFeatures
    distance = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(150))

    # define a path from the sketch curves
    path = rootComponent.features.createPath(spline, False)

    # set parameters to extrude surfaces according to the profileCollection
    extrudeInput = extrudes.createInput(path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extrudeInput.setOneSideExtent(distance, adsk.fusion.ExtentDirections.SymmetricExtentDirection)

    # indiciate that the extrude should be a surface, not a solid
    extrudeInput.isSolid = False

    # extrude and get the created body
    body = extrudes.add(extrudeInput).bodies.item(0)
    newSketch: adsk.fusion.Sketch = rootComponent.sketches.add(rootComponent.xYConstructionPlane)
    ret = newSketch.projectToSurface([body.faces.item(0)], [spline2], adsk.fusion.SurfaceProjectTypes.AlongVectorSurfaceProjectType, rootComponent.xConstructionAxis)
    body.isLightBulbOn = False

def run(context):
    try:
        # This will run the start function in each of your commands as defined in commands/__init__.py
        if not config.DEBUG:
            commands.start()
        else:
            commands.start()

        # Only for testing to execute the Board parsing

            progress = app.userInterface.createProgressDialog()
            progress.isCancelButtonShown = False
            progress.show("Converting S3DX file", "Load S3DX file", 0, 100, 0)
            # model: S3DModel = fromFile("C:/Users/Julian/plankton Kite/Kitefoilboards/Test2.s3dx", progress)
            # model: S3DModel = fromFile("C:/Users/Julian/plankton Kite/Kitefoilboards/TestBoard.s3dx", progress)
            model: S3DModel = S3DModel()
            settings = ConverterSettings()
            settings.closedStringer = False  # DONE
            settings.closedOutline = False  # DONE
            settings.closedSlices = True   # DONE
            settings.flipOutline = True  # DONE
            settings.mirrorSlices = False   # DONE
            settings.mirrorOutline = False  # DONE
            settings.fixedPoints = False    # DONE
            settings.fixedLines = False     # DONE
            config.debug_skip2d = False
            # settings.create3d = True

            settings.constrainedPoints = False

            converter = Converter(model, settings)
            converter.convertAll(app, None, progress)

        # test()

    except Exception as e:
        futil.handle_error('run')


def stop(context):
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        # This will run the stop function in each of your commands as defined in commands/__init__.py
        if not config.DEBUG:
            commands.stop()

    except Exception as e:
        futil.handle_error('stop')
