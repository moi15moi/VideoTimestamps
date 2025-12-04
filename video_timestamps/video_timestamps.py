from __future__ import annotations
from .abc_timestamps import ABCTimestamps
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
    ):
        """Initialize the VideoTimestamps object.

        Parameters:
            pts_list: A list containing the Presentation Time Stamps (PTS) for all frames.

                The last pts correspond to the pts of the last frame + it's duration. 
            time_scale: Unit of time (in seconds) in terms of which frame timestamps are represented.

                Important: Don't confuse time_scale with the time_base. As a reminder, time_base = 1 / time_scale.
            normalize: If True, it will shift the PTS to make them start from 0. If false, the option does nothing.
            fps: The frames per second of the video.

                It doesn't matter if you pass this parameter because the fps isn't used.
                It is only a parameter to avoid breaking change
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

    @classmethod
    def from_video_file(
        cls,
        video_path: Path,
        index: int = 0,
        normalize: bool = True,
        use_video_provider_to_guess_fps: bool = True,
        video_provider: ABCVideoProvider = FFMS2VideoProvider()
    ) -> VideoTimestamps:
        """Create timestamps based on the ``video_path`` provided.

        Parameters:
            video_path: A video path.
            index: Index of the video stream.
            normalize: If True, it will shift the PTS to make them start from 0. If false, the option does nothing.
            use_video_provider_to_guess_fps: If True, use the video_provider to guess the video fps.
                If not specified, the fps will be approximate from the first and last frame PTS.
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
            fps
        )
        return timestamps

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


    def _time_to_frame(
        self,
        time: Fraction,
        time_type: TimeType,
    ) -> int:
        if time > self.timestamps[-1]:
            if time_type == TimeType.END:
                return self.nbr_frames
            else:
                raise ValueError(f"Time {time} is over the video duration. The video duration is {self.timestamps[-1]} seconds.")

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
    ) -> Fraction:
        if frame > self.nbr_frames:
            raise ValueError(f"The frame {frame} is over the video duration. The video contains {self.nbr_frames} frames.")

        return self.timestamps[frame]


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VideoTimestamps):
            return False
        return (self.fps, self.time_scale, self.first_timestamps, self.pts_list, self.timestamps) == (
            other.fps, other.time_scale, other.first_timestamps, other.pts_list, other.timestamps
        )


    def __hash__(self) -> int:
        return hash(
            (
                self.fps,
                self.time_scale,
                self.first_timestamps,
                tuple(self.pts_list),
                tuple(self.timestamps),
            )
        )
