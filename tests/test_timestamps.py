import pytest
from fractions import Fraction
from math import ceil
from video_timestamps import (
    ABCTimestamps,
    FPSTimestamps,
    RoundingMethod,
    TimeType,
    VideoTimestamps
)


@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.ROUND, Fraction(24000), Fraction(24000, 1001)),
        VideoTimestamps([0, 1001, 2002, 3003, 4004, 5005], Fraction(24000)),
    ],
)
def test_frame_to_time_invalid_frame(timestamp: ABCTimestamps) -> None:

    with pytest.raises(ValueError) as exc_info:
        timestamp.frame_to_time(-1, TimeType.EXACT)
    assert str(exc_info.value) == "You cannot specify a frame under 0."

    with pytest.raises(ValueError) as exc_info:
        timestamp.frame_to_time(-1, TimeType.START)
    assert str(exc_info.value) == "You cannot specify a frame under 0."

    with pytest.raises(ValueError) as exc_info:
        timestamp.frame_to_time(-1, TimeType.END)
    assert str(exc_info.value) == "You cannot specify a frame under 0."

    with pytest.raises(ValueError) as exc_info:
        timestamp.frame_to_time(0, TimeType.EXACT, 9, True)
    assert str(exc_info.value) == "It doesn't make sense to use the time in the center of two frame for TimeType.EXACT."


@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.ROUND, Fraction(24000), Fraction(24000, 1001)),
        VideoTimestamps([0, 1001, 2002, 3003, 4004, 5005], Fraction(24000)),
    ],
)
def test_frame_to_time_invalid_output_unit(timestamp: ABCTimestamps) -> None:

    with pytest.raises(ValueError) as exc_info:
        timestamp.frame_to_time(0, TimeType.EXACT, -1)
    assert str(exc_info.value) == "The output_unit needs to be above or equal to 0."


@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.ROUND, Fraction(24000), Fraction(24000, 1001)),
        VideoTimestamps([0, 1001, 2002, 3003, 4004, 5005], Fraction(24000)),
    ],
)
def test_time_to_frame_invalid_input_unit(timestamp: ABCTimestamps) -> None:

    with pytest.raises(ValueError) as exc_info:
        timestamp.time_to_frame(10, TimeType.EXACT)
    assert str(exc_info.value) == "If input_unit is none, the time needs to be a Fraction."

    with pytest.raises(ValueError) as exc_info:
        timestamp.time_to_frame(Fraction(10), TimeType.START, 9)
    assert str(exc_info.value) == "If you specify a input_unit, the time needs to be a int."



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

@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.ROUND, Fraction(24000), Fraction(24000, 1001)),
        VideoTimestamps([0, 1001, 2002, 3003, 4004, 5005], Fraction(24000)),
        VideoTimestamps([0, 1001, 2002], Fraction(24000), fps=Fraction(24000, 1001)), # Test VideoTimestamps over the video lenght
    ],
)
def test_frame_to_time_round(timestamp: ABCTimestamps) -> None:

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


@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.ROUND, Fraction(24000), Fraction(24000, 1001)),
        VideoTimestamps([0, 1001, 2002, 3003, 4004, 5005], Fraction(24000)),
        VideoTimestamps([0, 1001, 2002], Fraction(24000), fps=Fraction(24000, 1001)), # Test VideoTimestamps over the video lenght
    ],
)
def test_time_to_frame_round(timestamp: ABCTimestamps) -> None:
    timestamp = FPSTimestamps(RoundingMethod.ROUND, Fraction(24000), Fraction(24000, 1001))

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
    assert str(exc_info.value) == "You cannot specify a time under or equals the first timestamps 0 with the TimeType.END."
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


# Frame 0 - PTS = 0    - TIME = 0 ns
# Frame 1 - PTS = 3753 - TIME = 41700000 ns
# Frame 2 - PTS = 7507 - TIME = 83411111.1 ns
# Frame 3 - PTS = 11261 - TIME = 125122222.2 ns
# Frame 4 - PTS = 15015 - TIME = 166833333.3 ns

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

@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.FLOOR, Fraction(90000), Fraction(24000, 1001)),
        VideoTimestamps([0, 3753, 7507, 11261, 15015, 18768], Fraction(90000)),
        VideoTimestamps([0, 3753, 7507], Fraction(90000), fps=Fraction(24000, 1001)), # Test VideoTimestamps over the video lenght
    ],
)
def test_frame_to_time_floor(timestamp: ABCTimestamps) -> None:

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


@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.FLOOR, Fraction(90000), Fraction(24000, 1001)),
        VideoTimestamps([0, 3753, 7507, 11261, 15015, 18768], Fraction(90000)),
        VideoTimestamps([0, 3753, 7507], Fraction(90000), fps=Fraction(24000, 1001)), # Test VideoTimestamps over the video lenght
    ],
)
def test_time_to_frame_floor(timestamp: ABCTimestamps) -> None:

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
    assert str(exc_info.value) == "You cannot specify a time under or equals the first timestamps 0 with the TimeType.END."
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


# For a fps=24000/1001 and a timescale of 90000,
# The default pts would be: 0, 3753, 7507, 11261, 15015, 18768
# But, let's say the first pts is -10000 (for m2ts files, it happen frequently that the first pts isn't 0)
# So, we add 3753 to all the pts which give: -10000, -6247, -2493, 1261, 5015, 8768

# Frame 0 - PTS = -10000 - TIME = -111111111.1 ns
# Frame 1 - PTS = -6247 - TIME = -69411111.1 ns
# Frame 2 - PTS = -2493 - TIME = -27700000 ns
# Frame 3 - PTS = 1261 - TIME = 14011111.1 ns
# Frame 4 - PTS = 5015 - TIME = 55722222.2 ns
# Frame 5 - PTS = 8768 - TIME = 97422222.2 ns

# EXACT
# [CurrentFrameTime,NextFrameTime[
# [⌈CurrentFrameTime⌉,⌈NextFrameTime⌉−1]
# Frame 0: [-111111111, -69411112]
# Frame 1: [-69411111, -27700001]
# Frame 2: [-27700000, 14011111]
# Frame 3: [14011112, 55722222]
# Frame 4: [55722223, 250233333]

# START
# ]PreviousFrameTime,CurrentFrameTime]
# [⌊PreviousFrameTime⌋+1,⌊CurrentFrameTime⌋]
# Frame 0: -111111112
# Frame 1: [-111111111, -69411112]
# Frame 2: [-69411111, -27700000]
# Frame 3: [-27699999, 14011111]
# Frame 4: [14011112, 55722222]

# END
# ]CurrentFrameTime,NextFrameTime]
# [⌊CurrentFrameTime⌋+1,⌊NextFrameTime⌋]
# Frame 0: [-111111111, -69411112]
# Frame 1: [-69411111, -27700000]
# Frame 2: [-27699999, 14011111]
# Frame 3: [14011112, 55722222]
@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.FLOOR, Fraction(90000), Fraction(24000, 1001), -10000),
        VideoTimestamps([-10000, -6247, -2493, 1261, 5015, 8768], Fraction(90000), False),
        VideoTimestamps([-10000, -6247, -2493], Fraction(90000), False, Fraction(24000, 1001), RoundingMethod.FLOOR), # Test VideoTimestamps over the video lenght
    ],
)
def test_frame_to_time_floor_first_pts_under_0(timestamp: ABCTimestamps) -> None:

    # TimeType.EXACT - precision
    assert timestamp.frame_to_time(0, TimeType.EXACT, None, False) == Fraction(-10000, 90000)
    assert timestamp.frame_to_time(1, TimeType.EXACT, None, False) == Fraction(-6247, 90000)
    assert timestamp.frame_to_time(2, TimeType.EXACT, None, False) == Fraction(-2493, 90000)
    assert timestamp.frame_to_time(3, TimeType.EXACT, None, False) == Fraction(1261, 90000)
    assert timestamp.frame_to_time(4, TimeType.EXACT, None, False) == Fraction(5015, 90000)

    # TimeType.EXACT - nanoseconds
    assert timestamp.frame_to_time(0, TimeType.EXACT, 9, False) == -111111111
    assert timestamp.frame_to_time(1, TimeType.EXACT, 9, False) == -69411111
    assert timestamp.frame_to_time(2, TimeType.EXACT, 9, False) == -27700000
    assert timestamp.frame_to_time(3, TimeType.EXACT, 9, False) == 14011112
    assert timestamp.frame_to_time(4, TimeType.EXACT, 9, False) == 55722223

    # TimeType.EXACT - milliseconds
    assert timestamp.frame_to_time(0, TimeType.EXACT, 3, False) == -111
    assert timestamp.frame_to_time(1, TimeType.EXACT, 3, False) == -69
    assert timestamp.frame_to_time(2, TimeType.EXACT, 3, False) == -27
    assert timestamp.frame_to_time(3, TimeType.EXACT, 3, False) == 15
    assert timestamp.frame_to_time(4, TimeType.EXACT, 3, False) == 56


    # TimeType.START - precision
    assert timestamp.frame_to_time(0, TimeType.START, None, False) == Fraction(-10000, 90000)
    assert timestamp.frame_to_time(1, TimeType.START, None, False) == Fraction(-6247, 90000)
    assert timestamp.frame_to_time(2, TimeType.START, None, False) == Fraction(-2493, 90000)
    assert timestamp.frame_to_time(3, TimeType.START, None, False) == Fraction(1261, 90000)
    assert timestamp.frame_to_time(4, TimeType.START, None, False) == Fraction(5015, 90000)

    # TimeType.START - nanoseconds - False
    assert timestamp.frame_to_time(0, TimeType.START, 9, False) == -111111112
    assert timestamp.frame_to_time(1, TimeType.START, 9, False) == -69411112
    assert timestamp.frame_to_time(2, TimeType.START, 9, False) == -27700000
    assert timestamp.frame_to_time(3, TimeType.START, 9, False) == 14011111
    assert timestamp.frame_to_time(4, TimeType.START, 9, False) == 55722222

    # TimeType.START - milliseconds - False
    assert timestamp.frame_to_time(0, TimeType.START, 3, False) == -112
    assert timestamp.frame_to_time(1, TimeType.START, 3, False) == -70
    assert timestamp.frame_to_time(2, TimeType.START, 3, False) == -28
    assert timestamp.frame_to_time(3, TimeType.START, 3, False) == 14
    assert timestamp.frame_to_time(4, TimeType.START, 3, False) == 55

    # TimeType.START - nanoseconds - True
    # round((prev_frame_time + curr_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.START, 9, True) == -111111112
    assert timestamp.frame_to_time(1, TimeType.START, 9, True) == -90261111
    assert timestamp.frame_to_time(2, TimeType.START, 9, True) == -48555556
    assert timestamp.frame_to_time(3, TimeType.START, 9, True) == -6844444
    assert timestamp.frame_to_time(4, TimeType.START, 9, True) == 34866667

    # TimeType.START - milliseconds - True
    # round((prev_frame_time + curr_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.START, 3, True) == -112
    assert timestamp.frame_to_time(1, TimeType.START, 3, True) == -90
    assert timestamp.frame_to_time(2, TimeType.START, 3, True) == -49
    assert timestamp.frame_to_time(3, TimeType.START, 3, True) == -7
    assert timestamp.frame_to_time(4, TimeType.START, 3, True) == 35


    # TimeType.END - precision
    assert timestamp.frame_to_time(0, TimeType.END, None, False) == Fraction(-6247, 90000)
    assert timestamp.frame_to_time(1, TimeType.END, None, False) == Fraction(-2493, 90000)
    assert timestamp.frame_to_time(2, TimeType.END, None, False) == Fraction(1261, 90000)
    assert timestamp.frame_to_time(3, TimeType.END, None, False) == Fraction(5015, 90000)

    # TimeType.END - nanoseconds - False
    assert timestamp.frame_to_time(0, TimeType.END, 9, False) == -69411112
    assert timestamp.frame_to_time(1, TimeType.END, 9, False) == -27700000
    assert timestamp.frame_to_time(2, TimeType.END, 9, False) == 14011111
    assert timestamp.frame_to_time(3, TimeType.END, 9, False) == 55722222

    # TimeType.END - milliseconds - False
    assert timestamp.frame_to_time(0, TimeType.END, 3, False) == -70
    assert timestamp.frame_to_time(1, TimeType.END, 3, False) == -28
    assert timestamp.frame_to_time(2, TimeType.END, 3, False) == 14
    assert timestamp.frame_to_time(3, TimeType.END, 3, False) == 55

    # TimeType.END - nanoseconds - True
    # round((curr_frame_time + next_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.END, 9, True) == -90261111
    assert timestamp.frame_to_time(1, TimeType.END, 9, True) == -48555556
    assert timestamp.frame_to_time(2, TimeType.END, 9, True) == -6844444
    assert timestamp.frame_to_time(3, TimeType.END, 9, True) == 34866667

    # TimeType.END - milliseconds - True
    # round((curr_frame_time + next_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.END, 3, True) == -90
    assert timestamp.frame_to_time(1, TimeType.END, 3, True) == -49
    assert timestamp.frame_to_time(2, TimeType.END, 3, True) == -7
    assert timestamp.frame_to_time(3, TimeType.END, 3, True) == 35

@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.FLOOR, Fraction(90000), Fraction(24000, 1001), -10000),
        VideoTimestamps([-10000, -6247, -2493, 1261, 5015, 8768], Fraction(90000), False),
        VideoTimestamps([-10000, -6247, -2493], Fraction(90000), False, Fraction(24000, 1001), RoundingMethod.FLOOR), # Test VideoTimestamps over the video lenght
    ],
)
def test_time_to_frame_floor_first_pts_under_0(timestamp: ABCTimestamps) -> None:

    # TimeType.EXACT - precision
    with pytest.raises(ValueError) as exc_info:
        timestamp.time_to_frame(Fraction(-10001, 90000), TimeType.EXACT, None)
    assert str(exc_info.value) == f"You cannot specify a time under the first timestamps {Fraction(-10000, 90000)} with the TimeType.EXACT."
    assert timestamp.time_to_frame(Fraction(-10000, 90000), TimeType.EXACT, None) == 0
    assert timestamp.time_to_frame(Fraction(-6247, 90000), TimeType.EXACT, None) == 1
    assert timestamp.time_to_frame(Fraction(-2493, 90000), TimeType.EXACT, None) == 2
    assert timestamp.time_to_frame(Fraction(1261, 90000), TimeType.EXACT, None) == 3
    assert timestamp.time_to_frame(Fraction(5015, 90000), TimeType.EXACT, None) == 4

    # TimeType.EXACT - nanoseconds
    assert timestamp.time_to_frame(-111111111, TimeType.EXACT, 9) == 0
    assert timestamp.time_to_frame(-69411112, TimeType.EXACT, 9) == 0
    assert timestamp.time_to_frame(-69411111, TimeType.EXACT, 9) == 1
    assert timestamp.time_to_frame(-27700001, TimeType.EXACT, 9) == 1
    assert timestamp.time_to_frame(-27700000, TimeType.EXACT, 9) == 2
    assert timestamp.time_to_frame(14011111, TimeType.EXACT, 9) == 2
    assert timestamp.time_to_frame(14011112, TimeType.EXACT, 9) == 3
    assert timestamp.time_to_frame(55722222, TimeType.EXACT, 9) == 3
    assert timestamp.time_to_frame(55722223, TimeType.EXACT, 9) == 4

    # TimeType.EXACT - milliseconds
    assert timestamp.time_to_frame(-111, TimeType.EXACT, 3) == 0
    assert timestamp.time_to_frame(-70, TimeType.EXACT, 3) == 0
    assert timestamp.time_to_frame(-69, TimeType.EXACT, 3) == 1
    assert timestamp.time_to_frame(-28, TimeType.EXACT, 3) == 1
    assert timestamp.time_to_frame(-27, TimeType.EXACT, 3) == 2
    assert timestamp.time_to_frame(14, TimeType.EXACT, 3) == 2
    assert timestamp.time_to_frame(15, TimeType.EXACT, 3) == 3
    assert timestamp.time_to_frame(55, TimeType.EXACT, 3) == 3
    assert timestamp.time_to_frame(56, TimeType.EXACT, 3) == 4


    # TimeType.START - precision
    assert timestamp.time_to_frame(Fraction(-10001, 90000), TimeType.START, None) == 0
    assert timestamp.time_to_frame(Fraction(-10000, 90000), TimeType.START, None) == 0
    assert timestamp.time_to_frame(Fraction(-6247, 90000), TimeType.START, None) == 1
    assert timestamp.time_to_frame(Fraction(-2493, 90000), TimeType.START, None) == 2
    assert timestamp.time_to_frame(Fraction(1261, 90000), TimeType.START, None) == 3
    assert timestamp.time_to_frame(Fraction(5015, 90000), TimeType.START, None) == 4

    # TimeType.START - nanoseconds
    assert timestamp.time_to_frame(-111111112, TimeType.START, 9) == 0
    assert timestamp.time_to_frame(-111111111, TimeType.START, 9) == 1
    assert timestamp.time_to_frame(-69411112, TimeType.START, 9) == 1
    assert timestamp.time_to_frame(-69411111, TimeType.START, 9) == 2
    assert timestamp.time_to_frame(-27700000, TimeType.START, 9) == 2
    assert timestamp.time_to_frame(-27699999, TimeType.START, 9) == 3
    assert timestamp.time_to_frame(14011111, TimeType.START, 9) == 3
    assert timestamp.time_to_frame(14011112, TimeType.START, 9) == 4
    assert timestamp.time_to_frame(55722222, TimeType.START, 9) == 4

    # TimeType.START - milliseconds
    assert timestamp.time_to_frame(-112, TimeType.START, 3) == 0
    assert timestamp.time_to_frame(-111, TimeType.START, 3) == 1
    assert timestamp.time_to_frame(-70, TimeType.START, 3) == 1
    assert timestamp.time_to_frame(-69, TimeType.START, 3) == 2
    assert timestamp.time_to_frame(-28, TimeType.START, 3) == 2
    assert timestamp.time_to_frame(-27, TimeType.START, 3) == 3
    assert timestamp.time_to_frame(14, TimeType.START, 3) == 3
    assert timestamp.time_to_frame(15, TimeType.START, 3) == 4
    assert timestamp.time_to_frame(55, TimeType.START, 3) == 4


    # TimeType.END - precision
    with pytest.raises(ValueError) as exc_info:
        timestamp.time_to_frame(Fraction(-10000, 90000), TimeType.END, None)
    assert str(exc_info.value) == f"You cannot specify a time under or equals the first timestamps {Fraction(-10000, 90000)} with the TimeType.END."
    assert timestamp.time_to_frame(Fraction(-9999, 90000), TimeType.END, None) == 0
    assert timestamp.time_to_frame(Fraction(-6247, 90000), TimeType.END, None) == 0
    assert timestamp.time_to_frame(Fraction(-2493, 90000), TimeType.END, None) == 1
    assert timestamp.time_to_frame(Fraction(1261, 90000), TimeType.END, None) == 2
    assert timestamp.time_to_frame(Fraction(5015, 90000), TimeType.END, None) == 3

    # TimeType.END - nanoseconds
    assert timestamp.time_to_frame(-111111111, TimeType.END, 9) == 0
    assert timestamp.time_to_frame(-69411112, TimeType.END, 9) == 0
    assert timestamp.time_to_frame(-69411111, TimeType.END, 9) == 1
    assert timestamp.time_to_frame(-27700000, TimeType.END, 9) == 1
    assert timestamp.time_to_frame(-27699999, TimeType.END, 9) == 2
    assert timestamp.time_to_frame(14011111, TimeType.END, 9) == 2
    assert timestamp.time_to_frame(14011112, TimeType.END, 9) == 3
    assert timestamp.time_to_frame(55722222, TimeType.END, 9) == 3

    # TimeType.END - milliseconds
    assert timestamp.time_to_frame(-111, TimeType.END, 3) == 0
    assert timestamp.time_to_frame(-70, TimeType.END, 3) == 0
    assert timestamp.time_to_frame(-69, TimeType.END, 3) == 1
    assert timestamp.time_to_frame(-28, TimeType.END, 3) == 1
    assert timestamp.time_to_frame(-27, TimeType.END, 3) == 2
    assert timestamp.time_to_frame(14, TimeType.END, 3) == 2
    assert timestamp.time_to_frame(15, TimeType.END, 3) == 3
    assert timestamp.time_to_frame(55, TimeType.END, 3) == 3


# For a fps=24000/1001 and a timescale of 90000,
# The default pts would be: 0, 3753, 7507, 11261, 15015, 18768
# But, let's say the first pts is 3753 (for m2ts files, it happen frequently that the first pts isn't 0)
# So, we add 3753 to all the pts which give: 3753, 7506, 11260, 15014, 18768, 22521

# Frame 0 - PTS = 3753 - TIME = 41700000 ns
# Frame 1 - PTS = 7506 - TIME = 83400000 ns
# Frame 2 - PTS = 11260 - TIME = 125111111.1 ns
# Frame 3 - PTS = 15014 - TIME = 166822222.2 ns
# Frame 4 - PTS = 18768 - TIME = 208533333.3 ns
# Frame 5 - PTS = 22521 - TIME = 250233333.3 ns

# EXACT
# [CurrentFrameTime,NextFrameTime[
# [⌈CurrentFrameTime⌉,⌈NextFrameTime⌉−1]
# Frame 0: [41700000, 83399999]
# Frame 1: [83400000, 125111111]
# Frame 2: [125111112, 166822222]
# Frame 3: [166822223, 208533333]
# Frame 4: [208533334, 250233333]

# START
# ]PreviousFrameTime,CurrentFrameTime]
# [⌊PreviousFrameTime⌋+1,⌊CurrentFrameTime⌋]
# Frame 0: 41700000
# Frame 1: [41700001, 83400000]
# Frame 2: [83400001, 125111111]
# Frame 3: [125111112, 166822222]
# Frame 4: [166822223, 208533333]

# END
# ]CurrentFrameTime,NextFrameTime]
# [⌊CurrentFrameTime⌋+1,⌊NextFrameTime⌋]
# Frame 0: [41700001, 83400000]
# Frame 1: [83400001, 125111111]
# Frame 2: [125111112, 166822222]
# Frame 3: [166822223, 208533333]

@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.FLOOR, Fraction(90000), Fraction(24000, 1001), 3753),
        VideoTimestamps([3753, 7506, 11260, 15014, 18768, 22521], Fraction(90000), False),
        VideoTimestamps([3753, 7506, 11260], Fraction(90000), False, Fraction(24000, 1001), RoundingMethod.FLOOR), # Test VideoTimestamps over the video lenght
    ],
)
def test_frame_to_time_floor_first_pts_over_0(timestamp: ABCTimestamps) -> None:

    # TimeType.EXACT - precision
    assert timestamp.frame_to_time(0, TimeType.EXACT, None, False) == Fraction(3753, 90000)
    assert timestamp.frame_to_time(1, TimeType.EXACT, None, False) == Fraction(7506, 90000)
    assert timestamp.frame_to_time(2, TimeType.EXACT, None, False) == Fraction(11260, 90000)
    assert timestamp.frame_to_time(3, TimeType.EXACT, None, False) == Fraction(15014, 90000)
    assert timestamp.frame_to_time(4, TimeType.EXACT, None, False) == Fraction(18768, 90000)

    # TimeType.EXACT - nanoseconds
    assert timestamp.frame_to_time(0, TimeType.EXACT, 9, False) == 41700000
    assert timestamp.frame_to_time(1, TimeType.EXACT, 9, False) == 83400000
    assert timestamp.frame_to_time(2, TimeType.EXACT, 9, False) == 125111112
    assert timestamp.frame_to_time(3, TimeType.EXACT, 9, False) == 166822223
    assert timestamp.frame_to_time(4, TimeType.EXACT, 9, False) == 208533334

    # TimeType.EXACT - milliseconds
    assert timestamp.frame_to_time(0, TimeType.EXACT, 3, False) == 42
    assert timestamp.frame_to_time(1, TimeType.EXACT, 3, False) == 84
    assert timestamp.frame_to_time(2, TimeType.EXACT, 3, False) == 126
    assert timestamp.frame_to_time(3, TimeType.EXACT, 3, False) == 167
    assert timestamp.frame_to_time(4, TimeType.EXACT, 3, False) == 209


    # TimeType.START - precision
    assert timestamp.frame_to_time(0, TimeType.START, None, False) == Fraction(3753, 90000)
    assert timestamp.frame_to_time(1, TimeType.START, None, False) == Fraction(7506, 90000)
    assert timestamp.frame_to_time(2, TimeType.START, None, False) == Fraction(11260, 90000)
    assert timestamp.frame_to_time(3, TimeType.START, None, False) == Fraction(15014, 90000)
    assert timestamp.frame_to_time(4, TimeType.START, None, False) == Fraction(18768, 90000)

    # TimeType.START - nanoseconds - False
    assert timestamp.frame_to_time(0, TimeType.START, 9, False) == 41700000
    assert timestamp.frame_to_time(1, TimeType.START, 9, False) == 83400000
    assert timestamp.frame_to_time(2, TimeType.START, 9, False) == 125111111
    assert timestamp.frame_to_time(3, TimeType.START, 9, False) == 166822222
    assert timestamp.frame_to_time(4, TimeType.START, 9, False) == 208533333

    # TimeType.START - milliseconds - False
    assert timestamp.frame_to_time(0, TimeType.START, 3, False) == 41
    assert timestamp.frame_to_time(1, TimeType.START, 3, False) == 83
    assert timestamp.frame_to_time(2, TimeType.START, 3, False) == 125
    assert timestamp.frame_to_time(3, TimeType.START, 3, False) == 166
    assert timestamp.frame_to_time(4, TimeType.START, 3, False) == 208

    # TimeType.START - nanoseconds - True
    # round((prev_frame_time + curr_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.START, 9, True) == 41700000
    assert timestamp.frame_to_time(1, TimeType.START, 9, True) == 62550000
    assert timestamp.frame_to_time(2, TimeType.START, 9, True) == 104255556
    assert timestamp.frame_to_time(3, TimeType.START, 9, True) == 145966667
    assert timestamp.frame_to_time(4, TimeType.START, 9, True) == 187677778

    # TimeType.START - milliseconds - True
    # round((prev_frame_time + curr_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.START, 3, True) == 41
    assert timestamp.frame_to_time(1, TimeType.START, 3, True) == 63
    assert timestamp.frame_to_time(2, TimeType.START, 3, True) == 104
    assert timestamp.frame_to_time(3, TimeType.START, 3, True) == 146
    assert timestamp.frame_to_time(4, TimeType.START, 3, True) == 188


    # TimeType.END - precision
    assert timestamp.frame_to_time(0, TimeType.END, None, False) == Fraction(7506, 90000)
    assert timestamp.frame_to_time(0, TimeType.END, None, False) == Fraction(7506, 90000)
    assert timestamp.frame_to_time(1, TimeType.END, None, False) == Fraction(11260, 90000)
    assert timestamp.frame_to_time(2, TimeType.END, None, False) == Fraction(15014, 90000)
    assert timestamp.frame_to_time(3, TimeType.END, None, False) == Fraction(18768, 90000)

    # TimeType.END - nanoseconds - False
    assert timestamp.frame_to_time(0, TimeType.END, 9, False) == 83400000
    assert timestamp.frame_to_time(1, TimeType.END, 9, False) == 125111111
    assert timestamp.frame_to_time(2, TimeType.END, 9, False) == 166822222
    assert timestamp.frame_to_time(3, TimeType.END, 9, False) == 208533333

    # TimeType.END - milliseconds - False
    assert timestamp.frame_to_time(0, TimeType.END, 3, False) == 83
    assert timestamp.frame_to_time(1, TimeType.END, 3, False) == 125
    assert timestamp.frame_to_time(2, TimeType.END, 3, False) == 166
    assert timestamp.frame_to_time(3, TimeType.END, 3, False) == 208

    # TimeType.END - nanoseconds - True
    # round((curr_frame_time + next_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.END, 9, True) == 62550000
    assert timestamp.frame_to_time(1, TimeType.END, 9, True) == 104255556
    assert timestamp.frame_to_time(2, TimeType.END, 9, True) == 145966667
    assert timestamp.frame_to_time(3, TimeType.END, 9, True) == 187677778

    # TimeType.END - milliseconds - True
    # round((curr_frame_time + next_frame_time) / 2)
    assert timestamp.frame_to_time(0, TimeType.END, 3, True) == 63
    assert timestamp.frame_to_time(1, TimeType.END, 3, True) == 104
    assert timestamp.frame_to_time(2, TimeType.END, 3, True) == 146
    assert timestamp.frame_to_time(3, TimeType.END, 3, True) == 188

@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.FLOOR, Fraction(90000), Fraction(24000, 1001), 3753),
        VideoTimestamps([3753, 7506, 11260, 15014, 18768, 22521], Fraction(90000), False),
        VideoTimestamps([3753, 7506, 11260], Fraction(90000), False, Fraction(24000, 1001), RoundingMethod.FLOOR), # Test VideoTimestamps over the video lenght
    ],
)
def test_time_to_frame_floor_first_pts_over_0(timestamp: ABCTimestamps) -> None:

    # TimeType.EXACT - precision
    with pytest.raises(ValueError) as exc_info:
        timestamp.time_to_frame(Fraction(3752, 90000), TimeType.EXACT, None)
    assert str(exc_info.value) == f"You cannot specify a time under the first timestamps {Fraction(3753, 90000)} with the TimeType.EXACT."
    assert timestamp.time_to_frame(Fraction(3753, 90000), TimeType.EXACT, None) == 0
    assert timestamp.time_to_frame(Fraction(7506, 90000), TimeType.EXACT, None) == 1
    assert timestamp.time_to_frame(Fraction(11260, 90000), TimeType.EXACT, None) == 2
    assert timestamp.time_to_frame(Fraction(15014, 90000), TimeType.EXACT, None) == 3

    # TimeType.EXACT - nanoseconds
    assert timestamp.time_to_frame(41700000, TimeType.EXACT, 9) == 0
    assert timestamp.time_to_frame(83399999, TimeType.EXACT, 9) == 0
    assert timestamp.time_to_frame(83400000, TimeType.EXACT, 9) == 1
    assert timestamp.time_to_frame(125111111, TimeType.EXACT, 9) == 1
    assert timestamp.time_to_frame(125111112, TimeType.EXACT, 9) == 2
    assert timestamp.time_to_frame(166822222, TimeType.EXACT, 9) == 2
    assert timestamp.time_to_frame(166822223, TimeType.EXACT, 9) == 3
    assert timestamp.time_to_frame(208533333, TimeType.EXACT, 9) == 3
    assert timestamp.time_to_frame(208533334, TimeType.EXACT, 9) == 4

    # TimeType.EXACT - milliseconds
    assert timestamp.time_to_frame(42, TimeType.EXACT, 3) == 0
    assert timestamp.time_to_frame(83, TimeType.EXACT, 3) == 0
    assert timestamp.time_to_frame(84, TimeType.EXACT, 3) == 1
    assert timestamp.time_to_frame(125, TimeType.EXACT, 3) == 1
    assert timestamp.time_to_frame(126, TimeType.EXACT, 3) == 2
    assert timestamp.time_to_frame(166, TimeType.EXACT, 3) == 2
    assert timestamp.time_to_frame(167, TimeType.EXACT, 3) == 3
    assert timestamp.time_to_frame(208, TimeType.EXACT, 3) == 3
    assert timestamp.time_to_frame(209, TimeType.EXACT, 3) == 4


    # TimeType.START - precision
    assert timestamp.time_to_frame(Fraction(3753, 90000), TimeType.START, None) == 0
    assert timestamp.time_to_frame(Fraction(7506, 90000), TimeType.START, None) == 1
    assert timestamp.time_to_frame(Fraction(11260, 90000), TimeType.START, None) == 2
    assert timestamp.time_to_frame(Fraction(15014, 90000), TimeType.START, None) == 3
    assert timestamp.time_to_frame(Fraction(18768, 90000), TimeType.START, None) == 4

    # TimeType.START - nanoseconds
    assert timestamp.time_to_frame(41700000, TimeType.START, 9) == 0
    assert timestamp.time_to_frame(41700001, TimeType.START, 9) == 1
    assert timestamp.time_to_frame(83400000, TimeType.START, 9) == 1
    assert timestamp.time_to_frame(83400001, TimeType.START, 9) == 2
    assert timestamp.time_to_frame(125111111, TimeType.START, 9) == 2
    assert timestamp.time_to_frame(125111112, TimeType.START, 9) == 3
    assert timestamp.time_to_frame(166822222, TimeType.START, 9) == 3
    assert timestamp.time_to_frame(166822223, TimeType.START, 9) == 4

    # TimeType.START - milliseconds
    assert timestamp.time_to_frame(41, TimeType.START, 3) == 0
    assert timestamp.time_to_frame(42, TimeType.START, 3) == 1
    assert timestamp.time_to_frame(83, TimeType.START, 3) == 1
    assert timestamp.time_to_frame(84, TimeType.START, 3) == 2
    assert timestamp.time_to_frame(125, TimeType.START, 3) == 2
    assert timestamp.time_to_frame(126, TimeType.START, 3) == 3
    assert timestamp.time_to_frame(166, TimeType.START, 3) == 3
    assert timestamp.time_to_frame(167, TimeType.START, 3) == 4


    # TimeType.END - precision
    with pytest.raises(ValueError) as exc_info:
        timestamp.time_to_frame(Fraction(3753, 90000), TimeType.END, None)
    assert str(exc_info.value) == f"You cannot specify a time under or equals the first timestamps {Fraction(3753, 90000)} with the TimeType.END."
    assert timestamp.time_to_frame(Fraction(3754, 90000), TimeType.END, None) == 0
    assert timestamp.time_to_frame(Fraction(7506, 90000), TimeType.END, None) == 0
    assert timestamp.time_to_frame(Fraction(11260, 90000), TimeType.END, None) == 1
    assert timestamp.time_to_frame(Fraction(15014, 90000), TimeType.END, None) == 2
    assert timestamp.time_to_frame(Fraction(18768, 90000), TimeType.END, None) == 3

    # TimeType.END - nanoseconds
    assert timestamp.time_to_frame(41700001, TimeType.END, 9) == 0
    assert timestamp.time_to_frame(83400000, TimeType.END, 9) == 0
    assert timestamp.time_to_frame(83400001, TimeType.END, 9) == 1
    assert timestamp.time_to_frame(125111111, TimeType.END, 9) == 1
    assert timestamp.time_to_frame(125111112, TimeType.END, 9) == 2
    assert timestamp.time_to_frame(166822222, TimeType.END, 9) == 2
    assert timestamp.time_to_frame(166822223, TimeType.END, 9) == 3
    assert timestamp.time_to_frame(208533333, TimeType.END, 9) == 3
    assert timestamp.time_to_frame(208533334, TimeType.END, 9) == 4

    # TimeType.END - milliseconds
    assert timestamp.time_to_frame(42, TimeType.END, 3) == 0
    assert timestamp.time_to_frame(83, TimeType.END, 3) == 0
    assert timestamp.time_to_frame(84, TimeType.END, 3) == 1
    assert timestamp.time_to_frame(125, TimeType.END, 3) == 1
    assert timestamp.time_to_frame(126, TimeType.END, 3) == 2
    assert timestamp.time_to_frame(166, TimeType.END, 3) == 2


@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.FLOOR, Fraction(90000), Fraction(24000, 1001)),
        VideoTimestamps([0, 3753, 7507, 11261, 15015, 18768], Fraction(90000)),
        VideoTimestamps([0, 3753, 7507], Fraction(90000), fps=Fraction(24000, 1001)), # Test VideoTimestamps over the video lenght
    ],
)
def test_frame_to_pts_floor(timestamp: ABCTimestamps) -> None:

    # TimeType.EXACT
    assert timestamp.frame_to_pts(0, TimeType.EXACT) == 0
    assert timestamp.frame_to_pts(1, TimeType.EXACT) == 3753
    assert timestamp.frame_to_pts(2, TimeType.EXACT) == 7507
    assert timestamp.frame_to_pts(3, TimeType.EXACT) == 11261
    assert timestamp.frame_to_pts(4, TimeType.EXACT) == 15015

    # TimeType.START
    assert timestamp.frame_to_pts(0, TimeType.START) == 0
    assert timestamp.frame_to_pts(1, TimeType.START) == 3753
    assert timestamp.frame_to_pts(2, TimeType.START) == 7507
    assert timestamp.frame_to_pts(3, TimeType.START) == 11261
    assert timestamp.frame_to_pts(4, TimeType.START) == 15015

    # TimeType.END
    assert timestamp.frame_to_pts(0, TimeType.END) == 3753
    assert timestamp.frame_to_pts(1, TimeType.END) == 7507
    assert timestamp.frame_to_pts(2, TimeType.END) == 11261
    assert timestamp.frame_to_pts(3, TimeType.END) == 15015
    assert timestamp.frame_to_pts(4, TimeType.END) == 18768


@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.FLOOR, Fraction(90000), Fraction(24000, 1001)),
        VideoTimestamps([0, 3753, 7507, 11261, 15015, 18768], Fraction(90000)),
        VideoTimestamps([0, 3753, 7507], Fraction(90000), fps=Fraction(24000, 1001)), # Test VideoTimestamps over the video lenght
    ],
)
def test_frame_to_pts_floor_with_timescale(timestamp: ABCTimestamps) -> None:
    MPLS_TIMESCALE = Fraction(45000)

    # TimeType.EXACT
    assert timestamp.frame_to_pts(0, TimeType.EXACT, MPLS_TIMESCALE) == ceil(0 / 2)
    assert timestamp.frame_to_pts(1, TimeType.EXACT, MPLS_TIMESCALE) == ceil(3753 / 2)
    assert timestamp.frame_to_pts(2, TimeType.EXACT, MPLS_TIMESCALE) == ceil(7507 / 2)
    assert timestamp.frame_to_pts(3, TimeType.EXACT, MPLS_TIMESCALE) == ceil(11261 / 2)
    assert timestamp.frame_to_pts(4, TimeType.EXACT, MPLS_TIMESCALE) == ceil(15015 / 2)

    # TimeType.START
    assert timestamp.frame_to_pts(0, TimeType.START, MPLS_TIMESCALE) == 0 // 2
    assert timestamp.frame_to_pts(1, TimeType.START, MPLS_TIMESCALE) == 3753 // 2
    assert timestamp.frame_to_pts(2, TimeType.START, MPLS_TIMESCALE) == 7507 // 2
    assert timestamp.frame_to_pts(3, TimeType.START, MPLS_TIMESCALE) == 11261 // 2
    assert timestamp.frame_to_pts(4, TimeType.START, MPLS_TIMESCALE) == 15015 // 2

    # TimeType.END
    assert timestamp.frame_to_pts(0, TimeType.END, MPLS_TIMESCALE) == 3753 // 2
    assert timestamp.frame_to_pts(1, TimeType.END, MPLS_TIMESCALE) == 7507 // 2
    assert timestamp.frame_to_pts(2, TimeType.END, MPLS_TIMESCALE) == 11261 // 2
    assert timestamp.frame_to_pts(3, TimeType.END, MPLS_TIMESCALE) == 15015 // 2
    assert timestamp.frame_to_pts(4, TimeType.END, MPLS_TIMESCALE) == 18768 // 2


@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.FLOOR, Fraction(90000), Fraction(24000, 1001)),
        VideoTimestamps([0, 3753, 7507, 11261, 15015, 18768], Fraction(90000)),
        VideoTimestamps([0, 3753, 7507], Fraction(90000), fps=Fraction(24000, 1001)), # Test VideoTimestamps over the video lenght
    ],
)
def test_pts_to_frame_floor(timestamp: ABCTimestamps) -> None:

    # TimeType.EXACT
    assert timestamp.pts_to_frame(0, TimeType.EXACT) == 0
    assert timestamp.pts_to_frame(3752, TimeType.EXACT) == 0
    assert timestamp.pts_to_frame(3753, TimeType.EXACT) == 1
    assert timestamp.pts_to_frame(7506, TimeType.EXACT) == 1
    assert timestamp.pts_to_frame(7507, TimeType.EXACT) == 2
    assert timestamp.pts_to_frame(11260, TimeType.EXACT) == 2
    assert timestamp.pts_to_frame(11261, TimeType.EXACT) == 3
    assert timestamp.pts_to_frame(15014, TimeType.EXACT) == 3
    assert timestamp.pts_to_frame(15015, TimeType.EXACT) == 4

    # TimeType.START
    assert timestamp.pts_to_frame(0, TimeType.START) == 0
    assert timestamp.pts_to_frame(1, TimeType.START) == 1
    assert timestamp.pts_to_frame(3753, TimeType.START) == 1
    assert timestamp.pts_to_frame(3754, TimeType.START) == 2
    assert timestamp.pts_to_frame(7507, TimeType.START) == 2
    assert timestamp.pts_to_frame(7508, TimeType.START) == 3
    assert timestamp.pts_to_frame(11261, TimeType.START) == 3
    assert timestamp.pts_to_frame(11262, TimeType.START) == 4
    assert timestamp.pts_to_frame(15015, TimeType.START) == 4

    # TimeType.END
    assert timestamp.pts_to_frame(1, TimeType.END) == 0
    assert timestamp.pts_to_frame(3753, TimeType.END) == 0
    assert timestamp.pts_to_frame(3754, TimeType.END) == 1
    assert timestamp.pts_to_frame(7507, TimeType.END) == 1
    assert timestamp.pts_to_frame(7508, TimeType.END) == 2
    assert timestamp.pts_to_frame(11261, TimeType.END) == 2
    assert timestamp.pts_to_frame(11262, TimeType.END) == 3
    assert timestamp.pts_to_frame(15015, TimeType.END) == 3


@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.FLOOR, Fraction(90000), Fraction(24000, 1001)),
        VideoTimestamps([0, 3753, 7507, 11261, 15015, 18768], Fraction(90000)),
        VideoTimestamps([0, 3753, 7507], Fraction(90000), fps=Fraction(24000, 1001)), # Test VideoTimestamps over the video lenght
    ],
)
def test_pts_to_frame_floor_with_timescale(timestamp: ABCTimestamps) -> None:
    MPLS_TIMESCALE = Fraction(45000)

    # TimeType.EXACT
    assert timestamp.pts_to_frame(ceil(0 / 2), TimeType.EXACT, MPLS_TIMESCALE) == 0
    assert timestamp.pts_to_frame(ceil(3753 / 2), TimeType.EXACT, MPLS_TIMESCALE) == 1
    assert timestamp.pts_to_frame(ceil(7507 / 2), TimeType.EXACT, MPLS_TIMESCALE) == 2
    assert timestamp.pts_to_frame(ceil(11261 / 2), TimeType.EXACT, MPLS_TIMESCALE) == 3
    assert timestamp.pts_to_frame(ceil(15015 / 2), TimeType.EXACT, MPLS_TIMESCALE) == 4

    # TimeType.START
    assert timestamp.pts_to_frame(0 // 2, TimeType.START, MPLS_TIMESCALE) == 0
    assert timestamp.pts_to_frame(3753 // 2, TimeType.START, MPLS_TIMESCALE) == 1
    assert timestamp.pts_to_frame(7507 // 2, TimeType.START, MPLS_TIMESCALE) == 2
    assert timestamp.pts_to_frame(11261 // 2, TimeType.START, MPLS_TIMESCALE) == 3
    assert timestamp.pts_to_frame(15015 // 2, TimeType.START, MPLS_TIMESCALE) == 4

    # TimeType.END
    assert timestamp.pts_to_frame(3753 // 2, TimeType.END, MPLS_TIMESCALE) == 0
    assert timestamp.pts_to_frame(7507 // 2, TimeType.END, MPLS_TIMESCALE) == 1
    assert timestamp.pts_to_frame(11261 // 2, TimeType.END, MPLS_TIMESCALE) == 2
    assert timestamp.pts_to_frame(15015 // 2, TimeType.END, MPLS_TIMESCALE) == 3
    assert timestamp.pts_to_frame(18768 // 2, TimeType.END, MPLS_TIMESCALE) == 4


@pytest.mark.parametrize(
    "timestamp",
    [
        FPSTimestamps(RoundingMethod.FLOOR, Fraction(90000), Fraction(24000, 1001)),
        VideoTimestamps([0, 3753, 7507, 11261, 15015, 18768], Fraction(90000)),
        VideoTimestamps([0, 3753, 7507], Fraction(90000), fps=Fraction(24000, 1001)), # Test VideoTimestamps over the video lenght
    ],
)
def test_move_time_to_frame(timestamp: ABCTimestamps) -> None:

    assert timestamp.move_time_to_frame(30, TimeType.EXACT, 3, 3) == 0
    assert timestamp.move_time_to_frame(50, TimeType.EXACT, 3, 3) == 42
    # Test without specifying the input_unit
    assert timestamp.move_time_to_frame(Fraction(50, 1000), TimeType.EXACT, 3) == 42
