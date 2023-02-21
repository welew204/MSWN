import pprint

from server_side.crud_bp import mover_info_dict

# make a new workout
# in THIS FORMAT:

# then record this workout as bouts


'''    {'comments': '',
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


def record_sim_CARs(db, moverid, date_done):

    workout_id = str(req.pop("workout_id"))

    mover_dict = mover_info_dict(db, moverid)
    # pprint(mover_dict)
    bout_array = []
    for inputID, vals in req.items():

        # these Rx values are based on the prescription of the drill
        drill = vals["Rx"]["drill_name"]
        if vals["Rx"]["rotational_value"] != "":
            rotational_value = int(vals["Rx"]["rotational_value"])
        else:
            rotational_value = 0

        # these conditionals unpack the 'coord' array if input is IC3 or Muscular Scan,
        # else, just stashes the start_ and end_ coord as ints
        if "coords" in vals:
            s_coord, e_coord = vals.pop("coords")
            start_coord = int(s_coord)
            end_coord = int(e_coord)
        else:
            start_coord = vals["Rx"]["start_coord"]
            if start_coord == '':
                start_coord = 0
            else:
                start_coord = int(start_coord)

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
        ref_zones_id_a = vals["Rx"]["ref_zones_id_a"]
        ref_zones_id_b = vals["Rx"]["ref_zones_id_b"]
        if side == "mid":
            ref_joint_name_string = str(ref_joint_name)
        else:
            ref_joint_name_string = str(side + " " + ref_joint_name)
        joint_id = mover_dict[ref_joint_name_string]["id"]

        # these 'results' values are based on the execution of the drill
        duration = int(vals["results"]["duration"])
        passive_duration = int(vals["results"]["passive_duration"])
        rpe = int(vals["results"]["rpe"])
        external_load = int(vals["results"]["external_load"])
        rails = vals["results"]["rails"]
        if rails == "True":
            rails = True
        else:
            rails = False

        if rotational_value < 0:
            # if joint is rotated IR, the tissues trained will be ER tissues in a lengethend position,
            # and therefore the 'trained' portion
            rotational_bias = "bkwd"
            rot_adj = "rot_b_adj_id"
            rails_adj = "rot_a_adj_id"
            rails_bias = "fwd"
        else:
            rotational_bias = "fwd"
            rot_adj = "rot_a_adj_id"
            rails_adj = "rot_b_adj_id"
            rails_bias = "bkwd"
        pails_length_value = 99+abs(rotational_value)
        rails_length_value = 99-abs(rotational_value)
        # collect all the INPUT vals i'll need for processing,
        # then fill this for each type...
        # DATA Needed for each item >>
        # ["<one of 'capsular', 'rotational', 'linear'>", tissue, joint_motion, (pos_a, pos_b), passive_duration, duration, rpe, load]

        def bout_dict_maker(tissue_type, tissue_id, joint_motion, tissue_start, tissue_end, passive_duration, duration, rpe, external_load):
            bout_hash = {}
            # input-specific vals
            bout_hash["date"] = date_done
            bout_hash["moverid"] = moverid
            bout_hash["joint_id"] = joint_id
            bout_hash["programmed_drills_id"] = inputID
            bout_hash["rotational_value"] = rotational_value
            # handed in vals
            bout_hash["tissue_type"] = tissue_type
            bout_hash["tissue_id"] = tissue_id
            bout_hash["joint_motion"] = joint_motion
            bout_hash["start_coord"] = tissue_start
            bout_hash["end_coord"] = tissue_end
            bout_hash["passive_duration"] = passive_duration
            bout_hash["duration"] = duration
            bout_hash["rpe"] = rpe
            bout_hash["external_load"] = external_load
            return bout_hash

        if drill == "CARs":
            # run appropriate drill_function
            print("Running CARs...")
            print(ref_joint_name_string)

            time_remaining_in_input = duration
            moving_direction = "fwd"

            rotational_position_value = 199
            # Each direction: Zonal ER and Linear isometric bout, then use a rotational (all fwd OR bkwd tissues) concentric bout to get from one zone to next
            working_index = syn_zone_deque.index("add")
            while time_remaining_in_input >= 20:
                if moving_direction == "fwd":
                    sinch_adj = "rot_b_adj_id"
                else:
                    sinch_adj = "rot_a_adj_id"
                rotational_tissues = mover_dict[ref_joint_name_string]["rotational_tissues"][moving_direction]
                for _ in range(len(syn_zone_deque)):
                    rotational_value = rotational_position_value - 100
                    # ^^^this will be written to the db
                    # as each bout_dict is make'd,
                    # essentially naming the rotated
                    # position at each zone of the CAR (cool!)
                    target_zone = mover_dict[ref_joint_name_string]["zones"][syn_zone_deque[working_index]]
                    # ASSUME the length of the shortened tissue is 5
                    lin_iso_bout = bout_dict_maker(
                        "linear", target_zone['linear_adj_id'], "isometric", 5, 5, 0, 1, rpe, external_load)
                    rot_iso_bout = bout_dict_maker(
                        "rotational", target_zone['rotational_adj_id'][sinch_adj], "isometric", 5, 5, 0, 1, rpe, external_load)
                    bout_array.append(lin_iso_bout)
                    bout_array.append(rot_iso_bout)
                    for tissue in rotational_tissues:
                        # HACK to get correct end-rotational value (using abs(199-200) to get 1 ...)
                        rot_conc_bout = bout_dict_maker(
                            "rotational", tissue, "concentric", rotational_position_value, abs(rotational_position_value-25), 0, 1, rpe, external_load)
                        bout_array.append(rot_conc_bout)
                    syn_zone_deque.rotate(1)
                    rotational_position_value -= 25

                # reset the length value now that we'll be rotating the OTHER direction
                rotational_position_value = 199

                if moving_direction == "fwd":
                    moving_direction = "bkwd"
                else:
                    moving_direction = "fwd"
                time_remaining_in_input -= 20

        bout_array_q_marks = ",".join(
            "?" for _ in range(len(bout_array[0].values())))

    bout_array_fields = ", ".join(bout_array[0].keys())

    bout_sql_statement = f"INSERT INTO bout_log ({bout_array_fields}) VALUES ({bout_array_q_marks})"

    bout_array_values = [list(b.values()) for b in bout_array]
    # print(bout_array_values)
    curs = db.cursor()
    curs.executemany(bout_sql_statement, bout_array_values)
    db.commit()

    curs.execute(
        '''UPDATE workouts 
            SET last_done = (?) 
            WHERE id = (?) 
            AND moverid = (?)''',
        (date_done, workout_id, moverid))
    db.commit()

    return f"Workout/results recorded!", 201
