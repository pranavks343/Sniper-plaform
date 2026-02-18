from datetime import datetime


def ensure_positive(value: float, field: str) -> None:
    if value <= 0:
        raise ValueError(f'{field} must be positive')


def ensure_date_order(start_date: datetime, end_date: datetime) -> None:
    if start_date >= end_date:
        raise ValueError('start_date must be earlier than end_date')
