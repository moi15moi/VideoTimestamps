from fractions import Fraction
from video_timestamps import TimestampsFactory, TimeType, RoundingMethod


def main() -> None:
    fps = Fraction(24000, 1001)
    # Read the documentation to find out which RoundingMethod suits your needs.
    timestamps = TimestampsFactory.from_fps(fps, RoundingMethod.FLOOR)

    frame = 10
    start_time = timestamps.frames_to_ms(frame, TimeType.START)
    end_time = timestamps.frames_to_ms(frame, TimeType.END)

    print(f"For the fps {fps}, the frame {frame} start at {start_time} ms and end at {end_time} ms.")

if __name__ == "__main__":
    main()
