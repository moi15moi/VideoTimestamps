from fractions import Fraction

__all__ = ['ABCVideoProvider']

class ABCVideoProvider:
    def get_pts(self, filename: str, index: int | None, video_stream_index: int | None = None) -> tuple[list[int], Fraction, Fraction]:
        """
        Parameters:
            filename: A video path.
            index: Absolute index of the stream in the file. Its position among *all* streams
                (audio, video, subtitles, etc.), regardless of their type.

                This is equivalent to ffmpeg/ffprobe's global stream index (ex: the `0` in `-map 0:0`).
                The stream at this index must be a video stream.

                Mutually exclusive with `video_stream_index`. Exactly one of the two must be specified.
            video_stream_index: Index of the video stream, relative to the other video streams in the file.

                This is equivalent to ffmpeg's `v` stream specifier (ex: `v:0` is the first video stream,
                `v:1` is the second video stream, etc).

                Mutually exclusive with `index`. Exactly one of the two must be specified.

        Returns:
            A tuple containing these 3 informations:

                1. A list of each frame's pts. The last pts correspond to the pts of the last frame + it's duration.
                2. The time_base.
                3. The fps.
        """
