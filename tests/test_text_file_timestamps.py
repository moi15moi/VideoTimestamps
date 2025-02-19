import os
from fractions import Fraction
from pathlib import Path
from video_timestamps import RoundingMethod, TextFileTimestamps, TimeType

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))


def test_frame_to_time_v1() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 30\n" "5,10,15\n"
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method)

    assert timestamps.pts_list == [0, 33, 67, 100, 133, 167, 233, 300, 367, 433, 500, 567]
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
    assert timestamps.time_to_frame(599, TimeType.EXACT, 3) == 11
    assert timestamps.time_to_frame(600, TimeType.EXACT, 3) == 12 # 1700/3 + 1/30 * 1000 = 600
    assert timestamps.time_to_frame(632, TimeType.EXACT, 3) == 12
    assert timestamps.time_to_frame(633, TimeType.EXACT, 3) == 13 # 1700/3 + 2/30 * 1000 = round(633.33) = 633
    assert timestamps.time_to_frame(666, TimeType.EXACT, 3) == 13
    assert timestamps.time_to_frame(667, TimeType.EXACT, 3) == 14 # 1700/3 + 3/30 * 1000 = round(666.66) = 667


def test_init_v1() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 30\n" "5,10,15\n" "13,16,40\n"
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamps_str, time_scale, rounding_method)

    assert timestamps.time_scale == Fraction(1000)
    assert timestamps.rounding_method == RoundingMethod.ROUND
    assert timestamps.fps == Fraction(30)
    assert timestamps.pts_list == [0, 33, 67, 100, 133, 167, 233, 300, 367, 433, 500, 567, 600, 633, 658, 683, 708, 733]
    # 7 * 1/30 + 6 * 1/15 + 4 * 1/40 = 11/15
    assert timestamps.last_timestamps == Fraction(11, 15)


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
    assert timestamps.pts_list == [0, 1000, 1500, 2000, 2001, 2002, 2003]


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

    assert timestamps.pts_list == [1000, 1500, 2000]


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

    assert timestamps.pts_list == [3, 4, 10, 20]


def test_init_from_file() -> None:
    timestamp_file_path = dir_path.joinpath("files", "timestamps.txt")
    time_scale = Fraction(1000)
    rounding_method = RoundingMethod.ROUND

    timestamps = TextFileTimestamps(timestamp_file_path, time_scale, rounding_method)

    assert timestamps.time_scale == Fraction(1000)
    assert timestamps.rounding_method == RoundingMethod.ROUND
    assert timestamps.fps == Fraction(2, Fraction(100, 1000))
    assert timestamps.pts_list == [0, 50, 100]


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
    timestamps_1 = TextFileTimestamps(timestamps_str, Fraction(1000), RoundingMethod.ROUND, True, None)
    timestamps_2 = TextFileTimestamps(timestamps_str, Fraction(1000), RoundingMethod.ROUND, True, None)
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
        None,
    )
    assert timestamps_1 != timestamps_3
    assert hash(timestamps_1) != hash(timestamps_3)

    timestamps_4 = TextFileTimestamps(
        timestamps_str,
        Fraction(1001), # different
        RoundingMethod.ROUND,
        True,
        None,
    )
    assert timestamps_1 != timestamps_4
    assert hash(timestamps_1) != hash(timestamps_4)

    timestamps_5 = TextFileTimestamps(
        timestamps_str,
        Fraction(1000),
        RoundingMethod.FLOOR, # different
        True,
        None,
    )
    assert timestamps_1 != timestamps_5
    assert hash(timestamps_1) != hash(timestamps_5)

    timestamps_6 = TextFileTimestamps(
        timestamps_str,
        Fraction(1000),
        RoundingMethod.ROUND,
        True,
        Fraction(1), # different
    )
    assert timestamps_1 != timestamps_6
    assert hash(timestamps_1) != hash(timestamps_6)
