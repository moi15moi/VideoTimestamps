from .mkvextract import MKVExtract
from .mkvmerge import MKVMerge
from ..timestamps import Timestamps
from ..abc_video_parser import ABCVideoParser
from ..rounding_method import RoundingMethod
from fractions import Fraction
from pathlib import Path


class MKVToolNixTimestamps(ABCVideoParser):

    @staticmethod
    def is_available() -> bool:
        return MKVExtract.is_mkv_extract_installed() and MKVMerge.is_mkv_merge_installed()


    @staticmethod
    def get_timestamps(video_path: Path, index: int, normalize: bool, rounding_method: RoundingMethod) -> tuple[Timestamps, Fraction]:
        mkvmerge_version = MKVMerge.get_version()
        if mkvmerge_version < (82, 0):
            # We need the version 82.0 for the timestamp_scale properties: https://help.mkvtoolnix.download/t/how-to-get-timestamp-scale-information-without-using-mkvinfo/299/3
            raise OSError(f"You need at least the version 82.0 of mkvmerge. You have the version {mkvmerge_version[0]}.{mkvmerge_version[1]}")

        mkv_info = MKVMerge.get_mkv_info(video_path)

        is_index_in_video = False
        for track in mkv_info["tracks"]:
            if track["id"] == index:
                if track["type"] != "video":
                    raise ValueError(f'The index {index} is not a video stream. It is an "{track["type"]}" stream.')
                is_index_in_video = True
                break

        if not is_index_in_video:
            raise ValueError(f"The index {index} is not in the file {video_path}.")

        timestamp_scale = mkv_info["container"]["properties"]["timestamp_scale"]
        # Technically, time_base = TimestampScale * TrackTimestampScale / 10^9
        # but mkvmerge doesn't report the TrackTimestampScale.
        # Even the MKVToolNix author suggested me to ignore the TrackTimestampScale [here](https://help.mkvtoolnix.download/t/how-to-get-timestamp-scale-information-without-using-mkvinfo/299/6?u=moi15moi)
        time_base = Fraction(timestamp_scale, 10**9)

        content = MKVExtract.get_timestamps_file_content(video_path, index)

        from ..timestamps_factory import TimestampsFactory
        timestamps = TimestampsFactory.from_timestamps_file(
            content,
            normalize,
            rounding_method
        )

        return timestamps, time_base
