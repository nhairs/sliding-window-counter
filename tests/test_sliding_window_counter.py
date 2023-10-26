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
@pytest.mark.parametrize("window,bucket", [(60, 1), (60, 10), (300, 60), (3600, 60)])
def test_bucket(window, bucket):
    with freeze_time() as time:
        counter = SlidingWindowCounter(window, bucket)
        buckets = window // bucket

        running_total = 0

        for i in range(buckets - 1):
            val = i + 1
            running_total += val
            counter.increment(val)
            time.tick(bucket)
            assert len(counter._buckets) == val
            # check sliding count
            assert counter.current_count == running_total

        counter.increment(buckets)
        running_total += buckets

        for i in range(buckets):
            assert counter._buckets[i].count == i + 1

        assert len(counter._buckets) == buckets
        assert counter.grand_total == running_total
        assert counter.current_count == running_total

        # Increment into new bucket
        time.tick(bucket)
        counter.increment(buckets + 1)
        running_total += buckets + 1

        assert counter.grand_total == running_total
        assert counter.current_count == running_total - 1
        assert counter._buckets[0].count == 2
        assert len(counter._buckets) == buckets

        time.tick(window)
        assert counter.grand_total == running_total
        assert counter.current_count == 0
        assert len(counter._buckets) == 0
