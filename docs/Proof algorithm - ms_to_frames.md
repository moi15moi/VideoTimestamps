# ms_to_frames for TimeType.EXACT CFR (Constant frame rate)
To convert an frame to an ms, here is the formula: $ms= frame \times {1 \over fps} \times 1000$

Important to note, $frame \in \mathbb{N}$, $ms \in \mathbb{N}$ and $fps \in \mathbb{R}^+$.

Since $ms \in \mathbb{N}$, there is always a rounding operation. There is 2 choice for the rounding operation: floor and round (see docs of timestamps.py for more information), so let's create the variable $roundingMethod$ which will represent floor/round.

Now, we have this equation: $ms= roundingMethod(frame \times {1 \over fps} \times 1000)$

From our equation, we can quickly find the ms for a frame:
```math
\begin{gather}
fps = 24000/1001 \\
roundingMethod = round \\
Frame_0 : 0 ms \\
Frame_1 : 42 ms \\
Frame_2 : 83 ms \\
Frame_3 : 125 ms
\end{gather}
```

But now, we can ask ourselves a question, which frame would be displayed at $ms=10$ ? $ms=10$ is between $Frame_0$ and $Frame_1$, so which frame does correspond to it? That's where we can use the ``TimeType.EXACT`` property. That property says that we need to use the largest $frame$ such that the $frame$ in rounded milliseconds does not exceed the requested $ms$.
This means we can now create interval for our frames:
```math
\begin{gather}
fps = 24000/1001 \\
roundingMethod = round \\
Frame_0 : [0, 42[ ms \\
Frame_1 : [42, 83[ ms \\
Frame_2 : [83, 125[ ms \\
Frame_3 : [125, 167[ ms
\end{gather}
```

From that property, we can deduce this equation: $roundingMethod(frame \times {1 \over fps} \times 1000) \leq ms$

## Explanation for rounding method CFR
$$\text{round}(frame \times {1 \over fps} \times 1000) \leq ms$$

Important to note, $\text{round}(x + 0.5) = \lfloor x + 0.5 \rfloor$ where $x \in \mathbb{R}^+$

From the previous equation, we can deduce: $frame \times {1 \over fps} \times 1000 < ms + 0.5$

And from the previous inequation, we can isolate $frame$ like this: $frame < (ms + 0.5) \times fps \times {1 \over 1000}$

And from the previous inequation, we can deduce: $frame = \lceil (ms + 0.5) \times fps \times {1 \over 1000} \rceil - 1$

## Explanation for floor method CFR
$$\lfloor frame \times {1 \over fps} \times 1000 \rfloor \leq ms$$

From the previous equation, we can deduce: $frame \times {1 \over fps} \times 1000 < ms + 1$

And from the previous inequation, we can isolate $frame$ like this: $frame < (ms + 1) \times fps \times {1 \over 1000}$

And from the previous inequation, we can deduce: $frame = \lceil (ms + 1) \times fps \times {1 \over 1000} \rceil - 1$


# ms_to_frames for TimeType.EXACT VFR (Variable frame rate)

Let's adapt the equation to support VFR.

Important to note, $nbrVideoFrames \in \mathbb{N}$ and $lastFrameMs \in \mathbb{R}^+$.

$$ms= roundingMethod((frame - nbrVideoFrames + 1) \times {1 \over fps} \times 1000 + lastFrameMs)$$

$$roundingMethod((frame - nbrVideoFrames + 1) \times {1 \over fps} \times 1000 + lastFrameMs) \leq ms$$

## Explanation for rounding method VFR
$$\text{round}((frame - nbrVideoFrames + 1) \times {1 \over fps} \times 1000 + lastFrameMs) \leq ms$$

Important to note, $\text{round}(x + 0.5) = \lfloor x + 0.5 \rfloor$ where $x \in \mathbb{R}^+$

$$(frame - nbrVideoFrames + 1) \times {1 \over fps} \times 1000 + lastFrameMs < ms + 0.5$$

$$frame - nbrVideoFrames + 1 < (ms + 0.5 - lastFrameMs) \times fps \times {1 \over 1000}$$

$$frame < (ms + 0.5 - lastFrameMs) \times fps \times {1 \over 1000} + nbrVideoFrames - 1$$

$$frame = \lceil (ms + 0.5 - lastFrameMs) \times fps \times {1 \over 1000} + nbrVideoFrames - 1 \rceil - 1$$

## Explanation for floor method VFR

$$\lfloor (frame - nbrVideoFrames + 1) \times {1 \over fps} \times 1000 + lastFrameMs \rfloor \leq ms$$

$$(frame - nbrVideoFrames + 1) \times {1 \over fps} \times 1000 + lastFrameMs < ms + 1$$

$$frame - nbrVideoFrames + 1 < (ms + 1 - lastFrameMs) \times fps \times {1 \over 1000}$$

$$frame < (ms + 1 - lastFrameMs) \times fps \times {1 \over 1000} + nbrVideoFrames - 1$$

$$frame = \lceil (ms + 1 - lastFrameMs) \times fps \times {1 \over 1000} + nbrVideoFrames - 1 \rceil - 1$$

## Acknowledgments

Thanks to [arch1t3cht](https://github.com/arch1t3cht) who helped me understand the math behind this conversion.