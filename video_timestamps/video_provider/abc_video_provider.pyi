from __future__ import annotations
from fractions import Fraction

__all__ = ['ABCVideoProvider']

class ABCVideoProvider:
    def get_pts(self, filename: str, index: int) -> tuple[list[int], Fraction, Fraction]:
        """
        Parameters:
            video_path (str): A video path.
            index (int): Index of the video stream.
        Returns:
            A tuple containing these 3 informations:
                1. A list of each pts sorted.
                2. The time_base.
                3. The fps.
        """
        ...
