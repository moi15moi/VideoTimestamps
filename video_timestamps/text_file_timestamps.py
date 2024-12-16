from .rounding_method import RoundingMethod
from .timestamps_file_parser import TimestampsFileParser
from .video_timestamps import VideoTimestamps
from fractions import Fraction
from io import StringIO
from pathlib import Path
from typing import Optional, Union
from warnings import warn

__all__ = ["TextFileTimestamps"]

class TextFileTimestamps(VideoTimestamps):
    """Create a Timestamps object from a mkv [timestamps file](https://mkvtoolnix.download/doc/mkvmerge.html#mkvmerge.external_timestamp_files).
    We only support the v2 and v4 format.

    See `ABCTimestamps` for more details.

    Attributes:
        pts_list (list[int]): A list containing the Presentation Time Stamps (PTS) for all frames.
        time_scale (Fraction): Unit of time (in seconds) in terms of which frame timestamps are represented.
            Important: Don't confuse time_scale with the time_base. As a reminder, time_base = 1 / time_scale.
        normalize (bool): If True, it will shift the PTS to make them start from 0. If false, the option does nothing.
        fps (Fraction): The frames per second of the video.
            If not specified, the fps will be approximate from the first and last frame PTS.
        rounding_method (RoundingMethod): The rounding method used to round/floor the PTS (Presentation Time Stamp).
            It will be used to approximate the timestamps after the video duration.
            Note: If None, it will try to guess it from the PTS and fps.
        approximate_pts_from_last_pts (bool): If True, use the last pts to guess pts over the video duration.
            If False, use the first pts.
            In general, you want this parameter to be False to have the best precision.
            You only want it true when the video is VFR.
        first_pts (int): PTS (Presentation Time Stamp) of the first frame of the video.
        first_timestamps (int): Time (in seconds) of the first frame of the video.
        timestamps (list[Fraction]): A list of timestamps (in seconds) corresponding to each frame, stored as `Fraction` for precision.
    """

    def __init__(
        self,
        path_to_timestamps_file_or_content: Union[str, Path],
        time_scale: Fraction,
        rounding_method: RoundingMethod,
        normalize: bool = True,
        fps: Optional[Fraction] = None,
        approximate_pts_from_last_pts: bool = False,
    ):
        if isinstance(path_to_timestamps_file_or_content, Path):
            with open(path_to_timestamps_file_or_content, "r", encoding="utf-8") as f:
                timestamps = TimestampsFileParser.parse_file(f)
        else:
            f = StringIO(path_to_timestamps_file_or_content)
            timestamps = TimestampsFileParser.parse_file(f)

        pts_list = [rounding_method(Fraction(time, pow(10, 3)) * time_scale) for time in timestamps]

        super().__init__(pts_list, time_scale, normalize, fps, rounding_method, approximate_pts_from_last_pts)
