from enum import Enum

__all__ = ["TimeType"]

class TimeType(Enum):
    """
    Represents different types of time intervals for video frames in a player.

    When working with a video that has a frame rate of 24000/1001 fps and using the RoundingMethod.ROUND,
    the first 4 frames will start at the following times in a video player:
        - Frame 0: 0 ms
        - Frame 1: 42 ms
        - Frame 2: 83 ms
        - Frame 3: 125 ms

    The three possible time interval types are:

    1. EXACT:
       Corresponds to the precise frame time in the video player.
       Each frame has an interval: [Current_frame_time_ms, Next_frame_time_ms - 1]

       Example:
           - fps = 24000/1001
           - rounding_method = RoundingMethod.ROUND

           Frame intervals:
               - Frame 0: [0, 41] ms
               - Frame 1: [42, 82] ms
               - Frame 2: [83, 124] ms

    2. START:
       Corresponds to the start time of the subtitle.
       Each frame has an interval: [Previous_frame_time_ms + 1, Current_frame_time_ms]

       Example:
           - fps = 24000/1001
           - rounding_method = RoundingMethod.ROUND

           Frame intervals:
               - Frame 0: 0 ms
               - Frame 1: [1, 42] ms
               - Frame 2: [43, 83] ms

    3. END:
       Corresponds to the end time of the subtitle.
       Each frame has an interval: [Current_frame_time_ms + 1, Next_frame_time_ms]

       Example:
           - fps = 24000/1001
           - rounding_method = RoundingMethod.ROUND

           Frame intervals:
               - Frame 0: [1, 42] ms
               - Frame 1: [43, 83] ms
               - Frame 2: [84, 125] ms
    """

    START = "START"
    END = "END"
    EXACT = "EXACT"
