# pylint: disable=missing-function-docstring,protected-access

### IMPORTS
### ============================================================================
## Standard Library

## Installed
from freezegun import freeze_time
import pytest

## Application
from sliding_window_counter import SlidingWindowCounter


### TESTS
### ============================================================================
@pytest.mark.parametrize(
    "window,bucket", [(60, 1), (60, 10), (300, 60), (3600, 60), (1, 1), (60, 60)]
)
def test_bucket_complete_filling(window, bucket):
    with freeze_time() as time:
        counter = SlidingWindowCounter(window, bucket)
        buckets = window // bucket

        # Fill buckets to match window_size
        running_total = 0

        for i in range(buckets - 1):
            val = i + 1
            running_total += val
            counter.increment(val)
            time.tick(bucket)
            assert len(counter._buckets) == val
            # check sliding count
            assert counter.current_total == running_total

        counter.increment(buckets)
        running_total += buckets

        # Check buckets
        for i in range(buckets):
            assert counter._buckets[i].count == i + 1

        assert len(counter._buckets) == buckets
        assert counter.grand_total == running_total
        assert counter.current_total == running_total

        # Increment time so that the window will slide into a new bucket.
        time.tick(bucket)
        counter.increment(buckets + 1)
        running_total += buckets + 1

        # Check new window
        assert counter.grand_total == running_total
        assert counter.current_total == running_total - 1
        assert counter._buckets[0].count == 2

        # After checking current_total (and with time frozen) we should be left
        # with only the included buckets
        assert len(counter._buckets) == buckets

        # We now drain the counter by moving forward a full window
        time.tick(window)
        assert counter.grand_total == running_total
        assert counter.current_total == 0
        assert len(counter._buckets) == 0
