from fractions import Fraction
from video_timestamps import TimestampsFactory, TimeType, RoundingMethod


def main() -> None:
    fps = Fraction(24000, 1001)
    timestamps = TimestampsFactory.from_fps(fps)

    # Read the documentation to find out which RoundingMethod suits your needs.
    frame = 10
    start_time = timestamps.frames_to_ms(frame, TimeType.START, RoundingMethod.FLOOR)
    end_time = timestamps.frames_to_ms(frame, TimeType.END, RoundingMethod.FLOOR)

    print(f"For the fps {fps}, the frame {frame} start at {start_time} ms and end at {end_time} ms.")

if __name__ == "__main__":
    main()
