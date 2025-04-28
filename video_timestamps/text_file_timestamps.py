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
    We only support the v1, v2 and v4 format.

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
        last_timestamps (Fraction): Time (in seconds) of the last frame of the video.
            Warning: The last_timestamps is not rounded, so it isn't really be last_timestamps.
        first_timestamps (Fraction): Time (in seconds) of the first frame of the video.
        timestamps (list[Fraction]): A list of timestamps (in seconds) corresponding to each frame, stored as `Fraction` for precision.
    """

    def __init__(
        self,
        path_to_timestamps_file_or_content: Union[str, Path],
        time_scale: Fraction,
        rounding_method: RoundingMethod,
        normalize: bool = True,
        fps: Optional[Fraction] = None,
    ):
        if isinstance(path_to_timestamps_file_or_content, Path):
            with open(path_to_timestamps_file_or_content, "r", encoding="utf-8") as f:
                timestamps, fps_from_file = TimestampsFileParser.parse_file(f)
        else:
            file = StringIO(path_to_timestamps_file_or_content)
            timestamps, fps_from_file = TimestampsFileParser.parse_file(file)

        if fps_from_file:
            if fps:
                warn(
                    "You have setted a fps, but the timestamps file also contain a fps. We will use the timestamps file fps.",
                    UserWarning,
                )
            fps = fps_from_file

        pts_list = [rounding_method(Fraction(time, pow(10, 3)) * time_scale) for time in timestamps]
        
        super().__init__(pts_list, time_scale, normalize, fps, rounding_method, Fraction(timestamps[-1], pow(10, 3)))
