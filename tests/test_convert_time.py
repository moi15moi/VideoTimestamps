import pytest
from video_timestamps import RoundingMethod, TimestampsFactory, TimeType


def test_frames_to_ms_vfr() -> None:
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
    timestamps = TimestampsFactory.from_timestamps_file(timestamps_str)

    assert 0 == timestamps.frames_to_ms(0, TimeType.EXACT)
    assert 1000 == timestamps.frames_to_ms(1, TimeType.EXACT)
    assert 1500 == timestamps.frames_to_ms(2, TimeType.EXACT)
    assert 2000 == timestamps.frames_to_ms(3, TimeType.EXACT)
    assert 2001 == timestamps.frames_to_ms(4, TimeType.EXACT)
    assert 2002 == timestamps.frames_to_ms(5, TimeType.EXACT)
    assert 2003 == timestamps.frames_to_ms(6, TimeType.EXACT)

    assert 0 == timestamps.frames_to_ms(0, TimeType.START)
    assert 500 == timestamps.frames_to_ms(1, TimeType.START)  # answer must be ]0, 1000]
    assert 1250 == timestamps.frames_to_ms(2, TimeType.START)  # answer must be ]1000, 1500]
    assert 1750 == timestamps.frames_to_ms(3, TimeType.START)  # answer must be ]1500, 2000]
    assert 2001 == timestamps.frames_to_ms(4, TimeType.START)  # answer must be ]2000, 2001]
    assert 2002 == timestamps.frames_to_ms(5, TimeType.START)  # answer must be ]2001, 2002]
    assert 2003 == timestamps.frames_to_ms(6, TimeType.START)  # answer must be ]2002, 2003]

    assert 500 == timestamps.frames_to_ms(0, TimeType.END)  # answer must be ]0, 1000]
    assert 1250 == timestamps.frames_to_ms(1, TimeType.END)  # answer must be ]1000, 1500]
    assert 1750 == timestamps.frames_to_ms(2, TimeType.END)  # answer must be ]1500, 2000]
    assert 2001 == timestamps.frames_to_ms(3, TimeType.END)  # answer must be ]2000, 2001]
    assert 2002 == timestamps.frames_to_ms(4, TimeType.END)  # answer must be ]2001, 2002]
    assert 2003 == timestamps.frames_to_ms(5, TimeType.END)  # answer must be ]2002, 2003]


def test_frames_to_ms_invalid_frame() -> None:
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
    timestamps = TimestampsFactory.from_timestamps_file(timestamps_str)

    with pytest.raises(ValueError) as exc_info:
        timestamps.frames_to_ms(-1, TimeType.EXACT)
    assert str(exc_info.value) == "You cannot specify a frame under 0."

    with pytest.raises(ValueError) as exc_info:
        timestamps.frames_to_ms(-1, TimeType.START)
    assert str(exc_info.value) == "You cannot specify a frame under 0."

    with pytest.raises(ValueError) as exc_info:
        timestamps.frames_to_ms(-1, TimeType.END)
    assert str(exc_info.value) == "You cannot specify a frame under 0."


def test_frames_to_ms_approximate() -> None:
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
    timestamps = TimestampsFactory.from_timestamps_file(timestamps_str)

    # fpms = 6/2003
    # round(1/fpms * 7) = round(2336.83) = 2337
    assert 2337 == timestamps.frames_to_ms(7, TimeType.EXACT)

    # 2003 + (2337 - 2003) // 2 = 2170
    assert 2170 == timestamps.frames_to_ms(7, TimeType.START)

    # fpms = 6/2003
    # round(1/fpms * 8) = round(2670.67) = 2671
    # 2337 + (2671 - 2337) // 2 = 2504
    assert 2504 == timestamps.frames_to_ms(7, TimeType.END)


def test_frames_to_ms_round() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 30\n" "5,10,15\n"

    timestamps = TimestampsFactory.from_timestamps_file(timestamps_str)

    # Frame 0 to 5 - 30 fps
    assert 0 == timestamps.frames_to_ms(0, TimeType.EXACT)
    assert 33 == timestamps.frames_to_ms(1, TimeType.EXACT)
    assert 67 == timestamps.frames_to_ms(2, TimeType.EXACT)
    assert 100 == timestamps.frames_to_ms(3, TimeType.EXACT)
    assert 133 == timestamps.frames_to_ms(4, TimeType.EXACT)
    assert 167 == timestamps.frames_to_ms(5, TimeType.EXACT)
    # Frame 6 to 11 - 15 fps
    assert 233 == timestamps.frames_to_ms(6, TimeType.EXACT)
    assert 300 == timestamps.frames_to_ms(7, TimeType.EXACT)
    assert 367 == timestamps.frames_to_ms(8, TimeType.EXACT)
    assert 433 == timestamps.frames_to_ms(9, TimeType.EXACT)
    assert 500 == timestamps.frames_to_ms(10, TimeType.EXACT)
    assert 567 == timestamps.frames_to_ms(11, TimeType.EXACT)
    # From here, we guess the ms from the last frame timestamps and fps
    # The last frame is equal to (5 * 1/30 * 1000 + 6 * 1/15 * 1000) = 1700/3 = 566.666
    assert 600 == timestamps.frames_to_ms(12, TimeType.EXACT)  # 1700/3 + 1/30 * 1000 = 600
    assert 633 == timestamps.frames_to_ms(13, TimeType.EXACT)  # 1700/3 + 2/30 * 1000 = round(633.33) = 633
    assert 667 == timestamps.frames_to_ms(14, TimeType.EXACT)  # 1700/3 + 3/30 * 1000 = round(666.66) = 667


def test_frames_to_ms_floor() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 30\n" "5,10,15\n"

    timestamps = TimestampsFactory.from_timestamps_file(
        timestamps_str, rounding_method=RoundingMethod.FLOOR
    )

    # Frame 0 to 5 - 30 fps
    assert 0 == timestamps.frames_to_ms(0, TimeType.EXACT)
    assert 33 == timestamps.frames_to_ms(1, TimeType.EXACT)
    assert 66 == timestamps.frames_to_ms(2, TimeType.EXACT)
    assert 100 == timestamps.frames_to_ms(3, TimeType.EXACT)
    assert 133 == timestamps.frames_to_ms(4, TimeType.EXACT)
    assert 166 == timestamps.frames_to_ms(5, TimeType.EXACT)
    # Frame 6 to 11 - 15 fps
    assert 233 == timestamps.frames_to_ms(6, TimeType.EXACT)
    assert 300 == timestamps.frames_to_ms(7, TimeType.EXACT)
    assert 366 == timestamps.frames_to_ms(8, TimeType.EXACT)
    assert 433 == timestamps.frames_to_ms(9, TimeType.EXACT)
    assert 500 == timestamps.frames_to_ms(10, TimeType.EXACT)
    assert 566 == timestamps.frames_to_ms(11, TimeType.EXACT)
    # From here, we guess the ms from the last frame timestamps and fps
    # The last frame is equal to (5 * 1/30 * 1000 + 6 * 1/15 * 1000) = 1700/3 = 566.666
    assert 600 == timestamps.frames_to_ms(12, TimeType.EXACT)  # 1700/3 + 1/30 * 1000 = 600
    assert 633 == timestamps.frames_to_ms(13, TimeType.EXACT)  # 1700/3 + 2/30 * 1000 = floor(633.33) = 633
    assert 666 == timestamps.frames_to_ms(14, TimeType.EXACT)  # 1700/3 + 3/30 * 1000 = floor(666.66) = 666


def test_ms_to_frames_vfr() -> None:
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
    timestamps = TimestampsFactory.from_timestamps_file(timestamps_str)

    assert 0 == timestamps.ms_to_frames(0, TimeType.EXACT)
    assert 0 == timestamps.ms_to_frames(999, TimeType.EXACT)
    assert 1 == timestamps.ms_to_frames(1000, TimeType.EXACT)
    assert 1 == timestamps.ms_to_frames(1499, TimeType.EXACT)
    assert 2 == timestamps.ms_to_frames(1500, TimeType.EXACT)
    assert 2 == timestamps.ms_to_frames(1999, TimeType.EXACT)
    assert 3 == timestamps.ms_to_frames(2000, TimeType.EXACT)
    assert 4 == timestamps.ms_to_frames(2001, TimeType.EXACT)
    assert 5 == timestamps.ms_to_frames(2002, TimeType.EXACT)
    assert 6 == timestamps.ms_to_frames(2003, TimeType.EXACT)
    assert 6 == timestamps.ms_to_frames(2004, TimeType.EXACT)

    assert 0 == timestamps.ms_to_frames(0, TimeType.START)
    assert 1 == timestamps.ms_to_frames(1, TimeType.START)
    assert 1 == timestamps.ms_to_frames(1000, TimeType.START)
    assert 2 == timestamps.ms_to_frames(1001, TimeType.START)
    assert 2 == timestamps.ms_to_frames(1500, TimeType.START)
    assert 3 == timestamps.ms_to_frames(1501, TimeType.START)
    assert 3 == timestamps.ms_to_frames(2000, TimeType.START)
    assert 4 == timestamps.ms_to_frames(2001, TimeType.START)
    assert 5 == timestamps.ms_to_frames(2002, TimeType.START)
    assert 6 == timestamps.ms_to_frames(2003, TimeType.START)
    assert 7 == timestamps.ms_to_frames(2004, TimeType.START)

    with pytest.raises(ValueError) as exc_info:
        timestamps.ms_to_frames(0, TimeType.END)
    assert str(exc_info.value) == "You cannot specify a time equals to the first timestamps 0 with the TimeType.END."
    assert 0 == timestamps.ms_to_frames(1, TimeType.END)
    assert 1 == timestamps.ms_to_frames(1500, TimeType.END)
    assert 2 == timestamps.ms_to_frames(1501, TimeType.END)
    assert 2 == timestamps.ms_to_frames(2000, TimeType.END)
    assert 3 == timestamps.ms_to_frames(2001, TimeType.END)
    assert 4 == timestamps.ms_to_frames(2002, TimeType.END)
    assert 5 == timestamps.ms_to_frames(2003, TimeType.END)
    assert 6 == timestamps.ms_to_frames(2004, TimeType.END)


def test_ms_to_frames_invalid_frame() -> None:
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
    timestamps = TimestampsFactory.from_timestamps_file(timestamps_str)

    with pytest.raises(ValueError) as exc_info:
        timestamps.ms_to_frames(-1, TimeType.EXACT)
    assert str(exc_info.value) == "You cannot specify a time under the first timestamps: 0."

    with pytest.raises(ValueError) as exc_info:
        timestamps.ms_to_frames(-1, TimeType.START)
    assert str(exc_info.value) == "You cannot specify a time under the first timestamps: 0."

    with pytest.raises(ValueError) as exc_info:
        timestamps.ms_to_frames(-1, TimeType.END)
    assert str(exc_info.value) == "You cannot specify a time under the first timestamps: 0."


def test_ms_to_frames_approximate() -> None:
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
    timestamps = TimestampsFactory.from_timestamps_file(timestamps_str)

    # fpms = 6/2003
    # round(1/fpms * 7) = round(2336.83) = 2337
    assert 6 == timestamps.ms_to_frames(2336, TimeType.EXACT)
    assert 7 == timestamps.ms_to_frames(2337, TimeType.EXACT)

    # 2003 + (2337 - 2003) // 2 = 2170
    assert 7 == timestamps.ms_to_frames(2170, TimeType.START)

    # fpms = 6/2003
    # round(1/fpms * 8) = round(2670.67) = 2671
    # 2337 + (2671 - 2337) // 2 = 2504
    assert 7 == timestamps.ms_to_frames(2504, TimeType.END)


def test_ms_to_frames_round() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 30\n" "5,10,15\n"

    timestamps = TimestampsFactory.from_timestamps_file(timestamps_str)

    # Frame 0 to 5 - 30 fps
    assert 0 == timestamps.ms_to_frames(0, TimeType.EXACT)
    assert 0 == timestamps.ms_to_frames(32, TimeType.EXACT)
    assert 1 == timestamps.ms_to_frames(33, TimeType.EXACT)
    assert 1 == timestamps.ms_to_frames(66, TimeType.EXACT)
    assert 2 == timestamps.ms_to_frames(67, TimeType.EXACT)
    assert 2 == timestamps.ms_to_frames(99, TimeType.EXACT)
    assert 3 == timestamps.ms_to_frames(100, TimeType.EXACT)
    assert 3 == timestamps.ms_to_frames(132, TimeType.EXACT)
    assert 4 == timestamps.ms_to_frames(133, TimeType.EXACT)
    assert 4 == timestamps.ms_to_frames(166, TimeType.EXACT)
    assert 5 == timestamps.ms_to_frames(167, TimeType.EXACT)
    assert 5 == timestamps.ms_to_frames(232, TimeType.EXACT)
    # Frame 6 to 11 - 15 fps
    assert 6 == timestamps.ms_to_frames(233, TimeType.EXACT)
    assert 6 == timestamps.ms_to_frames(299, TimeType.EXACT)
    assert 7 == timestamps.ms_to_frames(300, TimeType.EXACT)
    assert 7 == timestamps.ms_to_frames(366, TimeType.EXACT)
    assert 8 == timestamps.ms_to_frames(367, TimeType.EXACT)
    assert 8 == timestamps.ms_to_frames(432, TimeType.EXACT)
    assert 9 == timestamps.ms_to_frames(433, TimeType.EXACT)
    assert 9 == timestamps.ms_to_frames(499, TimeType.EXACT)
    assert 10 == timestamps.ms_to_frames(500, TimeType.EXACT)
    assert 10 == timestamps.ms_to_frames(566, TimeType.EXACT)
    assert 11 == timestamps.ms_to_frames(567, TimeType.EXACT)
    # From here, we guess the ms from the last frame timestamps and fps
    # The last frame is equal to (5 * 1/30 * 1000 + 6 * 1/15 * 1000) = 1700/3 = 566.666
    assert 11 == timestamps.ms_to_frames(599, TimeType.EXACT)
    assert 12 == timestamps.ms_to_frames(600, TimeType.EXACT)  # 1700/3 + 1/30 * 1000 = 600
    assert 12 == timestamps.ms_to_frames(632, TimeType.EXACT) 
    assert 13 == timestamps.ms_to_frames(633, TimeType.EXACT)  # 1700/3 + 2/30 * 1000 = round(633.33) = 633
    assert 13 == timestamps.ms_to_frames(666, TimeType.EXACT)
    assert 14 == timestamps.ms_to_frames(667, TimeType.EXACT)  # 1700/3 + 3/30 * 1000 = round(666.66) = 667

    # 16 fps is a "special" fps, because the frame 2 has a exact value
    # - Frame 0: 0 ms
    # - Frame 1: 62.5 ms
    # - Frame 2: 125 ms
    # - Frame 3: 187.5 ms
    timestamps = TimestampsFactory.from_fps(16)
    assert 0 == timestamps.ms_to_frames(62, TimeType.EXACT)
    assert 1 == timestamps.ms_to_frames(63, TimeType.EXACT)
    assert 1 == timestamps.ms_to_frames(124, TimeType.EXACT)
    assert 2 == timestamps.ms_to_frames(125, TimeType.EXACT)
    assert 2 == timestamps.ms_to_frames(187, TimeType.EXACT)
    assert 3 == timestamps.ms_to_frames(188, TimeType.EXACT)


def test_ms_to_frames_floor() -> None:
    timestamps_str = "# timecode format v1\n" "Assume 30\n" "5,10,15\n"

    timestamps = TimestampsFactory.from_timestamps_file(
        timestamps_str, rounding_method=RoundingMethod.FLOOR
    )

    # Frame 0 to 5 - 30 fps
    assert 0 == timestamps.ms_to_frames(0, TimeType.EXACT)
    assert 0 == timestamps.ms_to_frames(32, TimeType.EXACT)
    assert 1 == timestamps.ms_to_frames(33, TimeType.EXACT)
    assert 1 == timestamps.ms_to_frames(65, TimeType.EXACT)
    assert 2 == timestamps.ms_to_frames(66, TimeType.EXACT)
    assert 2 == timestamps.ms_to_frames(99, TimeType.EXACT)
    assert 3 == timestamps.ms_to_frames(100, TimeType.EXACT)
    assert 3 == timestamps.ms_to_frames(132, TimeType.EXACT)
    assert 4 == timestamps.ms_to_frames(133, TimeType.EXACT)
    assert 4 == timestamps.ms_to_frames(165, TimeType.EXACT)
    assert 5 == timestamps.ms_to_frames(166, TimeType.EXACT)
    assert 5 == timestamps.ms_to_frames(232, TimeType.EXACT)
    # Frame 6 to 11 - 15 fps
    assert 6 == timestamps.ms_to_frames(233, TimeType.EXACT)
    assert 6 == timestamps.ms_to_frames(299, TimeType.EXACT)
    assert 7 == timestamps.ms_to_frames(300, TimeType.EXACT)
    assert 7 == timestamps.ms_to_frames(365, TimeType.EXACT)
    assert 8 == timestamps.ms_to_frames(366, TimeType.EXACT)
    assert 8 == timestamps.ms_to_frames(432, TimeType.EXACT)
    assert 9 == timestamps.ms_to_frames(433, TimeType.EXACT)
    assert 9 == timestamps.ms_to_frames(499, TimeType.EXACT)
    assert 10 == timestamps.ms_to_frames(500, TimeType.EXACT)
    assert 10 == timestamps.ms_to_frames(565, TimeType.EXACT)
    assert 11 == timestamps.ms_to_frames(566, TimeType.EXACT)
    # From here, we guess the ms from the last frame timestamps and fps
    # The last frame is equal to (5 * 1/30 * 1000 + 6 * 1/15 * 1000) = 1700/3 = 566.666
    assert 11 == timestamps.ms_to_frames(599, TimeType.EXACT)
    assert 12 == timestamps.ms_to_frames(600, TimeType.EXACT)  # 1700/3 + 1/30 * 1000 = 600
    assert 12 == timestamps.ms_to_frames(632, TimeType.EXACT)
    assert 13 == timestamps.ms_to_frames(633, TimeType.EXACT)  # 1700/3 + 2/30 * 1000 = floor(633.33) = 633
    assert 13 == timestamps.ms_to_frames(665, TimeType.EXACT) 
    assert 14 == timestamps.ms_to_frames(666, TimeType.EXACT)  # 1700/3 + 3/30 * 1000 = floor(666.66) = 666

    # 15 fps is a "special" fps, because the frame 3 has a exact value
    # - Frame 0: 0 ms
    # - Frame 1: ~66.66 ms
    # - Frame 2: ~133.33 ms
    # - Frame 3: 200 ms
    timestamps = TimestampsFactory.from_fps(15, rounding_method=RoundingMethod.FLOOR)
    assert 0 == timestamps.ms_to_frames(65, TimeType.EXACT)
    assert 1 == timestamps.ms_to_frames(66, TimeType.EXACT)
    assert 1 == timestamps.ms_to_frames(132, TimeType.EXACT)
    assert 2 == timestamps.ms_to_frames(133, TimeType.EXACT)
    assert 2 == timestamps.ms_to_frames(199, TimeType.EXACT)
    assert 3 == timestamps.ms_to_frames(200, TimeType.EXACT)