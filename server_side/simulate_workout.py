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

'''WRITE WORKOUT request example:

{
    "id": "",
    "workout_title": "Latest Wkout Shape",
    "date_init": "2023-03-28",
    "moverid": 1,
    "comments": "",
    "inputs": {
        "1": {
            "id": 1,
            "drill_name": "push-up",
            "duration": 20,
            "reps_array": [
                2,
                5,
                1,
                1,
                1,
                1
            ],
            "rpe": 6,
            "external_load": 0,
            "side": "",
            "multijoint": true,
            "completed": true
        },
        "2": {
            "ref_joint_id": "14",
            "ref_joint_name": "knee",
            "id": 2,
            "ref_zones_id_a": "",
            "ref_zones_id_b": "",
            "fixed_side_anchor_id": "",
            "rotational_value": "",
            "start_coord": "",
            "end_coord": "",
            "drill_name": "CARs",
            "duration": 60,
            "passive_duration": "",
            "rpe": 6,
            "reps_array": [
                1,
                0,
                0,
                0,
                0,
                0
            ],
            "multijoint": false,
            "external_load": "",
            "ref_joint_side": "R",
            "completed": true
        },
        "3": {
            "ref_joint_id": 15,
            "ref_joint_name": "knee",
            "id": 3,
            "ref_zones_id_a": "",
            "ref_zones_id_b": "",
            "fixed_side_anchor_id": "",
            "rotational_value": "",
            "start_coord": "",
            "end_coord": "",
            "drill_name": "CARs",
            "duration": 60,
            "passive_duration": "",
            "rpe": 6,
            "reps_array": [
                1,
                0,
                0,
                0,
                0,
                0
            ],
            "multijoint": false,
            "external_load": "",
            "ref_joint_side": "L",
            "completed": true
        },
        "4": {
            "id": 4,
            "drill_name": "plank",
            "duration": 15,
            "reps_array": [
                2,
                0,
                0,
                0,
                0,
                0
            ],
            "rpe": 9,
            "external_load": 10,
            "side": "",
            "multijoint": true,
            "completed": true
        },
        "5": {
            "id": 5,
            "drill_name": "",
            "duration": 0,
            "reps_array": [
                1,
                0,
                0,
                0,
                0,
                0
            ],
            "rpe": 0,
            "external_load": 0,
            "side": "",
            "multijoint": true
        }
    },
    "schema": [
        {
            "circuit": [
                "1"
            ],
            "iterations": 1
        },
        {
            "circuit": [
                "2"
            ],
            "iterations": 1
        },
        {
            "circuit": [
                "3"
            ],
            "iterations": 1
        },
        {
            "circuit": [
                "4"
            ],
            "iterations": 1
        },
        {
            "circuit": [
                "5"
            ],
            "iterations": 1
        }
    ]
}'''
'''RECORD WORKOUT request example:
{
    "2": {
        "Rx": {
            "id": 2,
            "ref_zones_id_a": null,
            "ref_zones_id_b": null,
            "fixed_side_anchor_id": null,
            "rotational_value": null,
            "start_coord": null,
            "end_coord": null,
            "drill_name": "push-up",
            "rails": null,
            "reps_array": [
                2,
                5,
                1,
                1,
                1,
                1
            ],
            "multijoint": 1,
            "duration": 20,
            "passive_duration": null,
            "rpe": 6,
            "external_load": 0,
            "comments": null,
            "side": null,
            "ref_joint_name": null,
            "ref_joint_type": null,
            "ref_joint_id": null
        },
        "results": {
            "rails": null,
            "passive_duration": null,
            "duration": 20,
            "rpe": 6,
            "external_load": 0,
            "reps_array": [
                2,
                5,
                1,
                1,
                1,
                1
            ]
        }
    },
    "date_done": "2023-03-28T21:31:58.614Z",
    "workout_id": 2,
    "mover_id": 1
}'''


def clone_workout(db, workout_id, to_mover_id, simulation=False):
    # ***I only run this function if I ALREADY know I want/need to clone
    # query db with workout, + programmed_drills
    # TOTEST > workout_id is ASSUMED to exist
    curs = db.cursor()
    drill_query = curs.execute('''SELECT 
                                workouts.workout_title,
                                workouts.comments AS wkt_comments,
                                programmed_drills.*,
                                joints.ref_joints_id AS ref_joint_id,
                                ref_joints.joint_name AS ref_joint_name,
                                ref_joints.side
                                FROM workouts 
                                LEFT JOIN programmed_drills ON
                                workouts.id = programmed_drills.workout_id
                                LEFT JOIN joints ON
                                programmed_drills.joint_id = joints.id
                                LEFT JOIN ref_joints ON
                                joints.ref_joints_id = ref_joints.rowid
                                WHERE workouts.id = (?)''',
                               (workout_id,)).fetchall()
    if simulation:
        comments_string = f'simulation+clone of {drill_query[0]["workout_title"]}, previous comments: {drill_query[0]["wkt_comments"]}'
    else:
        comments_string = f'clone of ... {drill_query[0]["wkt_comments"]}'

    workout_request = {
        "workout_title": f'"{drill_query[0]["workout_title"]}" clone',
        "comments": comments_string,
        "moverid": to_mover_id,
        "date_init": datetime.date.today().strftime("%Y-%m-%d")
    }
    drills_as_inputs = {}
    schema = []
    for i, row in enumerate(drill_query):
        each_drill = {k: row[k] for k in row.keys() if k not in [
            "workout_title", "wkt_comments", "workout_id", "moverid", "joint_id"]}
        reps_array_as_list = [int(i)
                              for i in each_drill.pop('reps_array').split(',')]
        # print(reps_array_as_list)
        if each_drill['multijoint'] == 1:
            each_drill.pop("ref_joint_id")
            each_drill.pop("ref_joint_name")
            each_drill.pop("ref_zones_id_a")
            each_drill.pop("ref_zones_id_b")
            each_drill.pop("passive_duration")
            each_drill.pop("rails")
            each_drill.pop("end_coord")
            each_drill.pop("start_coord")
        else:
            each_drill['ref_joint_side'] = each_drill.pop('side')
        # print(f'working on cloning each drill (programmed_drill # {each_drill["id"]} shown below...)')
        # pprint.pprint(each_drill)
        date = each_drill.pop("date")
        each_drill["completed"] = True
        each_drill['reps_array'] = reps_array_as_list

        # this handles the schema info by ...
        # > taking payload info, and converting input_sequence into a list of strings
        # > use the circuit index to check for circuits,
        # > then if empty, add a fresh circuit with db vals
        # > else just add naive drill_id (i+1) to 'circuits' array
        # > and
        iterations = each_drill.pop("circuit_iterations")
        input_sequence = each_drill.pop("input_sequence").split('-')
        if len(schema) == 0 or int(input_sequence[0]) >= len(schema):
            # this is checking if item is in array yet! this is how python internally checks indexes!
            schema_to_add = {'circuit': [
                str(i+1)], 'iterations': iterations}
            schema.append(schema_to_add)
        else:
            # otherwise, just need to access the item in the schema
            # print(int(input_sequence[0]))
            schema[int(input_sequence[0])]['circuit'].append(str(i+1))

        drills_as_inputs[i+1] = each_drill

    #print("printing the workout request after pull from SQL...")
    workout_request["inputs"] = drills_as_inputs
    workout_request["schema"] = schema
    # pprint.pprint(workout_request)

    before_write_workout = workout_request

    new_workout_id = workout_writer.workout_writer(db, workout_request)
    # pprint.pprint(before_write_workout.keys())
    # pprint.pprint(workout_request.keys())
    # i believe this will return a CHANGED workout_request...
    return new_workout_id
    # add "simulation" to comments
    # --> i will be unpacking each input)


def generate_rx_record(date, input_payload):
    # INPUT: input_payload = (...everything needed below!)
    (circuit_iterations,
     drill_name,
     duration,
     end_coord,
     external_load,
     fixed_side_anchor_id,
     input_sequence,
     passive_duration,
     rails,
     ref_joint_id,
     ref_joint_name,
     ref_joint_side,
     ref_joint_type,
     ref_zones_id_a,
     ref_zones_id_b,
     rotational_value,
     rpe,
     start_coord,
     drill_id,
     moverid,
     workout_id,
     reps_array,
     multijoint
     ) = itemgetter(
        'circuit_iterations',
        'drill_name',
        'duration',
        'end_coord',
        'external_load',
        'fixed_side_anchor_id',
        'input_sequence',
        'passive_duration',
        'rails',
        'ref_joint_id',
        'ref_joint_name',
        'ref_joint_side',
        'ref_joint_type',
        'ref_zones_id_a',
        'ref_zones_id_b',
        'rotational_value',
        'rpe',
        'start_coord',
        'id',
        'moverid',
        'workout_id',
        'reps_array',
        'multijoint')(input_payload)
    # OUTPUT: needs to match fields below, beware of hard-coded values
    # be sure to grab input_payload as dictionary from sql query of db via workout_id
    # unpack input_payload
    # build an dictionary with the right fields...
    res = {drill_id: {'Rx': {
        'comments': "simulation",
        'drill_name': drill_name,
        'duration': duration,
        'end_coord': end_coord,
        'external_load': external_load,
        'fixed_side_anchor_id': fixed_side_anchor_id,
        'id': drill_id,
        'passive_duration': passive_duration,
        'rails': rails,
        'ref_joint_id': ref_joint_id,
        'ref_joint_name': ref_joint_name,
        'ref_joint_type': ref_joint_type,
        'ref_zones_id_a': ref_zones_id_a,
        'ref_zones_id_b': ref_zones_id_b,
        'rotational_value': rotational_value,
        'rpe': rpe,
        'side': ref_joint_side,
        'start_coord': start_coord,
        'reps_array': reps_array,
        'multijoint': multijoint},
        'results': {'duration': duration,
                    'external_load': external_load,
                    'passive_duration': passive_duration,
                    'rails': rails,
                    'rpe': rpe,
                    'reps_array': reps_array}},
        'date_done': date,
        'mover_id': moverid,
        'workout_id': workout_id}
    return res


def generate_workouts_over_time(db, start_date, time_span, days_per_week, wkt_id):
    '''return array of workout records --> workout_recorder.multiple_workout_recorder(),
    start_date comes in as a datetime already!'''
    curs = db.cursor()

    dates_array = [
        start_date + datetime.timedelta(days=x) for x in range(int(time_span))]

    # this RANDOMLY selects days each week to NOT do the indicated workout,
    # rest days determined by number of days per week
    dpw = int(days_per_week) if days_per_week <= 7 else 7
    rest_days = 7 - dpw
    days_to_skip = []
    for i, d in enumerate(dates_array):
        day_count = i % 7
        if day_count == 0:
            days_off = random.sample(range(7), rest_days)
        if day_count in days_off:
            days_to_skip.append(d)
    dates_array = [d for d in dates_array if d not in days_to_skip]
    # this includes randomly skipped days given the days per week

    wkt_rows = curs.execute('''SELECT programmed_drills.*,
                                joints.ref_joints_id AS ref_joint_id,
                                ref_joints.joint_name AS ref_joint_name,
                                ref_joints.side AS ref_joint_side,
                                ref_joints.joint_type AS ref_joint_type
                                FROM programmed_drills 
                                LEFT JOIN joints ON
                                programmed_drills.joint_id = joints.id
                                LEFT JOIN ref_joints ON
                                joints.ref_joints_id = ref_joints.rowid
                                WHERE programmed_drills.workout_id = (?)''',
                            (wkt_id,)).fetchall()

    wkts_to_record_array = []

    for i, d in enumerate(dates_array):
        for row in wkt_rows:
            each_input_payload = {k: row[k] for k in row.keys()}
            each_input_payload['reps_array'] = [int(i) for i in each_input_payload.pop(
                'reps_array').split(',')]
            # print(each_input_payload['reps_array'])
            #print(f'cloning each input as part of "generate_workouts_over_time"')
            # pprint.pprint(each_input_payload)
            wkt_record = generate_rx_record(
                d.strftime("%Y-%m-%d"), each_input_payload)
            wkts_to_record_array.append(wkt_record)

    # use wktid to get neccessary fields for 'generate_rx_record'
    # ---> build this function/ality
    # iterate through dates_array and run 'generate_rx_record' each time
    # return 'recorded_workout_array:=' (refactor'd)

    return wkts_to_record_array

#  BELOW:
#  Leaving this 'CARs' specific version, until I can build out auto. build a CARs
#  workout on init-db call
#  HEADS Up: this has some hard-coded values in it:
    # rpe == 5
    # duration = 120sec


def generate_CARs_record(date, inputID, ref_joint_id, joint_name, joint_type, side, moverid, workout_id):
    res = {inputID:
           {'Rx': {
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
            'start_coord': '',
            'multijoint': 0,
            'reps_array': [1, 0, 0, 0, 0, 0]},
            'results': {'duration': '120',
                        'external_load': 0,
                        'passive_duration': 0,
                        'rails': False,
                        'rpe': 5,
                        'reps_array': [1, 0, 0, 0, 0, 0]}},
           'date_done': f'{date}',
           'mover_id': moverid,
           'workout_id': workout_id}
    return res


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
    bodyweight = mover_dict.pop('bodyweight')
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
                                          'start_coord': '',
                                          'reps_array': [1, 0, 0, 0, 0, 0],
                                          'multijoint': 0}
        workout_request["schema"].append(
            {'circuit': [f'{i + 1}'], 'iterations': 1})

    # pprint.pprint(workout_request)

    workout_id = workout_writer.workout_writer(db, workout_request)
    # HEADS UP: writing this workout CHANGEs the workout_request data!
    # takes some values aways, adds some values, etc

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
             wkt_id,
             reps_array,
             multijoint) = itemgetter(
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
                'workout_id',
                'reps_array',
                'multijoint')(input)

            ref_joint_id, ref_joint_name, joint_side, joint_type = joint_info_lookups[joint_id]
            # print(joint_id)

            wkt_record = generate_CARs_record(
                d, inputID, ref_joint_id, ref_joint_name, joint_type, joint_side, mover_id, workout_id)

            recorded_workout_array.append(wkt_record)
    #print("got here...")
    # pprint.pprint(recorded_workout_array[0])
    workout_recorder.multiple_workout_recorder(db, recorded_workout_array)


@click.command('mswn-sim-workout')
def simulate_workout():
    db = get_db()
    curs = db.cursor()
    name = input(
        "What's the first name? (if exists, will look up, ELSE will create with last name will be 'SIM'): ")
    workoutID = input("What's the workout ID you'd like to use/clone?: ")
    # do a  little query validation (to make sure this workout exists)
    wkt_exists = curs.execute('''SELECT 
                                EXISTS(SELECT 1 
                                FROM workouts 
                                WHERE workouts.id=(?)) AS chkr''',
                              (workoutID, )).fetchone()
    while wkt_exists["chkr"] == 0:
        workoutID = input(
            "Oops, that wkout doesn't exist; try entering a new workout ID #: ")
        wkt_exists = curs.execute('''SELECT 
                                EXISTS(SELECT 1 
                                FROM workouts 
                                WHERE workouts.id=(?)) AS chkr''',
                                  (workoutID, )).fetchone()
    while True:
        try:
            days_per_week = int(input(
                "Number of days per week to do workouts? (enter integer): "))
            if days_per_week <= 0 or days_per_week > 14:
                print("Ooops, you must enter a valid integer (0 - 14). Try again...")
                continue
            break
        except ValueError:
            print("Ooops, you must enter a valid integer (0 - 14). Try again...")
    time_span = input("What time-span should these be done over (in days)?: ")

    while True:
        start_date = input(
            "What is the start date (format: MM/DD/YYYY)? [if empty, default will be today]: ")
        if start_date == "":
            # handling default date (today)
            start_date = datetime.date.today()
            break
        else:
            try:
                start_date = datetime.date(
                    int(start_date[6:]), int(start_date[:2]), int(start_date[3:5]))
                break
            except ValueError:
                print("Ooops, you must enter a valid date. Try again...")

    # do a SELECT to find mover, if exists then continue
    mover_exists = curs.execute('''SELECT movers.id
                                FROM movers 
                                WHERE movers.first_name=(?)''',
                                (name, )).fetchone()
    print("Checking if mover exists...")
    if not mover_exists:
        # no mover w/ that namem, so can ADD mover, then clone workout
        mvrID = add_mover.add_new_mover(db, name, 'SIM')
        new_workoutID = clone_workout(db, workoutID, mvrID, simulation=True)
        print(
            f"Requested mover does not exist, creating a new mover \n{name} @ id: {mvrID}")

    else:
        # mover w/ that name, then have to check if the workout BELONGs to that mover (yet)
        mvrID = mover_exists["id"]
        print(f'Mover DOES exist, @ id: {mover_exists["id"]}')
        wkt_assigned = curs.execute('''SELECT 
                                EXISTS(SELECT 1 
                                FROM workouts 
                                WHERE workouts.id=(?) 
                                AND moverid=(?)) AS chkr''',
                                    (workoutID, mvrID)).fetchone()
        if wkt_assigned["chkr"] == 0:
            new_workoutID = clone_workout(
                db, workoutID, mvrID, simulation=True)
        else:
            # mover exists, and already has workout assigned,
            # ---> then just have to 'generate_workouts_over_time'
            new_workoutID = workoutID

    to_record_array = generate_workouts_over_time(
        db, start_date, time_span, days_per_week, new_workoutID)

    # pprint.pprint(to_record_array)

    workout_recorder.multiple_workout_recorder(db, to_record_array)

    click.echo('Workout simulation executed!')


def run_simulated_workout(app):
    app.cli.add_command(simulate_workout)


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
