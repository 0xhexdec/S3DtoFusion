import io
from typing import Optional
from xml.dom.minidom import Element, parseString

import adsk
import adsk.core
from pyexpat import ExpatError

from ..s3dModel.types.utils import getStr
from ..utils import timer
from .board import Board


class S3DModel():
    board: Board
    # scene: Scene
    def __init__(self):
        self.board = Board()

    def fromXML(self, document: Element, progress: adsk.core.ProgressDialog):
        boardDocument = document.getElementsByTagName("Board")[0]
        self.board.fromXML(boardDocument, progress)

def fromFile(filename: str, progress: adsk.core.ProgressDialog) -> S3DModel:
    print("Start parsing...")
    timer.reset()
    progress.message = "Sanitize file"
    adsk.doEvents()
    with io.open(filename, 'r', encoding='utf-8-sig') as file:
        #points = adsk.core.ObjectCollection.create()
        sanitizedFile = ""
        for line in file.readlines():
            if line.find("Ref. point>") != -1:
                index = line.find("Ref. point>")
                newLine = line[0:index] + "Ref.point>" + line[index+11:]
                # futil.log(f"{line} -> {newLine}")
                sanitizedFile += newLine
            else:
                sanitizedFile += line

        try:
            s3dx = S3DModel()
            progress.message = "Parse File"
            progress.progressValue = 5
            adsk.doEvents()
            s3dx.fromXML(parseString(sanitizedFile), progress)
            timer.lap()
            print("Done")
            return s3dx
        except ExpatError as e:
            raise e
            # if e.code == 4:
            #     ui.messageBox(f"Failed parsing the file due to unknown XML Tag <{e}>")
            # else:
            #     ui.messageBox(f"Failed parsing the file due to {e}")
