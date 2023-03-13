from pprint import pprint
import sys

from server_side.mover_info_dict import mover_info_dict

from server_side.db_ref_vals import syn_zone_deque
from server_side.db_ref_vals import ses_zone_deque
from server_side.db_ref_vals import spine_zone_deque


def unpack_workout(req):

    moverid = req.pop("mover_id")
    workout_id = str(req.pop("workout_id"))
    date_done = req.pop("date_done")

    return (moverid, workout_id, date_done)


def unpack_inputs(inputs, mover_dict, date_done, moverid):
    bout_array = []

    for inputID, vals in inputs:

        # these Rx values are based on the prescription of the drill
        drill = vals["Rx"]["drill_name"]
        # I think this exists in the data!!! it should be the actual programmed_drills_id,
        # not just the ordered list made up from the browser
        inp_id = vals["Rx"]["id"]

        # should I even consider this input or not!?!?!?
        if int(vals['results']['duration']) == 0 or int(vals['results']['rpe']) == 0:
            print("not writing bouts bc DURATION and/or RPE is null...")
            continue

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
        passive_duration = vals["results"]["passive_duration"]
        passive_duration = 0 if passive_duration == '' else int(
            passive_duration)
        rpe = int(vals["results"]["rpe"])
        external_load = vals["results"]["external_load"]
        external_load = 0 if external_load == '' else int(external_load)
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

        def bout_dict_maker(tissue_type, tissue_id, joint_motion, tissue_start, tissue_end, passive_duration, duration, rpe, external_load):
            bout_hash = {}
            # input-specific vals
            bout_hash["date"] = date_done
            bout_hash["moverid"] = moverid
            bout_hash["joint_id"] = joint_id
            bout_hash["programmed_drills_id"] = inp_id
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
            rotate_int = 1

            rotational_position_value = 199
            # Each direction: Zonal ER and Linear isometric bout, then use a rotational (all fwd OR bkwd tissues) concentric bout to get from one zone to next
            if mover_dict[ref_joint_name_string]['type'] == 'spinal':
                deque_to_use = spine_zone_deque
                working_index = spine_zone_deque.index('flex')
            elif mover_dict[ref_joint_name_string]['type'] == 'sesamoid':
                deque_to_use = ses_zone_deque
                working_index = ses_zone_deque.index('protract')
            else:
                deque_to_use = syn_zone_deque
                working_index = syn_zone_deque.index('add')
            rotations_until_switch_direction = len(deque_to_use)
            rotation_counter = 0
            while time_remaining_in_input >= 20:
                if moving_direction == "fwd":
                    # "fwd" for spine is Rightward
                    sinch_adj = "rot_b_adj_id"
                else:
                    sinch_adj = "rot_a_adj_id"
                rotational_tissues = mover_dict[ref_joint_name_string]["rotational_tissues"][moving_direction]
                for _ in range(len(deque_to_use)):
                    rotational_value = rotational_position_value - 100
                    # ^^^this will be written to the db
                    # as each bout_dict is make'd,
                    # essentially naming the rotated
                    # position at each zone of the CAR (cool!)
                    target_zone = mover_dict[ref_joint_name_string]["zones"][deque_to_use[working_index]]
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
                    deque_to_use.rotate(rotate_int)
                    rotational_position_value -= 25

                    # reset the length value now that we'll be rotating the OTHER direction
                rotational_position_value = 199

                if rotation_counter == rotations_until_switch_direction and moving_direction == "fwd":
                    moving_direction = "bkwd"
                    rotation_counter = 0
                    rotate_int = -1
                elif rotation_counter == rotations_until_switch_direction and moving_direction == "bkwd":
                    moving_direction = "fwd"
                    rotation_counter = 0
                    rotate_int = 1
                else:
                    rotation_counter += 1 * rotate_int
                time_remaining_in_input -= 20

        # nb// bouts for CARs is added to bout_array!
        elif drill == "capsule CAR":
            print("Running Capsule CAR...")
            print(ref_joint_name_string)

            # doesn't really make SENSE that a
            # rotating exercise would have a SINGLE rotational value
            rotational_value = None

            rot_IR_tissues = mover_dict[ref_joint_name_string]["rotational_tissues"]["fwd"]
            rot_ER_tissues = mover_dict[ref_joint_name_string]["rotational_tissues"]["bkwd"]

            time_remaining_in_input = duration
            # ASSUME span is the entire range of the joint rotation (100% in each direction)
            # and saying that 20deg of rotation takes 1sec
            sec_per_length = 199 // 20
            pointer = 100
            while time_remaining_in_input > 0:
                joint_motion_c = "concentric"
                joint_motion_e = "eccentric"
                if pointer == 100:
                    terminate = -100
                    for tissue in rot_IR_tissues:
                        bout = bout_dict_maker(
                            "rotational", tissue, joint_motion_c, 199, 1, 0, sec_per_length, rpe, external_load)
                        bout_array.append(bout)
                    for tissue in rot_ER_tissues:
                        bout = bout_dict_maker(
                            "rotational", tissue, joint_motion_e, 1, 199, 0, sec_per_length, rpe, external_load)
                        bout_array.append(bout)
                else:
                    terminate = 100
                    for tissue in rot_ER_tissues:
                        bout = bout_dict_maker(
                            "rotational", tissue, joint_motion_c, 199, 1, 0, sec_per_length, rpe, external_load)
                        bout_array.append(bout)
                    for tissue in rot_IR_tissues:
                        bout = bout_dict_maker(
                            "rotational", tissue, joint_motion_e, 1, 199, 0, sec_per_length, rpe, external_load)
                        bout_array.append(bout)

                pointer = terminate
                time_remaining_in_input -= sec_per_length

            # ASSUME we only care about linear tissue impact
            # if the zone position is stated to be LESS than 30deg
            if start_coord < 30:
                for zone in mover_dict[ref_joint_name_string]["zones"]:
                    # print(f"Ref Zone {zone} id: " + f"{mover_dict[ref_joint_name_string]['zones'][zone]['ref_zone_id']}")
                    if mover_dict[ref_joint_name_string]['zones'][zone]['ref_zones_id'] == ref_zones_id_a:
                        target_zone_name = zone
                        break
                target_zone = mover_dict[ref_joint_name_string]["zones"][target_zone_name]
                bout = bout_dict_maker(
                    "linear", target_zone["linear_adj_id"], "isometric", start_coord, start_coord, 0, duration, rpe, external_load)
                bout_array.append(bout)
        # nb// bouts for Capsule CAR is added to bout_array
        elif drill == "IC1":
            print("Running IC 1")
            print(ref_joint_name_string)
            # pprint(mover_dict[ref_joint_name_string]["zones"])

            for zone in mover_dict[ref_joint_name_string]["zones"]:

                # grabbing CAPSULE tissue impacts
                target_tissue = mover_dict[ref_joint_name_string]["zones"][zone]["capsule_adj_id"]
                capsule_bout = bout_dict_maker(
                    "capsular", target_tissue, "isometric", 100, 100, passive_duration, duration, rpe, external_load)
                bout_array.append(capsule_bout)
            # grabbing ROTATIONAL tissue impacts

            rot_target_tissues = mover_dict[ref_joint_name_string]["rotational_tissues"][rotational_bias]
            for rot_tissue in rot_target_tissues:
                rot_bout = bout_dict_maker("rotational", rot_tissue, "isometric",
                                           pails_length_value, pails_length_value, passive_duration, duration, rpe, 0)
                bout_array.append(rot_bout)

            if rails is True:
                rails_rot_tissue = mover_dict[ref_joint_name_string]["rotational_tissues"][rails_bias]
                for rot_tissue in rails_rot_tissue:
                    rot_bout = bout_dict_maker(
                        "rotational", rot_tissue, "isometric", rails_length_value, rails_length_value, 0, duration/2, rpe, 0)
                    bout_array.append(rot_bout)
        # nb// bouts for IC 1 is added to bout_array
        # testing...
            # pprint(bout_array)
        elif drill == "IC2":
            print("Running IC 2")
            print(ref_joint_name_string)

            for zone in mover_dict[ref_joint_name_string]["zones"]:

                # print(f"Ref Zone {zone} id: " + f"{mover_dict[ref_joint_name_string]['zones'][zone]['ref_zone_id']}")

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
            # can set this automatically bc IC2 indicates LENGTH of user-selected tissue
            linear_pails_coord = start_coord
            if rails is True:
                # using imported syn_zone_deque to rotate through the zone_name strings easily by integer (number of rotations)
                #print(f"Syn Deque == {syn_zone_deque}")
                #print(f"Target ZONE NAME == {target_zone_name}")
                zone_index = syn_zone_deque.index(target_zone_name)
                #print(f"Target ZONE INDEX == {zone_index}")
                syn_zone_deque.rotate(4)
                rails_zone = syn_zone_deque[zone_index]
                #print(f"RAILs ZONE NAME == {rails_zone}")
                rails_target_zone = mover_dict[ref_joint_name_string]["zones"][rails_zone]
                linear_rails_coord = abs(99-linear_pails_coord)
                rails_rot_tissues = mover_dict[ref_joint_name_string][
                    "rotational_tissues"][f"{rails_bias}"]
            # nb// making a decison that 15% or less of rotation (either direction) means only linear tissue is targeted

            if abs(rotational_value) < 15:
                p_bout = bout_dict_maker("linear", target_zone["linear_adj_id"], "isometric",
                                         linear_pails_coord, linear_pails_coord, passive_duration, duration, rpe, 0)
                bout_array.append(p_bout)
                if rails is True:
                    r_bout = bout_dict_maker(
                        "linear", rails_target_zone["linear_adj_id"], "isometric", linear_rails_coord, linear_rails_coord, passive_duration, duration, rpe, 0)

                    bout_array.append(r_bout)
            elif abs(rotational_value) < 85:
                # trying to distrubute the load proprotionately to the amt of rotation
                linear_portion_factor = (85-abs(rotational_value))/85
                lp_p_bout = bout_dict_maker("linear", target_zone["linear_adj_id"], "isometric",
                                            linear_pails_coord, linear_pails_coord, passive_duration, duration, round(rpe*linear_portion_factor, 2), 0)
                bout_array.append(lp_p_bout)
                if rails is True:
                    lp_r_bout = bout_dict_maker("linear", rails_target_zone["linear_adj_id"], "isometric",
                                                linear_rails_coord, linear_rails_coord, passive_duration, duration, round(rpe*linear_portion_factor, 2), 0)
                    bout_array.append(lp_r_bout)

                rotational_portion_factor = round(
                    (abs(rotational_value))/85, 2)
                for rot_tissue in target_rotational_tissues:
                    rp_p_bout = bout_dict_maker("rotational", rot_tissue, "isometric",
                                                pails_length_value, pails_length_value, passive_duration, duration, round(rpe*rotational_portion_factor, 2), 0)
                    bout_array.append(rp_p_bout)
                if rails is True:
                    for rails_rot_tissue in rails_rot_tissues:
                        rp_r_bout = bout_dict_maker("rotational", rails_rot_tissue, "isometric", rails_length_value,
                                                    rails_length_value, 0, duration/2, round(rpe*rotational_portion_factor, 2), 0)
                        bout_array.append(rp_r_bout)
            else:
                for rot_tissue in target_rotational_tissues:
                    p_bout = bout_dict_maker("rotational", rot_tissue, "isometric",
                                             pails_length_value, pails_length_value, passive_duration, duration, rpe, 0)
                    bout_array.append(p_bout)
                if rails is True:
                    for rails_rot_tissue in rails_rot_tissues:
                        r_bout = bout_dict_maker("rotational", rails_rot_tissue, "isometric",
                                                 rails_length_value, rails_length_value, 0, duration/2, rpe, 0)
                        bout_array.append(r_bout)
        # nb// bouts for IC 2 is added to bout_array
        elif drill == "IC3":
            print("Running IC 3")
            print(ref_joint_name_string)

            # COPY of IC1 & 2
            for zone in mover_dict[ref_joint_name_string]["zones"]:

                # print(f"Ref Zone {zone} id: " + f"{mover_dict[ref_joint_name_string]['zones'][zone]['ref_zone_id']}")

                if mover_dict[ref_joint_name_string]['zones'][zone]['ref_zones_id'] == ref_zones_id_a:

                    target_zone_name = zone
                    break
            target_zone = mover_dict[ref_joint_name_string]["zones"][target_zone_name]

            # HACK to the right rotational tissue LENGTH values, with given rotational value
            rotational_tissue_position = abs(rotational_value) + 99

            # realize local-to-this-function variables exist:
            # rotational_bias = "bkwd"/"fwd"
            # rails_bias = "fwd"/"bkwd"
            # pails_length_value = 99+abs(rotational_value)
            # rails_length_value = 99-abs(rotational_value)

            if end_coord > start_coord:
                joint_motion = "eccentric"
                delta = end_coord - start_coord
                end_rotational_position_value = rotational_tissue_position + delta
                if end_rotational_position_value > 200:
                    # TODO how to FLAG stretching into NEW range (eccentric loading of rotational tissues?!)
                    end_rotational_position_value = 200

            else:
                joint_motion = "isometric"
                end_rotational_position_value = rotational_tissue_position

            if abs(rotational_value) < 15:
                bout = bout_dict_maker(
                    "linear", target_zone["linear_adj_id"], joint_motion, start_coord, end_coord, 0, duration, rpe, external_load)
                bout_array.append(bout)

            elif abs(rotational_value) < 85:
                linear_portion_factor = round(
                    ((85 - abs(rotational_value))/85), 2)
                lin_bout = bout_dict_maker("linear", target_zone["linear_adj_id"], joint_motion,
                                           start_coord, end_coord, 0, duration, round(linear_portion_factor*rpe, 2), external_load)
                bout_array.append(lin_bout)

                rotational_portion_factor = round(
                    ((abs(rotational_value))/85), 2)
                rot_bout = bout_dict_maker("rotational", target_zone["rotational_adj_id"][rot_adj], joint_motion,
                                           rotational_tissue_position, end_rotational_position_value, 0, duration, round(rotational_portion_factor*rpe, 2), external_load)
                bout_array.append(rot_bout)

            else:
                rot_bout = bout_dict_maker("rotational", target_zone["rotational_adj_id"][rot_adj], joint_motion,
                                           rotational_tissue_position, end_rotational_position_value, 0, duration, rpe, external_load)
                bout_array.append(rot_bout)
        # nb// bouts for IC 3 is added to bout_array
        elif drill == "PRH":
            print("Running PRH")
            print(ref_joint_name_string)

            # COPY of IC1 & 2
            for zone in mover_dict[ref_joint_name_string]["zones"]:

                # print(f"Ref Zone {zone} id: " + f"{mover_dict[ref_joint_name_string]['zones'][zone]['ref_zone_id']}")

                if mover_dict[ref_joint_name_string]['zones'][zone]['ref_zones_id'] == ref_zones_id_a:
                    # !!! target zone in this case is SHORT, so no need to hunt for RAILs tissue
                    target_zone_name = zone
                    target_zone = mover_dict[ref_joint_name_string]["zones"][target_zone_name]
                    break

            # ASSUME the positional value for this isometric ("short")
            start_coord = 5
            end_coord = 5

            # realize local-to-this-function variables exist:
            # rotational_bias = "bkwd"/"fwd"
            # rails_bias = "fwd"/"bkwd"
            # pails_length_value = 99+abs(rotational_value)
            # rails_length_value = 99-abs(rotational_value)

            if abs(rotational_value) < 15:
                bout = bout_dict_maker(
                    "linear", target_zone["linear_adj_id"], "isometric", start_coord, end_coord, 0, duration, rpe, external_load)
                bout_array.append(bout)

            elif abs(rotational_value) < 85:
                linear_portion_factor = round(
                    ((85 - abs(rotational_value))/85), 2)
                lin_bout = bout_dict_maker("linear", target_zone["linear_adj_id"], "isometric",
                                           start_coord, end_coord, 0, duration, round(linear_portion_factor*rpe, 2), external_load)
                bout_array.append(lin_bout)

                rotational_portion_factor = round(
                    ((abs(rotational_value))/85), 2)
                rot_bout = bout_dict_maker("rotational", target_zone["rotational_adj_id"][rails_adj], "isometric",
                                           start_coord, end_coord, 0, duration, round(rotational_portion_factor*rpe, 2), external_load)
                bout_array.append(rot_bout)

            else:
                rot_bout = bout_dict_maker("rotational", target_zone["rotational_adj_id"][rails_adj], "isometric",
                                           start_coord, end_coord, 0, duration, rpe, external_load)
                bout_array.append(rot_bout)
        # nb// bouts for PRH is added to bout_array
        elif drill == "Muscular Scan":
            print("Running Muscular Scan")
            print(ref_joint_name_string)

            # COPY of IC1 & 2
            for zone in mover_dict[ref_joint_name_string]["zones"]:

                # print(f"Ref Zone {zone} id: " + f"{mover_dict[ref_joint_name_string]['zones'][zone]['ref_zone_id']}")

                if mover_dict[ref_joint_name_string]['zones'][zone]['ref_zones_id'] == ref_zones_id_a:
                    # !!! target zone in this case is moving long<->short;
                    # no need to hunt for RAILs tissue (ala Kinetic Stretch)
                    target_zone_name = zone
                    target_zone = mover_dict[ref_joint_name_string]["zones"][target_zone_name]
                    break

            # realize local-to-this-function variables exist:
            # rotational_bias = "bkwd"/"fwd"
            # rails_bias = "fwd"/"bkwd"
            # pails_length_value = 99+abs(rotational_value)
            # rails_length_value = 99-abs(rotational_value)

            # HACK to the right rotational tissue LENGTH values, with given rotational value
            span = end_coord - start_coord
            rotational_tissue_position = abs(rotational_value) + 99
            end_rotational_position_value = rotational_tissue_position + span
            if end_rotational_position_value > 200:
                # TODO how to FLAG stretching into NEW range (eccentric loading of rotational tissues?!)
                end_rotational_position_value = 200

            time_remaining_in_input = duration
            sec_per_length = span // 10
            pointer = end_coord
            while time_remaining_in_input > 0:
                if pointer == end_coord:
                    joint_motion = "concentric"
                    terminate = start_coord
                    rot_end = rotational_tissue_position
                    rot_start = end_rotational_position_value
                else:
                    joint_motion = "eccentric"
                    terminate = end_coord
                    rot_start = rotational_tissue_position
                    rot_end = end_rotational_position_value
                if abs(rotational_value) < 15:
                    # linear only bout
                    bout = bout_dict_maker(
                        "linear", target_zone["linear_adj_id"], joint_motion, pointer, terminate, 0, sec_per_length, rpe, external_load)
                    bout_array.append(bout)
                elif abs(rotational_value) < 85:
                    # share proportionally
                    linear_portion_factor = round(
                        ((85 - abs(rotational_value))/85), 2)
                    lin_bout = bout_dict_maker("linear", target_zone["linear_adj_id"], joint_motion,
                                               pointer, terminate, 0, sec_per_length, round(linear_portion_factor*rpe, 2), external_load)
                    bout_array.append(lin_bout)

                    rotational_portion_factor = round(
                        ((abs(rotational_value))/85), 2)
                    rot_bout = bout_dict_maker("rotational", target_zone["rotational_adj_id"][rot_adj], joint_motion,
                                               rot_start, rot_end, 0, sec_per_length, round(rotational_portion_factor*rpe, 2), external_load)
                    # ^^^^ rot_adj variable works ok here
                    # to define WHICH tissue, bc it describes
                    # the working side of the joint
                    # (the side of the joint that is OPENED
                    # when joint is oriented at given rotational_value)
                    bout_array.append(rot_bout)

                else:
                    rotational_portion_factor = round(
                        ((abs(rotational_value))/85), 2)
                    rot_bout = bout_dict_maker("rotational", target_zone["rotational_adj_id"][rot_adj], joint_motion,
                                               rot_start, rot_end, 0, sec_per_length, rpe, external_load)

                    bout_array.append(rot_bout)

                pointer = terminate
                time_remaining_in_input -= sec_per_length
        # nb// bouts for Muscular Scan is added to bout_array
    for b in bout_array:
        if b["tissue_type"] == "capsular":
            b["capsular_tissue_id"] = b.pop("tissue_id")
            b["rotational_tissue_id"] = ""
            b["linear_tissue_id"] = ""
        elif b["tissue_type"] == "rotational":
            b["capsular_tissue_id"] = ""
            b["rotational_tissue_id"] = b.pop("tissue_id")
            b["linear_tissue_id"] = ""
        elif b["tissue_type"] == "linear":
            b["capsular_tissue_id"] = ""
            b["rotational_tissue_id"] = ""
            b["linear_tissue_id"] = b.pop("tissue_id")

    return bout_array


def prep_bouts_for_insertion(bout_array):
    bout_array_q_marks = ",".join(
        "?" for _ in range(len(bout_array[0].values())))

    bout_array_fields = ", ".join(bout_array[0].keys())

    bout_sql_statement = f"INSERT INTO bout_log ({bout_array_fields}) VALUES ({bout_array_q_marks})"

    bout_array_values = [list(b.values()) for b in bout_array]

    return bout_sql_statement, bout_array_values


def workout_recorder(db, req):

    # print(f"record_bout request: ", file=sys.stderr)

    moverid, workout_id, date_done = unpack_workout(req)

    mover_dict = mover_info_dict(db, moverid)

    inputs = req.items()

    bout_array = unpack_inputs(inputs, mover_dict, date_done, moverid)

    bout_sql_statement, bout_array_values = prep_bouts_for_insertion(
        bout_array)
    # print(bout_array_values)
    curs = db.cursor()
    curs.executemany(bout_sql_statement, bout_array_values)
    db.commit()


def multiple_workout_recorder(db, workout_array):
    '''This is intended to spare DB calls by running through
    an array of workouts to build one LARGE array of all consistuent 
    bouts'''

    sim_bout_array = []

    # doing this one time JUST to get the mover_dict with a single db call
    # (and not during each loop of the iterator below)
    moverid = workout_array[0].get('mover_id')
    mover_dict = mover_info_dict(db, moverid)

    for w in workout_array:
        moverid, workout_id, date_done = unpack_workout(w)
        inputs = w.items()
        this_bout_array = unpack_inputs(
            inputs, mover_dict, date_done, moverid)
        sim_bout_array.extend(this_bout_array)

    # pprint(sim_bout_array[0])

    all_bouts_sql_statement, all_bouts_array_values = prep_bouts_for_insertion(
        sim_bout_array)

    # for item in all_bouts_array_values[:1]:
    # print(all_bouts_sql_statement)
    # print(item)

    curs = db.cursor()
    curs.executemany(all_bouts_sql_statement, all_bouts_array_values)
    db.commit()
