from xml.dom.minidom import Element

from .utils import getFloat, getInt, getStr


class StringerD3D():

    name: str
    width: float
    shift: float
    tilt: float
    colorD3D: int
    mappingD3D: int
    imageMappedD3D: str
    displayD3D: int
    superpositionOrder: int

    def __init__(self) -> None:
        pass

    def fromXML(self, stringer: Element):
        self.name = getStr(stringer, "Name")
        self.width = getFloat(stringer, "Width")
        self.shift = getFloat(stringer, "Shift")
        self.tilt = getFloat(stringer, "Tilt")
        self.colorD3D = getInt(stringer, "ColorD3D")
        self.mappingD3D = getInt(stringer, "MappingD3D")
        self.imageMappedD3D = getStr(stringer, "ImageMappedD3D")
        self.displayD3D = getInt(stringer, "DisplayD3D")
        self.superpositionOrder = getInt(stringer, "SuperpositionOrder")
