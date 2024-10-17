import pytest
from fractions import Fraction
from video_timestamps import RoundingMethod, TimeType, FPSTimestamps


def test_frame_to_time_invalid_frame() -> None:
    rounding_method = RoundingMethod.ROUND
    timescale = Fraction(24000)
    fps = Fraction(24000, 1001)
    timestamp = FPSTimestamps(rounding_method, timescale, fps)

    with pytest.raises(ValueError) as exc_info:
        timestamp.frame_to_time(-1, TimeType.EXACT)
    assert str(exc_info.value) == "You cannot specify a frame under 0."

    with pytest.raises(ValueError) as exc_info:
        timestamp.frame_to_time(-1, TimeType.START)
    assert str(exc_info.value) == "You cannot specify a frame under 0."

    with pytest.raises(ValueError) as exc_info:
        timestamp.frame_to_time(-1, TimeType.END)
    assert str(exc_info.value) == "You cannot specify a frame under 0."


def test_frame_to_time_invalid_output_unit() -> None:
    rounding_method = RoundingMethod.ROUND
    timescale = Fraction(24000)
    fps = Fraction(24000, 1001)
    timestamp = FPSTimestamps(rounding_method, timescale, fps)

    with pytest.raises(ValueError) as exc_info:
        timestamp.frame_to_time(0, TimeType.EXACT, -1)
    assert str(exc_info.value) == "The output_unit needs to be above or equal to 0."


def test_time_to_frame_invalid_input_unit() -> None:
    rounding_method = RoundingMethod.ROUND
    timescale = Fraction(24000)
    fps = Fraction(24000, 1001)
    timestamp = FPSTimestamps(rounding_method, timescale, fps)

    with pytest.raises(ValueError) as exc_info:
        timestamp.time_to_frame(10, TimeType.EXACT)
    assert str(exc_info.value) == "If input_unit is none, the time needs to be a Fraction."

    with pytest.raises(ValueError) as exc_info:
        timestamp.time_to_frame(Fraction(10), TimeType.START, 9)
    assert str(exc_info.value) == "If you specify a input_unit, the time needs to be a int."


def test_frame_to_time_round() -> None:
    rounding_method = RoundingMethod.ROUND
    timescale = Fraction(24000)
    fps = Fraction(24000, 1001)
    timestamp = FPSTimestamps(rounding_method, timescale, fps)

    # Frame 0 - PTS = 0    - TIME = 0 ns
    # Frame 1 - PTS = 1001 - TIME = 41708333.3... ns
    # Frame 2 - PTS = 2002 - TIME = 83416666.6... ns
    # Frame 3 - PTS = 3003 - TIME = 125125000 ns
    # Frame 4 - PTS = 4004 - TIME = 166833333.3 ns

    # Frame 0: 0 ns
    # Frame 1: 41708333.3 ns
    # Frame 2: 83416666.6 ns
    # Frame 3: 125125000.0 ns
    # Frame 4: 166833333.3 ns

    # EXACT
    # [CurrentFrameTime,NextFrameTime[
    # [⌈CurrentFrameTime⌉,⌈NextFrameTime⌉−1]
    # Frame 0: [0, 41708333]
    # Frame 1: [41708334, 83416666]
    # Frame 2: [83416667, 125124999]
    # Frame 3: [125125000, 166833333]
    # Frame 4: [166833334, 208541666]

    # START
    # ]PreviousFrameTime,CurrentFrameTime]
    # [⌊PreviousFrameTime⌋+1,⌊CurrentFrameTime⌋]
    # Frame 0: 0 ns
    # Frame 1: [1, 41708333]
    # Frame 2: [41708334, 83416666]
    # Frame 3: [83416667, 125125000]
    # Frame 4: [125125001, 166833333]
    #
    # END
    # ]CurrentFrameTime,NextFrameTime]
    # [⌊CurrentFrameTime⌋+1,⌊NextFrameTime⌋]
    # Frame 0: [1, 41708333] ns
    # Frame 1: [41708334, 83416666]
    # Frame 2: [83416667, 125125000]
    # Frame 3: [125125001, 166833333]


    # TimeType.EXACT - precision
    assert timestamp.frame_to_time(0, TimeType.EXACT, None, False) == 0
    assert timestamp.frame_to_time(1, TimeType.EXACT, None, False) == Fraction(1001, 24000)
    assert timestamp.frame_to_time(2, TimeType.EXACT, None, False) == Fraction(2002, 24000)
    assert timestamp.frame_to_time(3, TimeType.EXACT, None, False) == Fraction(3003, 24000)
    assert timestamp.frame_to_time(4, TimeType.EXACT, None, False) == Fraction(4004, 24000)

    # TimeType.EXACT - nanoseconds
    assert timestamp.frame_to_time(0, TimeType.EXACT, 9, False) == 0
    assert timestamp.frame_to_time(1, TimeType.EXACT, 9, False) == 41708334
    assert timestamp.frame_to_time(2, TimeType.EXACT, 9, False) == 83416667
    assert timestamp.frame_to_time(3, TimeType.EXACT, 9, False) == 125125000
    assert timestamp.frame_to_time(4, TimeType.EXACT, 9, False) == 166833334

    # TimeType.EXACT - milliseconds
    assert timestamp.frame_to_time(0, TimeType.EXACT, 3, False) == 0
    assert timestamp.frame_to_time(1, TimeType.EXACT, 3, False) == 42
    assert timestamp.frame_to_time(2, TimeType.EXACT, 3, False) == 84
    assert timestamp.frame_to_time(3, TimeType.EXACT, 3, False) == 126
    assert timestamp.frame_to_time(4, TimeType.EXACT, 3, False) == 167


    # TimeType.START - precision
    assert timestamp.frame_to_time(0, TimeType.START, None, False) == 0
    assert timestamp.frame_to_time(1, TimeType.START, None, False) == Fraction(1001, 24000)
    assert timestamp.frame_to_time(2, TimeType.START, None, False) == Fraction(2002, 24000)
    assert timestamp.frame_to_time(3, TimeType.START, None, False) == Fraction(3003, 24000)
    assert timestamp.frame_to_time(4, TimeType.START, None, False) == Fraction(4004, 24000)

    # TimeType.START - nanoseconds - False
    assert timestamp.frame_to_time(0, TimeType.START, 9, False) == 0
    assert timestamp.frame_to_time(1, TimeType.START, 9, False) == 41708333
    assert timestamp.frame_to_time(2, TimeType.START, 9, False) == 83416666
    assert timestamp.frame_to_time(3, TimeType.START, 9, False) == 125125000
    assert timestamp.frame_to_time(4, TimeType.START, 9, False) == 166833333

    # TimeType.START - milliseconds - False
    assert timestamp.frame_to_time(0, TimeType.START, 3, False) == 0
    assert timestamp.frame_to_time(1, TimeType.START, 3, False) == 41
    assert timestamp.frame_to_time(2, TimeType.START, 3, False) == 83
    assert timestamp.frame_to_time(3, TimeType.START, 3, False) == 125
    assert timestamp.frame_to_time(4, TimeType.START, 3, False) == 166

    # TimeType.START - nanoseconds - True
    # round((prev_frame_time + curr_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.START, 9, True) == 0
    assert timestamp.frame_to_time(1, TimeType.START, 9, True) == 20854167
    assert timestamp.frame_to_time(2, TimeType.START, 9, True) == 62562500
    assert timestamp.frame_to_time(3, TimeType.START, 9, True) == 104270833
    assert timestamp.frame_to_time(4, TimeType.START, 9, True) == 145979167

    # TimeType.START - milliseconds - True
    # round((prev_frame_time + curr_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.START, 3, True) == 0
    assert timestamp.frame_to_time(1, TimeType.START, 3, True) == 21
    assert timestamp.frame_to_time(2, TimeType.START, 3, True) == 63
    assert timestamp.frame_to_time(3, TimeType.START, 3, True) == 104
    assert timestamp.frame_to_time(4, TimeType.START, 3, True) == 146


    # TimeType.END - precision
    assert timestamp.frame_to_time(0, TimeType.END, None, False) == Fraction(1001, 24000)
    assert timestamp.frame_to_time(1, TimeType.END, None, False) == Fraction(2002, 24000)
    assert timestamp.frame_to_time(2, TimeType.END, None, False) == Fraction(3003, 24000)
    assert timestamp.frame_to_time(3, TimeType.END, None, False) == Fraction(4004, 24000)
    assert timestamp.frame_to_time(4, TimeType.END, None, False) == Fraction(5005, 24000)

    # TimeType.END - nanoseconds - False
    assert timestamp.frame_to_time(0, TimeType.END, 9, False) == 41708333
    assert timestamp.frame_to_time(1, TimeType.END, 9, False) == 83416666
    assert timestamp.frame_to_time(2, TimeType.END, 9, False) == 125125000
    assert timestamp.frame_to_time(3, TimeType.END, 9, False) == 166833333

    # TimeType.END - milliseconds - False
    assert timestamp.frame_to_time(0, TimeType.END, 3, False) == 41
    assert timestamp.frame_to_time(1, TimeType.END, 3, False) == 83
    assert timestamp.frame_to_time(2, TimeType.END, 3, False) == 125
    assert timestamp.frame_to_time(3, TimeType.END, 3, False) == 166

    # TimeType.END - nanoseconds - True
    # round((curr_frame_time + next_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.END, 9, True) == 20854167
    assert timestamp.frame_to_time(1, TimeType.END, 9, True) == 62562500
    assert timestamp.frame_to_time(2, TimeType.END, 9, True) == 104270833
    assert timestamp.frame_to_time(3, TimeType.END, 9, True) == 145979167

    # TimeType.END - milliseconds - True
    # round((curr_frame_time + next_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.END, 3, True) == 21
    assert timestamp.frame_to_time(1, TimeType.END, 3, True) == 63
    assert timestamp.frame_to_time(2, TimeType.END, 3, True) == 104
    assert timestamp.frame_to_time(3, TimeType.END, 3, True) == 146


    # TODO ajouter test pour output_unit négatif


def test_time_to_frame_round() -> None:
    rounding_method = RoundingMethod.ROUND
    timescale = Fraction(24000)
    fps = Fraction(24000, 1001)
    timestamp = FPSTimestamps(rounding_method, timescale, fps)

    # TimeType.EXACT - precision
    assert timestamp.time_to_frame(Fraction(0), TimeType.EXACT, None) == 0
    assert timestamp.time_to_frame(Fraction(1001, 24000), TimeType.EXACT, None) == 1
    assert timestamp.time_to_frame(Fraction(2002, 24000), TimeType.EXACT, None) == 2
    assert timestamp.time_to_frame(Fraction(3003, 24000), TimeType.EXACT, None) == 3
    assert timestamp.time_to_frame(Fraction(4004, 24000), TimeType.EXACT, None) == 4

    # TimeType.EXACT - nanoseconds
    assert timestamp.time_to_frame(0, TimeType.EXACT, 9) == 0
    assert timestamp.time_to_frame(41708333, TimeType.EXACT, 9) == 0
    assert timestamp.time_to_frame(41708334, TimeType.EXACT, 9) == 1
    assert timestamp.time_to_frame(83416666, TimeType.EXACT, 9) == 1
    assert timestamp.time_to_frame(83416667, TimeType.EXACT, 9) == 2
    assert timestamp.time_to_frame(125124999, TimeType.EXACT, 9) == 2
    assert timestamp.time_to_frame(125125000, TimeType.EXACT, 9) == 3
    assert timestamp.time_to_frame(166833333, TimeType.EXACT, 9) == 3
    assert timestamp.time_to_frame(166833334, TimeType.EXACT, 9) == 4

    # TimeType.EXACT - milliseconds
    assert timestamp.time_to_frame(0, TimeType.EXACT, 3) == 0
    assert timestamp.time_to_frame(41, TimeType.EXACT, 3) == 0
    assert timestamp.time_to_frame(42, TimeType.EXACT, 3) == 1
    assert timestamp.time_to_frame(83, TimeType.EXACT, 3) == 1
    assert timestamp.time_to_frame(84, TimeType.EXACT, 3) == 2
    assert timestamp.time_to_frame(125, TimeType.EXACT, 3) == 2
    assert timestamp.time_to_frame(126, TimeType.EXACT, 3) == 3
    assert timestamp.time_to_frame(166, TimeType.EXACT, 3) == 3
    assert timestamp.time_to_frame(167, TimeType.EXACT, 3) == 4


    # TimeType.START - precision
    assert timestamp.time_to_frame(Fraction(0), TimeType.START, None) == 0
    assert timestamp.time_to_frame(Fraction(1001, 24000), TimeType.START, None) == 1
    assert timestamp.time_to_frame(Fraction(2002, 24000), TimeType.START, None) == 2
    assert timestamp.time_to_frame(Fraction(3003, 24000), TimeType.START, None) == 3
    assert timestamp.time_to_frame(Fraction(4004, 24000), TimeType.START, None) == 4

    # TimeType.START - nanoseconds
    assert timestamp.time_to_frame(0, TimeType.START, 9) == 0
    assert timestamp.time_to_frame(1, TimeType.START, 9) == 1
    assert timestamp.time_to_frame(41708333, TimeType.START, 9) == 1
    assert timestamp.time_to_frame(41708334, TimeType.START, 9) == 2
    assert timestamp.time_to_frame(83416666, TimeType.START, 9) == 2
    assert timestamp.time_to_frame(83416667, TimeType.START, 9) == 3
    assert timestamp.time_to_frame(125125000, TimeType.START, 9) == 3
    assert timestamp.time_to_frame(125125001, TimeType.START, 9) == 4
    assert timestamp.time_to_frame(166833333, TimeType.START, 9) == 4

    # TimeType.START - milliseconds
    assert timestamp.time_to_frame(0, TimeType.START, 3) == 0
    assert timestamp.time_to_frame(1, TimeType.START, 3) == 1
    assert timestamp.time_to_frame(41, TimeType.START, 3) == 1
    assert timestamp.time_to_frame(42, TimeType.START, 3) == 2
    assert timestamp.time_to_frame(83, TimeType.START, 3) == 2
    assert timestamp.time_to_frame(84, TimeType.START, 3) == 3
    assert timestamp.time_to_frame(125, TimeType.START, 3) == 3
    assert timestamp.time_to_frame(126, TimeType.START, 3) == 4
    assert timestamp.time_to_frame(166, TimeType.START, 3) == 4


    # TimeType.END - precision
    assert timestamp.time_to_frame(Fraction(1001, 24000), TimeType.END, None) == 0
    assert timestamp.time_to_frame(Fraction(2002, 24000), TimeType.END, None) == 1
    assert timestamp.time_to_frame(Fraction(3003, 24000), TimeType.END, None) == 2
    assert timestamp.time_to_frame(Fraction(4004, 24000), TimeType.END, None) == 3
    assert timestamp.time_to_frame(Fraction(5005, 24000), TimeType.END, None) == 4

    # TimeType.END - nanoseconds
    with pytest.raises(ValueError) as exc_info:
        timestamp.time_to_frame(0, TimeType.END, 9)
    assert str(exc_info.value) == "You cannot specify a time equals to the first timestamps 0 with the TimeType.END."
    assert timestamp.time_to_frame(1, TimeType.END, 9) == 0
    assert timestamp.time_to_frame(41708333, TimeType.END, 9) == 0
    assert timestamp.time_to_frame(41708334, TimeType.END, 9) == 1
    assert timestamp.time_to_frame(83416666, TimeType.END, 9) == 1
    assert timestamp.time_to_frame(83416667, TimeType.END, 9) == 2
    assert timestamp.time_to_frame(125125000, TimeType.END, 9) == 2
    assert timestamp.time_to_frame(125125001, TimeType.END, 9) == 3
    assert timestamp.time_to_frame(166833333, TimeType.END, 9) == 3

    # TimeType.END - milliseconds
    assert timestamp.time_to_frame(1, TimeType.END, 3) == 0
    assert timestamp.time_to_frame(41, TimeType.END, 3) == 0
    assert timestamp.time_to_frame(42, TimeType.END, 3) == 1
    assert timestamp.time_to_frame(83, TimeType.END, 3) == 1
    assert timestamp.time_to_frame(84, TimeType.END, 3) == 2
    assert timestamp.time_to_frame(125, TimeType.END, 3) == 2
    assert timestamp.time_to_frame(126, TimeType.END, 3) == 3
    assert timestamp.time_to_frame(166, TimeType.END, 3) == 3


def test_frame_to_time_floor() -> None:
    rounding_method = RoundingMethod.FLOOR
    timescale = Fraction(90000)
    fps = Fraction(24000, 1001)
    timestamp = FPSTimestamps(rounding_method, timescale, fps)

    # Frame 0 - PTS = 0    - TIME = 0 ns
    # Frame 1 - PTS = 3753 - TIME = 41700000 ns
    # Frame 2 - PTS = 7507 - TIME = 83411111.1 ns
    # Frame 3 - PTS = 11261 - TIME = 125122222.2 ns
    # Frame 4 - PTS = 15015 - TIME = 166833333.3 ns

    # Frame 0: 0 ns
    # Frame 1: 41700000 ns
    # Frame 2: 83411111.1 ns
    # Frame 3: 125122222.2 ns
    # Frame 4: 166833333.3 ns

    # EXACT
    # [CurrentFrameTime,NextFrameTime[
    # [⌈CurrentFrameTime⌉,⌈NextFrameTime⌉−1]
    # Frame 0: [0, 41699999]
    # Frame 1: [41700000, 83411111]
    # Frame 2: [83411112, 125122222]
    # Frame 3: [125122223, 166833333]
    # Frame 4: [166833334, 208533333]

    # START
    # ]PreviousFrameTime,CurrentFrameTime]
    # [⌊PreviousFrameTime⌋+1,⌊CurrentFrameTime⌋]
    # Frame 0: 0 ns
    # Frame 1: [1, 41700000]
    # Frame 2: [41700001, 83411111]
    # Frame 3: [83411112, 125122222]
    # Frame 4: [125122223, 166833333]
    #
    # END
    # ]CurrentFrameTime,NextFrameTime]
    # [⌊CurrentFrameTime⌋+1,⌊NextFrameTime⌋]
    # Frame 0: [1, 41700000] ns
    # Frame 1: [41700001, 83411111]
    # Frame 2: [83411112, 125122222]
    # Frame 3: [125122223, 166833333]


    # TimeType.EXACT - precision
    assert timestamp.frame_to_time(0, TimeType.EXACT, None, False) == 0
    assert timestamp.frame_to_time(1, TimeType.EXACT, None, False) == Fraction(3753, 90000)
    assert timestamp.frame_to_time(2, TimeType.EXACT, None, False) == Fraction(7507, 90000)
    assert timestamp.frame_to_time(3, TimeType.EXACT, None, False) == Fraction(11261, 90000)
    assert timestamp.frame_to_time(4, TimeType.EXACT, None, False) == Fraction(15015, 90000)

    # TimeType.EXACT - nanoseconds
    assert timestamp.frame_to_time(0, TimeType.EXACT, 9, False) == 0
    assert timestamp.frame_to_time(1, TimeType.EXACT, 9, False) == 41700000
    assert timestamp.frame_to_time(2, TimeType.EXACT, 9, False) == 83411112
    assert timestamp.frame_to_time(3, TimeType.EXACT, 9, False) == 125122223
    assert timestamp.frame_to_time(4, TimeType.EXACT, 9, False) == 166833334

    # TimeType.EXACT - milliseconds
    assert timestamp.frame_to_time(0, TimeType.EXACT, 3, False) == 0
    assert timestamp.frame_to_time(1, TimeType.EXACT, 3, False) == 42
    assert timestamp.frame_to_time(2, TimeType.EXACT, 3, False) == 84
    assert timestamp.frame_to_time(3, TimeType.EXACT, 3, False) == 126
    assert timestamp.frame_to_time(4, TimeType.EXACT, 3, False) == 167


    # TimeType.START - precision
    assert timestamp.frame_to_time(0, TimeType.START, None, False) == 0
    assert timestamp.frame_to_time(1, TimeType.START, None, False) == Fraction(3753, 90000)
    assert timestamp.frame_to_time(2, TimeType.START, None, False) == Fraction(7507, 90000)
    assert timestamp.frame_to_time(3, TimeType.START, None, False) == Fraction(11261, 90000)
    assert timestamp.frame_to_time(4, TimeType.START, None, False) == Fraction(15015, 90000)

    # TimeType.START - nanoseconds - False
    assert timestamp.frame_to_time(0, TimeType.START, 9, False) == 0
    assert timestamp.frame_to_time(1, TimeType.START, 9, False) == 41700000
    assert timestamp.frame_to_time(2, TimeType.START, 9, False) == 83411111
    assert timestamp.frame_to_time(3, TimeType.START, 9, False) == 125122222
    assert timestamp.frame_to_time(4, TimeType.START, 9, False) == 166833333

    # TimeType.START - milliseconds - False
    assert timestamp.frame_to_time(0, TimeType.START, 3, False) == 0
    assert timestamp.frame_to_time(1, TimeType.START, 3, False) == 41
    assert timestamp.frame_to_time(2, TimeType.START, 3, False) == 83
    assert timestamp.frame_to_time(3, TimeType.START, 3, False) == 125
    assert timestamp.frame_to_time(4, TimeType.START, 3, False) == 166

    # TimeType.START - nanoseconds - True
    # round((prev_frame_time + curr_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.START, 9, True) == 0
    assert timestamp.frame_to_time(1, TimeType.START, 9, True) == 20850000
    assert timestamp.frame_to_time(2, TimeType.START, 9, True) == 62555556
    assert timestamp.frame_to_time(3, TimeType.START, 9, True) == 104266667
    assert timestamp.frame_to_time(4, TimeType.START, 9, True) == 145977778

    # TimeType.START - milliseconds - True
    # round((prev_frame_time + curr_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.START, 3, True) == 0
    assert timestamp.frame_to_time(1, TimeType.START, 3, True) == 21
    assert timestamp.frame_to_time(2, TimeType.START, 3, True) == 63
    assert timestamp.frame_to_time(3, TimeType.START, 3, True) == 104
    assert timestamp.frame_to_time(4, TimeType.START, 3, True) == 146


    # TimeType.END - precision
    assert timestamp.frame_to_time(0, TimeType.END, None, False) == Fraction(3753, 90000)
    assert timestamp.frame_to_time(1, TimeType.END, None, False) == Fraction(7507, 90000)
    assert timestamp.frame_to_time(2, TimeType.END, None, False) == Fraction(11261, 90000)
    assert timestamp.frame_to_time(3, TimeType.END, None, False) == Fraction(15015, 90000)
    assert timestamp.frame_to_time(4, TimeType.END, None, False) == Fraction(18768, 90000)

    # TimeType.END - nanoseconds - False
    assert timestamp.frame_to_time(0, TimeType.END, 9, False) == 41700000
    assert timestamp.frame_to_time(1, TimeType.END, 9, False) == 83411111
    assert timestamp.frame_to_time(2, TimeType.END, 9, False) == 125122222
    assert timestamp.frame_to_time(3, TimeType.END, 9, False) == 166833333

    # TimeType.END - milliseconds - False
    assert timestamp.frame_to_time(0, TimeType.END, 3, False) == 41
    assert timestamp.frame_to_time(1, TimeType.END, 3, False) == 83
    assert timestamp.frame_to_time(2, TimeType.END, 3, False) == 125
    assert timestamp.frame_to_time(3, TimeType.END, 3, False) == 166

    # TimeType.END - nanoseconds - True
    # round((curr_frame_time + next_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.END, 9, True) == 20850000
    assert timestamp.frame_to_time(1, TimeType.END, 9, True) == 62555556
    assert timestamp.frame_to_time(2, TimeType.END, 9, True) == 104266667
    assert timestamp.frame_to_time(3, TimeType.END, 9, True) == 145977778

    # TimeType.END - milliseconds - True
    # round((curr_frame_time + next_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.END, 3, True) == 21
    assert timestamp.frame_to_time(1, TimeType.END, 3, True) == 63
    assert timestamp.frame_to_time(2, TimeType.END, 3, True) == 104
    assert timestamp.frame_to_time(3, TimeType.END, 3, True) == 146


def test_time_to_frame_floor() -> None:
    rounding_method = RoundingMethod.FLOOR
    timescale = Fraction(90000)
    fps = Fraction(24000, 1001)
    timestamp = FPSTimestamps(rounding_method, timescale, fps)

    # TimeType.EXACT - precision
    assert timestamp.time_to_frame(Fraction(0), TimeType.EXACT, None) == 0
    assert timestamp.time_to_frame(Fraction(3753, 90000), TimeType.EXACT, None) == 1
    assert timestamp.time_to_frame(Fraction(7507, 90000), TimeType.EXACT, None) == 2
    assert timestamp.time_to_frame(Fraction(11261, 90000), TimeType.EXACT, None) == 3
    assert timestamp.time_to_frame(Fraction(15015, 90000), TimeType.EXACT, None) == 4

    # TimeType.EXACT - nanoseconds
    assert timestamp.time_to_frame(0, TimeType.EXACT, 9) == 0
    assert timestamp.time_to_frame(41699999, TimeType.EXACT, 9) == 0
    assert timestamp.time_to_frame(41700000, TimeType.EXACT, 9) == 1
    assert timestamp.time_to_frame(83411111, TimeType.EXACT, 9) == 1
    assert timestamp.time_to_frame(83411112, TimeType.EXACT, 9) == 2
    assert timestamp.time_to_frame(125122222, TimeType.EXACT, 9) == 2
    assert timestamp.time_to_frame(125122223, TimeType.EXACT, 9) == 3
    assert timestamp.time_to_frame(166833333, TimeType.EXACT, 9) == 3
    assert timestamp.time_to_frame(166833334, TimeType.EXACT, 9) == 4

    # TimeType.EXACT - milliseconds
    assert timestamp.time_to_frame(0, TimeType.EXACT, 3) == 0
    assert timestamp.time_to_frame(41, TimeType.EXACT, 3) == 0
    assert timestamp.time_to_frame(42, TimeType.EXACT, 3) == 1
    assert timestamp.time_to_frame(83, TimeType.EXACT, 3) == 1
    assert timestamp.time_to_frame(84, TimeType.EXACT, 3) == 2
    assert timestamp.time_to_frame(125, TimeType.EXACT, 3) == 2
    assert timestamp.time_to_frame(126, TimeType.EXACT, 3) == 3
    assert timestamp.time_to_frame(166, TimeType.EXACT, 3) == 3
    assert timestamp.time_to_frame(167, TimeType.EXACT, 3) == 4


    # TimeType.START - precision
    assert timestamp.time_to_frame(Fraction(0), TimeType.START, None) == 0
    assert timestamp.time_to_frame(Fraction(3753, 90000), TimeType.START, None) == 1
    assert timestamp.time_to_frame(Fraction(7507, 90000), TimeType.START, None) == 2
    assert timestamp.time_to_frame(Fraction(11261, 90000), TimeType.START, None) == 3
    assert timestamp.time_to_frame(Fraction(15015, 90000), TimeType.START, None) == 4

    # TimeType.START - nanoseconds
    assert timestamp.time_to_frame(0, TimeType.START, 9) == 0
    assert timestamp.time_to_frame(1, TimeType.START, 9) == 1
    assert timestamp.time_to_frame(41700000, TimeType.START, 9) == 1
    assert timestamp.time_to_frame(41700001, TimeType.START, 9) == 2
    assert timestamp.time_to_frame(83411111, TimeType.START, 9) == 2
    assert timestamp.time_to_frame(83411112, TimeType.START, 9) == 3
    assert timestamp.time_to_frame(125122222, TimeType.START, 9) == 3
    assert timestamp.time_to_frame(125122223, TimeType.START, 9) == 4
    assert timestamp.time_to_frame(166833333, TimeType.START, 9) == 4

    # TimeType.START - milliseconds
    assert timestamp.time_to_frame(0, TimeType.START, 3) == 0
    assert timestamp.time_to_frame(1, TimeType.START, 3) == 1
    assert timestamp.time_to_frame(41, TimeType.START, 3) == 1
    assert timestamp.time_to_frame(42, TimeType.START, 3) == 2
    assert timestamp.time_to_frame(83, TimeType.START, 3) == 2
    assert timestamp.time_to_frame(84, TimeType.START, 3) == 3
    assert timestamp.time_to_frame(125, TimeType.START, 3) == 3
    assert timestamp.time_to_frame(126, TimeType.START, 3) == 4
    assert timestamp.time_to_frame(166, TimeType.START, 3) == 4


    # TimeType.END - precision
    assert timestamp.time_to_frame(Fraction(3753, 90000), TimeType.END, None) == 0
    assert timestamp.time_to_frame(Fraction(7507, 90000), TimeType.END, None) == 1
    assert timestamp.time_to_frame(Fraction(11261, 90000), TimeType.END, None) == 2
    assert timestamp.time_to_frame(Fraction(15015, 90000), TimeType.END, None) == 3
    assert timestamp.time_to_frame(Fraction(18768, 90000), TimeType.END, None) == 4

    # TimeType.END - nanoseconds
    with pytest.raises(ValueError) as exc_info:
        timestamp.time_to_frame(0, TimeType.END, 9)
    assert str(exc_info.value) == "You cannot specify a time equals to the first timestamps 0 with the TimeType.END."
    assert timestamp.time_to_frame(1, TimeType.END, 9) == 0
    assert timestamp.time_to_frame(41700000, TimeType.END, 9) == 0
    assert timestamp.time_to_frame(41700001, TimeType.END, 9) == 1
    assert timestamp.time_to_frame(83411111, TimeType.END, 9) == 1
    assert timestamp.time_to_frame(83411112, TimeType.END, 9) == 2
    assert timestamp.time_to_frame(125122222, TimeType.END, 9) == 2
    assert timestamp.time_to_frame(125122223, TimeType.END, 9) == 3
    assert timestamp.time_to_frame(166833333, TimeType.END, 9) == 3

    # TimeType.END - milliseconds
    assert timestamp.time_to_frame(1, TimeType.END, 3) == 0
    assert timestamp.time_to_frame(41, TimeType.END, 3) == 0
    assert timestamp.time_to_frame(42, TimeType.END, 3) == 1
    assert timestamp.time_to_frame(83, TimeType.END, 3) == 1
    assert timestamp.time_to_frame(84, TimeType.END, 3) == 2
    assert timestamp.time_to_frame(125, TimeType.END, 3) == 2
    assert timestamp.time_to_frame(126, TimeType.END, 3) == 3
    assert timestamp.time_to_frame(166, TimeType.END, 3) == 3
