from typing import Tuple

from ..s3dModel.board import Board


class LoftHandler():
    board: Board
    
    def __init__(self, board: Board) -> None:
        self.board = board
    
    def findPairs(self):
        # for top in self.board.curveDefTops.values():
        #     for side in self.board.curveDefSides.values():
        #         if top.bezier3d.name == side.bezier3d.name:
        #             tp = top.bezier3d.controlPoints.points
        #             sp = side.bezier3d.controlPoints.points
        #             if tp[1].x != 0.0 and tp[1].y != 0.0 and sp[1].x != 0.0 and sp[1].y != 0.0:
        pass
