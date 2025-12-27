# VideoTimestamps documentation

This tool allows recovering the timestamps of each frame in a video in any unit (seconds, milliseconds, nanoseconds, etc.).
It also helps convert a frame to a time in any units and vice versa.

## Example code

```python
--8<-- "examples/get_timestamps.py"
```

Output
```
For the fps 24000/1001, the frame 10 start at 417/1000 s and end at 459/1000 s.
For the fps 24000/1001, the frame 10 start at 417 ms and end at 459 ms.
```
