from fractions import Fraction
from .rounding_method import RoundingMethod
from .timestamps import Timestamps
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple


class ABCVideoParser(ABC):

    @staticmethod
    @abstractmethod
    def is_available() -> bool:
        """
        Returns:
            If the video parser is available.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_timestamps(video_path: Path, index: int, normalize: bool, rounding_method: RoundingMethod) -> Tuple[Timestamps, Fraction]:
        """Create timestamps based on the ``video_path`` provided.

        Parameters:
            video_path (Path): A video path.
            index (int): Index of the video stream.
            normalize (bool): If True, it will shift the timestamps to make them start from 0. If false, the option does nothing.
            rounding_method (RoundingMethod): A rounding method. See the comment in Timestamps class about FLOOR vs ROUND.
        Returns:
            A tuple containing a Timestamps instance and the time_base of the video.
        """
        pass
