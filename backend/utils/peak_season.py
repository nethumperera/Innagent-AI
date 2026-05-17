# ════════════════════════════════════════════════════════════════
# InnAgent AI — Peak Season & Multiplier Logic
# Sri Lanka holidays, events, and seasonal pricing multipliers
# ════════════════════════════════════════════════════════════════

from datetime import date, timedelta
from typing import List, Tuple


# Sri Lanka peak seasons and events with multiplier ranges
PEAK_EVENTS: List[dict] = [
    {
        "name": "Sinhala/Tamil New Year",
        "start_month": 4, "start_day": 13,
        "end_month": 4, "end_day": 14,
        "multiplier_min": 1.8, "multiplier_max": 2.2,
        "region": "all",
    },
    {
        "name": "Christmas/New Year",
        "start_month": 12, "start_day": 24,
        "end_month": 1, "end_day": 2,
        "multiplier_min": 1.6, "multiplier_max": 2.0,
        "region": "all",
    },
    {
        "name": "Wesak Poya",
        "start_month": 5, "start_day": 12,
        "end_month": 5, "end_day": 13,
        "multiplier_min": 1.3, "multiplier_max": 1.5,
        "region": "all",
    },
    {
        "name": "Kandy Esala Perahera",
        "start_month": 7, "start_day": 20,
        "end_month": 8, "end_day": 10,
        "multiplier_min": 1.5, "multiplier_max": 1.8,
        "region": "kandy",
    },
    {
        "name": "Independence Day",
        "start_month": 2, "start_day": 4,
        "end_month": 2, "end_day": 4,
        "multiplier_min": 1.2, "multiplier_max": 1.4,
        "region": "all",
    },
    {
        "name": "Poson Poya",
        "start_month": 6, "start_day": 12,
        "end_month": 6, "end_day": 13,
        "multiplier_min": 1.2, "multiplier_max": 1.5,
        "region": "anuradhapura",
    },
    {
        "name": "European Winter Season",
        "start_month": 12, "start_day": 1,
        "end_month": 3, "end_day": 31,
        "multiplier_min": 1.2, "multiplier_max": 1.5,
        "region": "coastal",
    },
]

# Sri Lanka public holidays (2025/2026 — fixed-date ones)
PUBLIC_HOLIDAYS: List[Tuple[int, int, str]] = [
    (1, 15, "Thai Pongal"),
    (2, 4, "Independence Day"),
    (5, 1, "May Day"),
    (12, 25, "Christmas Day"),
]


def _date_in_range(check_date: date, start_month: int, start_day: int, end_month: int, end_day: int) -> bool:
    """Check if a date falls within a month/day range (handles year wrap for Dec-Jan)."""
    year = check_date.year
    if start_month <= end_month:
        start = date(year, start_month, start_day)
        end = date(year, end_month, end_day)
        return start <= check_date <= end
    else:
        # Year wrap (e.g., Dec 24 to Jan 2)
        start_this_year = date(year, start_month, start_day)
        end_next_year = date(year + 1, end_month, end_day)
        start_last_year = date(year - 1, start_month, start_day)
        end_this_year = date(year, end_month, end_day)
        return (start_this_year <= check_date <= end_next_year) or (start_last_year <= check_date <= end_this_year)


def get_peak_multiplier(target_date: date, hotel_city: str = "") -> Tuple[float, List[str]]:
    """
    Calculate the peak season multiplier for a given date and location.
    Returns (multiplier, list_of_matching_events).
    Uses the highest multiplier if multiple events overlap.
    """
    city_lower = hotel_city.lower().strip() if hotel_city else ""
    matching_events = []
    max_multiplier = 1.0

    for event in PEAK_EVENTS:
        region = event["region"]

        # Check region match
        if region == "all" or region in city_lower:
            if _date_in_range(target_date, event["start_month"], event["start_day"], event["end_month"], event["end_day"]):
                # Use midpoint of multiplier range
                mid_mult = (event["multiplier_min"] + event["multiplier_max"]) / 2
                matching_events.append(event["name"])
                if mid_mult > max_multiplier:
                    max_multiplier = mid_mult

    # Check public holidays
    for month, day, name in PUBLIC_HOLIDAYS:
        if target_date.month == month and target_date.day == day:
            if name not in [e for e in matching_events]:
                matching_events.append(name)
                if max_multiplier < 1.3:
                    max_multiplier = 1.3  # Minimum public holiday multiplier

    return round(max_multiplier, 2), matching_events


def get_demand_signal(occupancy_rate: float, multiplier: float) -> str:
    """Determine demand signal based on occupancy and multiplier."""
    if multiplier >= 1.6 or occupancy_rate >= 90:
        return "peak"
    elif multiplier >= 1.3 or occupancy_rate >= 75:
        return "high"
    elif occupancy_rate >= 50:
        return "medium"
    else:
        return "low"


def get_events_for_range(start_date: date, end_date: date, hotel_city: str = "") -> List[dict]:
    """Get all events that fall within a date range."""
    events = []
    current = start_date
    seen = set()
    while current <= end_date:
        _, event_names = get_peak_multiplier(current, hotel_city)
        for name in event_names:
            if name not in seen:
                seen.add(name)
                mult, _ = get_peak_multiplier(current, hotel_city)
                events.append({"name": name, "date": current.isoformat(), "multiplier": mult})
        current += timedelta(days=1)
    return events
