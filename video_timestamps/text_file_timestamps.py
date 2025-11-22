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

        The `time_scale` and `rounding_method` are required because, in reality, if you provide a timestamps file to `mkvmerge`, it can round the result.
        For example, let's say we use this timestamps file with this command `mkvmerge --output output.mkv --timestamps 0:input_timestamps_file.txt input.mkv`
        ``` 
        # timestamp format v2
        0
        50.5
        100.4
        150.8
        200.9
        250
        ```

        Since mkvmerge set a default `timescale` of 1000 and use the `rounding_method` [`RoundingMethod.ROUND`][video_timestamps.rounding_method.RoundingMethod.ROUND],
        it cannot properly represent the provided timestamps.
        If you extract the timestamps with `mkvextract output.mkv timestamps_v2 0:final_timestamps_file.txt`, you will get this result:                
        ```
        # timestamp format v2
        0
        51
        100
        151
        201
        250
        ```

        Parameters:
            path_to_timestamps_file_or_content: If is it a Path, the path to the timestamps file.

                If it is a str, a timestamps file content.
            time_scale: Unit of time (in seconds) in terms of which frame timestamps are represented.

                Important: Don't confuse time_scale with the time_base. As a reminder, time_base = 1 / time_scale.
            rounding_method: The rounding method used to round/floor the PTS (Presentation Time Stamp).
            normalize: If True, it will shift the PTS to make them start from 0. If false, the option does nothing.
            fps: The frames per second of the video. Only used with V2 and V4 timestamps file.

                If None, the fps will be approximate from the first and last PTS.

                It will be used to approximate the timestamps over the video duration.
        """

        if isinstance(path_to_timestamps_file_or_content, Path):
            with open(path_to_timestamps_file_or_content, "r", encoding="utf-8") as f:
                timestamps, fps_from_file, version = TimestampsFileParser.parse_file(f)
        else:
            file = StringIO(path_to_timestamps_file_or_content)
            timestamps, fps_from_file, version = TimestampsFileParser.parse_file(file)

        if fps_from_file:
            if fps:
                warn(
                    "You have setted a fps, but the timestamps file also contain a fps. We will use the timestamps file fps.",
                    UserWarning,
                )
            fps = fps_from_file

        pts_list = [rounding_method(Fraction(time, pow(10, 3)) * time_scale) for time in timestamps]
        
        super().__init__(pts_list, time_scale, normalize, fps, rounding_method, Fraction(timestamps[-1], pow(10, 3)))

        self.__version = version

    @property
    def version(self) -> int:
        """
        Returns:
            The version of the timestamps file (1, 2 or 4).
        """
        return self.__version

    @property
    def nbr_frames(self) -> int:
        """
        Returns:
            The number of frames of the timestamps file. Note that you cannot use this property with v1 timestamps file.
        """
        if self.version in (2, 4):
            return super().nbr_frames
        else:
            raise ValueError("V1 timestamps file doesn't specify a number of frames.")
