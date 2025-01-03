from __future__ import annotations
from .abc_timestamps import ABCTimestamps
from .fps_timestamps import FPSTimestamps
from .rounding_method import RoundingMethod
from .time_type import TimeType
from .ffprobe.ffprobe import FFprobe
from bisect import bisect_left, bisect_right
from fractions import Fraction
from pathlib import Path
from typing import Optional

__all__ = ["VideoTimestamps"]

class VideoTimestamps(ABCTimestamps):
    """Create a Timestamps object from a video file.

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
        pts_list: list[int],
        time_scale: Fraction,
        normalize: bool = True,
        fps: Optional[Fraction] = None,
        rounding_method: Optional[RoundingMethod] = None,
        approximate_pts_from_last_pts: bool = False,
    ):
        # Validate the timestamps
        if len(pts_list) <= 1:
            raise ValueError("There must be at least 2 timestamps.")

        if any(pts_list[i] >= pts_list[i + 1] for i in range(len(pts_list) - 1)):
            raise ValueError("Timestamps must be in non-decreasing order.")

        self.__pts_list = pts_list
        self.__time_scale = time_scale

        if normalize:
            self.__pts_list = VideoTimestamps.normalize(self.pts_list)

        self.__timestamps = [pts / self.time_scale for pts in self.pts_list]

        if fps is None:
            self.__fps = Fraction(len(pts_list) - 1, Fraction((self.pts_list[-1] - self.pts_list[0]), self.time_scale))
        else:
            self.__fps = fps

        if rounding_method is None:
            self.__rounding_method = VideoTimestamps.guess_rounding_method(self.pts_list, self.time_scale, self.fps)
        else:
            self.__rounding_method = rounding_method

        self.__approximate_pts_from_last_pts = approximate_pts_from_last_pts
        if self.approximate_pts_from_last_pts:
            self.__fps_timestamps = FPSTimestamps(self.rounding_method, self.time_scale, self.fps, self.pts_list[-1])
        else:
            self.__fps_timestamps = FPSTimestamps(self.rounding_method, self.time_scale, self.fps, self.first_pts)


    @classmethod
    def from_video_file(
        cls,
        video_path: Path,
        index: int = 0,
        normalize: bool = True,
        rounding_method: Optional[RoundingMethod] = None,
        approximate_pts_from_last_pts: bool = False,
        use_ffprobe_to_guess_fps: bool = True,
    ) -> VideoTimestamps:
        """Create timestamps based on the ``video_path`` provided.

        Note:
            This method requires the ``ffprobe`` programs to be available.

        Parameters:
            video_path (Path): A video path.
            index (int): Index of the video stream.
            normalize (bool): If True, it will shift the PTS to make them start from 0. If false, the option does nothing.
            rounding_method (RoundingMethod): The rounding method used to round/floor the PTS (Presentation Time Stamp).
                It will be used to approximate the timestamps after the video duration.
                Note: If None, it will try to guess it from the PTS and fps.
            approximate_pts_from_last_pts (bool): If True, use the last pts to guess pts over the video duration.
                If False, use the first pts.
                In general, you want this parameter to be False to have the best precision.
                You only want it true when the video is VFR.
            use_ffprobe_to_guess_fps (bool): If True, use ffprobe to guess the video fps.
                If False, the fps will be approximate from the first and last frame PTS.

        Returns:
            An VideoTimestamps instance representing the video file.
        """

        if not video_path.is_file():
            raise FileNotFoundError(f'Invalid path for the video file: "{video_path}"')

        if not FFprobe.is_ffprobe_installed():
            raise OSError("FFprobe isn't in your environment variable.")

        pts_list, time_base = FFprobe.get_pts(video_path, index)
        time_scale = 1 / time_base

        fps = None
        if use_ffprobe_to_guess_fps:
            fps = FFprobe.get_fps(video_path, index)

        timestamps = VideoTimestamps(
            pts_list,
            time_scale,
            normalize,
            fps,
            rounding_method,
            approximate_pts_from_last_pts
        )
        return timestamps


    @property
    def rounding_method(self) -> RoundingMethod:
        return self.__rounding_method

    @property
    def fps(self) -> Fraction:
        return self.__fps

    @property
    def time_scale(self) -> Fraction:
        return self.__time_scale

    @property
    def first_pts(self) -> int:
        return self.pts_list[0]

    @property
    def first_timestamps(self) -> Fraction:
        return self.timestamps[0]

    @property
    def pts_list(self) -> list[int]:
        return self.__pts_list

    @property
    def timestamps(self) -> list[Fraction]:
        return self.__timestamps

    @property
    def approximate_pts_from_last_pts(self) -> bool:
        return self.__approximate_pts_from_last_pts

    @staticmethod
    def normalize(pts_list: list[int]) -> list[int]:
        """Shift the pts_list to make them start from 0. This way, frame 0 will start at pts 0.

        Parameters:
            pts_list (list[int]): A list containing the Presentation Time Stamps (PTS) for all frames.

        Returns:
            The pts_list normalized.
        """
        if pts_list[0]:
            return list(map(lambda pts: pts - pts_list[0], pts_list))
        return pts_list

    @staticmethod
    def guess_rounding_method(pts_list: list[int], time_scale: Fraction, fps: Fraction) -> RoundingMethod:
        """Guess the rounding method that have been used to generate the PTS.
        It only works with Constant Frame Rate (CFR) videos.
        If it fails to guess the RoundingMethod, it will return RoundingMethod.FLOOR, since it is the most common.

        Parameters:
            pts_list (list[int]): A list containing the Presentation Time Stamps (PTS) for all frames.
            time_scale (Fraction): Unit of time (in seconds) in terms of which frame timestamps are represented.
                Important: Don't confuse time_scale with the time_base. As a reminder, time_base = 1 / time_scale.
            fps (Fraction): The frames per second of the video.

        Returns:
            The guessed rounding method.
        """

        # Try to guess the RoundingMethod that have been used to generate the PTS
        # It only work with CFR videos.

        # We can skip the frame 0, since the time for the floor and round will always be the same
        frame = 1

        # By default, we fallback to RoundingMethod.FLOOR
        # Even if the guess isn't good, it is doesn't really mather because the rounding_method is only used
        # when the user requested a time/frame over the video duration.
        rounding_method = RoundingMethod.FLOOR
        while True:
            pts = frame * time_scale / fps + pts_list[0] * time_scale
            pts_floor = RoundingMethod.FLOOR(pts)
            pts_round = RoundingMethod.ROUND(pts)

            if pts_list[frame] == pts_floor and pts_list[frame] != pts_round:
                rounding_method = RoundingMethod.FLOOR
                break
            elif pts_list[frame] == pts_round and pts_list[frame] != pts_floor:
                rounding_method = RoundingMethod.ROUND
                break

            frame += 1

            if frame > len(pts_list) - 1:
                break
            elif frame == 20:
                break

        return rounding_method


    def _time_to_frame(
        self,
        time: Fraction,
        time_type: TimeType,
    ) -> int:

        if time > self.timestamps[-1]:
            if self.approximate_pts_from_last_pts:
                return len(self.timestamps) - 1 + self.__fps_timestamps.time_to_frame(time, time_type, None)
            else:
                return self.__fps_timestamps.time_to_frame(time, time_type, None)

        if time_type == TimeType.START:
            return bisect_left(self.timestamps, time)
        elif time_type == TimeType.END:
            return bisect_left(self.timestamps, time) - 1
        elif time_type == TimeType.EXACT:
            return bisect_right(self.timestamps, time) - 1
        else:
            raise ValueError(f'The TimeType "{time_type}" isn\'t supported.')


    def _frame_to_time(
        self,
        frame: int,
        time_type: TimeType,
        center_time: bool,
    ) -> Fraction:

        def get_time_at_frame(requested_frame: int) -> Fraction:
            if requested_frame > len(self.timestamps) - 1:
                if self.approximate_pts_from_last_pts:
                    return self.__fps_timestamps.frame_to_time(requested_frame - len(self.timestamps) + 1, TimeType.EXACT, None, False)
                else:
                    return self.__fps_timestamps.frame_to_time(requested_frame, TimeType.EXACT, None, False)
            else:
                return self.timestamps[requested_frame]

        if time_type == TimeType.START:
            if frame == 0:
                return self.timestamps[0]

            upper_bound = get_time_at_frame(frame)

            if center_time:
                lower_bound = get_time_at_frame(frame-1)
                time = (lower_bound + upper_bound) / 2
            else:
                time = upper_bound

        elif time_type == TimeType.END:
            upper_bound = get_time_at_frame(frame+1)

            if center_time:
                lower_bound = get_time_at_frame(frame)
                time = (lower_bound + upper_bound) / 2
            else:
                time = upper_bound

        elif time_type == TimeType.EXACT:
            time = get_time_at_frame(frame)

        else:
            raise ValueError(f'The TimeType "{time_type}" isn\'t supported.')

        return time


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VideoTimestamps):
            return False
        return (self.rounding_method, self.fps, self.time_scale, self.first_pts, self.first_timestamps, self.pts_list, self.timestamps, self.approximate_pts_from_last_pts) == (
            other.rounding_method, other.fps, other.time_scale, other.first_pts, other.first_timestamps, other.pts_list, other.timestamps, other.approximate_pts_from_last_pts
        )


    def __hash__(self) -> int:
        return hash(
            (
                self.rounding_method,
                self.fps,
                self.time_scale,
                self.first_pts,
                self.first_timestamps,
                tuple(self.pts_list),
                tuple(self.timestamps),
                self.approximate_pts_from_last_pts,
            )
        )
