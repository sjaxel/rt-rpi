# rt-rpi/core/utils.py
# Utility functions and classes for the rt-rpi project.

from dataclasses import dataclass
from typing import Iterator, Tuple
import time
from typing_extensions import Final

UTILVAR = "rt-rpi.utils"

def busy_wait(timeout: float = 0.1) -> None:
    """Busy-wait for a specified timeout."""
    end_time = time.monotonic() + timeout
    while time.monotonic() < end_time:
        pass  # Busy-waiting loop

def random_busy_wait(max: float) -> None:
    """Busy-wait for a random duration up to a maximum."""
    import random
    timeout = random.uniform(0, max)
    end_time = time.monotonic() + timeout
    while time.monotonic() < end_time:
        pass  # Busy-waiting loop

class LoopTimer:
    """A simple timer that yields the elapsed time and error at a fixed interval."""

    @dataclass
    class LoopTimerStats:
        """Tracks statistics for loop timing errors."""
        n: int = 0
        mean: float = 0.0
        M2: float = 0.0
        largest_error: float | None = None

        def update(self, error: float) -> None:
            """Update statistics with a new error value."""
            self.n += 1
            delta = error - self.mean
            self.mean += delta / self.n
            delta2 = error - self.mean
            self.M2 += delta * delta2
            if self.largest_error is None or abs(error) > abs(self.largest_error):
                self.largest_error = error

        def variance(self) -> float:
            """Return variance of observed values."""
            if self.n < 2:
                return 0.0
            return self.M2 / (self.n - 1)

        def stddev(self) -> float:
            """Return standard deviation of observed values."""
            return self.variance() ** 0.5

        def __str__(self) -> str:
            """String representation of statistics in microseconds."""
            return (
                f"LoopTimerStats(n={self.n}, mean={self.mean * 1e6:.3f} us, "
                f"variance={self.variance() * 1e12:.3f} us^2, stddev={self.stddev() * 1e6:.3f} us, "
                f"largest_error={self.largest_error * 1e6 if self.largest_error is not None else None:.3f} us)"
            )

    def __init__(self, period: float) -> None:
        """Initialize LoopTimer.

        Args:
            period: Loop period seconds.
        """
        self.period_ns: Final[int] = int(period * 1e9)
        self.stats: LoopTimer.LoopTimerStats = LoopTimer.LoopTimerStats()
        self._first = True
        self.next_time = time.monotonic_ns()
        self.last_time = self.next_time

    def __iter__(self) -> Iterator[Tuple[int, int]]:
        return self

    def __next__(self) -> Tuple[int, int]:
        """Yield (elapsed, error) in nanoseconds."""
        now = time.monotonic_ns()
        if self._first:
            # On first iteration, just initialize and yield zeros
            self._first = False
            self.last_time = now
            self.next_time = now + self.period_ns
            self.stats.update(0.0)
            return 0, 0

        # Sleep until the next scheduled time
        sleep_ns = self.next_time - now
        if sleep_ns > 0:
            time.sleep(sleep_ns * 1e-9)
        now = time.monotonic_ns()
        elapsed = now - self.last_time
        error = elapsed - self.period_ns
        self.stats.update(error * 1e-9)
        self.last_time = now
        self.next_time += self.period_ns

        # If we are behind, skip missed intervals
        # if now > self.next_time:
        #     missed = (now - self.next_time) // self.period_ns + 1
        #     self.next_time += missed * self.period_ns

        return elapsed, error
