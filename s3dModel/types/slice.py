from xml.dom.minidom import Element

from .bezier3d import Bezier3D
from .utils import getInt


class Slice():

    above: int  # Dessus
    below: int  # Dessous
    displayed: int
    bezier: Bezier3D

    def __init__(self) -> None:
        self.bezier = Bezier3D()

    def fromXML(self, slice: Element):
        self.above = getInt(slice, "Dessus")
        self.below = getInt(slice, "Dessous")
        self.displayed = getInt(slice, "Displayed")
        self.bezier.fromXML(slice.getElementsByTagName("Bezier3d")[0])
