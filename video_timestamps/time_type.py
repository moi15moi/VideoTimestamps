from enum import Enum

__all__ = ["TimeType"]

class TimeType(Enum):
    """
    Represents different types of time intervals for video frames in a player.

    When working with a video that has a frame rate of 24000/1001 fps, using the RoundingMethod.ROUND and with the Timescale 1000,
    the first 4 frames will start at the following times in a video player:
        - Frame 0: 0 ms
        - Frame 1: 42 ms
        - Frame 2: 83 ms
        - Frame 3: 125 ms

    The three possible time interval types are:

    1. EXACT:
       Corresponds to the precise frame time in the video player.
       Each frame has an interval: [Current_frame_time, Next_frame_time[

       Example:
           - fps = 24000/1001
           - rounding_method = RoundingMethod.ROUND
           - time_scale = 1000

           Frame intervals:
               - Frame 0: [0, 42[ ms
               - Frame 1: [42, 83[ ms
               - Frame 2: [83, 125[ ms

    2. START:
       Corresponds to the start time of the subtitle.
       Each frame has an interval: ]Previous_frame_time, Current_frame_time]

       Example:
           - fps = 24000/1001
           - rounding_method = RoundingMethod.ROUND
           - time_scale = 1000

           Frame intervals:
               - Frame 0: 0 ms
               - Frame 1: ]0, 42] ms
               - Frame 2: ]42, 83] ms

    3. END:
       Corresponds to the end time of the subtitle.
       Each frame has an interval: ]Current_frame_time, Next_frame_time]

       Example:
           - fps = 24000/1001
           - rounding_method = RoundingMethod.ROUND
           - time_scale = 1000

           Frame intervals:
               - Frame 0: ]0, 42] ms
               - Frame 1: ]42, 83] ms
               - Frame 2: ]83, 125] ms
    """

    START = "START"
    END = "END"
    EXACT = "EXACT"
