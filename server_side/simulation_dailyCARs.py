from collections import defaultdict
import datetime
import sqlite3
import click
import random
import pprint

#from server_side.f_db import get_db
#from server_side.add_mover import add_new_mover
import add_mover
import crud_bp
import refactor_CARs
import workout_writer
from server_side.crud_bp import mover_info_dict

# make a new workout
# in THIS FORMAT:

# then record this workout as bouts

'''
WRITE WORKOUT request example:

{'comments': '',
 'date_init': '2023-02-20',
 'id': '',
 'inputs': {'1': {'completed': True,
                  'drill_name': 'CARs',
                  'duration': '43',
                  'end_coord': '',
                  'external_load': '',
                  'fixed_side_anchor_id': '',
                  'id': 1,
                  'passive_duration': '',
                  'ref_joint_id': '3',
                  'ref_joint_name': 'LT',
                  'ref_joint_side': 'mid',
                  'ref_zones_id_a': '',
                  'ref_zones_id_b': '',
                  'rotational_value': '',
                  'rpe': 5,
                  'start_coord': ''},
 'moverid': 1,
 'schema': [{'circuit': ['1'], 'iterations': 1},
            {'circuit': ['2'], 'iterations': 1},
            {'circuit': ['3'], 'iterations': 1}],
 'workout_title': 'Trying API AGAIN'}
 
*****
RECORD WORKOUT request example:
{'15': {'Rx': {'comments': None,
               'drill_name': 'CARs',
               'duration': 36,
               'end_coord': '',
               'external_load': '',
               'fixed_side_anchor_id': '',
               'id': 15,
               'passive_duration': '',
               'rails': None,
               'ref_joint_id': 7,
               'ref_joint_name': 'GH',
               'ref_joint_type': 'synovial',
               'ref_zones_id_a': '',
               'ref_zones_id_b': '',
               'rotational_value': '',
               'rpe': 9,
               'side': 'L',
               'start_coord': ''},
        'results': {'duration': '38',
                    'external_load': 0,
                    'passive_duration': 0,
                    'rails': False,
                    'rpe': 6}},
 'date_done': '2023-02-22T17:19:07.782Z',
 'mover_id': '2',
 'workout_id': 8}
 '''


def dailyCARs(db, name, days_per_week, time_span, all=True, selected_CARs=[]):
    curs = db.cursor()
    tuday = datetime.date.today()
    add_mover.add_new_mover(db, name, 'SIM')
    # GET THIS ROW TO USE for mover_dict lookups
    moverid = curs.execute(
        'SELECT id FROM movers WHERE first_name = (?) AND last_name = (?)', (name, 'SIM'))

    workout_request = {'comments': 'simulated CARs inputs',
                       'date_init': f'{str(datetime.date.today())}',
                       'id': '',
                       'inputs': {},
                       'moverid': f'{moverid}',
                       'schema': [],
                       'workout_title': 'CARs Simulation'}

    mover_dict = mover_info_dict(db, moverid)

    joints_to_leave_out = ["Toes", "Hallux"]

    for i, j in enumerate(mover_dict.keys()):
        joint_name_list = j.split()
        if any(joint in j for joint in joints_to_leave_out):
            continue
        if not all:
            # 'all' here refers to ALL the CARs
            if joint_name_list[1] not in selected_CARs:
                continue

        workout_request["inputs"][i+1] = {'completed': True,
                                          'drill_name': 'CARs',
                                          'duration': '120',
                                          'end_coord': '',
                                          'external_load': '',
                                          'fixed_side_anchor_id': '',
                                          'id': i+1,
                                          'passive_duration': '',
                                          'ref_joint_id': f'{mover_dict[j]["id"]}',
                                          'ref_joint_name': f'{joint_name_list[1]}',
                                          'ref_joint_side': f'{mover_dict[j]["side"]}',
                                          'ref_zones_id_a': '',
                                          'ref_zones_id_b': '',
                                          'rotational_value': '',
                                          'rpe': 5,
                                          'start_coord': ''}
        workout_request["schema"].append(
            {'circuit': [f'{i + 1}'], 'iterations': 1})

    workout_writer.workout_writer(db, workout_request)

    workout_id = curs.execute(
        'SELECT id FROM workouts WHERE moverid = (?) AND workout_title = (?)', (moverid, 'CARs Simulation'))

    # TODO finish building this factory function that will generate CARs requests as needed...
    def record_a_workout(date, inputID, ref_joint_id, joint_name, joint_type, side):
        res = {f'{inputID}': {'Rx': {
            'comments': None,
            'drill_name': 'CARs',
            'duration': 120,
            'end_coord': '',
            'external_load': '',
            'fixed_side_anchor_id': '',
            'id': inputID,
            'passive_duration': '',
            'rails': None,
            'ref_joint_id': ref_joint_id,
            'ref_joint_name': f'{joint_name}',
            'ref_joint_type': f'{joint_type}',
            'ref_zones_id_a': '',
            'ref_zones_id_b': '',
            'rotational_value': '',
            'rpe': 5,
            'side': f'{side}',
            'start_coord': ''},
            'results': {'duration': '120',
                        'external_load': 0,
                        'passive_duration': 0,
                        'rails': False,
                        'rpe': 5}},
            'date_done': f'{date}',
            'mover_id': '2',
            'workout_id': 8}

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

    # use refactor_CARs.py function


# just for testing...

if __name__ == "__main__":
    db = sqlite3.connect(
        '/Users/williamhbelew/Hacking/MSWN/instance/mswnSim.sqlite')
    dailyCARs(db, "Faker", 4, 60)
