from fractions import Fraction

from video_timestamps import FPSTimestamps, RoundingMethod, TimeType

fps = Fraction(24000, 1001)
time_scale = Fraction(1000)
# Read the documentation to find out which RoundingMethod suits your needs.
# You can also create a ABCTimestamps instance with FPSTimestamps, VideoTimestamps or TextFileTimestamps
timestamps = FPSTimestamps(RoundingMethod.ROUND, time_scale, fps)

frame = 10
# Max precision
start_time_in_seconds = timestamps.frame_to_time(frame, TimeType.START)
end_time_in_seconds = timestamps.frame_to_time(frame, TimeType.END)
print(f"For the fps {fps}, the frame {frame} start at {start_time_in_seconds} s and end at {end_time_in_seconds} s.")

# Precision in milliseconds
start_time_in_ms = timestamps.frame_to_time(frame, TimeType.START, 3)
end_time_in_ms = timestamps.frame_to_time(frame, TimeType.END, 3)
print(f"For the fps {fps}, the frame {frame} start at {start_time_in_ms} ms and end at {end_time_in_ms} ms.")
