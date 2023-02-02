from collections import defaultdict, deque
from operator import itemgetter
from pprint import pprint
import sqlite3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
import sys
import json

from werkzeug.exceptions import abort

from server_side.f_db import get_db
from server_side.add_mover import add_new_mover
# these give a "double-ended queue" of values that can be rotated by step!
from server_side.db_ref_vals import syn_zone_deque
from server_side.db_ref_vals import ses_zone_deque
from server_side.db_ref_vals import spine_zone_deque


bp = Blueprint('tissues', __name__)


@bp.route('/')
def index(mover_id):
    #print(f"Got this far (to {index})", file=sys.stderr)
    db = get_db()
    bouts = db.execute(
        'SELECT * FROM bout_log'
    ).fetchall()

    return 'Done', 201


@bp.route('/movers_list')
def get_movers():
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
    add_new_mover(db, fname, lname)
    return f"{fname} {lname} is added to the DB!", 201


@bp.route('/write_workout', methods=('POST',))
def write_workout():
    db = get_db()
    cursor = db.cursor()
    req = request.get_json()[0]

    pprint(req)

    workout_to_add = []
    for key, val in req.items():
        if key == "id" or key == "inputs":
            continue
        if key == "schema":
            continue
        else:
            workout_to_add.append(val)
    workout_q_marks = ",".join("?" for _ in range(len(workout_to_add)))
    #print(f"WORKOUT qmarks: {workout_q_marks}", file=sys.stderr)
    cursor.execute(f'INSERT INTO workouts (workout_title, date_init, moverid, comments) VALUES ({workout_q_marks})',
                   tuple(workout_to_add))
    db.commit()
    wkt_id = cursor.lastrowid
    schema_lookups = {}
    for set, info in req["schema"].items():
        for i, inputID in enumerate(info["circuit"]):
            input_sequence = set + str(i+1)
            schema_lookups[inputID] = (input_sequence, str(info["iterations"]))
    #print(f"workout schema transcribed (schema_lookups): {schema_lookups}", file=sys.stderr)

    workout_title, date_init, moverid, comments = workout_to_add
    mover_dict = mover_info_dict(db, moverid)
    # pprint(mover_dict)
    for inputID, payload in req["inputs"].items():
        if "completed" not in payload:
            continue
        else:
            payload.pop("id")
            payload.pop("completed")
            payload.pop("ref_joint_id")
        if payload["ref_joint_side"] != 'mid':
            joint_key_string = payload["ref_joint_side"] + \
                " " + payload["ref_joint_name"]
        else:
            joint_key_string = payload["ref_joint_name"]

        payload.pop("ref_joint_name")
        payload.pop("ref_joint_side")

        if "ref_zone_name" in payload:
            fixed_side_anchor = mover_dict[joint_key_string]["zones"][payload["ref_zone_name"]
                                                                      ]["anchors"]["proximal"]
            #print(f"ANCHOR ID for mover: {fixed_side_anchor}", file=sys.stderr)
            payload["fixed_side_anchor_id"] = fixed_side_anchor
            payload.pop("ref_zone_name")

        joint_id = mover_dict[joint_key_string]["id"]
        payload["joint_id"] = joint_id

        input_seq, circuit_iterations = schema_lookups[inputID]
        payload["input_sequence"] = input_seq
        payload["circuit_iterations"] = circuit_iterations

        payload["date"] = date_init
        payload["moverid"] = moverid
        payload["workout_id"] = wkt_id

        input_fields = list(payload.keys())
        #input_fields[input_fields.index('rotational_bias')] = 'rotational_value'

        input_vals = list(payload.values())
        # pprint(payload)

        #print(f"INPUT fields: {input_fields}", file=sys.stderr)
        #print(f"INPUT values: {input_vals}", file=sys.stderr)

        input_q_marks = ",".join("?" for _ in range(len(input_fields)))
        #print(f"INPUT qmarks: {input_q_marks}", file=sys.stderr)
        sql_statement = f"INSERT INTO programmed_drills {tuple(input_fields)} VALUES ({input_q_marks})"
        #print(f"FINISHED SQL statement: {sql_statement}", file=sys.stderr)

        cursor.execute(sql_statement, tuple(input_vals))
        db.commit()

    print(f"Added workout (ID): {wkt_id}", file=sys.stderr)

    return f"Request is recieved!", 201


@bp.route('/record_workout', methods=('POST',))
def record_workout():
    db = get_db()
    req = request.get_json()
    print(f"record_workout request: ", file=sys.stderr)
    pprint(req)
    moverid = req.pop("mover_id")
    date_done = req.pop("date_done")
    mover_dict = mover_info_dict(db, moverid)
    # pprint(mover_dict)
    for inputID, vals in req.items():

        # these Rx values are based on the prescription of the drill
        drill = vals["Rx"]["drill_name"]
        rotational_value = int(vals["Rx"]["rotational_value"])
        start_coord = vals["Rx"]["start_coord"]
        if start_coord == '':
            start_coord = 0
        else:
            start_coord = int(start_coord)

        # should
        end_coord = vals["Rx"]["end_coord"]
        if end_coord == '':
            end_coord = 0
        else:
            end_coord = int(end_coord)

        comments = vals["Rx"]["comments"]
        side = vals["Rx"]["side"]
        ref_joint_id = vals["Rx"]["ref_joint_id"]
        ref_joint_name = vals["Rx"]["ref_joint_name"]
        # for quick lookups in the dict...
        ref_joint_name_string = str(side + " " + ref_joint_name)
        ref_zones_id_a = vals["Rx"]["ref_zones_id_a"]
        ref_zones_id_b = vals["Rx"]["ref_zones_id_b"]

        # these 'results' values are based on the execution of the drill
        duration = int(vals["results"]["duration"])
        passive_duration = int(vals["results"]["passive_duration"])
        rpe = int(vals["results"]["rpe"])
        external_load = int(vals["results"]["external_load"])
        rails = vals["results"]["rails"]
        if rotational_value < 0:
            # if joint is rotated ER, the tissues trained will be IR tissues in a lengethend position
            rotational_bias = "fwd"
            rails_bias = "bkwd"
        else:
            rotational_bias = "bkwd"
            rails_bias = "fwd"
        pails_length_value = 99+abs(rotational_value)
        rails_length_value = 99-abs(rotational_value)
        # collect all the INPUT vals i'll need for processing,
        # then fill this for each type...
        # DATA Needed for each item >>
        # ["<one of 'capsular', 'rotational', 'linear'>", tissue, joint_motion, (pos_a, pos_b), passive_duration, duration, rpe, load]
        bout_array = []
        if drill == "CARs":
            # run appropriate drill_function
            pass
        elif drill == "capsule CAR":
            pass
        elif drill == "IC1":
            print("Running IC 1")
            print(ref_joint_name_string)
            # pprint(mover_dict[ref_joint_name_string]["zones"])

            for zone in mover_dict[ref_joint_name_string]["zones"]:

                # grabbing CAPSULE tissue impacts
                target_tissue = mover_dict[ref_joint_name_string]["zones"][zone]["capsule_adj_id"]

                bout_array.append(
                    ["capsular", target_tissue, "isometric", (100, 100), passive_duration, duration, rpe, 0])

            # grabbing ROTATIONAL tissue impacts

            rot_target_tissues = mover_dict[ref_joint_name_string]["rotational_tissues"][rotational_bias]
            for rot_tissue in rot_target_tissues:
                bout_array.append(["rotational", rot_tissue, "isometric",
                                  (pails_length_value, pails_length_value), passive_duration, duration, rpe, 0])
            if rails is True:
                rails_rot_tissue = mover_dict[ref_joint_name_string]["rotational_tissues"][rails_bias]
                for rot_tissue in list(rails_rot_tissue.values()):
                    bout_array.append(
                        ["rotational", rot_tissue, "isometric", (rails_length_value, rails_length_value), 0, duration/2, rpe, 0])
        # nb// bout_array for IC 1 is built
        # testing...
            # pprint(bout_array)
        elif drill == "IC2":
            print("Running IC 2")
            print(ref_joint_name_string)

            for zone in mover_dict[ref_joint_name_string]["zones"]:

                #print(f"Ref Zone {zone} id: " + f"{mover_dict[ref_joint_name_string]['zones'][zone]['ref_zone_id']}")

                if mover_dict[ref_joint_name_string]['zones'][zone]['ref_zones_id'] == ref_zones_id_a:

                    target_zone_name = zone
                    break
            target_zone = mover_dict[ref_joint_name_string]["zones"][target_zone_name]

            # realize local-to-this-function variables exist:
            # rotational_bias = "bkwd"/"fwd"
            # rails_bias = "fwd"/"bkwd"
            # pails_length_value = 99+abs(rotational_value)
            # rails_length_value = 99-abs(rotational_value)
            target_rotational_tissues = mover_dict[ref_joint_name_string][
                "rotational_tissues"][rotational_bias]
            if rails is True:
                # using imported syn_zone_deque to rotate through the zone_name strings easily by integer (number of rotations)
                zone_index = syn_zone_deque.index(target_zone)
                rails_zone = syn_zone_deque.rotate(4)[zone_index]
                rails_target_zone = mover_dict[ref_joint_name_string]["zones"][rails_zone]
                rails_rot_tissues = mover_dict[ref_joint_name_string][
                    "rotational_tissues"][f"{rails_bias}"]
            # nb// making a decison that 15% or less of rotation (either direction) means only linear tissue is targeted
            if abs(rotational_value) < 15:
                bout_array.append(["linear", target_zone["linear_adj_id"], "isometric",
                                  (start_coord, end_coord), passive_duration, duration, rpe, 0])
                if rails is True:
                    bout_array.append(["linear", rails_target_zone["linear_adj_id"], "isometric", (
                        start_coord, end_coord), passive_duration, duration, rpe, 0])
            elif abs(rotational_value) < 85:
                # trying to distrubute the load proprotionately to the amt of rotation
                linear_portion_factor = (85-abs(rotational_value))/85
                bout_array.append(["linear", target_zone["linear_adj_id"], "isometric", (
                    start_coord, end_coord), passive_duration, duration, round(rpe*linear_portion_factor, 2), 0])
                if rails is True:
                    bout_array.append(["linear", rails_target_zone["linear_adj_id"], "isometric", (
                        start_coord, end_coord), passive_duration, duration, round(rpe*linear_portion_factor, 2), 0])

                rotational_portion_factor = round(
                    (abs(rotational_value))/85, 2)
                for rot_tissue in target_rotational_tissues:
                    bout_array.append(["rotational", rot_tissue, "isometric", (
                        pails_length_value, pails_length_value), passive_duration, duration, round(rpe*rotational_portion_factor, 2), 0])
                if rails is True:
                    for rails_rot_tissue in list(rails_rot_tissues.values()):
                        bout_array.append(
                            ["rotational", rails_rot_tissue, "isometric", (rails_length_value, rails_length_value), 0, duration/2, round(rpe*rotational_portion_factor, 2), 0])
            else:
                for rot_tissue in target_rotational_tissues:
                    bout_array.append(["rotational", rot_tissue, "isometric", (
                        pails_length_value, pails_length_value), passive_duration, duration, rpe, 0])
                if rails is True:
                    for rails_rot_tissue in list(rails_rot_tissues.values()):
                        bout_array.append(
                            ["rotational", rails_rot_tissue, "isometric", (rails_length_value, rails_length_value), 0, duration/2, rpe, 0])
        # nb// bout_array for IC 2 is built
        elif drill == "IC3":
            pass
        elif drill == "PRH":
            pass
        elif drill == "PRLO":
            pass
        # /// START HERE ///
        # ALL items in bout_array will need some vals (inputID, anything else?)
        # before getting written to bout_log table
        print(bout_array)
    return f"Request is recieved!", 201


@bp.route('/workouts/<int:mover_id>')
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
            #print(f"The schema circuit in question: {curr_wkout['schema'][circ]['circuit']}")
            #print(f"More info about the wonky one: ...")
            curr_wkout["schema"][circ]["circuit"].sort(key=lambda inp: inp[0])
            # list-comprehension to only snag the id part of each tuple
            new_circuit = [inp[1]
                           for inp in curr_wkout["schema"][circ]["circuit"]]
            # replace old "circuit" with streamlined array!
            curr_wkout["schema"][circ]["circuit"] = new_circuit
            # pprint(curr_wkout)

    array_to_send = [value for (key, value) in wkouts.items()]

    # pprint(array_to_send)
    return json.dumps(array_to_send), 200

# inputs is not getting used for anything right now


@bp.route('/inputs')
def get_inputs():
    with open('/Users/williamhbelew/Hacking/MSWN/server_side/fakeInputData.json') as w:
        inputs = json.load(w)
        return jsonify(inputs), 200


@bp.route('/drill_ref')
def drill_ref():
    drills_to_send = {
        "CARs": {},
        "capsule CAR": {"zones": []},
        "PRH": {"zones": [], "bias": [], "position": [0], "rotation": []},
        "PRLO": {"zones": [], "bias": [], "position": [0], "rotation": []},
        "IC1": {"zones": [], "bias": [-100, 100], "rails": [], "position": [100], "rotation": [-100, 100], "passive duration": []},
        "IC2": {"zones": [], "bias": [], "rails": [], "position": [100], "rotation": [], "passive duration": []},
        "IC3": {"zones": [], "bias": [], "position": [], "rotation": [], "position B": []}
    }

    return jsonify(drills_to_send), 200


@bp.route('/joint_ref')
def joint_ref():
    #print(f"Got this far (to {index})", file=sys.stderr)
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


@bp.route('/ttstatus/<int:mover_id>')
def ttstatus(mover_id):
    #print(f"Got this far (to {index})", file=sys.stderr)
    db = get_db()
    tissue_status = []
    # BELOW returns a list of sqlite3.Row objects (with index, and keys), but is NOT a real dict
    tissue_status_rows = db.execute(
        'SELECT * FROM tissue_status WHERE moverid = (?)', (mover_id,)
    ).fetchall()
    # this converts all rows returned into dictiornary, that is added to the tissue_status list
    for row in tissue_status_rows:
        tissue_status.append({k: row[k] for k in row.keys()})
    return jsonify({"tissue_status": tissue_status}), 200


@bp.route('/bout_log/<int:mover_id>')
def bout_log(mover_id):
    #print(f"Got this far (to {index})", file=sys.stderr)
    db = get_db()
    bout_log = []
    # BELOW returns a list of sqlite3.Row objects (with index, and keys), but is NOT a real dict
    bout_log_rows = db.execute(
        'SELECT * FROM bout_log WHERE moverid = (?)', (mover_id,)
    ).fetchall()
    # this converts all rows returned into dictiornary, that is added to the tissue_status list
    for row in bout_log_rows:
        bout_log.append({k: row[k] for k in row.keys()})
    # sort on way to react into DESCENDING order from most recent (by ['date'])
    bout_log_final = sorted(bout_log, key=itemgetter('date'), reverse=True)
    return jsonify({"bout_log": bout_log_final}), 200


@bp.route('/add_bout/<int:moverid>', methods=('POST',))
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


def mover_info_dict(db, moverid):
    curs = db.cursor()

    def make_zone_ddict():
        zone_dict_template = {
            "ref_zones_id": 0,
            "anchors": {"proximal": 0, "distal": 0},
            "capsule_adj_id": 0,
            "rotational_adj_id": {"rot_a_adj_id": 0, "rot_b_adj_id": 0},
            "linear_adj_id": 0
        }
        return zone_dict_template

    def make_joint_ddict():
        dict_template = {
            "id": 0,
            "type": "",
            "side": "",
            "zones": defaultdict(make_zone_ddict),
            "rotational_tissues": {"fwd": [], "bkwd": []}
        }
        return dict_template
    mover_joints_dict = defaultdict(make_joint_ddict)
    caps_adj_all = curs.execute('''SELECT
                joints.id,
                joints.joint_type,
                joints.side,
                capsule_adj.rowid,
                capsule_adj.ref_zones_id,
                capsule_adj.anchor_id_a,
                capsule_adj.anchor_id_b,
                ref_zones.zone_name,
                ref_joints.joint_name
                FROM capsule_adj
                LEFT JOIN joints
                ON joints.id = capsule_adj.joint_id
                LEFT JOIN ref_zones
                ON ref_zones.id = capsule_adj.ref_zones_id
                LEFT JOIN ref_joints
                ON joints.ref_joints_id = ref_joints.rowid
                WHERE capsule_adj.moverid = (?)''',
                                (moverid,)).fetchall()
    rot_adj_all = curs.execute('''SELECT
                joints.id,
                rotational_adj.rowid,
                rotational_adj.anchor_id_a,
                rotational_adj.anchor_id_b,
                rotational_adj.rotational_bias,
                ref_zones.zone_name,
                ref_joints.joint_name,
                joints.side
                FROM rotational_adj
                LEFT JOIN joints
                ON joints.id = rotational_adj.joint_id
                LEFT JOIN anchor
                ON anchor.id = rotational_adj.anchor_id_a
                LEFT JOIN ref_zones
                ON ref_zones.id = anchor.ref_zones_id
                LEFT JOIN ref_joints
                ON joints.ref_joints_id = ref_joints.rowid
                WHERE rotational_adj.moverid = (?)''',
                               (moverid,)).fetchall()
    lin_adj_all = curs.execute('''SELECT
                joints.id,
                joints.side,
                linear_adj.rowid,
                linear_adj.ref_zones_id,
                linear_adj.anchor_id_a,
                linear_adj.anchor_id_b,
                ref_zones.zone_name,
                ref_joints.joint_name
                FROM linear_adj
                LEFT JOIN joints
                ON joints.id = linear_adj.joint_id
                LEFT JOIN ref_zones
                ON ref_zones.id = linear_adj.ref_zones_id
                LEFT JOIN ref_joints
                ON joints.ref_joints_id = ref_joints.rowid
                WHERE linear_adj.moverid = (?)''',
                               (moverid,)).fetchall()
    for cadj in caps_adj_all:
        joints_id, joint_type, side, capsule_adj_id, ref_zones_id, anchor_id_a, anchor_id_b, zone_name, joint_name = cadj
        if side != 'mid':
            joint_name = side + " " + joint_name
        mover_joints_dict[joint_name]["id"] = joints_id
        mover_joints_dict[joint_name]["type"] = joint_type
        mover_joints_dict[joint_name]["side"] = side
        mover_joints_dict[joint_name]["zones"][zone_name]["ref_zones_id"] = ref_zones_id
        mover_joints_dict[joint_name]["zones"][zone_name]["anchors"]["proximal"] = anchor_id_a
        mover_joints_dict[joint_name]["zones"][zone_name]["anchors"]["distal"] = anchor_id_b
        mover_joints_dict[joint_name]["zones"][zone_name]["capsule_adj_id"] = capsule_adj_id
    for radj in rot_adj_all:
        joints_id, rotational_adj_id, anchor_id_a, anchor_id_b, rotational_bias, zone_name, joint_name, side = radj
        if side != 'mid':
            joint_name = side + " " + joint_name
        if rotational_bias not in ["IR", "Lf", "Oh"]:
            mover_joints_dict[joint_name]["zones"][zone_name]["rotational_adj_id"]["rot_a_adj_id"] = rotational_adj_id
            mover_joints_dict[joint_name]["rotational_tissues"]["fwd"].append(
                rotational_adj_id)
        else:
            mover_joints_dict[joint_name]["zones"][zone_name]["rotational_adj_id"]["rot_b_adj_id"] = rotational_adj_id
            mover_joints_dict[joint_name]["rotational_tissues"]["bkwd"].append(
                rotational_adj_id)

    for ladj in lin_adj_all:
        joints_id, side, linear_adj_id, ref_zones_id, anchor_id_a, anchor_id_b, zone_name, joint_name = ladj
        if side != 'mid':
            joint_name = side + " " + joint_name

        mover_joints_dict[joint_name]["zones"][zone_name]["linear_adj_id"] = linear_adj_id

    return mover_joints_dict


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
