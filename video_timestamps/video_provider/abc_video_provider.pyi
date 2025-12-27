from __future__ import annotations

from fractions import Fraction

__all__ = ['ABCVideoProvider']

class ABCVideoProvider:
    def get_pts(self, filename: str, index: int) -> tuple[list[int], Fraction, Fraction]:
        """
        Parameters:
            filename: A video path.
            index: Index of the video stream.

        Returns:
            A tuple containing these 3 informations:

                1. A list of each frame's pts. The last pts correspond to the pts of the last frame + it's duration.
                2. The time_base.
                3. The fps.
        """
        ...
