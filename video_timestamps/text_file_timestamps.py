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
    """

    def __init__(
        self,
        path_to_timestamps_file_or_content: Union[str, Path],
        time_scale: Fraction,
        rounding_method: RoundingMethod,
        normalize: bool = True,
        fps: Optional[Fraction] = None,
    ):
        """Initialize the VideoTimestamps object.

        Parameters:
            path_to_timestamps_file_or_content (Union[str, Path]): If is it a Path, the path to the timestamps file.

                If it is a str, a timestamps file content.
            time_scale (Fraction): Unit of time (in seconds) in terms of which frame timestamps are represented.

                Important: Don't confuse time_scale with the time_base. As a reminder, time_base = 1 / time_scale.
            rounding_method (RoundingMethod): The rounding method used to round/floor the PTS (Presentation Time Stamp).
            normalize (bool): If True, it will shift the PTS to make them start from 0. If false, the option does nothing.
            fps (Optional[RoundingMethod]): The frames per second of the video. Only used with V2 and V4 timestamps file.

                If None, the fps will be approximate from the first and last PTS.

                It will be used to approximate the timestamps over the video duration.
        """

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
