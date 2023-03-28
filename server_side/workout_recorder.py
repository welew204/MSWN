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


def bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, tissue_type, tissue_id, joint_motion, tissue_start, tissue_end, passive_duration, duration, rpe, external_load):
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


def pushup_tissue_bouts(inputID, input_values, mover_dict, date_done, moverid):
    out_bouts = []
    antagoist_synergistic_divisor = 3
    reps_array = input_values["results"]["reps_array"]
    rpe = input_values["results"]["rpe"]
    if reps_array[1] == 0:
        rb = False
        # this is a TUT input
        duration = input_values["results"]["duration"]
        # duration here is DURATION of each mini-set TIMES number of mini-sets (handled in browser)
    else:
        # this is a reps-based input (rb === "rep-based")
        rb = True
        rep_duration = sum(reps_array[2:])
        duration = reps_array[0] * reps_array[1] * rep_duration
        # 'duration' ==> mini-sets * reps * 'rep_duration' ; this is the total TUT for a rep-based input
        # still going to try to use rep_array data for inputting specific
    bodyweight_portion = mover_dict["bodyweight"]//2
    external_load = int(input_values["results"]
                        ["external_load"])
    load_used_in_pushup = external_load + bodyweight_portion
    # spinal loading!
    planking = planked_spinal_brace(
        inputID, input_values, mover_dict, date_done, moverid, load_used_in_pushup)
    out_bouts.extend(planking)
    bodyweight = mover_dict.pop('bodyweight')
    # wrist group -- just a TUT bout!
    wrists = {k: v for (k, v) in mover_dict.items() if 'wrist' in k}
    for jkey, joint in wrists.items():
        wrist_joint_id = joint['id']
        wrist_target_tissue = joint['zones']['flex']
        wrist_linear_tissue = wrist_target_tissue['linear_adj_id']
        wrist_linear_bout_to_add = bout_dict_maker(date_done, moverid, wrist_joint_id, inputID, 0,
                                                   'linear', wrist_linear_tissue, 'isometric', 95, 95, 0, duration, rpe, load_used_in_pushup)
        out_bouts.append(wrist_linear_bout_to_add)
        wrist_rot_a_tissue = wrist_target_tissue['rotational_adj_id']['rot_a_adj_id']
        wrist_rot_a_bout_to_add = bout_dict_maker(date_done, moverid, wrist_joint_id, inputID, 0,
                                                  'rotational', wrist_rot_a_tissue, 'isometric', 95, 95, 0, duration, rpe, load_used_in_pushup//2)
        out_bouts.append(wrist_rot_a_bout_to_add)
        wrist_rot_b_tissue = wrist_target_tissue['rotational_adj_id']['rot_b_adj_id']
        wrist_rot_b_bout_to_add = bout_dict_maker(date_done, moverid, wrist_joint_id, inputID, 0,
                                                  'rotational', wrist_rot_b_tissue, 'isometric', 95, 95, 0, duration, rpe, load_used_in_pushup//2)
        out_bouts.append(wrist_rot_b_bout_to_add)
    # elbow group
    elbows = {k: v for (k, v) in mover_dict.items() if 'elbow' in k}
    for jkey, joint in elbows.items():
        elbow_joint_id = joint['id']
        elbow_target_tissue = joint['zones']['ext']
        elbow_linear_tissue_id = elbow_target_tissue['linear_adj_id']
        elbow_rot_a_tissue_id = elbow_target_tissue['rotational_adj_id']['rot_a_adj_id']
        elbow_rot_b_tissue_id = elbow_target_tissue['rotational_adj_id']['rot_b_adj_id']

        if rb == True:
            for _ in range(reps_array[0] * reps_array[1]):
                # number of MINISETS times number of REPS
                # concentric-top-eccentric-bottom
                concentric_duration = reps_array[2] if reps_array[2] > 0 else 1
                # linear
                # TEST all starts should be > than end coordinates IF 'concentric' is joint_motion string
                concentric_linear_bout = bout_dict_maker(
                    date_done, moverid, elbow_joint_id, inputID, -90, 'linear', elbow_linear_tissue_id, 'concentric', 120, 5, 0, concentric_duration, rpe, load_used_in_pushup)
                concentric_elbow_rot_a_bout = bout_dict_maker(
                    date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_a_tissue_id, 'eccentric', 5, 10, 0, concentric_duration, rpe, load_used_in_pushup)
                concentric_elbow_rot_b_bout = bout_dict_maker(
                    date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_b_tissue_id, 'concentric', 195, 190, 0, concentric_duration, rpe//antagoist_synergistic_divisor, load_used_in_pushup)
                out_bouts.append(concentric_linear_bout)
                out_bouts.append(concentric_elbow_rot_a_bout)
                out_bouts.append(concentric_elbow_rot_b_bout)

                top_iso_duration = reps_array[3]

            # isometric TOP
                if top_iso_duration > 0:
                    top_iso_linear_bout = bout_dict_maker(
                        date_done, moverid, elbow_joint_id, inputID, -90, 'linear', elbow_linear_tissue_id, 'isometric', 5, 5, 0, top_iso_duration, rpe, load_used_in_pushup)
                    top_iso_rot_a_bout = bout_dict_maker(
                        date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_a_tissue_id, 'isometric', 10, 10, 0, top_iso_duration, rpe, load_used_in_pushup)
                    top_iso_rot_b_bout = bout_dict_maker(
                        date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_b_tissue_id, 'isometric', 190, 190, 0, top_iso_duration, rpe, load_used_in_pushup)
                    out_bouts.append(top_iso_linear_bout)
                    out_bouts.append(top_iso_rot_a_bout)
                    out_bouts.append(top_iso_rot_b_bout)
            # eccentric one
                eccentric_duration = reps_array[4] if reps_array[4] > 0 else 1
                eccentric_linear_bout = bout_dict_maker(
                    date_done, moverid, elbow_joint_id, inputID, -90, 'linear', elbow_linear_tissue_id, 'eccentric', 5, 120, 0, eccentric_duration, rpe, load_used_in_pushup)
                eccentric_rot_a_bout = bout_dict_maker(
                    date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_a_tissue_id, 'concentric', 10, 5, 0, eccentric_duration, rpe, load_used_in_pushup)
                eccentric_rot_b_bout = bout_dict_maker(
                    date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_b_tissue_id, 'eccentric', 190, 195, 0, eccentric_duration, rpe, load_used_in_pushup)
                out_bouts.append(eccentric_linear_bout)
                out_bouts.append(eccentric_rot_a_bout)
                out_bouts.append(eccentric_rot_b_bout)
            # isometric BOTTOM
                bottom_iso_duration = reps_array[5]
                if bottom_iso_duration > 0:
                    bottom_iso_linear_bout = bout_dict_maker(
                        date_done, moverid, elbow_joint_id, inputID, -90, 'linear', elbow_linear_tissue_id, 'isometric', 120, 120, 0, bottom_iso_duration, rpe, load_used_in_pushup)
                    bottom_iso_rot_a_bout = bout_dict_maker(
                        date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_a_tissue_id, 'isometric', 5, 5, 0, bottom_iso_duration, rpe, load_used_in_pushup)
                    bottom_iso_rot_b_bout = bout_dict_maker(
                        date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_b_tissue_id, 'isometric', 195, 195, 0, bottom_iso_duration, rpe, load_used_in_pushup)
                    out_bouts.append(bottom_iso_linear_bout)
                    out_bouts.append(top_iso_rot_a_bout)
                    out_bouts.append(top_iso_rot_b_bout)

        else:
            # each MOVING phase will  will equally divide the total duration instead (one big bout per each tissue)
            concentric_duration = duration // 2
            eccentric_duration = duration // 2
            concentric_linear_bout = bout_dict_maker(
                date_done, moverid, elbow_joint_id, inputID, -90, 'linear', elbow_linear_tissue_id, 'concentric', 120, 5, 0, concentric_duration, rpe, load_used_in_pushup)
            concentric_elbow_rot_a_bout = bout_dict_maker(
                date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_a_tissue_id, 'eccentric', 5, 10, 0, concentric_duration, rpe, load_used_in_pushup)
            concentric_elbow_rot_b_bout = bout_dict_maker(
                date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_b_tissue_id, 'concentric', 195, 190, 0, concentric_duration, rpe/antagoist_synergistic_divisor, load_used_in_pushup)
            out_bouts.append(concentric_linear_bout)
            out_bouts.append(concentric_elbow_rot_a_bout)
            out_bouts.append(concentric_elbow_rot_b_bout)

            eccentric_linear_bout = bout_dict_maker(
                date_done, moverid, elbow_joint_id, inputID, -90, 'linear', elbow_linear_tissue_id, 'eccentric', 5, 120, 0, eccentric_duration, rpe, load_used_in_pushup)
            eccentric_rot_a_bout = bout_dict_maker(
                date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_a_tissue_id, 'concentric', 10, 5, 0, eccentric_duration, rpe, load_used_in_pushup)
            eccentric_rot_b_bout = bout_dict_maker(
                date_done, moverid, elbow_joint_id, inputID, -90, 'rotational', elbow_rot_b_tissue_id, 'eccentric', 190, 195, 0, eccentric_duration, rpe, load_used_in_pushup)
            out_bouts.append(eccentric_linear_bout)
            out_bouts.append(eccentric_rot_a_bout)
            out_bouts.append(eccentric_rot_b_bout)
            # gh (adduct+flex)
    GHs = {k: v for (k, v) in mover_dict.items() if 'GH' in k}
    for jkey, joint in GHs.items():
        gh_joint_id = joint['id']
        gh_target_tissue = joint['zones']['flex-add']
        gh_linear_tissue_id = gh_target_tissue['linear_adj_id']
        gh_adductor_linear_tissue_id = joint['zones']['add']['linear_adj_id']
        gh_rot_a_tissue_id = gh_target_tissue['rotational_adj_id']['rot_a_adj_id']
        gh_rot_b_tissue_id = gh_target_tissue['rotational_adj_id']['rot_b_adj_id']

        if rb == True:
            for _ in range(reps_array[0] * reps_array[1]):
                # range is for MINISETS * REPS
                # concentric-top-eccentric-bottom
                concentric_duration = reps_array[2] if reps_array[2] > 0 else 1
                concentric_gh_linear_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'linear',
                                                            gh_linear_tissue_id, 'concentric', 180, 90, 0, concentric_duration, rpe, load_used_in_pushup)
                # PLUS an additional GH adductor (linear-only) bout for the final half of the mov't (so ha;f the concentric duration)
                concentric_gh_adductor_linear_bout = bout_dict_maker(
                    date_done, moverid, gh_joint_id, inputID, 0, 'linear', gh_adductor_linear_tissue_id, 'concentric', 160, 30, 0, concentric_duration//2, rpe, load_used_in_pushup)
                concentric_gh_rot_a_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'rotational',
                                                           gh_rot_a_tissue_id, 'concentric', 110, 90, 0, concentric_duration, rpe, load_used_in_pushup)
                concentric_gh_rot_b_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'rotational', gh_rot_b_tissue_id,
                                                           'eccentric', 90, 110, 0, concentric_duration, rpe//antagoist_synergistic_divisor, load_used_in_pushup)
                out_bouts.append(concentric_gh_linear_bout)
                out_bouts.append(concentric_gh_adductor_linear_bout)
                out_bouts.append(concentric_gh_rot_a_bout)
                out_bouts.append(concentric_gh_rot_b_bout)

                top_iso_duration = reps_array[3]
                if top_iso_duration > 0:
                    top_iso_gh_linear_bout = bout_dict_maker(
                        date_done, moverid, gh_joint_id, inputID, 0, 'linear', gh_linear_tissue_id, 'isometric', 90, 90, 0, top_iso_duration, rpe, load_used_in_pushup)
                    top_iso_gh_adductor_linear_bout = bout_dict_maker(
                        date_done, moverid, gh_joint_id, inputID, 0, 'linear', gh_adductor_linear_tissue_id, 'isometric', 30, 30, 0, top_iso_duration, rpe, load_used_in_pushup)
                    top_iso_gh_rot_a_bout = bout_dict_maker(
                        date_done, moverid, gh_joint_id, inputID, 0, 'rotational', gh_rot_a_tissue_id, 'isometric', 90, 90, 0, top_iso_duration, rpe, load_used_in_pushup)
                    top_iso_gh_rot_b_bout = bout_dict_maker(
                        date_done, moverid, gh_joint_id, inputID, 0, 'rotational', gh_rot_b_tissue_id, 'isometric', 110, 110, 0, top_iso_duration, rpe, load_used_in_pushup)
                    out_bouts.append(top_iso_gh_linear_bout)
                    out_bouts.append(top_iso_gh_adductor_linear_bout)
                    out_bouts.append(top_iso_gh_rot_a_bout)
                    out_bouts.append(top_iso_gh_rot_b_bout)

                eccentric_duration = reps_array[4] if reps_array[4] > 0 else 1
                eccentric_gh_linear_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'linear',
                                                           gh_linear_tissue_id, 'eccentric', 90, 180, 0, eccentric_duration, rpe, load_used_in_pushup)
                # PLUS an additional GH adductor (linear-only) bout for the final half of the mov't (so ha;f the concentric duration)
                eccentric_gh_adductor_linear_bout = bout_dict_maker(
                    date_done, moverid, gh_joint_id, inputID, 0, 'linear', gh_adductor_linear_tissue_id, 'eccentric', 30, 160, 0, eccentric_duration//2, rpe, load_used_in_pushup)
                eccentric_gh_rot_a_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'rotational',
                                                          gh_rot_a_tissue_id, 'eccentric', 90, 110, 0, eccentric_duration, rpe, load_used_in_pushup)
                eccentric_gh_rot_b_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'rotational', gh_rot_b_tissue_id,
                                                          'concentric', 110, 90, 0, eccentric_duration, rpe//antagoist_synergistic_divisor, load_used_in_pushup)
                out_bouts.append(eccentric_gh_linear_bout)
                out_bouts.append(eccentric_gh_adductor_linear_bout)
                out_bouts.append(eccentric_gh_rot_a_bout)
                out_bouts.append(eccentric_gh_rot_b_bout)

                bottom_iso_duration = reps_array[5]
                if bottom_iso_duration > 0:
                    bottom_iso_gh_linear_bout = bout_dict_maker(
                        date_done, moverid, gh_joint_id, inputID, 0, 'linear', gh_linear_tissue_id, 'isometric', 180, 180, 0, bottom_iso_duration, rpe, load_used_in_pushup)
                    bottom_iso_gh_rot_a_bout = bout_dict_maker(
                        date_done, moverid, gh_joint_id, inputID, 0, 'rotational', gh_rot_a_tissue_id, 'isometric', 110, 110, 0, bottom_iso_duration, rpe, load_used_in_pushup)
                    bottom_iso_gh_rot_b_bout = bout_dict_maker(
                        date_done, moverid, gh_joint_id, inputID, 0, 'rotational', gh_rot_b_tissue_id, 'isometric', 90, 90, 0, bottom_iso_duration, rpe, load_used_in_pushup)
                    out_bouts.append(bottom_iso_gh_linear_bout)
                    out_bouts.append(bottom_iso_gh_rot_a_bout)
                    out_bouts.append(bottom_iso_gh_rot_b_bout)

        else:
            concentric_duration = duration//2
            eccentric_duration = duration//2

            concentric_gh_linear_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'linear',
                                                        gh_linear_tissue_id, 'concentric', 180, 90, 0, concentric_duration, rpe, load_used_in_pushup)
            # PLUS an additional GH adductor (linear-only) bout for the final half of the mov't (so ha;f the concentric duration)
            concentric_gh_adductor_linear_bout = bout_dict_maker(
                date_done, moverid, gh_joint_id, inputID, 0, 'linear', gh_adductor_linear_tissue_id, 'concentric', 160, 30, 0, concentric_duration//2, rpe, load_used_in_pushup)
            concentric_gh_rot_a_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'rotational',
                                                       gh_rot_a_tissue_id, 'concentric', 110, 90, 0, concentric_duration, rpe, load_used_in_pushup)
            concentric_gh_rot_b_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'rotational', gh_rot_b_tissue_id,
                                                       'eccentric', 90, 110, 0, concentric_duration, rpe//antagoist_synergistic_divisor, load_used_in_pushup)
            out_bouts.append(concentric_gh_linear_bout)
            out_bouts.append(concentric_gh_adductor_linear_bout)
            out_bouts.append(concentric_gh_rot_a_bout)
            out_bouts.append(concentric_gh_rot_b_bout)

            eccentric_gh_linear_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'linear',
                                                       gh_linear_tissue_id, 'eccentric', 90, 180, 0, eccentric_duration, rpe, load_used_in_pushup)
            # PLUS an additional GH adductor (linear-only) bout for the final half of the mov't (so ha;f the concentric duration)
            eccentric_gh_adductor_linear_bout = bout_dict_maker(
                date_done, moverid, gh_joint_id, inputID, 0, 'linear', gh_adductor_linear_tissue_id, 'eccentric', 30, 160, 0, eccentric_duration//2, rpe, load_used_in_pushup)
            eccentric_gh_rot_a_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'rotational',
                                                      gh_rot_a_tissue_id, 'eccentric', 90, 110, 0, eccentric_duration, rpe, load_used_in_pushup)
            eccentric_gh_rot_b_bout = bout_dict_maker(date_done, moverid, gh_joint_id, inputID, 0, 'rotational', gh_rot_b_tissue_id,
                                                      'concentric', 110, 90, 0, eccentric_duration, rpe//antagoist_synergistic_divisor, load_used_in_pushup)
            out_bouts.append(eccentric_gh_linear_bout)
            out_bouts.append(eccentric_gh_adductor_linear_bout)
            out_bouts.append(eccentric_gh_rot_a_bout)
            out_bouts.append(eccentric_gh_rot_b_bout)
    # scap-thoracic protraction --> same scheme as GH, tho no 'rotational' bouts for this joint (??)
    scapulas = {k: v for (k, v) in mover_dict.items() if 'scapula' in k}
    for jkey, joint in scapulas.items():
        scap_joint_id = joint['id']
        scap_target_tissue = joint['zones']['protract']
        scap_linear_tissue_id = scap_target_tissue['linear_adj_id']

        if rb == True:
            for _ in range(reps_array[0] * reps_array[1]):
                # range is for MINISETS * REPS
                concentric_duration = reps_array[2] if reps_array[2] > 0 else 1
                concentric_scap_linear_bout = bout_dict_maker(date_done, moverid, scap_joint_id, inputID, 0, 'linear',
                                                              scap_linear_tissue_id, 'concentric', 190, 10, 0, concentric_duration, rpe, load_used_in_pushup)
                out_bouts.append(concentric_scap_linear_bout)

                top_iso_duration = reps_array[3]
                if top_iso_duration > 0:
                    top_iso_scap_linear_bout = bout_dict_maker(date_done, moverid, scap_joint_id, inputID, 0, 'linear',
                                                               scap_linear_tissue_id, 'isometric', 10, 10, 0, top_iso_duration, rpe, load_used_in_pushup)
                    out_bouts.append(top_iso_scap_linear_bout)

                eccentric_duration = reps_array[4] if reps_array[4] > 0 else 1
                eccentric_scap_linear_bout = bout_dict_maker(date_done, moverid, scap_joint_id, inputID, 0, 'linear',
                                                             scap_linear_tissue_id, 'concentric', 10, 190, 0, eccentric_duration, rpe, load_used_in_pushup)
                out_bouts.append(eccentric_scap_linear_bout)

                bottom_iso_duration = reps_array[5]
                if bottom_iso_duration > 0:
                    bottom_iso_scap_linear_bout = bout_dict_maker(date_done, moverid, scap_joint_id, inputID, 0, 'linear',
                                                                  scap_linear_tissue_id, 'isometric', 10, 10, 0, bottom_iso_duration, rpe, load_used_in_pushup)
                    out_bouts.append(bottom_iso_scap_linear_bout)
        else:
            concentric_duration = duration // 2
            eccentric_duration = duration // 2

            concentric_scap_linear_bout = bout_dict_maker(date_done, moverid, scap_joint_id, inputID, 0, 'linear',
                                                          scap_linear_tissue_id, 'concentric', 190, 10, 0, concentric_duration, rpe, load_used_in_pushup)
            out_bouts.append(concentric_scap_linear_bout)
            eccentric_scap_linear_bout = bout_dict_maker(date_done, moverid, scap_joint_id, inputID, 0, 'linear',
                                                         scap_linear_tissue_id, 'concentric', 10, 190, 0, eccentric_duration, rpe, load_used_in_pushup)
            out_bouts.append(eccentric_scap_linear_bout)
    # lower body (copied from 'planking')
    hips = {joint_name: joint_data for (joint_name, joint_data) in mover_dict.items()
            if "hip" in joint_name}
    for jkey, joint in hips.items():
        hip_joint_id = joint['id']
        hip_tissue = joint['zones']['flex']
        linear_tissue = hip_tissue['linear_adj_id']
        linear_bout_to_add = bout_dict_maker(date_done, moverid, hip_joint_id, inputID, 0,
                                             'linear', linear_tissue, 'isometric', 50, 50, 0, duration, rpe, load_used_in_pushup)
        out_bouts.append(linear_bout_to_add)
        rotational_tissue_a = hip_tissue['rotational_adj_id']['rot_a_adj_id']
        rot_a_bout_to_add = bout_dict_maker(date_done, moverid, hip_joint_id, inputID, 0,
                                            'rotational', rotational_tissue_a, 'isometric', 50, 50, 0, duration, rpe, load_used_in_pushup//2)
        out_bouts.append(rot_a_bout_to_add)
        rotational_tissue_b = hip_tissue['rotational_adj_id']['rot_b_adj_id']
        rot_b_bout_to_add = bout_dict_maker(date_done, moverid, hip_joint_id, inputID, 0,
                                            'rotational', rotational_tissue_b, 'isometric', 50, 50, 0, duration, rpe, load_used_in_pushup//2)
        out_bouts.append(rot_b_bout_to_add)
    knee_divisor_on_plank_load = 2
    knee_load = load_used_in_pushup//knee_divisor_on_plank_load
    knees = {joint_name: joint_data for (joint_name, joint_data) in mover_dict.items()
             if "knee" in joint_name}
    for jkey, joint in knees.items():
        knee_joint_id = joint['id']
        linear_knee_tissue = joint['zones']['ext']['linear_adj_id']
        linear_bout_to_add = bout_dict_maker(
            date_done, moverid, knee_joint_id, inputID, 0, 'linear', linear_knee_tissue, 'isometric', 5, 5, 0, duration, rpe, knee_load)
        out_bouts.append(linear_bout_to_add)
    # hallux!
    hallux_load = knee_load
    halluxs = {joint_name: joint_data for (joint_name, joint_data) in mover_dict.items()
               if 'hallux' in joint_name}
    for jkey, joint in halluxs.items():
        hallux_joint_id = joint['id']
        linear_hallux_tissue = joint['zones']['flex']['linear_adj_id']
        linear_hallux_bout_to_add = bout_dict_maker(
            date_done, moverid, hallux_joint_id, inputID, 0, 'linear', linear_hallux_tissue, 'isometric', 190, 190, 0, duration, rpe, hallux_load)
        out_bouts.append(linear_hallux_bout_to_add)

    pprint(out_bouts)
    print(len(out_bouts))

    return out_bouts


def planked_spinal_brace(inputID, input_values, mover_dict, date_done, moverid, loading_param):
    rpe = input_values["results"]["rpe"]
    # DURATION is for the TOTAL number of mini-sets...... is this what i  want??
    duration = input_values["results"]["duration"]
    out_bouts = []
    spine_tissues = {k: v for (k, v) in mover_dict.items()
                     if k != 'bodyweight' and v["type"] == "spinal"}
    # if joint_data["type"] == "spinal"}
    for jkey, joint in spine_tissues.items():
        # for each tissue, grab the specific zone of tissue, calc the duration/rpe demands
        # EXCEPTION for ... grab neck > ext zone
        spinal_joint_id = joint['id']
        if jkey != 'AO':
            target_zone = joint['zones']['flex']
            linear_tissue = target_zone['linear_adj_id']
            linear_bout_to_add = bout_dict_maker(date_done, moverid, spinal_joint_id, inputID, 0,
                                                 'linear', linear_tissue, 'isometric', 50, 50, 0, duration, rpe, loading_param)
            out_bouts.append(linear_bout_to_add)
            rotational_tissue_a = target_zone['rotational_adj_id']['rot_a_adj_id']
            rot_a_bout_to_add = bout_dict_maker(date_done, moverid, spinal_joint_id, inputID, 0,
                                                'rotational', rotational_tissue_a, 'isometric', 50, 50, 0, duration, rpe, loading_param//2)
            out_bouts.append(rot_a_bout_to_add)
            rotational_tissue_b = target_zone['rotational_adj_id']['rot_a_adj_id']
            rot_b_bout_to_add = bout_dict_maker(date_done, moverid, spinal_joint_id, inputID, 0,
                                                'rotational', rotational_tissue_b, 'isometric', 50, 50, 0, duration, rpe, loading_param//2)
            out_bouts.append(rot_b_bout_to_add)
        else:
            target_zone = joint['zones']['ext']
            # TODO potentionally reset this w/ better research?
            load_on_neck_extension = 30
            linear_tissue = target_zone['linear_adj_id']
            linear_bout_to_add = bout_dict_maker(date_done, moverid, spinal_joint_id, inputID, 0,
                                                 'linear', linear_tissue, 'isometric', 50, 50, 0, duration, rpe, load_on_neck_extension)
            out_bouts.append(linear_bout_to_add)
            rotational_tissue_a = target_zone['rotational_adj_id']['rot_a_adj_id']
            rot_a_bout_to_add = bout_dict_maker(date_done, moverid, spinal_joint_id, inputID, 0,
                                                'rotational', rotational_tissue_a, 'isometric', 50, 50, 0, duration, rpe, load_on_neck_extension//2)
            out_bouts.append(rot_a_bout_to_add)
            rotational_tissue_b = target_zone['rotational_adj_id']['rot_a_adj_id']
            rot_b_bout_to_add = bout_dict_maker(date_done, moverid, spinal_joint_id, inputID, 0,
                                                'rotational', rotational_tissue_b, 'isometric', 50, 50, 0, duration, rpe, load_on_neck_extension//2)
            out_bouts.append(rot_b_bout_to_add)
    return out_bouts


def plank_tissue_bouts(inputID, input_values, mover_dict, date_done, moverid):
    resulting_bouts = []
    rpe = input_values["results"]["rpe"]
    # DURATION is for the TOTAL number of mini-sets...... is this what i  want??
    duration = input_values["results"]["duration"]
    bodyweight_portion = mover_dict["bodyweight"]//2
    external_load = int(input_values["results"]
                        ["external_load"])
    load_used_in_plank = external_load + bodyweight_portion
    # >>full rpe/load inputs...
    # grab all spinal sections > flex zone EXCEPT for neck > ext zone
    # WATCH OUT FOR 'bodyweight' KEY!!!!!
    planked_spinal_brace(inputID, input_values, mover_dict,
                         date_done, moverid, load_used_in_plank)
    # grab hip flexors (bilateral)
    hips = {joint_name: joint_data for (joint_name, joint_data) in mover_dict.items()
            if joint_name != 'bodyweight' and "hip" in joint_name}
    for jkey, joint in hips.items():
        hip_joint_id = joint['id']
        hip_tissue = joint['zones']['flex']
        linear_tissue = hip_tissue['linear_adj_id']
        linear_bout_to_add = bout_dict_maker(date_done, moverid, hip_joint_id, inputID, 0,
                                             'linear', linear_tissue, 'isometric', 50, 50, 0, duration, rpe, load_used_in_plank)
        resulting_bouts.append(linear_bout_to_add)
        rotational_tissue_a = hip_tissue['rotational_adj_id']['rot_a_adj_id']
        rot_a_bout_to_add = bout_dict_maker(date_done, moverid, hip_joint_id, inputID, 0,
                                            'rotational', rotational_tissue_a, 'isometric', 50, 50, 0, duration, rpe, load_used_in_plank//2)
        rotational_tissue_b = hip_tissue['rotational_adj_id']['rot_b_adj_id']
        resulting_bouts.append(rot_a_bout_to_add)
        rot_b_bout_to_add = bout_dict_maker(date_done, moverid, hip_joint_id, inputID, 0,
                                            'rotational', rotational_tissue_b, 'isometric', 50, 50, 0, duration, rpe, load_used_in_plank//2)
        resulting_bouts.append(rot_b_bout_to_add)

    # grab scap protractors
    scaps = {joint_name: joint_data for (joint_name, joint_data) in mover_dict.items()
             if joint_name != 'bodyweight' and "scapula" in joint_name}

    for jkey, joint in scaps.items():
        scap_joint_id = joint['id']
        scap_tissue = joint['zones']['protract']
        linear_tissue = scap_tissue["linear_adj_id"]
        linear_bout_to_add = bout_dict_maker(date_done, moverid, scap_joint_id, inputID, 0,
                                             'linear', linear_tissue, 'isometric', 20, 20, 0, duration, rpe, load_used_in_plank)
        resulting_bouts.append(linear_bout_to_add)
        rotational_tissue_a = scap_tissue["rotational_adj_id"]["rot_a_adj_id"]
        rot_a_bout_to_add = bout_dict_maker(date_done, moverid, scap_joint_id, inputID, 0,
                                            'rotational', rotational_tissue_a, 'isometric', 20, 20, 0, duration, rpe, load_used_in_plank//2)
        resulting_bouts.append(rot_a_bout_to_add)
        rotational_tissue_b = scap_tissue["rotational_adj_id"]["rot_b_adj_id"]
        rot_b_bout_to_add = bout_dict_maker(date_done, moverid, scap_joint_id, inputID, 0,
                                            'rotational', rotational_tissue_b, 'isometric', 20, 20, 0, duration, rpe, load_used_in_plank//2)
        resulting_bouts.append(rot_b_bout_to_add)
    # >>partial rpe/load inputs...
    # grab knee extensors
    knee_divisor_on_plank_load = 2
    knee_load = load_used_in_plank//knee_divisor_on_plank_load
    knees = {joint_name: joint_data for (joint_name, joint_data) in mover_dict.items()
             if joint_name != 'bodyweight' and "knee" in joint_name}
    for jkey, joint in knees.items():
        knee_joint_id = joint['id']
        linear_knee_tissue = joint['zones']['ext']['linear_adj_id']
        linear_bout_to_add = bout_dict_maker(
            date_done, moverid, knee_joint_id, inputID, 0, 'linear', linear_knee_tissue, 'isometric', 5, 5, 0, duration, rpe, knee_load)
        resulting_bouts.append(linear_bout_to_add)
    # hallux!
    hallux_load = knee_load
    halluxs = {joint_name: joint_data for (joint_name, joint_data) in mover_dict.items()
               if joint_name != 'bodyweight' and 'hallux' in joint_name}
    for jkey, joint in halluxs.items():
        hallux_joint_id = joint['id']
        linear_hallux_tissue = joint['zones']['flex']['linear_adj_id']
        linear_hallux_bout_to_add = bout_dict_maker(
            date_done, moverid, hallux_joint_id, inputID, 0, 'linear', linear_hallux_tissue, 'isometric', 190, 190, 0, duration, rpe, hallux_load)
        resulting_bouts.append(linear_hallux_bout_to_add)

    pprint(resulting_bouts)
    return resulting_bouts


def unpack_mj_input(inputID, drill_name, input_values, mover_dict, date_done, moverid):
    """this function is called when a 'multijoint' input is detected; 
    uses a case-switcher and the 'drill_name' to generate a set of 
    bouts specific to this mover's tissues; @returns the set of bouts
    associated with this multijoint input """
    mj_bouts_to_add = []

    if drill_name == "plank":
        plank_bouts = plank_tissue_bouts(
            inputID, input_values, mover_dict, date_done, moverid)
        # refactor into a seperate FUNCTION so that it can be called individually
        mj_bouts_to_add.extend(plank_bouts)
    elif drill_name == "push-up":
        pushup_bouts = pushup_tissue_bouts(
            inputID, input_values, mover_dict, date_done, moverid)
        mj_bouts_to_add.extend(pushup_bouts)

    return mj_bouts_to_add


def unpack_inputs(inputs, mover_dict, date_done, moverid):
    bout_array = []

    for inputID, vals in inputs:
        # better way to check for existence in incoming JSON?

        drill = vals["Rx"]["drill_name"]
        inp_id = vals["Rx"]["id"]

        try:
            mj = vals["Rx"]["multijoint"]
            mj = True
        except KeyError:
            mj = False

        # should I even consider this input or not!?!?!?
        if int(vals['results']['duration']) == 0 or int(vals['results']['rpe']) == 0:
            print("not writing bouts bc DURATION and/or RPE is null...")
            continue

        if mj == True:
            mj_bouts = unpack_mj_input(
                inp_id, drill, vals, mover_dict, date_done, moverid)
            # this will return several bouts to get added to the bulk 'bout_array'
            bout_array.extend(mj_bouts)
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
            if start_coord == '' or start_coord == None:
                start_coord = 0
            else:
                start_coord = int(start_coord)

            end_coord = vals["Rx"]["end_coord"]
            if end_coord == '' or end_coord == None:
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

        # ripe for refactor; just pass in params that are outside for... loop

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
                    lin_iso_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
                                                   "linear", target_zone['linear_adj_id'], "isometric", 5, 5, 0, 1, rpe, external_load)
                    rot_iso_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
                                                   "rotational", target_zone['rotational_adj_id'][sinch_adj], "isometric", 5, 5, 0, 1, rpe, external_load)
                    bout_array.append(lin_iso_bout)
                    bout_array.append(rot_iso_bout)
                    for tissue in rotational_tissues:
                        # HACK to get correct end-rotational value (using abs(199-200) to get 1 ...)
                        rot_conc_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
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
                        bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
                                               "rotational", tissue, joint_motion_c, 199, 1, 0, sec_per_length, rpe, external_load)
                        bout_array.append(bout)
                    for tissue in rot_ER_tissues:
                        bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
                                               "rotational", tissue, joint_motion_e, 1, 199, 0, sec_per_length, rpe, external_load)
                        bout_array.append(bout)
                else:
                    terminate = 100
                    for tissue in rot_ER_tissues:
                        bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
                                               "rotational", tissue, joint_motion_c, 199, 1, 0, sec_per_length, rpe, external_load)
                        bout_array.append(bout)
                    for tissue in rot_IR_tissues:
                        bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
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
                bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
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
                capsule_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
                                               "capsular", target_tissue, "isometric", 100, 100, passive_duration, duration, rpe, external_load)
                bout_array.append(capsule_bout)
            # grabbing ROTATIONAL tissue impacts

            rot_target_tissues = mover_dict[ref_joint_name_string]["rotational_tissues"][rotational_bias]
            for rot_tissue in rot_target_tissues:
                rot_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "rotational", rot_tissue, "isometric",
                                           pails_length_value, pails_length_value, passive_duration, duration, rpe, 0)
                bout_array.append(rot_bout)

            if rails is True:
                rails_rot_tissue = mover_dict[ref_joint_name_string]["rotational_tissues"][rails_bias]
                for rot_tissue in rails_rot_tissue:
                    rot_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
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
                p_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "linear", target_zone["linear_adj_id"], "isometric",
                                         linear_pails_coord, linear_pails_coord, passive_duration, duration, rpe, 0)
                bout_array.append(p_bout)
                if rails is True:
                    r_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
                                             "linear", rails_target_zone["linear_adj_id"], "isometric", linear_rails_coord, linear_rails_coord, passive_duration, duration, rpe, 0)

                    bout_array.append(r_bout)
            elif abs(rotational_value) < 85:
                # trying to distrubute the load proprotionately to the amt of rotation
                linear_portion_factor = (85-abs(rotational_value))/85
                lp_p_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "linear", target_zone["linear_adj_id"], "isometric",
                                            linear_pails_coord, linear_pails_coord, passive_duration, duration, round(rpe*linear_portion_factor, 2), 0)
                bout_array.append(lp_p_bout)
                if rails is True:
                    lp_r_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "linear", rails_target_zone["linear_adj_id"], "isometric",
                                                linear_rails_coord, linear_rails_coord, passive_duration, duration, round(rpe*linear_portion_factor, 2), 0)
                    bout_array.append(lp_r_bout)

                rotational_portion_factor = round(
                    (abs(rotational_value))/85, 2)
                for rot_tissue in target_rotational_tissues:
                    rp_p_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "rotational", rot_tissue, "isometric",
                                                pails_length_value, pails_length_value, passive_duration, duration, round(rpe*rotational_portion_factor, 2), 0)
                    bout_array.append(rp_p_bout)
                if rails is True:
                    for rails_rot_tissue in rails_rot_tissues:
                        rp_r_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "rotational", rails_rot_tissue, "isometric", rails_length_value,
                                                    rails_length_value, 0, duration/2, round(rpe*rotational_portion_factor, 2), 0)
                        bout_array.append(rp_r_bout)
            else:
                for rot_tissue in target_rotational_tissues:
                    p_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "rotational", rot_tissue, "isometric",
                                             pails_length_value, pails_length_value, passive_duration, duration, rpe, 0)
                    bout_array.append(p_bout)
                if rails is True:
                    for rails_rot_tissue in rails_rot_tissues:
                        r_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "rotational", rails_rot_tissue, "isometric",
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
                bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
                                       "linear", target_zone["linear_adj_id"], joint_motion, start_coord, end_coord, 0, duration, rpe, external_load)
                bout_array.append(bout)

            elif abs(rotational_value) < 85:
                linear_portion_factor = round(
                    ((85 - abs(rotational_value))/85), 2)
                lin_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "linear", target_zone["linear_adj_id"], joint_motion,
                                           start_coord, end_coord, 0, duration, round(linear_portion_factor*rpe, 2), external_load)
                bout_array.append(lin_bout)

                rotational_portion_factor = round(
                    ((abs(rotational_value))/85), 2)
                rot_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "rotational", target_zone["rotational_adj_id"][rot_adj], joint_motion,
                                           rotational_tissue_position, end_rotational_position_value, 0, duration, round(rotational_portion_factor*rpe, 2), external_load)
                bout_array.append(rot_bout)

            else:
                rot_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "rotational", target_zone["rotational_adj_id"][rot_adj], joint_motion,
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
                bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
                                       "linear", target_zone["linear_adj_id"], "isometric", start_coord, end_coord, 0, duration, rpe, external_load)
                bout_array.append(bout)

            elif abs(rotational_value) < 85:
                linear_portion_factor = round(
                    ((85 - abs(rotational_value))/85), 2)
                lin_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "linear", target_zone["linear_adj_id"], "isometric",
                                           start_coord, end_coord, 0, duration, round(linear_portion_factor*rpe, 2), external_load)
                bout_array.append(lin_bout)

                rotational_portion_factor = round(
                    ((abs(rotational_value))/85), 2)
                rot_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "rotational", target_zone["rotational_adj_id"][rails_adj], "isometric",
                                           start_coord, end_coord, 0, duration, round(rotational_portion_factor*rpe, 2), external_load)
                bout_array.append(rot_bout)

            else:
                rot_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "rotational", target_zone["rotational_adj_id"][rails_adj], "isometric",
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
                    bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value,
                                           "linear", target_zone["linear_adj_id"], joint_motion, pointer, terminate, 0, sec_per_length, rpe, external_load)
                    bout_array.append(bout)
                elif abs(rotational_value) < 85:
                    # share proportionally
                    linear_portion_factor = round(
                        ((85 - abs(rotational_value))/85), 2)
                    lin_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "linear", target_zone["linear_adj_id"], joint_motion,
                                               pointer, terminate, 0, sec_per_length, round(linear_portion_factor*rpe, 2), external_load)
                    bout_array.append(lin_bout)

                    rotational_portion_factor = round(
                        ((abs(rotational_value))/85), 2)
                    rot_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "rotational", target_zone["rotational_adj_id"][rot_adj], joint_motion,
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
                    rot_bout = bout_dict_maker(date_done, moverid, joint_id, inp_id, rotational_value, "rotational", target_zone["rotational_adj_id"][rot_adj], joint_motion,
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
    print("done with compiling bouts to add....")
    print(len(bout_array))
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

    # pprint(workout_array)

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
