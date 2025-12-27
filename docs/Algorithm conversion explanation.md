## Introduction

To understand how ``frame_to_time`` and ``time_to_frame`` of [`FPSTimestamps`][video_timestamps.fps_timestamps.FPSTimestamps], we need to fully understand how [`TimeType`][video_timestamps.time_type.TimeType] works.

Here is an example of timestamps and their TimeType with a $fps = {24000 \over 1001}$, a $timebase = {1 \over 1000}$ and a $roundingMethod = \text{ROUND}$:

**Timestamps**

$$
\begin{gather}
\text{Frame 0}: 0 \text{ ms} \\
\text{Frame 1}: 42 \text{ ms} \\
\text{Frame 2}: 83 \text{ ms} \\
\text{Frame 3}: 125 \text{ ms} \\
\text{Frame 4}: 167 \text{ ms} \\
\text{Frame 5}: 209 \text{ ms}
\end{gather}
$$

**EXACT**

$$
\begin{gather}
\text{Frame 0}: [0, 42[ \text{ ms} \\
\text{Frame 1}: [42, 83[ \text{ ms} \\
\text{Frame 2}: [83, 167[ \text{ ms} \\
\text{Frame 3}: [167, 209[ \text{ ms} \\
\text{Frame 4}: [209, 250[ \text{ ms}
\end{gather}
$$

**START**

$$
\begin{gather}
\text{Frame 0}:  0 \text{ ms} \\
\text{Frame 1}: ]0, 42] \text{ ms} \\
\text{Frame 2}: ]42, 83] \text{ ms} \\
\text{Frame 3}: ]83, 167] \text{ ms} \\
\text{Frame 4}: ]167, 209] \text{ ms}
\end{gather}
$$

**END**

$$
\begin{gather}
\text{Frame 0}: ]0, 42] \text{ ms} \\
\text{Frame 1}: ]42, 83] \text{ ms} \\
\text{Frame 2}: ]83, 167] \text{ ms} \\
\text{Frame 3}: ]167, 209] \text{ ms} \\
\text{Frame 4}: ]209, 250] \text{ ms}
\end{gather}
$$

The interval for each type of timing are defined like this:

$$
\begin{gather}
\text{EXACT : } [\text{CurrentFrameTimestamps}, \text{NextFrameTimestamps}[ \\
\text{START : } ]\text{PreviousFrameTimestamps} , \text{CurrentFrameTimestamps}] \\
\text{END : } ]\text{CurrentFrameTimestamps}, \text{NextFrameTimestamps}]
\end{gather}
$$




## frame_to_time

A lot of people think that the time can be calculated like this: $time= frame \times {1 \over fps}$, but this is only a approximation. Actually, videos use this formula: $pts\_time= pts \times timebase$. So, the "real" name for $time$ is $pts\_time$, but note that, in some case, a video stream may not contains any $pts$. In those case, in general, player fallback to $dts$.

Important to note:

$$
\begin{gather}
pts \in \mathbb{N} \\
timebase \in \mathbb{Q}^{+} \\
pts\_time \in \mathbb{Q} \\
\end{gather}
$$

[Source for pts](https://ffmpeg.org/doxygen/7.0/structAVPacket.html#a73bde0a37f3b1efc839f11295bfbf42a)

[Source for timebase](https://www.ffmpeg.org/doxygen/7.0/structAVStream.html#a9db755451f14e2bf590d4b85d82b32e6)


But, how are $pts$ and $timebase$ setted?

The $timebase$ depend on the codec/container. For example, for .m2ts file, the $timebase$ will always be ${1 \over 90000}$. By default mkvtoolnix set the timebase to ${1 \over 1000}$. Important to note that there is a really similar value to $timebase$ called $timescale$. It is defined like this:

$$timescale = {1 \over timebase}$$

For the $pts$, it is simple, $pts = \text{roundingMethod}(frame \times ticks)$. The $\text{roundingMethod}$ depend on the implementation. For example, for .m2ts file, it will always be floored and mkvtoolnix will always round them. Note that the $ticks$ is defined like this:

$$ticks = {timescale \over fps}$$

So, in brief, the expended formula is:

$time = pts \times timebase$

$time = {\text{roundingMethod}(frame \times ticks) \over timescale}$

$time = {\text{roundingMethod}(frame \times {timescale \over fps}) \over timescale}$

This works, but it assume that the first frame start at PTS 0 which isn't necessary the case.
To avoid this, we could do this:

$time = {\text{roundingMethod}(frame \times {timescale \over fps}) + first\_pts \over timescale}$

But, to properly support v1 timestamps file, we need to do this:

$time = {\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale}$





### frame_to_time for TimeType.EXACT
$\text{EXACT : } [\text{CurrentFrameTimestamps}, \text{NextFrameTimestamps}[$

The lower bound is: $time = {\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale}$

The upper bound is: $time = {\text{roundingMethod}(({(frame + 1) \over fps} + first\_timestamps) \times timescale) \over timescale}$

### frame_to_time for TimeType.START
$\text{START : } ]\text{PreviousFrameTimestamps} , \text{CurrentFrameTimestamps}]$

The lower bound is: $time = {\text{roundingMethod}(({(frame - 1) \over fps} + first\_timestamps) \times timescale) \over timescale}$

The upper bound is: $time = {\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale}$

### frame_to_time for TimeType.END
$\text{END : } ]\text{CurrentFrameTimestamps}, \text{NextFrameTimestamps}]$

The lower bound is: $time = {\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale}$

The upper bound is: $time = {\text{roundingMethod}(({(frame + 1) \over fps} + first\_timestamps) \times timescale) \over timescale}$




## time_to_frame

### time_to_frame for TimeType.EXACT

``time_to_frame`` need to be exactly the inverse of ``frame_to_time``.
Since there are rounding operation, we cannot directly isolate it. To do so, we need to use the interval to our advantage. Here is a example:

$$
\begin{gather}
fps = 24000/1001 \\
\text{Frame 0}: [0, 42[ ms \\
\text{Frame 1}: [42, 83[ ms \\
\text{Frame 2}: [83, 125[ ms \\
\text{Frame 3}: [125, 167[ ms
\end{gather}
$$

PS: *The number are in milliseconds for simplicity, but actually, the formula give time in second.*

With that in mind, we know can say that the property says that we need to use the largest $frame$ such that the $frame$ does not exceed the requested $time$.

From that property, we can deduce this equation: ${\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale} \leq time$

We can isolate our roundingMethod like this: $\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \leq time \times timescale$

Now, we have an inequation and it is possible to isolate properly our $frame$ variable. Since the $\text{roundingMethod}$ can be floor or rounded, we will have 2 final equations that are described below:

#### Explanation for rounding method
$\text{round}(({frame \over fps} + first\_timestamps) \times timescale) \leq time \times timescale$

$({frame \over fps} + first\_timestamps) \times timescale < \lfloor time \times timescale \rfloor + 0.5$

${frame \over fps} + first\_timestamps < {\lfloor time \times timescale \rfloor + 0.5 \over timescale}$

${frame \over fps} < {\lfloor time \times timescale \rfloor + 0.5 \over timescale} - first\_timestamps$

$frame < ({\lfloor time \times timescale \rfloor + 0.5 \over timescale} - first\_timestamps) \times fps$

$frame < \lceil ({\lfloor time \times timescale \rfloor + 0.5 \over timescale} - first\_timestamps) \times fps \rceil$

$frame \leq \lceil ({\lfloor time \times timescale \rfloor + 0.5 \over timescale} - first\_timestamps) \times fps \rceil - 1$

$frame = \lceil ({\lfloor time \times timescale \rfloor + 0.5 \over timescale} - first\_timestamps) \times fps \rceil - 1$


#### Explanation for floor method

$\lfloor ({frame \over fps} + first\_timestamps) \times timescale \rfloor \leq time \times timescale$

$({frame \over fps} + first\_timestamps) \times timescale < \lfloor time \times timescale \rfloor + 1$

${frame \over fps} + first\_timestamps < {\lfloor time \times timescale \rfloor + 1 \over timescale}$

${frame \over fps} < {\lfloor time \times timescale \rfloor + 1 \over timescale} - first\_timestamps$

$frame < ({\lfloor time \times timescale \rfloor + 1 \over timescale} - first\_timestamps) \times fps$

$frame < \lceil ({\lfloor time \times timescale \rfloor + 1 \over timescale} - first\_timestamps) \times fps \rceil$

$frame \leq \lceil ({\lfloor time \times timescale \rfloor + 1 \over timescale} - first\_timestamps) \times fps \rceil - 1$

$frame = \lceil ({\lfloor time \times timescale \rfloor + 1 \over timescale} - first\_timestamps) \times fps \rceil - 1$




### time_to_frame for TimeType.START

$time = {\text{roundingMethod}(({(frame - 1) \over fps} + first\_timestamps) \times timescale) \over timescale}$

${\text{roundingMethod}(({(frame - 1) \over fps} + first\_timestamps) \times timescale) \over timescale} < time$

$\text{roundingMethod}(({(frame - 1) \over fps} + first\_timestamps) \times timescale) < time \times timescale$


#### Explanation for rounding method

$\text{round}(({(frame - 1) \over fps} + first\_timestamps) \times timescale) < time \times timescale$

$({(frame - 1) \over fps} + first\_timestamps) \times timescale + 0.5 < \lceil time \times timescale \rceil$

$({(frame - 1) \over fps} + first\_timestamps) \times timescale < \lceil time \times timescale \rceil - 0.5$

${(frame - 1) \over fps} + first\_timestamps < {\lceil time \times timescale \rceil - 0.5 \over timescale}$

${(frame - 1) \over fps} < {\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps$

$frame - 1 < ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps$

$frame < ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps + 1$

$frame < \lceil ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps + 1 \rceil$

$frame \leq \lceil ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps + 1 \rceil - 1$

$frame = \lceil ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps + 1 \rceil - 1$


#### Explanation for floor method

$\lfloor ({(frame - 1) \over fps} + first\_timestamps) \times timescale) \rfloor < time \times timescale$

$({(frame - 1) \over fps} + first\_timestamps) \times timescale) < \lceil time \times timescale \rceil$

${(frame - 1) \over fps} + first\_timestamps < {\lceil time \times timescale \rceil \over timescale}$

${(frame - 1) \over fps} < {\lceil time \times timescale \rceil \over timescale} - first\_timestamps$

$frame - 1 < ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps$

$frame < ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps + 1$

$frame < \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps + 1 \rceil$

$frame \leq \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps + 1 \rceil - 1$

$frame = \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps + 1 \rceil - 1$





### time_to_frame for TimeType.END

$time = {\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale}$

${\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale} < time$

$\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) < time \times timescale$

#### Explanation for rounding method

$\text{round}(({frame \over fps} + first\_timestamps) \times timescale) < time \times timescale$

$({frame \over fps} + first\_timestamps) \times timescale + 0.5 < \lceil time \times timescale \rceil$

$({frame \over fps} + first\_timestamps) \times timescale < \lceil time \times timescale \rceil - 0.5$

${frame \over fps} + first\_timestamps < {\lceil time \times timescale \rceil - 0.5 \over timescale}$

${frame \over fps} < {\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps$

$frame < ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps$

$frame < \lceil ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps \rceil$

$frame \leq \lceil ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps \rceil - 1$

$frame = \lceil ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps \rceil - 1$

#### Explanation for floor method

$\lfloor({frame \over fps} + first\_timestamps) \times timescale \rfloor < time \times timescale$

$({frame \over fps} + first\_timestamps) \times timescale < \lceil time \times timescale \rceil$

${frame \over fps} + first\_timestamps < {\lceil time \times timescale \rceil \over timescale}$

${frame \over fps} < {\lceil time \times timescale \rceil \over timescale} - first\_timestamps$

$frame < ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps$

$frame < \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps \rceil$

$frame \leq \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps \rceil - 1$

$frame = \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps \rceil - 1$





## Acknowledgments
Thanks to [arch1t3cht](https://github.com/arch1t3cht) who helped me understand the math behind this conversion.
