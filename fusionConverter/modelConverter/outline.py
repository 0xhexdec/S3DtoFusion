import adsk.core
import adsk.fusion
from adsk.fusion import ConstructionPlane, Sketch

from ...s3dModel.types.bezier3d import Bezier3D
from ...s3dModel.types.point3d import Point3d
from ..converterSettings import ConverterSettings
from ..typeConverter.bezierToSketch import bezier2dToSketch
from ..typeConverter.lines import pointsToLine
from ..typeConverter.utils import BezierPlane, fixAllLinesInSketch


def convert(comp: adsk.fusion.Component, outlinePlane: ConstructionPlane, outline: Bezier3D, settings: ConverterSettings):
    outlineSketch: Sketch = comp.sketches.add(outlinePlane)  # type: ignore
    outlineSketch.name = "Outline"
    if settings.flipOutline or settings.mirrorOutline:
        if settings.mirrorOutline:
            bezier2dToSketch(outlineSketch, outline, BezierPlane.XY, settings)
        outline = outline.getMirrored(False, True, False)
    bezier2dToSketch(outlineSketch, outline, BezierPlane.XY, settings)
    if settings.closedOutline:
        # Tail to origin
        pointsToLine(outlineSketch, outline.controlPoints.points[0], Point3d.new(0, 0, 0), BezierPlane.XY, settings)
        nbOfPoints = outline.controlPoints.numberOfPoints - 1
        centerNose: Point3d = Point3d.new(outline.controlPoints.points[nbOfPoints].x, 0, 0)
        # Middle line
        pointsToLine(outlineSketch, centerNose, Point3d.new(0, 0, 0), BezierPlane.XY, settings)
        # nose to center line
        pointsToLine(outlineSketch, outline.controlPoints.points[nbOfPoints], centerNose, BezierPlane.XY, settings)

        if settings.mirrorOutline:
            # mirrored tail to origin
            pointsToLine(outlineSketch, outline.controlPoints.points[0].getMirrored(False, True, False), Point3d.new(0, 0, 0), BezierPlane.XY, settings)
            # mirrored nose to center line
            pointsToLine(outlineSketch, outline.controlPoints.points[nbOfPoints].getMirrored(False, True, False), centerNose, BezierPlane.XY, settings)

    if settings.mirrorOutline and not settings.closedOutline:
        # connect Tail point with its mirrored counterpart
        pointsToLine(outlineSketch, outline.controlPoints.points[0], outline.controlPoints.points[0].getMirrored(False, True, False), BezierPlane.XY, settings)
        # connect Nose Point with its mirrored counterpart
        nbOfPoints = outline.controlPoints.numberOfPoints - 1
        pointsToLine(outlineSketch, outline.controlPoints.points[nbOfPoints], outline.controlPoints.points[nbOfPoints].getMirrored(False, True, False), BezierPlane.XY, settings)

    if settings.fixedPoints:
        for i in range(outlineSketch.sketchPoints.count):
            outlineSketch.sketchPoints.item(i).isFixed = True

    if settings.fixedLines:
        fixAllLinesInSketch(outlineSketch)
    
    if settings.create3d:
        outlineSketch.isLightBulbOn = False
