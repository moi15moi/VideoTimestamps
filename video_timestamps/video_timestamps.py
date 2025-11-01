from __future__ import annotations
from .abc_timestamps import ABCTimestamps
from .fps_timestamps import FPSTimestamps
from .rounding_method import RoundingMethod
from .time_type import TimeType
from .video_provider import ABCVideoProvider, FFMS2VideoProvider
from bisect import bisect_left, bisect_right
from fractions import Fraction
from pathlib import Path
from typing import Optional

__all__ = ["VideoTimestamps"]

class VideoTimestamps(ABCTimestamps):
    """Create a Timestamps object from a video file.
    """

    def __init__(
        self,
        pts_list: list[int],
        time_scale: Fraction,
        normalize: bool = True,
        fps: Optional[Fraction] = None,
        rounding_method: Optional[RoundingMethod] = None,
        last_timestamps: Optional[Fraction] = None
    ):
        """Initialize the VideoTimestamps object.

        Parameters:
            pts_list: A list containing the Presentation Time Stamps (PTS) for all frames.

                The last pts correspond to the pts of the last frame + it's duration. 
            time_scale: Unit of time (in seconds) in terms of which frame timestamps are represented.

                Important: Don't confuse time_scale with the time_base. As a reminder, time_base = 1 / time_scale.
            normalize: If True, it will shift the PTS to make them start from 0. If false, the option does nothing.
            fps: The frames per second of the video.

                If None, the fps will be approximate from the first and last PTS.

                It will be used to approximate the timestamps over the video duration.
            rounding_method: The rounding method used to round/floor the PTS (Presentation Time Stamp).
                
                If None, it will try to guess it from the PTS and fps. Note that this is only reliable with CFR video.

                It will be used to approximate the timestamps over the video duration.
            last_timestamps: If not provided, this value defaults to last_pts/timescale,
                where last_pts is the final presentation timestamp in pts_list.
                Users should specify last_timestamps when they need precise results while requesting a frame or timestamp over the video duration (a.k.a over the last pts of ``pts_list``).
                By default, since last_timestamps is derived from last_pts/timescale, rounding errors occur due to the inherent rounding of last_pts.
                For constant frame rate (CFR) videos, you can set last_timestamps to (len(pts_list) - 1) / fps for more accurate timing.
        """
        # Validate the PTS
        if len(pts_list) <= 1:
            raise ValueError("There must be at least 2 pts.")

        if any(pts_list[i] >= pts_list[i + 1] for i in range(len(pts_list) - 1)):
            raise ValueError("PTS must be in non-decreasing order.")

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

        if last_timestamps is None:
            self.__last_timestamps = self.timestamps[-1]
        else:
            self.__last_timestamps = last_timestamps
        self.__fps_timestamps = FPSTimestamps(self.rounding_method, self.time_scale, self.fps, self.last_timestamps)


    @classmethod
    def from_video_file(
        cls,
        video_path: Path,
        index: int = 0,
        normalize: bool = True,
        rounding_method: Optional[RoundingMethod] = None,
        use_video_provider_to_guess_fps: bool = True,
        last_timestamps: Optional[Fraction] = None,
        video_provider: ABCVideoProvider = FFMS2VideoProvider()
    ) -> VideoTimestamps:
        """Create timestamps based on the ``video_path`` provided.

        Parameters:
            video_path: A video path.
            index: Index of the video stream.
            normalize: If True, it will shift the PTS to make them start from 0. If false, the option does nothing.
            rounding_method: The rounding method used to round/floor the PTS (Presentation Time Stamp).
                
                If None, it will try to guess it from the PTS and fps. Note that this is only reliable with CFR video.

                It will be used to approximate the timestamps over the video duration.
            use_video_provider_to_guess_fps: If True, use the video_provider to guess the video fps.
                If not specified, the fps will be approximate from the first and last frame PTS.
            last_timestamps: If not provided, this value defaults to last_pts/timescale,
                where last_pts is the final presentation timestamp in pts_list.
                Users should specify last_timestamps when they need precise results while requesting a frame or timestamp over the video duration (a.k.a over the last pts of ``pts_list``).
                For constant frame rate (CFR) videos, you can set last_timestamps to (len(pts_list) - 1) / fps for more accurate timing.
            video_provider: The video provider to use to get the information about the video timestamps/fps.
                
        Returns:
            An VideoTimestamps instance representing the video file.
        """

        if not video_path.is_file():
            raise FileNotFoundError(f'Invalid path for the video file: "{video_path}"')

        pts_list, time_base, fps_from_video_provider = video_provider.get_pts(str(video_path.resolve()), index)
        time_scale = 1 / time_base

        if use_video_provider_to_guess_fps:
            fps = fps_from_video_provider
        else:
            fps = None

        timestamps = VideoTimestamps(
            pts_list,
            time_scale,
            normalize,
            fps,
            rounding_method,
            last_timestamps
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
    def first_timestamps(self) -> Fraction:
        return self.timestamps[0]

    @property
    def pts_list(self) -> list[int]:
        """
        Returns:
            A list containing the Presentation Time Stamps (PTS) for all frames.
                The last pts correspond to the pts of the last frame + it's duration. 
        """
        return self.__pts_list

    @property
    def timestamps(self) -> list[Fraction]:
        """
        Returns:
            A list of timestamps (in seconds) corresponding to each frame, stored as `Fraction` for precision.
        """
        return self.__timestamps

    @property
    def last_timestamps(self) -> Fraction:
        """
        Returns:
            Time (in seconds) of the last frame of the video.
        """
        return self.__last_timestamps
    
    @property
    def nbr_frames(self) -> int:
        """
        Returns:
            Number of frames in the video.
        """
        return len(self.__pts_list) - 1

    @staticmethod
    def normalize(pts_list: list[int]) -> list[int]:
        """Shift the pts_list to make them start from 0. This way, frame 0 will start at pts 0.

        Parameters:
            pts_list: A list containing the Presentation Time Stamps (PTS) for all frames.

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
        If it fails to guess the [`RoundingMethod`][video_timestamps.rounding_method.RoundingMethod], it will return [`RoundingMethod.FLOOR`][video_timestamps.rounding_method.RoundingMethod.FLOOR], since it is the most common.

        Parameters:
            pts_list: A list containing the Presentation Time Stamps (PTS) for all frames.
            time_scale: Unit of time (in seconds) in terms of which frame timestamps are represented.
                Important: Don't confuse time_scale with the time_base. As a reminder, time_base = 1 / time_scale.
            fps: The frames per second of the video.

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
            return len(self.timestamps) - 1 + self.__fps_timestamps.time_to_frame(time, time_type, None)

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
                return self.__fps_timestamps.frame_to_time(requested_frame - len(self.timestamps) + 1, TimeType.EXACT, None, False)
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
        return (self.rounding_method, self.fps, self.time_scale, self.first_timestamps, self.pts_list, self.timestamps, self.last_timestamps) == (
            other.rounding_method, other.fps, other.time_scale, other.first_timestamps, other.pts_list, other.timestamps, other.last_timestamps
        )


    def __hash__(self) -> int:
        return hash(
            (
                self.rounding_method,
                self.fps,
                self.time_scale,
                self.first_timestamps,
                tuple(self.pts_list),
                tuple(self.timestamps),
                self.last_timestamps
            )
        )
