
import uuid
import datetime as dt

from server_side.db_ref_vals import default_joint_dict


"""gesture = a unidirectional vector of stress that does NOT cross midline"""


def joint_rotation(joint, moverid, fixed_side_anchor_id, mover_joint_dict, rotational_bias_start, rotational_bias_end):
    """generate set of rotational gestures:
    a "simultaneous" joint_roll tuple for all rot_tissues of a given joint,
    in the mover_joint_dict["joint"]["rotational_tissues"]
    rotation = diff btw _start and _end (gives rotational_bias, which is used to select 'fwd' or 'bkwd' tissues by id)
    """
    rotational_delta = rotational_bias_end - rotational_bias_start
    if rotational_delta > 0:
        rotational_bias = "fwd"
    elif rotational_delta < 0:
        rotational_bias = "bkwd"
    else:
        rotational_bias = None
    rot_tissues = mover_joint_dict[joint]["rotational_tissues"]
    shortening_tissues = []
    if rotational_bias != None:
        shortening_tissues.extend(rot_tissues[rotational_bias])
    else:
        shortening_tissues.extend(rot_tissues["fwd"], rot_tissues["bkwd"])

    result = []
    for tissue in shortening_tissues:
        joint_roll_to_add = joint_roll(
            tissue, fixed_side_anchor_id, rotational_bias_start, rotational_bias_end)
        result.append(joint_roll_to_add)

    return result
    # this is a list of joint_roll() results (np.arrays of integrals!), that can be


def joint_fe(lin_tissue_id, fixed_anchor_side, start_pos, end_pos=None):
    """positions are just 0-100 values repr that dimension of np.array obj"""

    if end_pos == None:
        contraction_motion = "isometric"

    elif end_pos > start_pos:
        contraction_motion = "eccentric"
    else:
        contraction_motion = "concentric"
    pass
    # HANDLE THE INTEGRAL/POINT VALUES in []
    # return (tissue_id, np.array(?), contraction_motion)


def joint_roll(rot_tissue_id, fixed_anchor_side, start_pos, end_pos=None):
    """positions are -100 --  +100 values repr that dimension of np.array obj"""
    if end_pos == None:
        joint_motion = "isometric"
    elif abs(end_pos) > abs(start_pos):
        joint_motion = "eccentric"
    else:
        joint_motion = "concentric"
    pass
    # HANDLE THE INTEGRAL VALUES in [] np.array


def CARs(joint, moverid, mover_joint_dict, reverse=False, closed_chain=False):
    '''"joint" must be sided (as in R GH), returns a series of gestures that can be passed to an apply() function'''
    joint_zones = mover_joint_dict[joint]["zones"]
    joint_id = mover_joint_dict[joint]["id"]
    all_gestures = []
    start_rot_rom = 100
    for zone in joint_zones.keys():
        # an isometric at each axis (zone)
        ref_zone_id = joint_zones[zone]["ref_zones_id"]
        fixed_side_anchor_id = joint_zones[zone]["anchors"]["proximal"]
        rotational_tissue_fwd_id = joint_zones[zone]["rotational_adj_id"]["rot_a_adj_id"]
        rotational_tissue_bkwd_id = joint_zones[zone]["rotational_adj_id"]["rot_b_adj_id"]
        linear_tissue_id = joint_zones[zone]["linear_adj_id"]
        pulse = (ref_zone_id, joint_fe(
            linear_tissue_id, fixed_side_anchor_id, 10))
        # extra 'sinching' of joint into end-range
        rot_pulse_a = (ref_zone_id, joint_roll(
            rotational_tissue_fwd_id, fixed_side_anchor_id, 5))
        rot_pulse_b = (ref_zone_id, joint_roll(
            rotational_tissue_bkwd_id, fixed_side_anchor_id, 5))
        # to get from one zone to the next
        roll = (ref_zone_id, joint_rotation(joint, moverid, fixed_side_anchor_id,
                mover_joint_dict, start_rot_rom, start_rot_rom-25))
        all_gestures.extend([pulse, rot_pulse_a, rot_pulse_b, roll])
        start_rot_rom -= 25
        # 25 (%) not 45 (deg) because I want to map percent rotation onto specific mover values if/when needed

    return (moverid, joint_id, all_gestures)


'''def apply_drill(gesture_tuple, date, rpe, duration, load=1, comments=None):
    moverid, joint_id, all_gestures = gesture_tuple
    tut_for_each_gesture = duration/len(all_gestures)
    starting_moment = date
    bouts = []
    for tissue in all_gestures:
        ref_zones_id, joint_motion = tissue
        tissue_id, < integral object > , contraction_motion = joint_motion
        bout_date = starting_moment
        # get...
        # ref_zones_id_a
        # ref_zones_id_b
        # rotational_bias (conditionally)
        #  from the db upon insert using tissue_id as key?? fast way to do this??


# def opp_tissue(), locate the opposing tissue_id, opposing position using the 'gesture parser engine'

"""    date = dt.datetime.now()
    moverid INTEGER NOT NULL,
    joint_id INTEGER NOT NULL,
    ref_zones_id_a INTEGER NOT NULL,
    ref_zones_id_b INTEGER,
    fixed_side_anchor_id INTEGER NOT NULL,
    rotational_bias TEXT,
    joint_motion TEXT NOT NULL, 
    start_coord INTEGER,
    end_coord INTEGER,
    tissue_id INTEGER,
    drill_name TEXT,
    duration INTEGER NOT NULL,
    passive_duration INTEGER,
    rpe INT NOT NULL,
    external_load INTEGER,
    comments TEXT, """


class InputCycle1:
    def __init__(self, joint, bias, zone):
        self.joint = joint
        self.bias = bias
        self.zone = zone
        # need to SELECT ref_tissues that correspond with this joint:bias:zone from DB, store to arrays of tissue_ref_id...
        self.tissues_trained_prog = []
        self.tissues_trained_reg = []

    def apply_impact(self, mover_id, duration, rpe, load=1, passive_duration=0, pails=True, rails=False):
        self.mover_id = mover_id
        self.duration = duration
        self.rpe = rpe
        self.load = load
        self.passive_duration = passive_duration
        self.pails = pails
        self.rails = rails
        # this generates a psuedo-random key to help group bouts as PART of this input upon application
        self.date_applied = dt.datetime.now()
        self.input_id = uuid.uuid4()
        tissues_to_write_to = []
        if pails:
            for tissue in self.tissues_trained_prog:
                pass
                # need to SELECT mover-specific tissue_ids, then use that combined with IMPACT vals to create np.array
                # that will get stored in each tissue's BLOBs (musc, ct which we KNOW bc this IC is isometric)
        if rails:
            for tissue in self.tissues_trained_prog:
                pass
        # executemany using tissues to write to
        # seperate execute to bout_log
    # add assign() when getting to progrmaming step
'''
