# Table of contents
1. [Introduction](#introduction)
2. [frame_to_time](#frame_to_time)
    1. [frame_to_time_exact](#frame_to_time_exact)
    2. [frame_to_time_start](#frame_to_time_start)
    3. [frame_to_time_end](#frame_to_time_end)
3. [time_to_frame](#time_to_frame)
    1. [time_to_frame_exact](#time_to_frame_exact)
    2. [time_to_frame_start](#time_to_frame_start)
    3. [time_to_frame_end](#time_to_frame_end)
4. [Acknowledgments](#acknowledgments)


## Introduction <a name="introduction"></a>

To understand how ``frame_to_time`` and ``time_to_frame`` works, we need to fully understand how TimeType works.

Here is an example of timestamps and their TimeType with a $fps = 30$:

**Timestamps**
```math
\begin{gather}
Frame_0 : 0 \text{ ms} \\
Frame_1 : 33.333333 \text{ ms} \\
Frame_2 : 66.666666 \text{ ms} \\
Frame_3 : 100 \text{ ms} \\
Frame_4 : 133.333333 \text{ ms} \\
Frame_5 : 166.666666 \text{ ms}
\end{gather}
```

**EXACT**
```math
\begin{gather}
Frame_0 : [0, 33] \text{ ms} \\
Frame_1 : [34, 66] \text{ ms} \\
Frame_2 : [67, 99] \text{ ms} \\
Frame_3 : [100, 133] \text{ ms} \\
Frame_4 : [134, 166] \text{ ms}
\end{gather}
```

**START**
```math
\begin{gather}
Frame_0 : 0 \text{ ms} \\
Frame_1 : [1, 33] \text{ ms} \\
Frame_2 : [34, 66] \text{ ms} \\
Frame_3 : [67, 100] \text{ ms} \\
Frame_4 : [101, 133] \text{ ms}
\end{gather}
```

**END**
```math
\begin{gather}
Frame_0 : [1, 33] \text{ ms} \\
Frame_1 : [34, 66] \text{ ms} \\
Frame_2 : [67, 100] \text{ ms} \\
Frame_3 : [101, 133] \text{ ms}
\end{gather}
```

The interval for each type of timing are defined like this:

```math
\begin{gather}
\text{EXACT : } [\text{CurrentFrameTimestamps}, \text{NextFrameTimestamps}[ \\
\text{START : } ]\text{PreviousFrameTimestamps} , \text{CurrentFrameTimestamps}] \\
\text{END : } ]\text{CurrentFrameTimestamps}, \text{NextFrameTimestamps}]
\end{gather}
```





# frame_to_time <a name="frame_to_time"></a>

A lot of people think that the time can be calculated like this: $time= frame \times {1 \over fps}$, but this is only a approximation. Actually, videos use this formula: $pts\_time= pts \times timebase$. So, the "real" name for $time$ is $pts\_time$, but note that, in some case (especially with .avi file), a video stream may not contains any $pts$. In those case, in general, player fallback to $dts$.

Important to note:
```math
\begin{gather}
pts \in \mathbb{N} \\
timebase \in \mathbb{Q}^{+} \\
pts\_time \in \mathbb{Q} \\
\end{gather}
```

[Source for pts](https://ffmpeg.org/doxygen/7.0/structAVPacket.html#a73bde0a37f3b1efc839f11295bfbf42a)

[Source for timebase](https://www.ffmpeg.org/doxygen/7.0/structAVStream.html#a9db755451f14e2bf590d4b85d82b32e6)


But, how are $pts$ and $timebase$ setted?

The $timebase$ also depend on the implementation that varie a lot. For example, for .m2ts file, the $timebase$ will always be ${1 \over 90000}$. By default mkvtoolnix set the timebase to ${1 \over 1000}$. Important to note that there is a really similar value to $timebase$ which is called $timescale$. It id defined like this:

$$timebase = {1 \over timescale}$$

For the $pts$, it is simple, $pts = \text{roundingMethod}(frame \times ticks)$. The $\text{roundingMethod}$ depend on the implementation. For example, for .m2ts file, it will always be floored and mkvtoolnix will always round them.

$$ticks = {timescale \over fps}$$

So, in brief, the expended formula is: $time = {\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale} $

But, that would make time in seconds and it would be a rational number which would be not precise.
We choosed that the maximum precision that a user could need is nanoseconds.





# frame_to_time for TimeType.EXACT <a name="frame_to_time_exact"></a>
$\text{EXACT : } [\text{CurrentFrameTimestamps}, \text{NextFrameTimestamps}[$

The lower bound is: $time = {\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale}$

The upper bound is: $time = {\text{roundingMethod}(({(frame + 1) \over fps} + first\_timestamps) \times timescale) \over timescale}$

# frame_to_time for TimeType.START <a name="frame_to_time_start"></a>
$\text{START : } ]\text{PreviousFrameTimestamps} , \text{CurrentFrameTimestamps}]$

The lower bound is: $time = {\text{roundingMethod}(({(frame - 1) \over fps} + first\_timestamps) \times timescale) \over timescale}$

The upper bound is: $time = {\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale}$

# frame_to_time for TimeType.END <a name="frame_to_time_end"></a>
$\text{END : } ]\text{CurrentFrameTimestamps}, \text{NextFrameTimestamps}]$

The lower bound is: $time = {\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale}$

The upper bound is: $time = {\text{roundingMethod}(({(frame + 1) \over fps} + first\_timestamps) \times timescale) \over timescale}$




# time_to_frame <a name="time_to_frame"></a>

# time_to_frame for TimeType.EXACT <a name="time_to_frame_exact"></a>

``time_to_frame`` need to be exactly the inverse of ``frame_to_time``.
Since there are rounding operation, we cannot directly isolate it. To do so, we need to use the interval to our advantage. Here is a example::
```math
\begin{gather}
fps = 24000/1001 \\
Frame_0 : [0, 42[ ms \\
Frame_1 : [42, 83[ ms \\
Frame_2 : [83, 125[ ms \\
Frame_3 : [125, 167[ ms
\end{gather}
```
PS: *The number are in milliseconds for simplicity, but actually, the formula give time in second.*

With that in mind, we know can say that the property says that we need to use the largest $frame$ such that the $frame$ does not exceed the requested $time$.

From that property, we can deduce this equation: ${\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale} \leq time$

We can isolate our roundingMethod like this: $\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \leq time \times timescale$

Now, we have an inequation and it is possible to isolate properly our $frame$ variable. Since the $\text{roundingMethod}$ can be floor or rounded, we will have 2 final equations that are described below:

## Explanation for rounding method
$\text{round}(({frame \over fps} + first\_timestamps) \times timescale) \leq time \times timescale$

$({frame \over fps} + first\_timestamps) \times timescale < \lfloor time \times timescale \rfloor + 0.5$

${frame \over fps} + first\_timestamps < {\lfloor time \times timescale \rfloor + 0.5 \over timescale}$

${frame \over fps} < {\lfloor time \times timescale \rfloor + 0.5 \over timescale} - first\_timestamps$

$frame < ({\lfloor time \times timescale \rfloor + 0.5 \over timescale} - first\_timestamps) \times fps$

$frame < \lceil ({\lfloor time \times timescale \rfloor + 0.5 \over timescale} - first\_timestamps) \times fps \rceil$

$frame \leq \lceil ({\lfloor time \times timescale \rfloor + 0.5 \over timescale} - first\_timestamps) \times fps \rceil - 1$

$frame = \lceil ({\lfloor time \times timescale \rfloor + 0.5 \over timescale} - first\_timestamps) \times fps \rceil - 1$


## Explanation for floor method

$\lfloor ({frame \over fps} + first\_timestamps) \times timescale \rfloor \leq time \times timescale$

$({frame \over fps} + first\_timestamps) \times timescale < \lfloor time \times timescale \rfloor + 1$

${frame \over fps} + first\_timestamps < {\lfloor time \times timescale \rfloor + 1 \over timescale}$

${frame \over fps} < {\lfloor time \times timescale \rfloor + 1 \over timescale} - first\_timestamps$

$frame < ({\lfloor time \times timescale \rfloor + 1 \over timescale} - first\_timestamps) \times fps$

$frame < \lceil ({\lfloor time \times timescale \rfloor + 1 \over timescale} - first\_timestamps) \times fps \rceil$

$frame \leq \lceil ({\lfloor time \times timescale \rfloor + 1 \over timescale} - first\_timestamps) \times fps \rceil - 1$

$frame = \lceil ({\lfloor time \times timescale \rfloor + 1 \over timescale} - first\_timestamps) \times fps \rceil - 1$




# time_to_frame for TimeType.START <a name="time_to_frame_start"></a>

$time = {\text{roundingMethod}(({(frame - 1) \over fps} + first\_timestamps) \times timescale) \over timescale}$

${\text{roundingMethod}(({(frame - 1) \over fps} + first\_timestamps) \times timescale) \over timescale} < time$

$\text{roundingMethod}(({(frame - 1) \over fps} + first\_timestamps) \times timescale) < time \times timescale$


## Explanation for rounding method

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


## Explanation for floor method

$\lfloor ({(frame - 1) \over fps} + first\_timestamps) \times timescale) \rfloor < time \times timescale$

$({(frame - 1) \over fps} + first\_timestamps) \times timescale) < \lceil time \times timescale \rceil$

${(frame - 1) \over fps} + first\_timestamps < {\lceil time \times timescale \rceil \over timescale}$

${(frame - 1) \over fps} < {\lceil time \times timescale \rceil \over timescale} - first\_timestamps$

$frame - 1 < ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps$

$frame < ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps + 1$

$frame < \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps + 1 \rceil$

$frame \leq \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps + 1 \rceil - 1$

$frame = \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps + 1 \rceil - 1$





# time_to_frame for TimeType.END <a name="time_to_frame_end"></a>

$time = {\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale}$

${\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) \over timescale} < time$

$\text{roundingMethod}(({frame \over fps} + first\_timestamps) \times timescale) < time \times timescale$

## Explanation for rounding method

$\text{round}(({frame \over fps} + first\_timestamps) \times timescale) < time \times timescale$

$({frame \over fps} + first\_timestamps) \times timescale + 0.5 < \lceil time \times timescale \rceil$

$({frame \over fps} + first\_timestamps) \times timescale < \lceil time \times timescale \rceil - 0.5$

${frame \over fps} + first\_timestamps < {\lceil time \times timescale \rceil - 0.5 \over timescale}$

${frame \over fps} < {\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps$

$frame < ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps$

$frame < \lceil ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps \rceil$

$frame \leq \lceil ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps \rceil - 1$

$frame = \lceil ({\lceil time \times timescale \rceil - 0.5 \over timescale} - first\_timestamps) \times fps \rceil - 1$

## Explanation for floor method

$\lfloor({frame \over fps} + first\_timestamps) \times timescale \rfloor < time \times timescale$

$({frame \over fps} + first\_timestamps) \times timescale < \lceil time \times timescale \rceil$

${frame \over fps} + first\_timestamps < {\lceil time \times timescale \rceil \over timescale}$

${frame \over fps} < {\lceil time \times timescale \rceil \over timescale} - first\_timestamps$

$frame < ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps$

$frame < \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps \rceil$

$frame \leq \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps \rceil - 1$

$frame = \lceil ({\lceil time \times timescale \rceil \over timescale} - first\_timestamps) \times fps \rceil - 1$





## Acknowledgments <a name="acknowledgments"></a>
Thanks to [arch1t3cht](https://github.com/arch1t3cht) who helped me understand the math behind this conversion.
