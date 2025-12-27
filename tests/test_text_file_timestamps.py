import os
from fractions import Fraction
from pathlib import Path

import pytest

from video_timestamps import RoundingMethod, TextFileTimestamps, TimeType

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))


def test_frame_to_time_3_frames_before_23976_fps_v1() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 23.976\n" "0,2,12.5\n"
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method)

    assert timestamps.fps == Fraction("23.976")

    # Frame 0 to 3 - 12.5 fps
    assert timestamps.frame_to_time(0, TimeType.EXACT) == Fraction(0)
    assert timestamps.frame_to_time(1, TimeType.EXACT) == Fraction(80, 1000)
    assert timestamps.frame_to_time(2, TimeType.EXACT) == Fraction(160, 1000)
    assert timestamps.frame_to_time(3, TimeType.EXACT) == Fraction(240, 1000)
    # From here, we guess the ms from the last frame timestamps and fps
    assert timestamps.frame_to_time(4, TimeType.EXACT) == Fraction(282, 1000)
    assert timestamps.frame_to_time(5, TimeType.EXACT) == Fraction(323, 1000)
    assert timestamps.frame_to_time(6, TimeType.EXACT) == Fraction(365, 1000)
    assert timestamps.frame_to_time(7, TimeType.EXACT) == Fraction(407, 1000)
    assert timestamps.frame_to_time(8, TimeType.EXACT) == Fraction(449, 1000)
    assert timestamps.frame_to_time(9, TimeType.EXACT) == Fraction(490, 1000)
    assert timestamps.frame_to_time(10, TimeType.EXACT) == Fraction(532, 1000)
    assert timestamps.frame_to_time(11, TimeType.EXACT) == Fraction(574, 1000)


def test_time_to_frame_3_frames_before_23976_fps_v1() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 23.976\n" "0,2,12.5\n"
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method)

    # Frame 0 to 3 - 12.5 fps
    # precision
    assert timestamps.time_to_frame(Fraction(0), TimeType.EXACT) == 0
    assert timestamps.time_to_frame(Fraction(80, 1000), TimeType.EXACT) == 1
    assert timestamps.time_to_frame(Fraction(160, 1000), TimeType.EXACT) == 2
    assert timestamps.time_to_frame(Fraction(240, 1000), TimeType.EXACT) == 3
    # milliseconds
    assert timestamps.time_to_frame(0, TimeType.EXACT, 3) == 0
    assert timestamps.time_to_frame(79, TimeType.EXACT, 3) == 0
    assert timestamps.time_to_frame(80, TimeType.EXACT, 3) == 1
    assert timestamps.time_to_frame(159, TimeType.EXACT, 3) == 1
    assert timestamps.time_to_frame(160, TimeType.EXACT, 3) == 2
    assert timestamps.time_to_frame(239, TimeType.EXACT, 3) == 2
    assert timestamps.time_to_frame(240, TimeType.EXACT, 3) == 3
    assert timestamps.time_to_frame(281, TimeType.EXACT, 3) == 3
    # From here, we guess the ms from the last frame timestamps and fps
    assert timestamps.time_to_frame(Fraction(282, 1000), TimeType.EXACT) == 4
    assert timestamps.time_to_frame(Fraction(323, 1000), TimeType.EXACT) == 5
    assert timestamps.time_to_frame(Fraction(365, 1000), TimeType.EXACT) == 6
    assert timestamps.time_to_frame(Fraction(407, 1000), TimeType.EXACT) == 7
    assert timestamps.time_to_frame(Fraction(449, 1000), TimeType.EXACT) == 8
    assert timestamps.time_to_frame(Fraction(490, 1000), TimeType.EXACT) == 9
    assert timestamps.time_to_frame(Fraction(532, 1000), TimeType.EXACT) == 10
    assert timestamps.time_to_frame(Fraction(574, 1000), TimeType.EXACT) == 11
    assert timestamps.time_to_frame(282, TimeType.EXACT, 3) == 4
    assert timestamps.time_to_frame(322, TimeType.EXACT, 3) == 4
    assert timestamps.time_to_frame(323, TimeType.EXACT, 3) == 5
    assert timestamps.time_to_frame(364, TimeType.EXACT, 3) == 5
    assert timestamps.time_to_frame(365, TimeType.EXACT, 3) == 6
    assert timestamps.time_to_frame(406, TimeType.EXACT, 3) == 6
    assert timestamps.time_to_frame(407, TimeType.EXACT, 3) == 7
    assert timestamps.time_to_frame(448, TimeType.EXACT, 3) == 7
    assert timestamps.time_to_frame(449, TimeType.EXACT, 3) == 8
    assert timestamps.time_to_frame(489, TimeType.EXACT, 3) == 8
    assert timestamps.time_to_frame(490, TimeType.EXACT, 3) == 9
    assert timestamps.time_to_frame(531, TimeType.EXACT, 3) == 9
    assert timestamps.time_to_frame(532, TimeType.EXACT, 3) == 10


def test_frame_to_time_2_frames_before_23976_fps_v1() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 23.976\n" "0,1,12.5\n"
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method)

    assert timestamps.fps == Fraction("23.976")

    # Frame 0 to 2 - 12.5 fps
    assert timestamps.frame_to_time(0, TimeType.EXACT) == Fraction(0)
    assert timestamps.frame_to_time(1, TimeType.EXACT) == Fraction(80, 1000)
    assert timestamps.frame_to_time(2, TimeType.EXACT) == Fraction(160, 1000)
    # From here, we guess the ms from the last frame timestamps and fps
    assert timestamps.frame_to_time(3, TimeType.EXACT) == Fraction(202, 1000)
    assert timestamps.frame_to_time(4, TimeType.EXACT) == Fraction(243, 1000)
    assert timestamps.frame_to_time(5, TimeType.EXACT) == Fraction(285, 1000)
    assert timestamps.frame_to_time(6, TimeType.EXACT) == Fraction(327, 1000)
    assert timestamps.frame_to_time(7, TimeType.EXACT) == Fraction(369, 1000)
    assert timestamps.frame_to_time(8, TimeType.EXACT) == Fraction(410, 1000)
    assert timestamps.frame_to_time(9, TimeType.EXACT) == Fraction(452, 1000)
    assert timestamps.frame_to_time(10, TimeType.EXACT) == Fraction(494, 1000)
    assert timestamps.frame_to_time(11, TimeType.EXACT) == Fraction(535, 1000)


def test_time_to_frame_2_frames_before_23976_fps_v1() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 23.976\n" "0,1,12.5\n"
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method)

    # Frame 0 to 2 - 12.5 fps
    # precision
    assert timestamps.time_to_frame(Fraction(0), TimeType.EXACT) == 0
    assert timestamps.time_to_frame(Fraction(80, 1000), TimeType.EXACT) == 1
    assert timestamps.time_to_frame(Fraction(160, 1000), TimeType.EXACT) == 2
    # milliseconds
    assert timestamps.time_to_frame(0, TimeType.EXACT, 3) == 0
    assert timestamps.time_to_frame(79, TimeType.EXACT, 3) == 0
    assert timestamps.time_to_frame(80, TimeType.EXACT, 3) == 1
    assert timestamps.time_to_frame(159, TimeType.EXACT, 3) == 1
    assert timestamps.time_to_frame(160, TimeType.EXACT, 3) == 2
    # From here, we guess the ms from the last frame timestamps and fps
    assert timestamps.time_to_frame(Fraction(202, 1000), TimeType.EXACT) == 3
    assert timestamps.time_to_frame(Fraction(243, 1000), TimeType.EXACT) == 4
    assert timestamps.time_to_frame(Fraction(285, 1000), TimeType.EXACT) == 5
    assert timestamps.time_to_frame(Fraction(327, 1000), TimeType.EXACT) == 6
    assert timestamps.time_to_frame(Fraction(369, 1000), TimeType.EXACT) == 7
    assert timestamps.time_to_frame(Fraction(410, 1000), TimeType.EXACT) == 8
    assert timestamps.time_to_frame(Fraction(452, 1000), TimeType.EXACT) == 9
    assert timestamps.time_to_frame(201, TimeType.EXACT, 3) == 2
    assert timestamps.time_to_frame(202, TimeType.EXACT, 3) == 3
    assert timestamps.time_to_frame(242, TimeType.EXACT, 3) == 3
    assert timestamps.time_to_frame(243, TimeType.EXACT, 3) == 4
    assert timestamps.time_to_frame(284, TimeType.EXACT, 3) == 4
    assert timestamps.time_to_frame(285, TimeType.EXACT, 3) == 5
    assert timestamps.time_to_frame(326, TimeType.EXACT, 3) == 5
    assert timestamps.time_to_frame(327, TimeType.EXACT, 3) == 6
    assert timestamps.time_to_frame(368, TimeType.EXACT, 3) == 6
    assert timestamps.time_to_frame(369, TimeType.EXACT, 3) == 7


def test_frame_to_time_v1() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 30\n" "5,10,15\n"
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method)

    assert timestamps._video_timestamps.pts_list == [0, 33, 67, 100, 133, 167, 233, 300, 367, 433, 500, 567]
    assert timestamps.fps == Fraction(30)

    # Frame 0 to 5 - 30 fps
    assert timestamps.frame_to_time(0, TimeType.EXACT) == Fraction(0)
    assert timestamps.frame_to_time(1, TimeType.EXACT) == Fraction(33, 1000)
    assert timestamps.frame_to_time(2, TimeType.EXACT) == Fraction(67, 1000)
    assert timestamps.frame_to_time(3, TimeType.EXACT) == Fraction(100, 1000)
    assert timestamps.frame_to_time(4, TimeType.EXACT) == Fraction(133, 1000)
    assert timestamps.frame_to_time(5, TimeType.EXACT) == Fraction(167, 1000)
    # Frame 6 to 11 - 15 fps
    assert timestamps.frame_to_time(6, TimeType.EXACT) == Fraction(233, 1000)
    assert timestamps.frame_to_time(7, TimeType.EXACT) == Fraction(300, 1000)
    assert timestamps.frame_to_time(8, TimeType.EXACT) == Fraction(367, 1000)
    assert timestamps.frame_to_time(9, TimeType.EXACT) == Fraction(433, 1000)
    assert timestamps.frame_to_time(10, TimeType.EXACT) == Fraction(500, 1000)
    assert timestamps.frame_to_time(11, TimeType.EXACT) == Fraction(567, 1000)
    # From here, we guess the ms from the last frame timestamps and fps
    # The last frame is equal to (5 * 1/30 * 1000 + 6 * 1/15 * 1000) = 1700/3 = 566.666.
    assert timestamps.frame_to_time(12, TimeType.EXACT) == Fraction(600, 1000) # 1700/3 + 1/30 * 1000 = 600
    assert timestamps.frame_to_time(13, TimeType.EXACT) == Fraction(633, 1000) # 1700/3 + 2/30 * 1000 = round(633.33) = 633
    assert timestamps.frame_to_time(14, TimeType.EXACT) == Fraction(667, 1000) # 1700/3 + 3/30 * 1000 = round(666.66) = 667
    assert timestamps.frame_to_time(15, TimeType.EXACT) == Fraction(700, 1000) # 1700/3 + 4/30 * 1000 = 700
    assert timestamps.frame_to_time(16, TimeType.EXACT) == Fraction(733, 1000) # 1700/3 + 5/30 * 1000 = round(733.33) = 733

    # Small test for center_time
    assert timestamps.frame_to_time(10, TimeType.END, center_time=True) == Fraction(5335, 10000)
    assert timestamps.frame_to_time(11, TimeType.END, center_time=True) == Fraction(5835, 10000)
    assert timestamps.frame_to_time(12, TimeType.END, center_time=True) == Fraction(6165, 10000)


def test_time_to_frame_round_v1() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 30\n" "5,10,15\n"
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method)

    # Frame 0 to 5 - 30 fps
    # precision
    assert timestamps.time_to_frame(Fraction(0), TimeType.EXACT) == 0
    assert timestamps.time_to_frame(Fraction(33, 1000), TimeType.EXACT) == 1
    assert timestamps.time_to_frame(Fraction(67, 1000), TimeType.EXACT) == 2
    assert timestamps.time_to_frame(Fraction(100, 1000), TimeType.EXACT) == 3
    assert timestamps.time_to_frame(Fraction(133, 1000), TimeType.EXACT) == 4
    assert timestamps.time_to_frame(Fraction(167, 1000), TimeType.EXACT) == 5
    # milliseconds
    assert timestamps.time_to_frame(0, TimeType.EXACT, 3) == 0
    assert timestamps.time_to_frame(32, TimeType.EXACT, 3) == 0
    assert timestamps.time_to_frame(33, TimeType.EXACT, 3) == 1
    assert timestamps.time_to_frame(66, TimeType.EXACT, 3) == 1
    assert timestamps.time_to_frame(67, TimeType.EXACT, 3) == 2
    assert timestamps.time_to_frame(99, TimeType.EXACT, 3) == 2
    assert timestamps.time_to_frame(100, TimeType.EXACT, 3) == 3
    assert timestamps.time_to_frame(132, TimeType.EXACT, 3) == 3
    assert timestamps.time_to_frame(133, TimeType.EXACT, 3) == 4
    assert timestamps.time_to_frame(166, TimeType.EXACT, 3) == 4
    assert timestamps.time_to_frame(167, TimeType.EXACT, 3) == 5
    assert timestamps.time_to_frame(232, TimeType.EXACT, 3) == 5
    # Frame 6 to 11 - 15 fps
    # precision
    assert timestamps.time_to_frame(Fraction(233, 1000), TimeType.EXACT) == 6
    assert timestamps.time_to_frame(Fraction(300, 1000), TimeType.EXACT) == 7
    assert timestamps.time_to_frame(Fraction(367, 1000), TimeType.EXACT) == 8
    assert timestamps.time_to_frame(Fraction(433, 1000), TimeType.EXACT) == 9
    assert timestamps.time_to_frame(Fraction(500, 1000), TimeType.EXACT) == 10
    assert timestamps.time_to_frame(Fraction(567, 1000), TimeType.EXACT) == 11
    # milliseconds
    assert timestamps.time_to_frame(233, TimeType.EXACT, 3) == 6
    assert timestamps.time_to_frame(299, TimeType.EXACT, 3) == 6
    assert timestamps.time_to_frame(300, TimeType.EXACT, 3) == 7
    assert timestamps.time_to_frame(366, TimeType.EXACT, 3) == 7
    assert timestamps.time_to_frame(367, TimeType.EXACT, 3) == 8
    assert timestamps.time_to_frame(432, TimeType.EXACT, 3) == 8
    assert timestamps.time_to_frame(433, TimeType.EXACT, 3) == 9
    assert timestamps.time_to_frame(499, TimeType.EXACT, 3) == 9
    assert timestamps.time_to_frame(500, TimeType.EXACT, 3) == 10
    assert timestamps.time_to_frame(566, TimeType.EXACT, 3) == 10
    assert timestamps.time_to_frame(567, TimeType.EXACT, 3) == 11
    # From here, we guess the ms from the last frame timestamps and fps
    # The last frame is equal to (5 * 1/30 * 1000 + 6 * 1/15 * 1000) = 1700/3 = 566.666
    assert timestamps.time_to_frame(Fraction(600, 1000), TimeType.EXACT) == 12
    assert timestamps.time_to_frame(Fraction(633, 1000), TimeType.EXACT) == 13
    assert timestamps.time_to_frame(Fraction(667, 1000), TimeType.EXACT) == 14
    assert timestamps.time_to_frame(Fraction(700, 1000), TimeType.EXACT) == 15
    assert timestamps.time_to_frame(Fraction(733, 1000), TimeType.EXACT) == 16
    assert timestamps.time_to_frame(599, TimeType.EXACT, 3) == 11
    assert timestamps.time_to_frame(600, TimeType.EXACT, 3) == 12 # 1700/3 + 1/30 * 1000 = 600
    assert timestamps.time_to_frame(632, TimeType.EXACT, 3) == 12
    assert timestamps.time_to_frame(633, TimeType.EXACT, 3) == 13 # 1700/3 + 2/30 * 1000 = round(633.33) = 633
    assert timestamps.time_to_frame(666, TimeType.EXACT, 3) == 13
    assert timestamps.time_to_frame(667, TimeType.EXACT, 3) == 14 # 1700/3 + 3/30 * 1000 = round(666.66) = 667
    assert timestamps.time_to_frame(699, TimeType.EXACT, 3) == 14
    assert timestamps.time_to_frame(700, TimeType.EXACT, 3) == 15 # 1700/3 + 4/30 * 1000 = round(666.66) = 667
    assert timestamps.time_to_frame(732, TimeType.EXACT, 3) == 15
    assert timestamps.time_to_frame(733, TimeType.EXACT, 3) == 16 # 1700/3 + 4/30 * 1000 = round(666.66) = 667


def test_init_v1() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 30\n" "5,10,15\n" "13,16,40\n"
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method)

    assert timestamps.time_scale == Fraction(1000)
    assert timestamps.rounding_method == RoundingMethod.ROUND
    assert timestamps.fps == Fraction(30)
    assert timestamps._video_timestamps.pts_list == [0, 33, 67, 100, 133, 167, 233, 300, 367, 433, 500, 567, 600, 633, 658, 683, 708, 733]
    # 7 * 1/30 + 6 * 1/15 + 4 * 1/40 = 11/15
    assert timestamps._fps_timestamps is not None
    assert timestamps._fps_timestamps.first_timestamps == Fraction(11, 15)
    assert timestamps.version == 1

    with pytest.raises(ValueError) as exc_info:
        timestamps.nbr_frames
    assert str(exc_info.value) == "V1 timestamps file doesn't specify a number of frames."


def test_init_v2() -> None:
    timestamps_str = (
        "# timecode format v2\n"
        "0\n"
        "1000\n"
        "1500\n"
        "2000\n"
        "2001\n"
        "2002\n"
        "2003\n"
    )
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method)

    assert timestamps.time_scale == Fraction(1000)
    assert timestamps.rounding_method == RoundingMethod.ROUND
    assert timestamps.fps == Fraction(6, Fraction(2003, 1000))
    assert timestamps._video_timestamps.pts_list == [0, 1000, 1500, 2000, 2001, 2002, 2003]
    assert timestamps.version == 2

    assert timestamps.nbr_frames == 6


def test_empty_line_v2() -> None:
    timestamps_str = (
        "# timecode format v2\n"
        "\n"
        "1000\n"
        "1500\n"
        "2000\n"
    )
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method, normalize=False)

    assert timestamps._video_timestamps.pts_list == [1000, 1500, 2000]


def test_single_carriage_return_v2() -> None:
    timestamps_str = (
        "# timecode format v2\r\n"
        "3\r"
        "4\r\n"
        "10\r\n"
        "20\r\n"
    )
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method, normalize=False)

    assert timestamps._video_timestamps.pts_list == [3, 4, 10, 20]

def test_frame_to_time_over_video_duration_v2() -> None:
    timestamps_str = (
        "# timecode format v2\n"
        "\n"
        "1000\n"
        "1500\n"
        "2000\n"
    )
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method)

    with pytest.raises(ValueError) as exc_info:
        timestamps.frame_to_time(3, TimeType.EXACT)
    assert str(exc_info.value) == "The frame 3 is over the video duration. The video contains 2 frames."


def test_time_to_frame_over_video_duration_v2() -> None:
    timestamps_str = (
        "# timecode format v2\n"
        "\n"
        "1000\n"
        "1500\n"
        "2000\n"
    )
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method, normalize=False)

    with pytest.raises(ValueError) as exc_info:
        timestamps.time_to_frame(2001, TimeType.EXACT, 3)
    assert str(exc_info.value) == "Time 2001/1000 is over the video duration. The video duration is 2 seconds."


test_time_to_frame_over_video_duration_v2()
def test_init_from_file() -> None:
    timestamp_file_path = dir_path.joinpath("files", "timestamps.txt")
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamp_file_path, time_scale, rounding_method)

    assert timestamps.time_scale == Fraction(1000)
    assert timestamps.fps == Fraction(2, Fraction(100, 1000))
    assert timestamps._video_timestamps.pts_list == [0, 50, 100]


def test__eq__and__hash__() -> None:
    timestamps_str = (
        "# timecode format v2\n"
        "0\n"
        "1000\n"
        "1500\n"
        "2000\n"
        "2001\n"
        "2002\n"
        "2003\n"
    )
    timestamps_1 = TextFileTimestamps(timestamps_str, Fraction(1000), RoundingMethod.ROUND, True)
    timestamps_2 = TextFileTimestamps(timestamps_str, Fraction(1000), RoundingMethod.ROUND, True)
    assert timestamps_1 == timestamps_2
    assert hash(timestamps_1) == hash(timestamps_2)

    timestamps_3_str = (
        "# timecode format v2\n"
        "0\n"
        "1000\n"
        "1500\n"
    )
    timestamps_3 = TextFileTimestamps(
        timestamps_3_str, # different
        Fraction(1000),
        RoundingMethod.ROUND,
        True,
    )
    assert timestamps_1 != timestamps_3
    assert hash(timestamps_1) != hash(timestamps_3)

    timestamps_4 = TextFileTimestamps(
        timestamps_str,
        Fraction(1001), # different
        RoundingMethod.ROUND,
        True,
    )
    assert timestamps_1 != timestamps_4
    assert hash(timestamps_1) != hash(timestamps_4)

    timestamps_5 = TextFileTimestamps(
        timestamps_str,
        Fraction(1000),
        RoundingMethod.FLOOR, # different
        True,
    )
    assert timestamps_1 != timestamps_5
    assert hash(timestamps_1) != hash(timestamps_5)
