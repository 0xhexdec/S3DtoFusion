import adsk.core


# settings object allows:
#   - adding constraints to handles
#   - adding constraints to points
#   - adding the "Fix" Constraint to handles
#   - adding the "Fix" Constraint to points
class ConverterSettings():
    constrainedPoints: bool = False
    fixedPoints: bool = False
    fixedLines: bool = False
    mergePoints: bool = False
    zUp: bool = False
    closedStringer: bool = True
    closedOutline: bool = True
    closedSlices: bool = True
    flipOutline: bool = True
    mirrorSlices: bool = False
    mirrorOutline: bool = False
    create3d: bool = False
    loftAsSolid: bool = True
    boxesAsBody: bool = True
    boxesCutFromBoard: bool = False
    filename: str = ""

    def __init__(self) -> None:
        self.zUp = adsk.core.Application.get().preferences.generalPreferences.defaultModelingOrientation == adsk.core.DefaultModelingOrientations.ZUpModelingOrientation
