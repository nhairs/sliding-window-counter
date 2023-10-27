### IMPORTS
### ============================================================================
## Standard Library
from collections import deque
from dataclasses import dataclass
import datetime as dt
import sys
import time
import threading
from typing import Deque, Union, Dict, Any

## Installed

## Application


### CONSTANTS
### ============================================================================


### FUNCTIONS
### ============================================================================
def now() -> int:
    """Return the current time as an integer"""
    return int(time.time())


def _dataclass_slots() -> Dict[str, Any]:
    """Generate dataclass slots kwarg if it is supported by the current version of python"""
    if sys.version_info >= (3, 10):
        return {"slots": True}
    return {}


### CLASSES
### ============================================================================


@dataclass(**_dataclass_slots())
class _Bucket:
    bucket: int
    count: int = 0

    def __repr__(self) -> str:
        return f"({self.bucket}: {self.count})"


class SlidingWindowCounter:
    """Time based sliding window counter"""

    def __init__(
        self,
        window_size: Union[int, dt.timedelta],
        bucket_size: Union[int, dt.timedelta],
        start_immediately: bool = False,
        cleanup_frequency: Union[int, None] = None,
    ) -> None:
        """Inititalise new SlidingWindowCounter

        `window_size` is the length of time we want to track in seconds.
        `bucket_size` is the resolution of our underlying counters in seconds.
        A higher bucket_size will allow for finer grained counting but will require
        more memory to store.
        `start_immediately` will set `self.start_time` during `__init__` if `True`,
        otherwise `self.start_time` will be set during first call to `self.increment`.
        `cleanup_frequency` is the time in seconds to check if we need to do internal
        cleanups. This can be tuned to do cleanups less often at the expense of
        potentially increased memory usage. If `None` then will use `window_size // 5`
        with a minimum value of `1`.
        """
        if isinstance(window_size, dt.timedelta):
            window_size = int(window_size.total_seconds())
        if window_size < 1:
            raise ValueError("window_size must be >= 1")
        self._window_size = window_size

        if isinstance(bucket_size, dt.timedelta):
            bucket_size = int(bucket_size.total_seconds())
        if bucket_size < 1:
            raise ValueError("bucket_size must be >= 1")
        if bucket_size > window_size:
            # Note: we allow bucket_size == window_size which means that we will
            # keep 1 bucket per window
            raise ValueError("bucket_size must be <= window_size")
        if window_size % bucket_size != 0:
            raise ValueError("bucket_size must divide evenly into window_size")
        self._bucket_size = bucket_size

        self._last_cleanup = now()

        if cleanup_frequency is None:
            cleanup_frequency = max(1, window_size // 5)
        if cleanup_frequency < 1:
            raise ValueError("cleanup_frequency must be >= 1")
        self._cleanup_frequency = cleanup_frequency

        self._lock = threading.RLock()

        self._grand_total = 0
        self._start_time = 0

        if start_immediately:
            self.start()

        self._buckets: Deque[_Bucket] = deque()
        return

    def increment(self, amount: int = 1) -> None:
        """Increment the current bucket by amount"""
        if amount < 1:
            raise ValueError("amount must be >= 1")

        with self._lock:
            if not self.started:
                self.start()

            # Increment grand total
            self._grand_total += amount

            # Get current bucket
            desired_bucket = self._get_current_bucket()

            if len(self._buckets) and (bucket := self._buckets[-1]).bucket == desired_bucket:
                # We have an existing bucket
                bucket.count += amount

            else:
                # Need a new bucket
                self._buckets.append(_Bucket(desired_bucket, amount))

        self._run_cleanup_if_needed()
        return

    def start(self) -> bool:
        """Manually start counter.

        Return `True` if the counter was not started. Otherwise does nothing and returns `False`.
        """
        with self._lock:
            if not self.started:
                self._start_time = now()
                return True
        return False

    def _get_current_bucket(self) -> int:
        # Ref: https://stackoverflow.com/a/65725123/12281814
        now_ = now()
        return now_ - (now_ % self.bucket_size)

    ## Read only properties
    ## -------------------------------------------------------------------------
    @property
    def window_size(self) -> int:
        """window_size in seconds"""
        return self._window_size

    @property
    def bucket_size(self) -> int:
        """bucket_size in seconds"""
        return self._bucket_size

    @property
    def start_time(self) -> int:
        """start time as unix timestamp in seconds"""
        return self._start_time

    @property
    def running_time(self) -> int:
        """Seconds since this SlidingWindowCounter started"""
        self._run_cleanup_if_needed()
        if not self.started:
            return 0
        return now() - self.start_time

    @property
    def grand_total(self) -> int:
        """Total count since this SlidingWindowCounter started"""
        self._run_cleanup_if_needed()
        return self._grand_total

    @property
    def current_total(self) -> int:
        """Get the total for the current window"""
        with self._lock:
            # Do cleanup so we know that the deque only has valid buckets
            self._run_cleanup()
            total = sum(bucket.count for bucket in self._buckets)
        return total

    @property
    def current_throughput(self) -> float:
        """The current throughput of the counter.

        If the counter has been running for less than `window_length` seconds,
        will instead calculate based on `running_time` giving more accurate values
        during the startup period.

        If the counter is not started will return `0.0`.
        If `running_time` is `0` (e.g. because started and checked within a second) will
        return the current total as if it was across the whole second.
        """
        self._run_cleanup_if_needed()
        if not self.started:
            return 0.0

        running_time = self.running_time
        if running_time == 0:
            return self.current_total
        if running_time < self.window_size:
            # We've not been running very long, use running_time
            return self.current_total / running_time
        return self.current_total / self.window_size

    @property
    def started(self) -> bool:
        """Is counter started"""
        return self._start_time != 0

    ## Cleanup
    ## -------------------------------------------------------------------------
    def _should_cleanup(self) -> bool:
        """Determine if we should run a cleanup task"""
        if not self.started:
            return False
        return now() - self._last_cleanup > self._cleanup_frequency

    def _run_cleanup(self) -> None:
        """Cleanup old buckets"""
        min_bucket = self._get_current_bucket() - self.window_size + self.bucket_size
        with self._lock:
            while self._buckets and self._buckets[0].bucket < min_bucket:
                self._buckets.popleft()
            self._last_cleanup = now()
        return

    def _run_cleanup_if_needed(self) -> None:
        """Run a cleanup if necesary"""
        if self._should_cleanup():
            self._run_cleanup()
        return
