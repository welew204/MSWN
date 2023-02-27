from collections import defaultdict
import datetime
import sqlite3
import click
import random
import pprint
from operator import itemgetter

#from server_side.f_db import get_db
#from server_side.add_mover import add_new_mover
import server_side.add_mover as add_mover
import server_side.workout_writer as workout_writer
import server_side.workout_recorder as workout_recorder
from server_side.crud_bp import mover_info_dict
from server_side.f_db import get_db

# make a new workout
# in THIS FORMAT:

# then record this workout as bouts

'''WRITE WORKOUT request example:

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
 'workout_title': 'Trying API AGAIN'}'''
'''RECORD WORKOUT request example:
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
    if selected_CARs:
        print(selected_CARs)
    curs = db.cursor()
    tuday = datetime.date.today()
    moverid = add_mover.add_new_mover(db, name, 'SIM')

    workout_request = {'comments': 'simulated CARs inputs',
                       'date_init': f'{str(datetime.date.today())}',
                       'id': '',
                       'inputs': {},
                       'moverid': moverid,
                       'schema': [],
                       'workout_title': 'CARs Simulation'}

    mover_dict = mover_info_dict(db, moverid)
    # pprint.pprint(mover_dict)

    joints_to_leave_out = ["Toes", "Hallux"]

    joint_info_lookups = {}

    for i, j in enumerate(mover_dict.keys()):
        j_type = mover_dict[j]["type"]
        j_side = mover_dict[j]["side"]
        j_ref_id = mover_dict[j]["ref_joint_id"]

        if j_type == "spinal":
            j_name = j
        else:
            joint_name_list = j.split()
            j_name = joint_name_list[1]

        joint_info_lookups[mover_dict[j]["id"]] = (
            j_ref_id, j_name, j_side, j_type)

        if any(joint in j for joint in joints_to_leave_out):
            continue
        if not all:
            # 'all' here refers to ALL the CARs
            if j_name not in selected_CARs:
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
                                          'ref_joint_name': f'{j_name}',
                                          'ref_joint_side': f'{mover_dict[j]["side"]}',
                                          'ref_zones_id_a': '',
                                          'ref_zones_id_b': '',
                                          'rotational_value': '',
                                          'rpe': 5,
                                          'start_coord': ''}
        workout_request["schema"].append(
            {'circuit': [f'{i + 1}'], 'iterations': 1})

    # pprint.pprint(workout_request)

    workout_id = workout_writer.workout_writer(db, workout_request)
    # HEADS UP: writing this workout CHANGEs the workout_request data!
    # takes some values aways, adds some values, etc

    # HEADS Up: this has some hard-coded values in it:
    # rpe == 5
    # duration = 120sec

    def record_a_workout(date, inputID, ref_joint_id, joint_name, joint_type, side):
        res = {inputID: {'Rx': {
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
            'mover_id': moverid,
            'workout_id': workout_id}
        return res

    dates_array = [
        tuday + datetime.timedelta(days=x) for x in range(int(time_span))]

    # this RANDOMLY selects days each week to NOT do CARs,
    # rest days determined by number of days per week
    dpw = int(days_per_week)
    rest_days = (7 - dpw) if dpw <= 7 else 2
    day_per_week_counter = 0
    days_to_skip = []
    for i, d in enumerate(dates_array):
        day_count = i % 7
        if day_count == 0:
            days_off = random.sample(range(7), rest_days)
        if day_count in days_off:
            days_to_skip.append(d)
    dates_array = [d for d in dates_array if d not in days_to_skip]

    recorded_workout_array = []

    #print("here's the workout_request after getting written...")
    # pprint.pprint(workout_request)

    for i, d in enumerate(dates_array):
        for inputID, input in workout_request["inputs"].items():
            # pprint.pprint(list(workout_request["inputs"][input].values()))

            (circuit_iterations,
             date,
             drill_name,
             duration,
             end_coord,
             external_load,
             fixed_side_anchor_id,
             input_sequence,
             joint_id,
             mover_id,
             passive_duration,
             ref_zones_id_a,
             ref_zones_id_b,
             rotational_value,
             rpe,
             start_coord,
             wkt_id) = itemgetter(
                'circuit_iterations',
                'date',
                'drill_name',
                'duration',
                'end_coord',
                'external_load',
                'fixed_side_anchor_id',
                'input_sequence',
                'joint_id',
                'moverid',
                'passive_duration',
                'ref_zones_id_a',
                'ref_zones_id_b',
                'rotational_value',
                'rpe',
                'start_coord',
                'workout_id')(input)

            ref_joint_id, ref_joint_name, joint_side, joint_type = joint_info_lookups[joint_id]
            # print(joint_id)

            # START HERE
            wkt_record = record_a_workout(
                d, inputID, ref_joint_id, ref_joint_name, joint_type, joint_side)

            recorded_workout_array.append(wkt_record)
    #print("got here...")
    # pprint.pprint(recorded_workout_array[0])
    workout_recorder.multiple_workout_recorder(db, recorded_workout_array)


@click.command('mswn-sim-dailyCARs')
def simulate_dailyCARs():
    db = get_db()
    name = input("What's the first name? (last name will be 'SIM'): ")
    days_per_week = input("Number of days per week? (enter integer): ")
    time_span = input("What time-span should these be done over (in days)?: ")
    joints_included = input(
        "Enter ALL for all joints, or a comma-seperated list of joints ")
    if joints_included == "ALL":
        dailyCARs(db, name, days_per_week, time_span)
    else:
        joints_list = joints_included.split(", ")
        dailyCARs(db, name, days_per_week, time_span,
                  all=False, selected_CARs=joints_list)
    click.echo('Simulated CARs have been added!')


def run_simulated_CARs(app):
    app.cli.add_command(simulate_dailyCARs)


# just for testing...
if __name__ == "__main__":
    db = sqlite3.connect(
        '/Users/williamhbelew/Hacking/MSWN/instance/mswnSim.sqlite')
    dailyCARs(db, "Faker", 4, 60)
