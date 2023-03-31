from pprint import pprint
import sys

from server_side.mover_info_dict import mover_info_dict


def workout_writer(db, req):
    cursor = db.cursor()

    # pprint(req)

    workout_to_add = {}

    for key, val in req.items():
        if key == "id" or key == "inputs":
            continue
        if key == "schema":
            continue
        else:
            workout_to_add[key] = val
    workout_q_marks = ",".join("?" for _ in range(len(workout_to_add.keys())))
    workout_fields = ", ".join(list(workout_to_add.keys()))

    workout_sql_statement = f'INSERT INTO workouts ({workout_fields}) VALUES ({workout_q_marks})'
    # print(f"WORKOUT qmarks: {workout_q_marks}", file=sys.stderr)
    cursor.execute(workout_sql_statement,
                   tuple(workout_to_add.values()))
    db.commit()
    wkt_id = cursor.lastrowid
    schema_lookups = {}
    for j, info in enumerate(req["schema"]):
        for i, inputID in enumerate(info["circuit"]):
            input_sequence = f"{j}-{str(i+1)}"
            # example of input_sequence: 0-1, 1-1, etc (aka SET - inputIndex)
            # it IS ZERO-INDEXED!
            schema_lookups[int(inputID)] = (
                input_sequence, str(info["iterations"]))
    # pprint(schema_lookups)

    # print(f"workout schema transcribed (schema_lookups): {schema_lookups}", file=sys.stderr)
    # pprint(workout_to_add)
    workout_title = workout_to_add["workout_title"]
    comments = workout_to_add["comments"]
    moverid = workout_to_add["moverid"]
    date_init = workout_to_add["date_init"]
    mover_dict = mover_info_dict(db, moverid)
    # pprint(mover_dict)
    for inputID, payload in req["inputs"].items():
        if "completed" not in payload:
            continue
        elif payload["multijoint"] == True:
            print(f"Working on MJ input ID: {inputID}")
            mj_drill_unpack(payload)
        else:
            print(f"Working on SJ input ID: {inputID}")
            # pprint(payload)
            sj_drill_unpack(payload, mover_dict)

        input_seq, circuit_iterations = schema_lookups[int(inputID)]
        payload["input_sequence"] = input_seq
        payload["circuit_iterations"] = circuit_iterations

        payload["date"] = date_init
        payload["moverid"] = moverid
        payload["workout_id"] = wkt_id

        input_fields = list(payload.keys())

        input_vals = list(payload.values())
        # pprint(payload)

        write_sql(db, input_fields, input_vals)

    print(f"Added workout (ID): {wkt_id}", file=sys.stderr)

    return wkt_id


def sj_drill_unpack(payload, mover_dict):
    payload.pop("completed")
    payload.pop("ref_joint_id")
    payload.pop("id")
    if payload["ref_joint_side"] != 'mid':
        joint_key_string = payload["ref_joint_side"] + \
            " " + payload["ref_joint_name"]
    else:
        joint_key_string = payload["ref_joint_name"]

    if "coords" in payload:
        s_coord, e_coord = payload.pop("coords")
        payload["start_coord"] = s_coord
        payload["end_coord"] = e_coord

    payload.pop("ref_joint_name")
    payload.pop("ref_joint_side")

    if "ref_zone_name" in payload:
        fixed_side_anchor = mover_dict[joint_key_string]["zones"][payload["ref_zone_name"]
                                                                  ]["anchors"]["proximal"]
        # print(f"ANCHOR ID for mover: {fixed_side_anchor}", file=sys.stderr)
        payload["fixed_side_anchor_id"] = fixed_side_anchor
        payload.pop("ref_zone_name")

    joint_id = mover_dict[joint_key_string]["id"]
    payload["joint_id"] = joint_id
    payload["multijoint"] = 0
    reps_array = payload["reps_array"]
    reps_array_string = ",".join([str(i) for i in reps_array])
    payload["reps_array"] = reps_array_string


def mj_drill_unpack(payload):
    #print("MJ drill unpacking...(payload)...")
    # pprint(payload)
    payload.pop("completed")
    payload["multijoint"] = 1
    payload.pop("id")
    # SIDE will be used to pass to the actual drill unpack'r when/if needed
    side = payload.pop("side")
    # handling reps_array...
    reps_array = payload["reps_array"]
    # print(reps_array)
    reps_array_string = ",".join([str(i) for i in reps_array])
    #print(f"here's the reps_array in string: {reps_array_string}")
    payload["reps_array"] = reps_array_string


def write_sql(db, input_fields, input_vals):
    curs = db.cursor()
    #pprint({input_fields[i]: input_vals[i] for i in range(len(input_fields))})

    input_q_marks = ",".join("?" for _ in range(len(input_fields)))
    # print(f"INPUT qmarks: {input_q_marks}", file=sys.stderr)
    sql_statement = f"INSERT INTO programmed_drills {tuple(input_fields)} VALUES ({input_q_marks})"
    # NEED to get the programmed_drills.id from each INSERT,
    # so that when the workout object goes to browser the new workout has the RIGHT
    # drills.id for each 'input'

    curs.execute(sql_statement, tuple(input_vals))
    db.commit()
