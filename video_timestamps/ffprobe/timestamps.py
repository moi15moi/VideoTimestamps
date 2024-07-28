from .ffprobe import FFprobe
from ..timestamps import Timestamps
from ..abc_video_parser import ABCVideoParser
from ..rounding_method import RoundingMethod
from fractions import Fraction
from pathlib import Path
from typing import Tuple


class FFprobeTimestamps(ABCVideoParser):

    @staticmethod
    def is_available() -> bool:
        return FFprobe.is_ffprobe_installed()

    @staticmethod
    def get_timestamps(video_path: Path, index: int, normalize: bool, rounding_method: RoundingMethod) -> Tuple[Timestamps, Fraction]:
        timestamps_list, time_base, first_frame_time, last_frame_time = FFprobe.get_timestamps(video_path, index, rounding_method)

        fpms = Fraction(len(timestamps_list) - 1) / (last_frame_time - first_frame_time)

        timestamps = Timestamps(
            rounding_method=rounding_method,
            timestamps=timestamps_list,
            normalize=normalize,
            fpms=fpms,
            last_frame_time=last_frame_time,
        )

        return timestamps, time_base
