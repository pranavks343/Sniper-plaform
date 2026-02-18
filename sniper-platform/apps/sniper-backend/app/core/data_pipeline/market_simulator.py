from __future__ import annotations

import csv
import time
from datetime import datetime


class MarketSimulator:
    def __init__(self) -> None:
        self._rows: list[dict] = []
        self._index = 0
        self._paused = False

    def load_data(self, file_path: str, start_date: datetime | None = None, end_date: datetime | None = None) -> None:
        self._rows.clear()
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ts = datetime.fromisoformat(row['timestamp'])
                if start_date and ts < start_date:
                    continue
                if end_date and ts > end_date:
                    continue
                self._rows.append(row)
        self._index = 0

    def start_replay(self, speed: float = 1.0):
        while self._index < len(self._rows):
            if self._paused:
                time.sleep(0.1)
                continue
            row = self._rows[self._index]
            self._index += 1
            yield row
            time.sleep(max(0.001, 1.0 / max(speed, 1e-6)))

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def seek(self, timestamp: datetime) -> None:
        for i, row in enumerate(self._rows):
            if datetime.fromisoformat(row['timestamp']) >= timestamp:
                self._index = i
                break
