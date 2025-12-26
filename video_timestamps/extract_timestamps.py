from argparse import ArgumentParser
from math import ceil, floor
from pathlib import Path

from .rounding_method import RoundingCallType, RoundingMethod
from .video_provider import (
    ABCVideoProvider,
    BestSourceVideoProvider,
    FFMS2VideoProvider
)
from .video_timestamps import VideoTimestamps


def main() -> None:
    parser = ArgumentParser(
        description="Video timestamps extractor."
    )
    parser.add_argument(
        "video",
        type=Path,
        help="""
        Path to the video file to extract timestamps from.
    """,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="""
        Path to save the timestamps file.
        By default, it will be saved in the same directory as the video with the video name and index.
        Example: For "video.mkv" and --index 1, it will be "video_1.txt".
    """,
    )
    parser.add_argument(
        "-i",
        "--index",
        default=0,
        type=int,
        help="""
        Index of the track to extract timestamps from (default: 0).
    """,
    )
    parser.add_argument(
        "-n",
        "--normalize",
        action="store_true",
        help="""
        If specified, shift the timestamps to make them start from 0.
    """,
    )
    parser.add_argument(
        "-vp",
        "--video-provider",
        choices=["ffms2", "bestsource"],
        default="ffms2",
        help="""
        Video provider to use for timestamps extraction (default: ffms2).
    """,
    )
    parser.add_argument(
        "--precision",
        type=int,
        default=9,
        help="""
        Number of decimal places for timestamps (default: 9).
        Common values:
        - 3 means milliseconds
        - 6 means microseconds
        - 9 means nanoseconds
    """,
    )
    parser.add_argument(
        "--precision-rounding",
        choices=["floor", "round", "ceil"],
        default="round",
        help="""
        Rounding method to use for timestamps (default: round).
        Examples:
        - Timestamp: 453.4 ms, --precision 3, --precision-rounding round --> 453
        - Timestamp: 453.4569 ms, --precision 6, --precision-rounding round --> 453.457
        """,
    )
    parser.add_argument(
        "--use-fraction",
        action="store_true",
        help="""
        If specified, the timestamps produced will be represented has a fraction (ex: "30/2") instead of decimal (ex: "3.434").
        Note that this is not a conform to the specification.
    """,
    )

    args = parser.parse_args()

    video_path: Path = args.video
    video_index: int = args.index
    normalize: bool = args.normalize
    use_fraction: bool = args.use_fraction
    precision: int = args.precision

    timestamps_filename: Path
    if args.output is not None:
        timestamps_filename = args.output
    else:
        # Remove the video file extension and add "_VIDEO_INDEX.txt"
        timestamps_filename = video_path.with_suffix("").with_name(video_path.stem + f"_{video_index}").with_suffix(".txt")

    video_provider: ABCVideoProvider
    if args.video_provider == "ffms2":
        video_provider = FFMS2VideoProvider()
    elif args.video_provider == "bestsource":
        video_provider = BestSourceVideoProvider()
    else:
        raise ValueError(f"The provider \"{args.video_provider}\" is not supported.")

    precision_rounding: RoundingCallType
    if args.precision_rounding == "floor":
        precision_rounding = floor
    elif args.precision_rounding == "round":
        precision_rounding = RoundingMethod.ROUND
    elif args.precision_rounding == "ceil":
        precision_rounding = ceil
    else:
        raise ValueError(f"The precision-rounding \"{args.precision_rounding}\" is not supported.")

    video_timestamps = VideoTimestamps.from_video_file(video_path, video_index, normalize, video_provider=video_provider)
    if use_fraction:
        video_timestamps.export_timestamps(timestamps_filename, use_fraction=use_fraction)
    else:
        video_timestamps.export_timestamps(timestamps_filename, precision=precision, precision_rounding=precision_rounding)


if __name__ == "__main__":
    main()
