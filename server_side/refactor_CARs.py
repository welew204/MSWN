import pprint


from server_side.db_ref_vals import syn_zone_deque
from server_side.db_ref_vals import ses_zone_deque
from server_side.db_ref_vals import spine_zone_deque

''' this module was an attempt/start at refactoring, not completed;
known issues: BOUT DICT MAKER here is NOT correct'''


def ifCARs(mover_dict, ref_joint_name_string, duration, rpe, external_load, bout_dict_maker):
    print("Running CARs...")
    print(ref_joint_name_string)

    bout_array = []

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

    return bout_array
