from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path
from random import gauss


def main() -> None:
    out = Path(__file__).resolve().parents[1] / 'data' / 'sample_ticks.csv'
    out.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.utcnow().replace(second=0, microsecond=0)
    price = 22500.0
    rows = []
    for i in range(2000):
        ts = now + timedelta(seconds=i)
        shock = gauss(0, 3)
        price = max(100.0, price + shock)
        rows.append(
            {
                'timestamp': ts.isoformat(),
                'symbol': 'NIFTY',
                'ltp': round(price, 2),
                'volume': int(abs(gauss(250, 70))),
                'bid': round(price - 0.1, 2),
                'ask': round(price + 0.1, 2),
                'bid_qty': int(abs(gauss(500, 120))),
                'ask_qty': int(abs(gauss(500, 120))),
            }
        )

    with out.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f'Wrote {len(rows)} sample ticks to {out}')


if __name__ == '__main__':
    main()
