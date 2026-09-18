import pandas as pd
from datetime import date, timedelta

WINDOW_START = date(2024, 3, 1)
WINDOW_END = date(2025, 8, 31)

# (festival name, start date, end date) — a few days around each festival, not just one day
FESTIVAL_WINDOWS = [
    ("Holi 2024",           date(2024, 3, 24), date(2024, 3, 26)),
    ("Eid al-Fitr 2024",    date(2024, 4, 10), date(2024, 4, 12)),
    ("Independence Day 2024", date(2024, 8, 14), date(2024, 8, 16)),
    ("Raksha Bandhan 2024", date(2024, 8, 18), date(2024, 8, 20)),
    ("Ganesh Chaturthi 2024", date(2024, 9, 6), date(2024, 9, 8)),
    ("Dussehra 2024",       date(2024, 10, 11), date(2024, 10, 13)),
    ("Diwali 2024",         date(2024, 10, 29), date(2024, 11, 3)),
    ("Christmas/New Year 2024-25", date(2024, 12, 24), date(2025, 1, 2)),
    ("Republic Day 2025",   date(2025, 1, 25), date(2025, 1, 27)),
    ("Holi 2025",           date(2025, 3, 13), date(2025, 3, 15)),
    ("Eid al-Fitr 2025",    date(2025, 3, 30), date(2025, 4, 1)),
    ("Independence Day 2025", date(2025, 8, 14), date(2025, 8, 16)),
]


def get_season(month: int) -> str:
    if month in (12, 1, 2):
        return "Winter"
    elif month in (3, 4, 5, 6):
        return "Summer"
    else:  # 7-11
        return "Monsoon"


def is_festive(d: date) -> bool:
    return any(start <= d <= end for _, start, end in FESTIVAL_WINDOWS)


rows = []
current = WINDOW_START
while current <= WINDOW_END:
    rows.append({
        "date_id": current,
        "day_of_week": current.strftime("%A"),
        "is_weekend": current.weekday() >= 5,  # Sat=5, Sun=6
        "month": current.month,
        "month_name": current.strftime("%B"),
        "quarter": (current.month - 1) // 3 + 1,
        "year": current.year,
        "season": get_season(current.month),
        "is_festive_period": is_festive(current),
    })
    current += timedelta(days=1)

dim_date = pd.DataFrame(rows)
dim_date.to_csv("../data/dim_date.csv", index=False)

print(f"Total days generated: {len(dim_date)}\n")

print("--- Season distribution ---")
print(dim_date["season"].value_counts())

print("\n--- Weekend vs weekday ---")
print(dim_date["is_weekend"].value_counts())

print("\n--- Festive days ---")
print(f"Total festive days flagged: {dim_date['is_festive_period'].sum()}")

print("\n--- Spot check: known dates ---")
spot_checks = [date(2024, 11, 1), date(2024, 3, 15), date(2025, 8, 15)]
print(dim_date[dim_date["date_id"].isin(spot_checks)])

print("\n--- Integrity check: is_weekend matches day_of_week ---")
bad = dim_date[dim_date["is_weekend"] != dim_date["day_of_week"].isin(["Saturday", "Sunday"])]
print(f"Violations found: {len(bad)} (should be 0)")
