import os
from fractions import Fraction
from pathlib import Path

import pytest

from video_timestamps import (
    ABCVideoProvider,
    BestSourceVideoProvider,
    FFMS2VideoProvider
)

dir_path = Path(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


@pytest.mark.parametrize("video_provider", [BestSourceVideoProvider(), FFMS2VideoProvider()])
def test_get_pts_mkv(video_provider: ABCVideoProvider) -> None:
    video_file_path = dir_path.joinpath("files", "test_video.mkv")
    pts_list, time_base, fps = video_provider.get_pts(str(video_file_path), 0)

    assert len(pts_list) == 501
    assert pts_list[:10] == [3, 45, 86, 128, 170, 212, 253, 295, 337, 378]
    assert pts_list[-10:] == [20482, 20524, 20565, 20607, 20649, 20690, 20732, 20774, 20815, 20856]
    assert time_base == Fraction(1, 1000)
    assert fps == Fraction(24000, 1001)


@pytest.mark.parametrize("video_provider", [BestSourceVideoProvider(), FFMS2VideoProvider()])
def test_get_pts_mp4(video_provider: ABCVideoProvider) -> None:
    video_file_path = dir_path.joinpath("files", "test_video.mp4")
    pts_list, time_base, fps = video_provider.get_pts(str(video_file_path), 0)

    assert len(pts_list) == 501
    assert pts_list[:10] == [0, 1001, 2002, 3003, 4004, 5005, 6006, 7007, 8008, 9009]
    assert pts_list[-10:] == [491491, 492492, 493493, 494494, 495495, 496496, 497497, 498498, 499499, 500500]
    assert time_base == Fraction(1, 24000)
    assert fps == Fraction(24000, 1001)


@pytest.mark.parametrize("video_provider", [BestSourceVideoProvider(), FFMS2VideoProvider()])
def test_get_pts_avi(video_provider: ABCVideoProvider) -> None:
    video_file_path = dir_path.joinpath("files", "test_video.avi")
    pts_list, time_base, fps = video_provider.get_pts(str(video_file_path), 0)

    assert len(pts_list) == 501
    assert pts_list[:10] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert pts_list[-10:] == [491, 492, 493, 494, 495, 496, 497, 498, 499, 500]
    assert time_base == Fraction(1001, 24000)
    assert fps == Fraction(24000, 1001)


@pytest.mark.parametrize("video_provider", [BestSourceVideoProvider(), FFMS2VideoProvider()])
def test_get_pts_file_without_pts(video_provider: ABCVideoProvider) -> None:
    video_file_path = dir_path.joinpath("files", "video_without_pts_time.avi")
    pts_list, time_base, fps = video_provider.get_pts(str(video_file_path), 0)

    assert pts_list[:10] == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
    assert pts_list[-10:] == [982, 984, 986, 988, 990, 992, 994, 996, 998, 999]
    assert time_base == Fraction(1001, 48000)
    assert fps == Fraction(24000, 1001)


@pytest.mark.parametrize("video_provider", [FFMS2VideoProvider()])
def test_get_pts_file_with_negative_pts(video_provider: ABCVideoProvider) -> None:
    # We don't test this with bestsource because the video is broken and bestsource return us unordered PTS. For more info, see: https://github.com/vapoursynth/bestsource/issues/105
    video_file_path = dir_path.joinpath("files", "video_with_negative_pts.mp4")
    pts_list, time_base, fps = video_provider.get_pts(str(video_file_path), 0)

    assert len(pts_list) == 496
    assert pts_list[:10] == [0, 3754, 7508, 11261, 15015, 18769, 22523, 26276, 30030, 33784]
    assert pts_list[-10:] == [1824323, 1828076, 1831830, 1835584, 1839338, 1843091, 1846845, 1850599, 1854353, 1858107]
    assert time_base == Fraction(1, 90000)
    assert fps == Fraction(100000, 4213)


@pytest.mark.parametrize("video_provider", [BestSourceVideoProvider(), FFMS2VideoProvider()])
def test_get_pts_mkv_cs(video_provider: ABCVideoProvider) -> None:
    video_file_path = dir_path.joinpath("files", "mkv_timescale_cs.mkv")
    pts_list, time_base, fps = video_provider.get_pts(str(video_file_path), 0)

    assert len(pts_list) == 501
    assert pts_list[:10] == [0, 4, 8, 13, 17, 21, 25, 29, 33, 38]
    assert pts_list[-10:] == [2048, 2052, 2056, 2060, 2065, 2069, 2073, 2077, 2081, 2085]
    assert time_base == Fraction(1, pow(10, 2))
    assert fps == Fraction(24000, 1001)


@pytest.mark.parametrize("video_provider", [BestSourceVideoProvider(), FFMS2VideoProvider()])
def test_get_pts_mkv_us(video_provider: ABCVideoProvider) -> None:
    video_file_path = dir_path.joinpath("files", "mkv_timescale_us.mkv")
    pts_list, time_base, fps = video_provider.get_pts(str(video_file_path), 0)

    assert len(pts_list) == 501
    assert pts_list[:10] == [0, 41708, 83417, 125125, 166833, 208542, 250250, 291958, 333667, 375375]
    assert pts_list[-10:] == [20478792, 20520500, 20562208, 20603917, 20645625, 20687333, 20729042, 20770750, 20812458, 20854166]
    assert time_base == Fraction(1, pow(10, 6))
    assert fps == Fraction(24000, 1001)


@pytest.mark.parametrize("video_provider", [BestSourceVideoProvider(), FFMS2VideoProvider()])
def test_get_pts_mkv_10_frames(video_provider: ABCVideoProvider) -> None:
    video_file_path = dir_path.joinpath("files", "test_video_10_frames.mkv")
    pts_list, time_base, fps = video_provider.get_pts(str(video_file_path), 0)

    assert pts_list == [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 475]
    assert time_base == Fraction(1, 1000)
    assert fps == Fraction(20)


@pytest.mark.parametrize("video_provider", [BestSourceVideoProvider(), FFMS2VideoProvider()])
def test_get_pts_non_video_index(video_provider: ABCVideoProvider) -> None:
    video_file_path = dir_path.joinpath("files", "test_video.mkv")

    with pytest.raises(ValueError) as exc_info:
        video_provider.get_pts(str(video_file_path), 1)
    assert str(exc_info.value) == "The index 1 is not a video stream. It is an \"audio\" stream."


@pytest.mark.parametrize("video_provider", [BestSourceVideoProvider(), FFMS2VideoProvider()])
def test_get_pts_invalid_index(video_provider: ABCVideoProvider) -> None:
    video_file_path = dir_path.joinpath("files", "test_video.mkv")

    with pytest.raises(ValueError) as exc_info:
        video_provider.get_pts(str(video_file_path), 2)
    assert str(exc_info.value) == f"The index 2 is not in the file {video_file_path}."


@pytest.mark.parametrize("video_provider", [BestSourceVideoProvider(), FFMS2VideoProvider()])
def test_is_instance_ABCVideoProvider(video_provider: ABCVideoProvider) -> None:
    assert isinstance(video_provider, ABCVideoProvider)
