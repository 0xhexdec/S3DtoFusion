from typing import Optional
from xml.dom.minidom import Element

from ...utils.Exceptions import ElementNotFoundException
from .point2d import Point2d
from .point3d import Point3d
from .utils import getBool, getFloat, getInt, getStr, getOptionalFloat


class Box():

    name: str
    style: int
    style2: int
    length: float
    width: float
    height: float
    cornerRadius: Optional[float]
    color: int
    reflexion_coef: int
    even: bool
    central: bool
    symNoseTail: int
    iFixedToBt: int
    distFixedTo: Optional[float]
    aFixedTo: Optional[float]
    fixedTail: int
    fixedNose: int
    fixedCenter: int
    fixedRail: int
    face: int
    referencePoint: Point3d
    pointReference: Point3d
    pointreferenceDx: float
    pointreferenceDy: float
    pointCenter: Point3d
    finLenght: float
    angleOz: float
    autoAdjustSurface: bool
    displayD3D: int
    mappingD3D: int
    imageMappedD3D: str
    cutCNC: int
    dpLibelle: Point2d


    def __init__(self):
        self.referencePoint = Point3d()
        self.pointReference = Point3d()
        self.pointCenter = Point3d()
        self.dpLibelle = Point2d()
        self.cornerRadius = None
        self.autoAdjustSurface = True

    def fromXML(self, box: Element):
        self.name = getStr(box, "Name")
        self.style = getInt(box, "Style")
        self.style2 = getInt(box, "Style2")
        self.length = getFloat(box, "Length")
        self.width = getFloat(box, "Width")
        self.height = getFloat(box, "Height")
        if self.style2 == 0:
            self.cornerRadius = getFloat(box, "CornerRadius")
        self.color = getInt(box, "Color")
        self.reflexion_coef = getInt(box, "Reflexion_coef")
        self.even = getBool(box, "Even")
        self.central = getBool(box, "Central")
        self.symNoseTail = getInt(box, "SymNoseTail")
        self.iFixedToBt = getInt(box, "IFixedToBt")
        self.distFixedTo = getOptionalFloat(box, "DistFixedTo")
        self.aFixedTo = getOptionalFloat(box, "AFixedTo")
        self.fixedTail = getInt(box, "FixedTail")
        self.fixedNose = getInt(box, "FixedNose")
        self.fixedCenter = getInt(box, "FixedCenter")
        self.fixedRail = getInt(box, "FixedRail")
        self.face = getInt(box, "Face")
        self.pointreferenceDx = getFloat(box, "PointRefDx")
        self.pointreferenceDy = getFloat(box, "PointRefDy")
        self.finLenght = getFloat(box, "FinLength")
        self.angleOz = getFloat(box, "AngleOz")

        try:
            self.autoAdjustSurface = getBool(box, "AutoAjusteSurface")
        except ElementNotFoundException:
            # if the exception gets thrown here, the Tag is not present and therefore its value is <True>
            pass

        self.displayD3D = getInt(box, "DisplayD3D")
        self.mappingD3D = getInt(box, "MappingD3D")
        self.imageMappedD3D = getStr(box, "ImageMappedD3D")
        self.cutCNC = getInt(box, "CutCNC")

        self.referencePoint.fromXML(box.getElementsByTagName("Point3d")[0])
        self.pointReference.fromXML(box.getElementsByTagName("Point3d")[1])
        self.pointCenter.fromXML(box.getElementsByTagName("Point3d")[2])
        self.dpLibelle.fromXML(box.getElementsByTagName("Point2d")[0])

