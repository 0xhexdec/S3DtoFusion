# The Converter class takes a S3DModel and converts its content to Fusion360 Sketches
from typing import List, Optional, Set

import adsk
import adsk.core
import adsk.fusion
from adsk.fusion import ConstructionPlane

from .. import config
from ..fusionConverter.loftHandler import LoftHandler
from ..fusionConverter.typeConverter.lines import (
    intersection_curve_via_surface_project,
    intersection_curve_via_text_command)
from ..s3dModel.s3dx import S3DModel
from ..s3dModel.types.bezier3d import Bezier3D
from ..utils import timer
from ..utils.transform import sketchPointListToPoint3DList
from .converterSettings import ConverterSettings
from .modelConverter import box as boxconverter
from .modelConverter import curveDef, outline
from .modelConverter import slice as sliceconverter
from .modelConverter import stringer


class Converter():
    model: S3DModel
    settings: ConverterSettings
    def __init__(self, model: S3DModel, settings: Optional[ConverterSettings]) -> None:
        self.model = model
        if settings is None:
            self.settings = ConverterSettings()
        else:
            self.settings = settings

    def convertAll(self, app: adsk.core.Application, rockerPlane: Optional[ConstructionPlane], progress: adsk.core.ProgressDialog):
        print("Start converting an creating sketches...")
        timer.reset()
        rootComponent = adsk.fusion.Design.cast(app.activeProduct).rootComponent
        component = rootComponent
        if rockerPlane is None:
            rootComponent = adsk.fusion.Design.cast(app.activeProduct).rootComponent
            if self.settings.zUp:
                rockerPlane = rootComponent.xZConstructionPlane
                # rockerPlane = rootComponent.
                tailPlane: ConstructionPlane = rootComponent.yZConstructionPlane
                outlinePlane: ConstructionPlane = rootComponent.xYConstructionPlane
            else:

                rockerPlane = rootComponent.xYConstructionPlane
                tailPlane = rootComponent.yZConstructionPlane
                outlinePlane: ConstructionPlane = rootComponent.xZConstructionPlane
        else:
            # TODO implement creation based on given rockerplane
            # create plane for tail slice
            tailPlane = None
            # create plane for Outline
            outlinePlane = None
            component = None
            raise NotImplementedError()

        if not config.debug_skip2d:
            progress.progressValue = 55
            progress.message = "Building Stringer"
            adsk.doEvents()
            self.convertStringer(component, rockerPlane)  # type: ignore
            progress.progressValue = 60
            progress.message = "Building Outline"
            adsk.doEvents()
            self.convertOutline(component, outlinePlane)  # type: ignore
            progress.progressValue = 65
            progress.message = "Building Slices"
            adsk.doEvents()
            self.convertSlices(component, tailPlane)  # type: ignore
            progress.progressValue = 70
            progress.message = "Building Misc Lines"
            adsk.doEvents()
            self.convertCurveDefs(component, outlinePlane, rockerPlane)  # type: ignore
            progress.progressValue = 75
            progress.message = "Building Boxes"
            adsk.doEvents()
            self.convertBoxes(component, outlinePlane)  # type: ignore
            progress.progressValue = 80

        progress.message = "Building 3D Lines"
        adsk.doEvents()
        self.create3D(component, outlinePlane)  # type: ignore

        timer.lap()
        print("Done")

    def convertStringer(self, comp: adsk.fusion.Component, rockerPlane: ConstructionPlane):
        stringer.convert(comp, rockerPlane, self.model.board.strDeck, self.model.board.strBot, self.settings)

    def convertOutline(self, comp: adsk.fusion.Component, outlinePlane: ConstructionPlane):
        outline.convert(comp, outlinePlane, self.model.board.otl, self.settings)

    def convertCurveDefs(self, comp: adsk.fusion.Component, outlinePlane: ConstructionPlane, rockerPlane: ConstructionPlane):
        curveDef.convert(comp, outlinePlane, rockerPlane, self.model.board.curveDefTops, self.model.board.curveDefSides, self.settings)

    # runs the slice conversion for all slices
    def convertSlices(self, comp: adsk.fusion.Component, tailPlane: ConstructionPlane):
        i: int = 0
        for board_slice in self.model.board.slices:
            i += 1
            sliceconverter.convert(comp, tailPlane, board_slice, f"Slice {i}", self.settings)

    def convertBoxes(self, comp: adsk.fusion.Component, outlinePlane: ConstructionPlane):
        # for box in self.model.board.boxes:
        #     boxconverter.covert(app)
        #     pass
        boxconverter.convertEasy(comp, outlinePlane, self.model.board.boxes, self.settings)

    def create3D(self, comp: adsk.fusion.Component, outlinePlane: ConstructionPlane):
        # Part Zero: Check if all needed Curves are present (Rail, Apex, Deck)
        # 3D
        nameList: List[str] = []
        doublesList: List[str] = []
        for i in range(comp.sketches.count):
            sketch = comp.sketches.item(i)
            name = sketch.name
            if name.find("(") == -1:
                continue
            sketch.isLightBulbOn = False
            name = name.replace(" (Top)", "").replace(" (Side)", "")
            if name in nameList:
                doublesList.append(name)
            else:
                nameList.append(name)
        print(doublesList)

        # Part One: Create 3D Splines by using intersectioncurves
        for entry in doublesList:
            sideSketch = comp.sketches.itemByName(entry + " (Side)")
            sideSketch.isLightBulbOn = False
            sideSplines = sideSketch.sketchCurves.sketchControlPointSplines

            topSketch = comp.sketches.itemByName(entry + " (Top)")
            topSketch.isLightBulbOn = False
            topSplines = topSketch.sketchCurves.sketchControlPointSplines

            if config.experimental_3d_spline_implementation == config.SplineImplementationTechnique.TEXTCOMMANDS:
                sketch: adsk.fusion.Sketch = comp.sketches.add(outlinePlane)  # type: ignore
                sketch.name = entry + " 3D"
                intersection_curve_via_text_command(sideSplines, topSplines, sketch, False)
            
                # comp.sketches.itemByName(entry + " (Top)").sketchCurves.sketchControlPointSplines.add(side, 3)
                # check if Splines are reversed (don't know why this happens)
                splinePointsList: List[List[adsk.core.Point3D]] = []
                isReversed: bool = False
                print(len(sketch.sketchCurves.sketchControlPointSplines))
                for spline in sketch.sketchCurves.sketchControlPointSplines:
                    points = sketchPointListToPoint3DList(spline.controlPoints)
                    if spline.startSketchPoint.geometry.x > spline.endSketchPoint.geometry.x:
                        # spline is revered -> the start point is further away from x=0 than the end point
                        print(f"start {spline.startSketchPoint.geometry.x} -> end {spline.endSketchPoint.geometry.x}")
                        points.reverse()
                        isReversed = True
                    splinePointsList.append(points)

                # this flipps the reversed splines BUT the new creation of the splines also fixes some weird errors
                # so even if the splines were all correct, delete and create them new!

                for i in range(sketch.sketchCurves.sketchControlPointSplines.count -1, -1, -1):
                    sketch.sketchCurves.sketchControlPointSplines[i].deleteMe()

                for splinePoints in splinePointsList:
                    sketch.sketchCurves.sketchControlPointSplines.add(splinePoints, 3)  # type: ignore

                # make splines continuous
                for i in range(sketch.sketchCurves.sketchControlPointSplines.count - 1):
                    spline1 = sketch.sketchCurves.sketchControlPointSplines[i]
                    spline2 = sketch.sketchCurves.sketchControlPointSplines[i+1]
                    # set the startpoint to the endpoint of the last
                    spline2.startSketchPoint.merge(spline1.endSketchPoint)

                # constrain control lines from the splines so that the splines are continuous and smooth
                constraints = sketch.geometricConstraints
                lineIndex = -1
                for i in range(sketch.sketchCurves.sketchControlPointSplines.count - 1):
                    lineIndex += len(sketch.sketchCurves.sketchControlPointSplines[i].controlPoints) - 1
                    # sketch.sketchCurves.sketchLines[lineIndex].isFixed = False
                    constraints.addCollinear(sketch.sketchCurves.sketchLines[lineIndex], sketch.sketchCurves.sketchLines[lineIndex + 1])
            elif config.experimental_3d_spline_implementation == config.SplineImplementationTechnique.PROJECT_TO_SURFACE:
                sketch = intersection_curve_via_surface_project(sideSplines, topSplines, entry + " 3D")
            else:
                raise NotImplementedError()
