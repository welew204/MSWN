from collections import defaultdict, deque
from operator import itemgetter
from pprint import pprint
import sqlite3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
import sys
import json
import datetime

from werkzeug.exceptions import abort

from server_side.f_db import get_db
from server_side.add_mover import add_new_mover
from server_side.workout_writer import workout_writer
from server_side.workout_recorder import workout_recorder
from server_side.mover_info_dict import mover_info_dict
# these give a "double-ended queue" of values that can be rotated by step!
from server_side.db_ref_vals import syn_zone_deque
from server_side.db_ref_vals import ses_zone_deque
from server_side.db_ref_vals import spine_zone_deque


bp = Blueprint('tissues', __name__)


@bp.route('/')
def index(mover_id):
    # print(f"Got this far (to {index})", file=sys.stderr)
    db = get_db()
    bouts = db.execute(
        'SELECT * FROM bout_log'
    ).fetchall()

    return 'Done', 201


@bp.route('/movers_list')
def get_movers():
    print(datetime.datetime.now())
    db = get_db()
    mover_rows = db.execute('SELECT * FROM movers').fetchall()
    res = {}
    for m in mover_rows:
        res[m["id"]] = [i for i in m]
    return jsonify(res), 201


@bp.route('/add_mover', methods=('POST',))
def add_mover_to_db():

    db = get_db()
    req = request.get_json()[0]
    fname = req['firstName']
    lname = req['lastName']
    mover_id = add_new_mover(db, fname, lname)

    return f"{fname} {lname} is added to the DB! ID: {mover_id}", 201


@bp.route('/write_workout', methods=('POST',))
def write_workout():
    db = get_db()
    req = request.get_json()
    with open('fake_workout_seeds.json', 'a') as json_seeds:
        json.dump(req, json_seeds)

    wkt_id = workout_writer(db, req)

    return f"Workout ID: {wkt_id} is written!", 201


@bp.route('/record_bout', methods=('POST',))
def record_bout():
    db = get_db()
    req = request.get_json()
    # ACTIVATE some bout harvesting as needed
    # with open('fake_record_seeds.json', 'a') as json_seeds:
    #json.dump(req, json_seeds)
    # pprint(req)
    workout_recorder(db, req)

    return f"Workout/results recorded!", 201


@bp.route('/record_workout', methods=('POST',))
def record_workout():
    db = get_db()
    req = request.get_json()
    with open('fake_rwkout_seeds.json', 'a') as json_seeds:
        json.dump(req, json_seeds)
    print("Recording workout as done")
    pprint(req)

    date_done, workout_id, moverid = req

    curs = db.cursor()

    curs.execute(
        '''UPDATE workouts 
            SET last_done = (?) 
            WHERE id = (?) 
            AND moverid = (?)''',
        (date_done, workout_id, moverid))
    db.commit()

    return f"Workout/results recorded!", 201


@bp.route('/delete_workout', methods=('POST',))
def delete_workout():
    db = get_db()
    curs = db.cursor()
    req = request.get_json()
    mover_id, id_to_delete = req

    pprint(req)
    curs.execute('''DELETE FROM workouts
                    WHERE workouts.moverid = (?)
                    AND workouts.id = (?)
                    ''', (mover_id, id_to_delete))
    db.commit()
    to_return = get_workouts(mover_id)
    return to_return


@ bp.route('/workouts/<int:mover_id>')
def get_workouts(mover_id):
    if mover_id == 0:
        return json.dumps(["Sorry! No workouts yet."]), 200
    db = get_db()
    curs = db.cursor()
    workout_rows = curs.execute('''SELECT
                                    workouts.id,
                                    date_init,
                                    last_done,
                                    workout_title,
                                    workouts.moverid,
                                    workouts.comments
                                    FROM workouts
                                    WHERE workouts.moverid = (?)
                                    ''', (mover_id,)).fetchall()

    wkouts = {}

    def schema_factory():
        return {"circuit": [], "iterations": 0}

    for row in workout_rows:
        wkout = {k: row[k] for k in row.keys()}
        wkout["inputs"] = []
        wkout["schema"] = defaultdict(schema_factory)
        wkouts[wkout['id']] = wkout

    # pprint(wkouts)

    for workout_id in wkouts.keys():
        curr_wkout = wkouts[workout_id]
        input_rows = curs.execute('''SELECT
                                    programmed_drills.id,
                                    programmed_drills.moverid,

                                    input_sequence,
                                    circuit_iterations,
                                    ref_zones_id_a,
                                    ref_zones_id_b,
                                    fixed_side_anchor_id,
                                    rotational_value,
                                    start_coord,
                                    end_coord,
                                    drill_name,
                                    rails,
                                    reps_array,
                                    multijoint,
                                    duration,
                                    passive_duration,
                                    rpe,
                                    external_load,
                                    comments,
                                    joints.side,
                                    ref_joints.rowid,
                                    ref_joints.joint_name,
                                    ref_joints.joint_type,
                                    ref_joints.joint_name
                                    FROM programmed_drills
                                    LEFT JOIN joints
                                    ON joints.id = joint_id
                                    LEFT JOIN ref_joints
                                    ON ref_joints.rowid = joints.ref_joints_id
                                    WHERE programmed_drills.moverid = (?) AND workout_id = (?)''', (mover_id, workout_id))
        for row in input_rows:
            input = {k: row[k] for k in row.keys() if k != "moverid"}

            input_sequence = input.pop("input_sequence")
            circuit_iterations = input.pop("circuit_iterations")

            input["ref_joint_name"] = input.pop("joint_name")
            input["ref_joint_type"] = input.pop("joint_type")
            input["ref_joint_id"] = input.pop("rowid")
            input["reps_array"] = [int(i)
                                   for i in input["reps_array"].split(',')]

            if input["rails"] == "1":
                input["rails"] = True
            elif input["rails"] == "0":
                input["rails"] = False

            curr_wkout["schema"][input_sequence[0]]["circuit"].append(
                (input_sequence[1], input["id"]))
            curr_wkout["schema"][input_sequence[0]
                                 ]["iterations"] = circuit_iterations

            curr_wkout["inputs"].append(input)

        for circ in curr_wkout["schema"]:
            # sort the "circuit" array based on passed in ordering
            curr_wkout["schema"][circ]["circuit"].sort(key=lambda inp: inp[0])
            # list-comprehension to only snag the id part of each tuple
            new_circuit = [inp[1]
                           for inp in curr_wkout["schema"][circ]["circuit"]]
            # replace old "circuit" with streamlined array!
            curr_wkout["schema"][circ]["circuit"] = new_circuit
        curr_wkout["schema"] = [i for i in curr_wkout["schema"].values()]

    array_to_send = [value for (key, value) in wkouts.items()]
    return json.dumps(array_to_send), 200

# inputs is not getting used for anything right now


@ bp.route('/inputs')
def get_inputs():
    with open('/Users/williamhbelew/Hacking/MSWN/server_side/fakeInputData.json') as w:
        inputs = json.load(w)
        return jsonify(inputs), 200


@ bp.route('/drill_ref')
def drill_ref():
    drills_to_send = {
        "CARs": {},
        "capsule CAR": {"zones": []},
        "PRH": {"zones": [], "bias": [], "position": [0], "rotation": []},
        "Muscular Scan": {"zones": [], "bias": [], "position": [0], "rotation": []},
        "IC1": {"zones": [], "bias": [-100, 100], "rails": [], "position": [100], "rotation": [-100, 100], "passive duration": []},
        "IC2": {"zones": [], "bias": [], "rails": [], "position": [100], "rotation": [], "passive duration": []},
        "IC3": {"zones": [], "bias": [], "position": [], "rotation": [], "position B": []}
    }

    return jsonify(drills_to_send), 200


@ bp.route('/joint_ref')
def joint_ref():
    db = get_db()
    joint_ref = defaultdict(list)
    joint_ref_final = []

    # BELOW returns a list of sqlite3.Row objects (with index, and keys), but is NOT a real dict
    zone_ref_rows = db.execute('''SELECT
                            ref_zones.id,
                            ref_zones.side,
                            ref_zones.zone_name,
                            ref_joints.joint_type,
                            ref_joints.joint_name,
                            ref_joints.rowid
                            FROM ref_zones
                            INNER JOIN ref_joints
                            ON ref_zones.ref_joints_id=ref_joints.rowid''').fetchall()
    for row in zone_ref_rows:
        zone = {k: row[k] for k in row.keys()}
        # only want one side and spine for reference
        if row["side"] != "mid":
            joint_ref[row["side"]+" " + row["joint_name"]].append(zone)
        else:
            joint_ref[row["joint_name"]].append(zone)
    # cleaning up nested object to send to react:
    for joint in joint_ref.keys():
        j = joint_ref[joint]
        joint_obj = {"name": joint, "id": j[0]["rowid"], "zones": j}
        joint_ref_final.append(joint_obj)

    return jsonify(joint_ref_final), 200


# can't quite get my selects working right! so just hard-coding in adjacency table...
prox_neighbor_joints = {'l-ankle': {'proximal_joint_id': 15,
                                    'proximal_joint_selector': 'l-knee',
                                    'ref_joint_id': 17},
                        'l-elbow': {'proximal_joint_id': 7,
                                    'proximal_joint_selector': 'l-gh',
                                    'ref_joint_id': 9},
                        'l-gh': {'proximal_joint_id': 5,
                                 'proximal_joint_selector': 'l-scapular-thoracic',
                                 'ref_joint_id': 7},
                        'l-hallux': {'proximal_joint_id': 17,
                                     'proximal_joint_selector': 'l-ankle',
                                     'ref_joint_id': 21},
                        'l-hip': {'proximal_joint_id': 3,
                                  'proximal_joint_selector': 'lt',
                                  'ref_joint_id': 13},
                        'l-knee': {'proximal_joint_id': 13,
                                   'proximal_joint_selector': 'l-hip',
                                   'ref_joint_id': 15},
                        'l-scapular-thoracic': {'proximal_joint_id': 2,
                                                'proximal_joint_selector': 'tc',
                                                'ref_joint_id': 5},
                        'l-toes': {'proximal_joint_id': 17,
                                   'proximal_joint_selector': 'l-ankle',
                                   'ref_joint_id': 20},
                        'l-wrist': {'proximal_joint_id': 9,
                                    'proximal_joint_selector': 'l-elbow',
                                    'ref_joint_id': 11},
                        'ao': {'proximal_joint_id': None, 'ref_joint_id': 1},
                        'lt': {'proximal_joint_id': 2,
                               'proximal_joint_selector': 'tc',
                               'ref_joint_id': 3},
                        'tc': {'proximal_joint_id': 1,
                               'proximal_joint_selector': 'ao',
                               'ref_joint_id': 2},
                        'r-ankle': {'proximal_joint_id': 14,
                                    'proximal_joint_selector': 'r-knee',
                                    'ref_joint_id': 16},
                        'r-elbow': {'proximal_joint_id': 6,
                                    'proximal_joint_selector': 'r-gh',
                                    'ref_joint_id': 8},
                        'r-gh': {'proximal_joint_id': 4,
                                 'proximal_joint_selector': 'r-scapular-thoracic',
                                 'ref_joint_id': 6},
                        'r-hallux': {'proximal_joint_id': 16,
                                     'proximal_joint_selector': 'r-ankle',
                                     'ref_joint_id': 19},
                        'r-hip': {'proximal_joint_id': 3,
                                  'proximal_joint_selector': 'lt',
                                  'ref_joint_id': 12},
                        'r-knee': {'proximal_joint_id': 12,
                                   'proximal_joint_selector': 'r-hip',
                                   'ref_joint_id': 14},
                        'r-scapular-thoracic': {'proximal_joint_id': 2,
                                                'proximal_joint_selector': 'tc',
                                                'ref_joint_id': 4},
                        'r-toes': {'proximal_joint_id': 16,
                                   'proximal_joint_selector': 'r-ankle',
                                   'ref_joint_id': 18},
                        'r-wrist': {'proximal_joint_id': 8,
                                    'proximal_joint_selector': 'r-elbow',
                                    'ref_joint_id': 10}}


def failed_proximal_joint_lookups():
    db = get_db()
    curs = db.cursor()
    # start by building an adjacency table (neighboring joints)
    bone_lookups = {}
    ref_joints_rows = curs.execute('''SELECT 
                                ref_bone_end.id,
                                ref_bone_end.bone_name,
                                ref_bone_end.side, 
                                ref_bone_end.end,
                                ref_joints.rowid AS ref_joint_id,
                                ref_joints.joint_name 
                                FROM ref_bone_end
                                LEFT JOIN ref_joints
                                ON ref_bone_end.id = ref_joints.bone_end_id_b''').fetchall()
    for row in ref_joints_rows:
        if row["end"] == 1:
            print("this is a bone-end of '1'...")
            pprint({k: row[k] for k in row.keys()})
            continue
            # these are bone-ends that are the bone_end_id_a for a joint!!!! thus, None in this SELECT
        # print(row)
        else:
            raw_ref = {k: row[k] for k in row.keys()}
            bone_lookups[(raw_ref["bone_name"], raw_ref["side"])
                         ] = raw_ref

    print("here are the bone lookups...")
    pprint(bone_lookups)

    neighbor_joints = {}

    for k, v in bone_lookups.items():
        res = curs.execute('''SELECT ref_joints.rowid AS ref_joint_id,
                                        ref_joints.joint_name,
                                        ref_joints.side, 
                                        ref_joints.joint_type,
                                        ref_joints.bone_end_id_a,
                                        ref_joints.bone_end_id_b,
                                        ref_bone_end.bone_name AS proximal_bone, 
                                        ref_bone_end.side AS bone_side
                                        FROM ref_joints
                                        LEFT JOIN ref_bone_end
                                        ON ref_bone_end.id = ref_joints.bone_end_id_a''').fetchall()
        for row in res:
            # NEED TO TROUBLE SHOOT THESE... proximal_joint_id is NONE for toes, scapular-thoracic, hallux
            # possibly related to my 'ends' filter used in the inital select (on bone-ends)
            raw_row = {
                k: row[k] for k in row.keys()}
            # pprint(raw_row)
            jname_str = f'{row["side"]}-{row["joint_name"]}'

            prox_joint_id = bone_lookups[(
                row["proximal_bone"], row["bone_side"])]["ref_joint_id"]
            neighbor_joints[jname_str.lower()] = {
                "ref_joint_id": row["ref_joint_id"], "proximal_joint_id": prox_joint_id}

    pprint(neighbor_joints)


@ bp.route('/status/<int:mover_id>')
def status(mover_id):
    # print(f"Got this far (to {index})", file=sys.stderr)
    db = get_db()
    curs = db.cursor()
    # start by building an adjacency table (neighboring joints)

    tissue_status = []
    # BELOW returns a list of sqlite3.Row objects (with index, and keys), but is NOT a real dict
    tissue_status_rows = db.execute(
        '''SELECT  bout_log.joint_id,
                bout_log.id,
                bout_log.date, 
                bout_log.duration, 
                bout_log.rpe, 
                bout_log.tissue_type,
                bout_log.rotational_value,
                joints.ref_joints_id,
                ref_joints.joint_name,
                ref_joints.side
                FROM bout_log 
                LEFT JOIN joints
                ON bout_log.joint_id = joints.id
                LEFT JOIN ref_joints
                ON joints.ref_joints_id = ref_joints.rowid
                WHERE bout_log.moverid = (?) 
                ''', (mover_id,)
    ).fetchall()

    for row in tissue_status_rows:
        row_goods = {k: row[k] for k in row.keys()}
        if row_goods["side"] != 'mid':
            svg_zone_selector = f'{row_goods["side"].lower()}-{row_goods.pop("joint_name").lower()}'
        else:
            svg_zone_selector = f'{row_goods.pop("joint_name").lower()}'
        if svg_zone_selector == "ao":
            proximal_joint_selector = "occiput"
        else:
            proximal_joint_selector = prox_neighbor_joints[svg_zone_selector]['proximal_joint_selector']
        row_goods['svg_zone_selector'] = svg_zone_selector
        row_goods['rotational_value'] = int(
            row_goods['rotational_value']) if row_goods['rotational_value'] is not None else ""
        row_goods['joint_name_selector'] = f'jt-{svg_zone_selector}'
        row_goods['proximal_joint_selector'] = f'jt-{proximal_joint_selector}'

        tissue_status.append(row_goods)
    return jsonify({"status": tissue_status}), 200


@ bp.route('/training_log/<int:mover_id>')
def training_log(mover_id):

    db = get_db()
    training_log = []
    # BELOW returns a list of sqlite3.Row objects (with index, and keys),
    # but is NOT a real dict

    # START HERE ... I now need this
    # to select from bout_log ONLY
    # unique workouts
    # (left join on programmed_drills)
    # so that I can list them in the timeline
    training_log_rows = db.execute(
        '''SELECT DISTINCT workouts.workout_title, 
                    workouts.id,
                    bout_log.date 
                    FROM bout_log 
                    LEFT JOIN programmed_drills  
                    ON bout_log.programmed_drills_id = programmed_drills.id
                    LEFT JOIN workouts 
                    ON programmed_drills.workout_id = workouts.id 
                    WHERE bout_log.moverid = (?)''', (
            mover_id,)
    ).fetchall()
    # this converts all rows returned into dictiornary, that is added to the tissue_status list
    for row in training_log_rows:
        training_log.append({k: row[k] for k in row.keys()})
    # sort on way to react into DESCENDING order from most recent (by ['date'])
    training_log_final = sorted(
        training_log, key=itemgetter('date'), reverse=True)
    return jsonify({"training_log": training_log_final}), 200


@ bp.route('/add_bout/<int:moverid>', methods=('POST',))
def add_bout(moverid):
    req = request.get_json()
    print(req, file=sys.stderr)
    return "Oh ya!", 201

    db = get_db()
    curs = db.cursor()
    bouts_to_input = []
    print(req)

    for b in req:
        bundle = []
        field_names = []
        qmarks = []
        for key in list(b.keys()):
            # exec() function runs a string as python, so I can use an f-string to dynamically create vraible from a stirng
            exec(f"{key}_field = b[key]")
            exec(f"print({key}_field)")
            # then, I add the field_name (string) to an array -- THIS MUST MATCH THE DB!
            field_names.append(f"{key}")
            # then, I add the value of that variable to the bundle
            exec(f"bundle.append({key}_field)")
            # and finally a question mark for each field
            qmarks += '?'
        # once I've gone through ALL keys included in the request bout, I will have a tuple that has...
        bundle.insert(1, moverid)
        field_names.insert(1, "moverid")
        qmarks.insert(1, "?")
        bouts_to_input.append([field_names, qmarks, bundle])

    for bout in bouts_to_input:
        field_names = ",".join(bout[0])
        qmarks = ",".join(bout[1])
        curs.execute(
            f'INSERT INTO bout_log ({field_names}) VALUES ({qmarks})', (bout[2]))
        db.commit()

    return f"{len(bouts_to_input)} bout(s) logged!", 201


if __name__ == "__main__":
    """db = sqlite3.connect('/Users/williamhbelew/Hacking/MSWN/instance/mswnapp.sqlite')
    mover_1_id = 1
    mover_2_id = 2
    mover_1_info = mover_info_dict(db, mover_1_id)
    mover_2_info = mover_info_dict(db, mover_2_id)
    print("hello")

    get_movers()
    """


"""
@bp.route('/delete_bouts')

@bp.route('/read_bouts') """
