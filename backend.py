"""Example API backend"""
import datetime


WEEKDAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thurday",
    "Friday",
    "Saturday",
    "Sunday"
]


async def current_weekday():
    now = datetime.datetime.now()
    # monday is 1, we want it to be 0 so subtract 1
    return WEEKDAY_NAMES[now.isoweekday() - 1]
