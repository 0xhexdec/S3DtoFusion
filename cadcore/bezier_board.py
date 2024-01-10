from typing import List

from cadcore.bezier_slice import BezierSlice

class BezierBoard():
    bezier_slices: List[BezierSlice]
    bezier_deck: BezierSlice
    bezier_bottom: BezierSlice
    bezier_outline: BezierSlice

    def __init__(self, bezier_slices: List[BezierSlice], bezier_deck: BezierSlice, 
                 bezier_bottom: BezierSlice, bezier_outline: BezierSlice):
        self.bezier_slices = bezier_slices
        self.bezier_deck = bezier_deck
        self.bezier_bottom = bezier_bottom
        self.bezier_outline = bezier_outline

    def get_nearest_slice_index(self, x: float):
        slice_positions = [s.position for s in self.bezier_slices]
        slice_distances = [abs(x - pos) for pos in slice_positions]
        min_dist = min(slice_distances)
        return slice_distances.index(min_dist)

    def get_deck_at_pos(self, pos: float):
        return self.bezier_deck.get_value_at(pos)

    def get_rocker_at_pos(self, pos: float):
        return self.bezier_bottom.get_value_at(pos)

    def get_thickness_at_pos(self, pos: float):
        return self.get_deck_at_pos(pos) - self.get_rocker_at_pos(pos)

    def get_width_at_pos(self, pos: float):
        return self.bezier_outline.get_value_at(pos) * 2

    def get_interpolated_slice(self, x: float):
        # Find nearest slices
        idx = self.get_nearest_slice_index(x)
        if self.bezier_slices[idx].position > x:
            idx -= 1
        next_idx = idx + 1

        slice1 = self.bezier_slices[idx]
        slice2 = self.bezier_slices[next_idx]

        # Calculate t
        t = (x - slice1.position) / (slice2.position - slice1.position)

        # Interpolate slice
        interpolated_slice = slice1.interpolate(slice2, t)

        # Calculate scale
        thickness = self.get_thickness_at_pos(x)

        if thickness < 0.5:
            thickness = 0.5

        width = self.get_width_at_pos(x)

        if width < 0.5:
            width = 0.5

        interpolated_slice = interpolated_slice.scale(thickness, width)
        interpolated_slice.position = x

        return interpolated_slice