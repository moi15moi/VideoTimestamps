To understand how ``frame_to_time`` and ``time_to_frame`` works, we need to fully understand how TimeType works.

Here is an example of timestamps and their TimeType:

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


But, for our case, the interval are always integer, so it gives:

```math
\begin{gather}
\text{EXACT : } [\lceil \text{CurrentFrameTimestamps} \rceil, \lceil \text{NextFrameTimestamps} \rceil - 1] \\
\text{START : } [\lfloor \text{PreviousFrameTimestamps} \rfloor + 1, \lfloor \text{CurrentFrameTimestamps} \rfloor] \\
\text{END : } [\lfloor \text{CurrentFrameTimestamps} \rfloor + 1, \lfloor \text{NextFrameTimestamps} \rfloor]
\end{gather}
```

The interval are integer because float/double don't have infinite precision, so there are some rounding issues that we don't want. But, there is a drawback. We cannot have a higher precision then the unit that the integer represent. So, I arbitrarily choosed to use nanoseconds because in all the chapter and subtitle format that I know, this is the smallest unit available.   





# frame_to_time

A lot of people think that the time can be calculated like this: $time= frame \times {1 \over fps}$, but this is only a approximation. Actually, videos use this formula: $pts\_time= pts \times timebase$. So, the "real" name for $time$ is $pts\_time$, but note that, in some case (especially with .avi file), a video stream may not contains any $pts$. In those case, in general, player fallback to $dts$.

Important to note:
```math
\begin{gather}
pts \in \mathbb{N} \\
timebase \in \mathbb{Q}^{+} \\
pts\_time \in \mathbb{Q}^{+} \\
\end{gather}
```

But, how are $pts$ and $timebase$ setted?

The $timebase$ also depend on the implementation that varie a lot. For example, for .m2ts file, the $timebase$ will always be ${1 \over 90000}$. By default mkvtoolnix set the timebase to ${1 \over 1000}$. Important to note that there is a really similar value to $timebase$ which is called $timescale$. It id defined like this:

$$timebase = {1 \over timescale}$$

For the $pts$, it is simple, $pts = \text{roundingMethod}(frame \times ticks)$. The $\text{roundingMethod}$ depend on the implementation. For example, for .m2ts file, it will always be floored and mkvtoolnix will always round them.

$$ticks = {timescale \over fps}$$

So, in brief, the expended formula is: $time = \text{roundingMethod}(frame \times {timescale \over fps}) \times {1 \over timescale}$

But, that would make time in seconds and it would be a rational number which would be not precise.
We choosed that the maximum precision that a user could need is nanoseconds.





# frame_to_time for TimeType.EXACT

$\text{EXACT : } [\lceil \text{CurrentFrameTimestamps} \rceil, \lceil \text{NextFrameTimestamps} \rceil - 1]$

The lower bound is: $timens = \lceil \text{roundingMethod}(frame \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rceil$

The upper bound is: $timens = \lceil \text{roundingMethod}((frame + 1) \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rceil - 1$

# frame_to_time for TimeType.START

$\text{START : } [\lfloor \text{PreviousFrameTimestamps} \rfloor + 1, \lfloor \text{CurrentFrameTimestamps} \rfloor]$

The lower bound is: $timens = \lfloor \text{roundingMethod}((frame - 1) \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor + 1$

The upper bound is: $timens = \lfloor \text{roundingMethod}(frame \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor$

# frame_to_time for TimeType.END

$\text{END : } [\lfloor \text{CurrentFrameTimestamps} \rfloor + 1, \lfloor \text{NextFrameTimestamps} \rfloor]$

The lower bound is: $timens = \lfloor \text{roundingMethod}(frame \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor + 1$

The upper bound is: $timens = \lfloor \text{roundingMethod}((frame + 1) \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor$





# time_to_frame for TimeType.EXACT

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
PS: *The number are in milliseconds for simplicity, but actually, the formula give time in $10^{-9}$ second.*

With that in mind, we know can say that the property says that we need to use the largest $frame$ such that the $frame$ does not exceed the requested $timens$.

From that property, we can deduce this equation: $\lfloor \text{roundingMethod}(frame \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor \leq timens$

Now, we have an inequation and it is possible to isolate properly our $frame$ variable. Since the $\text{roundingMethod}$ can be floor or rounded, we will have 2 final equations that are described below

$\lfloor \text{roundingMethod}(frame \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor \leq timens$

$\text{roundingMethod}(frame \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} < timens + 1$

$\text{roundingMethod}(frame \times {timescale \over fps}) < (timens + 1) \times timescale \times 10^{-9}$





## Explanation for rounding method
$\text{round}(frame \times {timescale \over fps}) < (timens + 1) \times timescale \times 10^{-9}$

$frame \times {timescale \over fps} + 0.5 < \lceil (timens + 1) \times timescale \times 10^{-9} \rceil$

$frame \times {timescale \over fps} < \lceil (timens + 1) \times timescale \times 10^{-9} \rceil - 0.5$

$frame < (\lceil (timens + 1) \times timescale \times 10^{-9} \rceil - 0.5) \times {fps \over timescale}$

$frame < \lceil (\lceil (timens + 1) \times timescale \times 10^{-9} \rceil - 0.5) \times {fps \over timescale} \rceil$

$frame \leq  \lceil (\lceil (timens + 1) \times timescale \times 10^{-9} \rceil - 0.5) \times {fps \over timescale} \rceil - 1$

$frame =  \lceil (\lceil (timens + 1) \times timescale \times 10^{-9} \rceil - 0.5) \times {fps \over timescale} \rceil - 1$





## Explanation for floor method
$\lfloor frame \times {timescale \over fps} \rfloor < (timens + 1) \times timescale \times 10^{-9}$

$frame \times {timescale \over fps} < \lceil (timens + 1) \times timescale \times 10^{-9} \rceil$

$frame < \lceil (timens + 1) \times timescale \times 10^{-9} \rceil \times {fps \over timescale}$

$frame < \lceil \lceil (timens + 1) \times timescale \times 10^{-9} \rceil \times {fps \over timescale} \rceil$

$frame \leq \lceil \lceil (timens + 1) \times timescale \times 10^{-9} \rceil \times {fps \over timescale} \rceil - 1$

$frame = \lceil \lceil (timens + 1) \times timescale \times 10^{-9} \rceil \times {fps \over timescale} \rceil - 1$





# time_to_frame for TimeType.START
$timens = \lfloor \text{roundingMethod}((frame - 1) \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor + 1$

$\lfloor \text{roundingMethod}((frame - 1) \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor + 1 \leq timens$

$\lfloor \text{roundingMethod}((frame - 1) \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor \leq timens - 1$

$\text{roundingMethod}((frame - 1) \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} < timens$

$\text{roundingMethod}((frame - 1) \times {timescale \over fps}) < timens \times timescale \times 10^{-9}$


## Explanation for rounding method
$\text{round}((frame - 1) \times {timescale \over fps}) < timens \times timescale \times 10^{-9}$

$(frame - 1) \times {timescale \over fps} + 0.5 < \lceil timens \times timescale \times 10^{-9} \rceil$

$(frame - 1) \times {timescale \over fps} < \lceil timens \times timescale \times 10^{-9} \rceil - 0.5$

$frame - 1 < (\lceil timens \times timescale \times 10^{-9} \rceil - 0.5) \times {fps \over timescale}$

$frame < (\lceil timens \times timescale \times 10^{-9} \rceil - 0.5) \times {fps \over timescale} + 1$

$frame < \lceil (\lceil timens \times timescale \times 10^{-9} \rceil - 0.5) \times {fps \over timescale} + 1 \rceil$

$frame \leq \lceil (\lceil timens \times timescale \times 10^{-9} \rceil - 0.5) \times {fps \over timescale} + 1 \rceil - 1$

$frame = \lceil (\lceil timens \times timescale \times 10^{-9} \rceil - 0.5) \times {fps \over timescale} + 1 \rceil - 1$


## Explanation for floor method

$\lfloor (frame - 1) \times {timescale \over fps} \rfloor < timens \times timescale \times 10^{-9}$

$(frame - 1) \times {timescale \over fps} < \lceil timens \times timescale \times 10^{-9} \rceil$

$frame - 1 < \lceil timens \times timescale \times 10^{-9} \rceil \times {fps \over timescale}$

$frame < \lceil timens \times timescale \times 10^{-9} \rceil \times {fps \over timescale} + 1$

$frame < \lceil \lceil timens \times timescale \times 10^{-9} \rceil \times {fps \over timescale} + 1 \rceil$

$frame \leq \lceil \lceil timens \times timescale \times 10^{-9} \rceil \times {fps \over timescale} + 1 \rceil - 1$

$frame = \lceil \lceil timens \times timescale \times 10^{-9} \rceil \times {fps \over timescale} + 1 \rceil - 1$





# time_to_frame for TimeType.END
$timens = \lfloor \text{roundingMethod}(frame \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor + 1$

$\lfloor \text{roundingMethod}(frame \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor + 1 \leq timens$

$\lfloor \text{roundingMethod}(frame \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} \rfloor \leq timens - 1$

$\text{roundingMethod}(frame \times {timescale \over fps}) \times {1\over timescale} \times 10^{9} < timens$

$\text{roundingMethod}(frame \times {timescale \over fps}) < timens \times timescale \times 10^{9}$


## Explanation for rounding method

$\text{round}(frame \times {timescale \over fps}) < timens \times timescale \times 10^{9}$

$frame \times {timescale \over fps} + 0.5 < \lceil timens \times timescale \times 10^{9} \rceil$

$frame \times {timescale \over fps} < \lceil timens \times timescale \times 10^{9} \rceil - 0.5$

$frame < (\lceil timens \times timescale \times 10^{9} \rceil - 0.5) \times {fps \over timescale}$

$frame < \lceil (\lceil timens \times timescale \times 10^{9} \rceil - 0.5) \times {fps \over timescale} \rceil$

$frame \leq \lceil (\lceil timens \times timescale \times 10^{9} \rceil - 0.5) \times {fps \over timescale} \rceil - 1$

$frame = \lceil (\lceil timens \times timescale \times 10^{9} \rceil - 0.5) \times {fps \over timescale} \rceil - 1$

## Explanation for floor method

$\lfloor frame \times {timescale \over fps} \rfloor < timens \times timescale \times 10^{9}$

$frame \times {timescale \over fps} < \lceil timens \times timescale \times 10^{9} \rceil$

$frame < \lceil timens \times timescale \times 10^{9} \rceil \times {fps \over timescale}$

$frame < \lceil \lceil timens \times timescale \times 10^{9} \rceil \times {fps \over timescale} \rceil$

$frame \leq \lceil \lceil timens \times timescale \times 10^{9} \rceil \times {fps \over timescale} \rceil - 1$

$frame = \lceil \lceil timens \times timescale \times 10^{9} \rceil \times {fps \over timescale} \rceil - 1$





## Acknowledgments
Thanks to [arch1t3cht](https://github.com/arch1t3cht) who helped me understand the math behind this conversion.
