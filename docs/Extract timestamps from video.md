## Usage
```console
$ extracttimestamps --help
usage: extracttimestamps [-h] [-o OUTPUT] [-i INDEX] [-n] [-vp {ffms2,bestsource}] [--precision PRECISION] [--precision-rounding {floor,round,ceil}] [--use-fraction] video

Video timestamps extractor.

positional arguments:
  video                 Path to the video file to extract timestamps from.

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Path to save the timestamps file. By default, it will be saved in the same directory as the video with the video name and index. Example: For "video.mkv" and --index 1, it will be "video_1.txt".
  -i, --index INDEX     Index of the track to extract timestamps from (default: 0).
  -n, --normalize       If specified, shift the timestamps to make them start from 0.
  -vp, --video-provider {ffms2,bestsource}
                        Video provider to use for timestamps extraction (default: ffms2).
  --precision PRECISION
                        Number of decimal places for timestamps (default: 9). Common values: - 3 means milliseconds - 6 means microseconds - 9 means nanoseconds
  --precision-rounding {floor,round,ceil}
                        Rounding method to use for timestamps (default: round). Examples: - Timestamp: 453.4 ms, --precision 3, --precision-rounding round --> 453 - Timestamp: 453.4569 ms, --precision 6, --precision-rounding round --> 453.457
  --use-fraction        If specified, the timestamps produced will be represented has a fraction (ex: "30/2") instead of decimal (ex: "3.434"). Note that this is not a conform to the specification.
```
