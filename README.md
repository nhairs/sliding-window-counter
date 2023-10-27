# Sliding Window Counter

[![PyPi](https://img.shields.io/pypi/v/sliding-window-counter.svg)](https://pypi.python.org/pypi/sliding-window-counter/)
[![PyPI - Status](https://img.shields.io/pypi/status/sliding-window-counter)](https://pypi.python.org/pypi/sliding-window-counter/)
[![Python Versions](https://img.shields.io/pypi/pyversions/sliding-window-counter.svg)](https://github.com/nhairs/sliding-window-counter)
[![License](https://img.shields.io/github/license/nhairs/sliding-window-counter.svg)](https://github.com/nhairs/sliding-window-counter)

`sliding-window-counter` provides time based sliding window counters. These are useful for tracking things like throughput metrics for long running applications.

## Installation
### Install via pip
```shell
pip3 install sliding-window-counter
```

## Quick Start

```python
## Creating Counters
## -----------------------------------------------------------------------------
import datetime as dt
from sliding_window_counter import SlidingWindowCounter

# Count across 1 minute with 5 second resolution
small_counter = SlidingWindowCounter(60, 5)

# Count across 1 hour with 1 minute resolution
long_counter = SlidingWindowCounter(dt.timedelta(hours=1), dt.timedelta(minutes=1))

# Count across 12 hours with 10 second resolution (not a good idea to be honest)
long_and_precise_counter = SlidingWindowCounter(dt.timdelta(hours=12), 10)

## Using Counters
## -----------------------------------------------------------------------------
import random
import time

mini_counter = SlidingWindowCounter(10, 1)

# fill it up and check it's state
for i in range(20):
    add = random.randint(1,20)
    mini_counter.increment(add)
    print(f"{i:>3}s Added: {add:<3} Window: {mini_counter.current_total:<6} Total: {mini_counter.grand_total:<6} Avg: {mini_counter.current_throughput:>5.2f}/s")
    time.sleep(1)

# Watch it drain
for i in range(12):
    time.sleep(1)
    print(f"Window: {mini_counter.current_total:<5} Total: {mini_counter.grand_total:<5} Avg: {mini_counter.current_throughput:>5.2f}/s")
```

## Bugs, Feature Requests etc
TLDR: Please [submit an issue on github](https://github.com/nhairs/sliding-window-counter/issues).

In the case of bug reports, please help me help you by following best practices [1](https://marker.io/blog/write-bug-report/) [2](https://www.chiark.greenend.org.uk/~sgtatham/bugs.html).

In the case of feature requests, please provide background to the problem you are trying to solve so to help find a solution that makes the most sense for the library as well as your usecase.

## Development
The only development dependency is bash and docker. All actions are run within docker for ease of use. See `./dev.sh help` for commands. Typical commands are `format`, `lint`, `test`, `repl`, `build`.

I am still working through open source licencing and contributing, so not taking PRs at this point in time. Instead raise and issue and I'll try get to it as soon a feasible.

## Licence
This project is licenced under the MIT Licence - see [`LICENCE`](https://github.com/nhairs/sliding-window-counter/blob/master/LICENCE).

This project may include other open source licenced software - see [`NOTICE`](https://github.com/nhairs/sliding-window-counter/blob/master/NOTICE).

## Authors
A project by Nicholas Hairs - [www.nicholashairs.com](https://www.nicholashairs.com).
