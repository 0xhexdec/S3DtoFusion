# Shape3d X representation of a board

from __future__ import annotations
from typing import Optional

from typing import Dict, List
from xml.dom.minidom import Element, Node

import adsk
import adsk.core
from pyexpat import ExpatError

from .types.bezier3d import Bezier3D
from .types.bezierDef import BezierDef
from .types.box import Box
from .types.point3d import Point3d
from .types.slice import Slice
from .types.stringerd3d import StringerD3D
from .types.utils import getFloat, getInt, getStr, getOptionalInt


class Board:

    version: int
    versionNumber: str
    name: str
    author: str
    comment: str
    category: str
    categoryType: str
    length: float
    lengthDev: float
    width: float
    thickness: float
    tail_rocker: float
    nose_rocker: float
    stringerMeasurement: int
    volume: float
    surfaceProj: float
    nbCalquesFastLoad: int
    nbBoxesFastLoad: int
    rockerLengthRescaleRatio: float
    widthLengthRescaleRatio: float
    thicknessLengthRescaleRatio: float
    stockLMin: float
    stockLMax: float
    vCResizeThickness: Optional[int]
    vCResizeRocker: Optional[int]
    vCResizeNone: Optional[int]
    volumeTail: float
    volumeNose: float
    surfaceProjTail: float
    surfaceProjNose: float
    rayonCourbureTail: float
    rayonCourbureNose: float
    railCoefficientTail: float
    railCoefficientNose: float
    vConcaveTail: float
    vConcaveNose: float
    lengthEff: float
    volumeEff: float
    surfaceProjEff: float
    rayonCourbureEff: float
    railCoefficientEff: float
    vConcaveEff: float
    license: str
    options: int
    symmetry: int
    ThicknessZStretch: Optional[int]
    afficheCourbureThck: int
    colorThck: int
    colorCourbureThck: int
    afficheCourbureCpl: int
    afficheGuidelinesCpl: int
    colorCpl: int
    colorCourbureCpl: int
    colorGuidelinesCpl: int
    nbTracesMesuresTopView: Optional[int]
    nbTracesMesuresSideView: Optional[int]
    nbTracesMesuresThicknessView: Optional[int]
    nbTracesMesuresSlicesView: Optional[int]
    ligneFlotaison: float
    numberOfSlices: int
    sandwich: float
    rock_angle: float
    color: int
    colorBot: int
    colorRail: int
    reflexion_coef: int
    reflexion_coef_Bot: int
    reflexion_coef_Rail: int
    nb_of_computed_slices: int
    nb_of_lines: int
    color_boitiers: int
    color_Maillage: int
    color_CouplesDef: int
    colorBoitiersD3D: int
    displayBothSides: int
    displayDeck: int
    displayBot: int
    imageMappingDeck: int
    imageMappingBot: int
    imageMappingRail: int
    extendDecoBot: int
    extendDecoRail: int
    duplicateDecoBot: int
    decoSideMargin: float
    decoSideMarginBot: float
    openContourTail: int
    nbLogos: int
    nbStringers: int
    nbLiseres: int
    nbBoxes: int
    nbcdTop: int
    nbcdSide: int

    otl: Bezier3D
    strBot: Bezier3D
    strDeck: Bezier3D
    curveDefTops: Dict[str, BezierDef]
    curveDefSides: Dict[str, BezierDef]
    slices: List[Slice]
    decoOrigin: Point3d
    # logos?
    # logos: List[Logo]
    stringers: List[StringerD3D]
    # liseres?
    boxes: List[Box]


    def __init__(self):
        self.otl = Bezier3D()
        self.strBot = Bezier3D()
        self.strDeck = Bezier3D()
        self.curveDefTops = {}
        self.curveDefSides = {}
        self.nbcdTop = 0
        self.nbcdSide = 0
        self.slices = []
        self.decoOrigin = Point3d()
        self.stringers = []
        self.boxes = []

    def fromXML(self, board: Element, progress: adsk.core.ProgressDialog):
        try:
            progress.message = "Parse Outline"
            adsk.doEvents()
            self.otl.fromXML(board.getElementsByTagName("Otl")[0].childNodes[1])
            progress.message = "Parse Stringer"
            progress.progressValue = 7
            adsk.doEvents()
            self.strBot.fromXML(board.getElementsByTagName("StrBot")[0].childNodes[1])
            self.strDeck.fromXML(board.getElementsByTagName("StrDeck")[0].childNodes[1])

            progress.message = "Find and parse curves"
            progress.progressValue = 10
            adsk.doEvents()

            nodes: List[Element] = board.childNodes
            for node in nodes:
                if node.nodeType != Node.TEXT_NODE:
                    if node.nodeName.startswith("curveDefTop"):
                        self.curveDefTops[node.nodeName] = BezierDef().fromXMLAndGet(node.childNodes[1])
                        continue
                    elif node.nodeName.startswith("curveDefSide"):
                        self.curveDefSides[node.nodeName] = BezierDef().fromXMLAndGet(node.childNodes[1])
                        continue

            progress.message = "Parse Outline Data"
            progress.progressValue = 33
            adsk.doEvents()

            for item in ["OutlineDef", "OutlineDevDef"]:
                if len(board.getElementsByTagName(item)) != 0:
                    self.curveDefTops[item] = BezierDef().fromXMLAndGet(board.getElementsByTagName(item)[0].childNodes[1])

            progress.message = "Parse Stringer Data"
            progress.progressValue = 35
            adsk.doEvents()

            for item in ["ProfilBotDef", "ProfilTopDef", "TrueWaterlineSideDef"]:
                if len(board.getElementsByTagName(item)) != 0:
                    self.curveDefSides[item] = BezierDef().fromXMLAndGet(board.getElementsByTagName(item)[0].childNodes[1])

            progress.message = "Parse Slices"
            progress.progressValue = 38
            adsk.doEvents()

            self.numberOfSlices = getInt(board, "Number_of_slices")
            for i in range(self.numberOfSlices):
                s = Slice()
                s.fromXML(board.getElementsByTagName("Couples_" + str(i))[0])
                self.slices.append(s)

            self.decoOrigin.fromXML(board.getElementsByTagName("Deco_origin")[0].childNodes[1])

            self.nbLogos = getInt(board, "NbLogos")
            # for i in range(self.nbLogos):
            #     s = Logo()
            #     s.fromXML(board.getElementsByTagName("Logo_" + str(i))[0])
            #     self.logos.append(s)

            progress.message = "Parse Stringer"
            progress.progressValue = 43
            adsk.doEvents()

            self.nbStringers = getInt(board, "NbStringers")
            for i in range(self.nbStringers):
                s = StringerD3D()
                s.fromXML(board.getElementsByTagName("Stringer_" + str(i))[0])
                self.stringers.append(s)

            self.nbLiseres = getInt(board, "NbLiseres")
            # for i in range(self.nbLiseres):
            #     s = Lisere()
            #     s.fromXML(board.getElementsByTagName("Lisere_" + str(i))[0])
            #     self.liseres.append(s)

            progress.message = "Parse Boxes"
            progress.progressValue = 45
            adsk.doEvents()

            self.nbBoxes = getInt(board, "Nb_Boxes")
            for i in range(self.nbBoxes):
                b = Box()
                b.fromXML(board.getElementsByTagName("Box_" + str(i))[0])
                self.boxes.append(b)

            progress.message = "Parse Misc"
            progress.progressValue = 47
            adsk.doEvents()

            self.version = getInt(board, "Version")
            self.versionNumber = getStr(board, "VersionNumber")
            self.name = getStr(board, "Name")
            self.author = getStr(board, "Author")
            self.comment = getStr(board, "Comment")
            self.category = getStr(board, "Category")
            self.categoryType = getStr(board, "CategoryType")
            self.length = getFloat(board, "Length")
            self.lengthDev = getFloat(board, "LengthDev")
            self.width = getFloat(board, "Width")
            self.thickness = getFloat(board, "Thickness")
            self.tail_rocker = getFloat(board, "Tail_rocker")
            self.nose_rocker = getFloat(board, "Nose_rocker")
            self.stringerMeasurement = getInt(board, "StringerMeasurement")
            self.volume = getFloat(board, "Volume")
            self.surfaceProj = getFloat(board, "SurfaceProj")
            self.nbCalquesFastLoad = getInt(board, "NbCalquesFastLoad")
            self.nbBoxesFastLoad = getInt(board, "NbBoxesFastLoad")
            self.rockerLengthRescaleRatio = getFloat(board, "RockerLengthRescaleRatio")
            self.widthLengthRescaleRatio = getFloat(board, "WidthLengthRescaleRatio")
            self.thicknessLengthRescaleRatio = getFloat(board, "ThicknessLengthRescaleRatio")
            self.stockLMin = getFloat(board, "StockLMin")
            self.stockLMax = getFloat(board, "StockLMax")
            self.vCResizeThickness = getOptionalInt(board, "VCResizeThickness")
            self.vCResizeRocker = getOptionalInt(board, "VCResizeRocker")
            self.vCResizeNone = getOptionalInt(board, "VCResizeNone")
            self.volumeTail = getFloat(board, "VolumeTail")
            self.volumeNose = getFloat(board, "VolumeNose")
            self.surfaceProjTail = getFloat(board, "SurfaceProjTail")
            self.surfaceProjNose = getFloat(board, "SurfaceProjNose")
            self.rayonCourbureTail = getFloat(board, "RayonCourbureTail")
            self.rayonCourbureNose = getFloat(board, "RayonCourbureNose")
            self.railCoefficientTail = getFloat(board, "RailCoefficientTail")
            self.railCoefficientNose = getFloat(board, "RailCoefficientNose")
            self.vConcaveTail = getFloat(board, "VConcaveTail")
            self.vConcaveNose = getFloat(board, "VConcaveNose")
            self.lengthEff = getFloat(board, "LengthEff")
            self.volumeEff = getFloat(board, "VolumeEff")
            self.surfaceProjEff = getFloat(board, "SurfaceProjEff")
            self.rayonCourbureEff = getFloat(board, "RayonCourbureEff")
            self.railCoefficientEff = getFloat(board, "RailCoefficientEff")
            self.vConcaveEff = getFloat(board, "VConcaveEff")
            self.license = getStr(board, "License")
            self.options = getInt(board, "Options")
            self.symmetry = getInt(board, "Symmetry")
            self.ThicknessZStretch = getOptionalInt(board, "ThicknessZStretch")
            self.afficheCourbureThck = getInt(board, "AfficheCourbureThck")
            self.colorThck = getInt(board, "ColorThck")
            self.colorCourbureThck = getInt(board, "ColorCourbureThck")
            self.afficheCourbureCpl = getInt(board, "AfficheCourbureCpl")
            self.afficheGuidelinesCpl = getInt(board, "AfficheGuidelinesCpl")
            self.colorCpl = getInt(board, "ColorCpl")
            self.colorCourbureCpl = getInt(board, "ColorCourbureCpl")
            self.colorGuidelinesCpl = getInt(board, "ColorGuidelinesCpl")
            self.nbTracesMesuresTopView = getOptionalInt(board, "nbTracesMesuresTopView")
            self.nbTracesMesuresSideView = getOptionalInt(board, "nbTracesMesuresSideView")
            self.nbTracesMesuresThicknessView = getOptionalInt(board, "nbTracesMesuresThicknessView")
            self.nbTracesMesuresSlicesView = getOptionalInt(board, "nbTracesMesuresSlicesView")
            self.ligneFlotaison = getFloat(board, "LigneFlotaison")
            self.sandwich = getFloat(board, "Sandwich")
            self.rock_angle = getFloat(board, "Rock_angle")
            self.color = getInt(board, "Color")
            self.colorBot = getInt(board, "ColorBot")
            self.colorRail = getInt(board, "ColorRail")
            self.reflexion_coef = getInt(board, "Reflexion_coef")
            self.reflexion_coef_Bot = getInt(board, "Reflexion_coef_Bot")
            self.reflexion_coef_Rail = getInt(board, "Reflexion_coef_Rail")
            self.nb_of_computed_slices = getInt(board, "Nb_of_computed_slices")
            self.nb_of_lines = getInt(board, "Nb_of_lines")
            self.color_boitiers = getInt(board, "Color_boitiers")
            self.color_Maillage = getInt(board, "Color_Maillage")
            self.color_CouplesDef = getInt(board, "Color_CouplesDef")
            self.colorBoitiersD3D = getInt(board, "ColorBoitiersD3D")
            self.displayBothSides = getInt(board, "DisplayBothSides")
            self.displayDeck = getInt(board, "DisplayDeck")
            self.displayBot = getInt(board, "DisplayBot")
            self.imageMappingDeck = getInt(board, "ImageMappingDeck")
            self.imageMappingBot = getInt(board, "ImageMappingBot")
            self.imageMappingRail = getInt(board, "ImageMappingRail")
            self.extendDecoBot = getInt(board, "ExtendDecoBot")
            self.extendDecoRail = getInt(board, "ExtendDecoRail")
            self.duplicateDecoBot = getInt(board, "DuplicateDecoBot")
            self.decoSideMargin = getFloat(board, "DecoSideMargin")
            self.decoSideMarginBot = getFloat(board, "DecoSideMarginBot")
            self.openContourTail = getInt(board, "OpenContourTail")
            self.nbcdTop = getInt(board, "nbcdTop")
            self.nbcdSide = getInt(board, "nbcdSide")

        except ExpatError as e:
            pass
            # if e.code == 4:
            #     ui.messageBox(f"Failed parsing the file due to unknown XML Tag <{e}>")
            # else:
            #     ui.messageBox(f"Failed parsing the file due to {e}")
