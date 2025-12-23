from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class ClockConfig:
    start: pd.Timestamp
    end: pd.Timestamp
    freq: str            # "1D", "1H", "5min", etc.
    tz: str | None = None


class Clock:
    def __init__(self, config: ClockConfig):
        self._timestamps = pd.date_range(
            start=config.start,
            end=config.end,
            freq=config.freq,
            tz=config.tz
        )

        if len(self._timestamps) == 0:
            raise ValueError("Clock has no timestamps")

        self.i = -1
        self.now = None
        self._n = len(self._timestamps)

    def next(self) -> bool:
        """
        move forward one step.
        Returns True if there is a next timestamp, False if the end is reached.
        """
        self.i += 1

        if self.i >= self._n:
            return False

        self.now = self._timestamps[self.i]
        return True
    
    def prev(self) -> bool:
        """
        move backward one step.
        Returns True if there is a previous timestamp, False if the start is reached.
        """
        self.i -= 1

        if self.i < 0:
            return False

        self.now = self._timestamps[self.i]
        return True
    
    def reset(self):
        """reset the clock to the initial state."""
        self.i = -1
        self.now = None

if __name__ == "__main__":
    config = ClockConfig(
        start=pd.Timestamp("2025-01-01"),
        end=pd.Timestamp("2025-12-22"),
        freq="1D",
        tz="UTC"
    )

    clock = Clock(config)

    while clock.next():
        print(clock.now)