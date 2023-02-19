from collections import defaultdict
import datetime
import sqlite3
import click
import random
import pprint

#from server_side.f_db import get_db
#from server_side.add_mover import add_new_mover
import add_mover


def dailyCARs(db, name, days_per_week, time_span, all=True, selected_CARs=[]):
    curs = db.cursor()
    tuday = datetime.date.today()
    add_mover.add_new_mover(db, name, 'SIM')

    dates_array = [
        tuday + datetime.timedelta(days=x) for x in range(time_span)]

    # this RANDOMLY selects days each week to NOT do CARs,
    # rest days determined by number of days per week
    rest_days = (7 - days_per_week) if days_per_week <= 7 else 2
    day_per_week_counter = 0
    days_to_skip = []
    for i, d in enumerate(dates_array):
        day_count = i % 7
        if day_count == 0:
            days_off = random.sample(range(7), rest_days)
        if day_count in days_off:
            days_to_skip.append(d)
    dates_array = [d for d in dates_array if d not in days_to_skip]

# just for testing...


if __name__ == "__main__":
    db = sqlite3.connect(
        '/Users/williamhbelew/Hacking/MSWN/instance/mswnSim.sqlite')
    dailyCARs(db, "Faker", 4, 60)
