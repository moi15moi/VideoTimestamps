import os
import shutil
import subprocess
from datetime import timedelta
from fractions import Fraction
from textwrap import dedent

from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # create an image
    out = Image.new("RGB", (1280, 720), (255, 255, 255))

    # get a font
    font = ImageFont.truetype(os.path.join(dir_path, "Alegreya-Bold.otf"), 32)

    fps = Fraction(24000, 1001)
    num_frames = 500

    # If img folder exist, delete it
    if os.path.isdir(os.path.join(dir_path, "img")):
        shutil.rmtree(os.path.join(dir_path, "img"))

    os.makedirs(os.path.join(dir_path, "img"))

    for frame in range(num_frames):
        canvas = out.copy()
        # get a drawing context
        d = ImageDraw.Draw(canvas)

        ms = round(1000 * frame * 1 / fps)
        us = round(1000_000 * frame * 1 / fps)
        t1 = timedelta(microseconds=us)
        text = dedent(
            f"""\
        Frame {frame:04}
        T = {ms:06} ms ({t1}) @ {float(fps):.3f} fps
        """
        ).strip()
        # draw multiline text
        d.multiline_text((10, 10), text, font=font, fill=(0, 0, 0))

        canvas.save(os.path.join(dir_path, "img", f"test_video_{frame:04}.png"))

    # Create 1 mp4 and 1 mkv video with an silence audio track
    video_formats = ["mp4", "mkv"]
    for format in video_formats:
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-r",
                f"{fps}",
                "-i",
                os.path.join(dir_path, "img", "test_video_%04d.png"),
                "-f",
                "lavfi",
                "-i",
                "anullsrc",
                "-pix_fmt",
                "yuv420p",
                "-shortest",
                os.path.join(dir_path, f"test_video.{format}"),
            ]
        )

    # Create a avi without the sound. It can create problem with it
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-r",
            f"{fps}",
            "-i",
            os.path.join(dir_path, "img", "test_video_%04d.png"),
            "-pix_fmt",
            "yuv420p",
            os.path.join(dir_path, "test_video.avi"),
        ]
    )

    # I don't know why, but this create a video without pts_time. This is usefull to test bestsource/ffms2
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            os.path.join(dir_path, "test_video.mp4"),
            "-vcodec",
            "copy",
            os.path.join(dir_path, "video_without_pts_time.avi"),
        ]
    )

    # Create a mkv with negative PTS
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            os.path.join(dir_path, "test_video.mp4"),
            "-video_track_timescale",
            "90000",
            "-bsf:v",
            "setts=ts=(N/TB*1001/24000)-5",
            os.path.join(dir_path, "video_with_negative_pts.mp4"),
        ]
    )

    # Create a mkv with microsecond timestamps precision
    subprocess.check_call(
        [
            "mkvmerge",
            "--output",
            os.path.join(dir_path, "mkv_timescale_us.mkv"),
            "--timestamp-scale",
            "1000",  # 1000 means microsecond
            "--default-duration",
            "0:24000/1001p",
            os.path.join(dir_path, "test_video.mkv"),
        ]
    )

    # Create a mkv with centisecond timestamps precision
    subprocess.check_call(
        [
            "mkvmerge",
            "--output",
            os.path.join(dir_path, "mkv_timescale_cs.mkv"),
            "--timestamp-scale",
            "10000000",  # 10000000 means centisecond
            "--default-duration",
            "0:24000/1001p",
            os.path.join(dir_path, "test_video.mkv"),
        ]
    )

    # Create a video with only 10 frames
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-r",
            f"{fps}",
            "-i",
            os.path.join(dir_path, "img", "test_video_%04d.png"),
            "-f",
            "lavfi",
            "-i",
            "anullsrc",
            "-frames:v", "10", # only first 10 frames
            "-pix_fmt",
            "yuv420p",
            "-shortest",
            os.path.join(dir_path, "test_video_10_frames_temp.mkv"),
        ]
    )

    subprocess.check_call(
        [
            "mkvmerge",
            "--output",
            os.path.join(dir_path, "test_video_10_frames.mkv"),
            "--timestamps",
            f"0:{os.path.join(dir_path, 'timestamps_test_video_10_frames.txt')}",
            os.path.join(dir_path, "test_video_10_frames_temp.mkv"),
        ]
    )

    os.remove(os.path.join(dir_path, "test_video_10_frames_temp.mkv"))

    # If img folder exist, delete it
    if os.path.isdir(os.path.join(dir_path, "img")):
        shutil.rmtree(os.path.join(dir_path, "img"))


if __name__ == "__main__":
    main()
