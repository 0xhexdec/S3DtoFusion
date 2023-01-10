from __future__ import annotations

from xml.dom.minidom import Element

from .bezier3d import Bezier3D
from .utils import getInt


class BezierDef():

    top: int
    npCouple: int
    edited: int
    displayed: int
    displayCurvature: int
    displayCurvatureRadius: int
    displayCurvatureRadiusDir: int
    displayGuidelines: int
    color: int
    colorCurvature: int
    colorCurvatureRadius: int
    colorCurvatureRadiusDir: int
    colorGuidelines: int
    fixedRelativeTo: int
    bezDiffHorthoValid: int
    bezier3d: Bezier3D

    def __init__(self):
        self.bezier3d = Bezier3D()

    def fromXML(self, bezierDef: Element):
        self.top = getInt(bezierDef, "Top")
        self.npCouple = getInt(bezierDef, "NpCouple")
        self.edited = getInt(bezierDef, "Edited")
        self.displayed = getInt(bezierDef, "Displayed")
        self.displayCurvature = getInt(bezierDef, "DisplayCurvature")
        self.displayCurvatureRadius = getInt(bezierDef, "DisplayCurvatureRadius")
        self.displayCurvatureRadiusDir = getInt(bezierDef, "DisplayCurvatureRadiusDir")
        self.displayGuidelines = getInt(bezierDef, "DisplayGuidelines")
        self.color = getInt(bezierDef, "Color")
        self.colorCurvature = getInt(bezierDef, "ColorCurvature")
        self.colorCurvatureRadius = getInt(bezierDef, "ColorCurvatureRadius")
        self.colorCurvatureRadiusDir = getInt(bezierDef, "ColorCurvatureRadiusDir")
        self.colorGuidelines = getInt(bezierDef, "ColorGuidelines")
        self.fixedRelativeTo = getInt(bezierDef, "FixedRelativeTo")
        self.bezDiffHorthoValid = getInt(bezierDef, "BezDiffHorthoValide")
        self.bezier3d.fromXML(bezierDef.getElementsByTagName("Bezier3d")[0])
    
    def fromXMLAndGet(self, bezierDef: Element) -> BezierDef:
        self.fromXML(bezierDef)
        return self
