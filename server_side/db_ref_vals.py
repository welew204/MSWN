from collections import defaultdict, deque
import sqlite3
from flask import g, current_app
from datetime import datetime
import copy
import pprint

syn_zone_relations_list = ["flex", "flex-abd", "abd", "ext-abd", "ext", "ext-add", "add", "flex-add"]
sesamoid_zone_relations_list = ["protract", "elevate", "retract", "depress"]
spinal_zone_relations_list = ["flex", "r_rotate", "ext", "l_rotate"]
syn_zone_deque = deque(syn_zone_relations_list)
ses_zone_deque = deque(sesamoid_zone_relations_list)
spine_zone_deque = deque(spinal_zone_relations_list)
# usezone_deque.rotate() to move right (+) and left (-)


def_values = {
    "hip": {
        "pcapsule_ir_rom": 35,
        "pcapsule_er_rom": 60,
        "acapsule_ir_rom": 20,
        "acapsule_er_rom": 45
    },
    "knee": {
        "pcapsule_ir_rom": 15,
        "pcapsule_er_rom": 35,
        "acapsule_ir_rom": 10,
        "acapsule_er_rom": 20
    },
    "ankle": {
        "pcapsule_ir_rom": 15,
        "pcapsule_er_rom": 35,
        "acapsule_ir_rom": 5,
        "acapsule_er_rom": 20
    },
    "GH": {
        "pcapsule_ir_rom": 75,
        "pcapsule_er_rom": 90,
        "acapsule_ir_rom": 60,
        "acapsule_er_rom": 75
    },
    "elbow": {
        "pcapsule_ir_rom": 90,
        "pcapsule_er_rom": 90,
        "acapsule_ir_rom": 75,
        "acapsule_er_rom": 75
    },
    "wrist": {
        "pcapsule_ir_rom": 20,
        "pcapsule_er_rom": 40,
        "acapsule_ir_rom": 5,
        "acapsule_er_rom": 25
    },
    "hallux": {
        "pcapsule_ir_rom": 0,
        "pcapsule_er_rom": 0,
        "acapsule_ir_rom": 0,
        "acapsule_er_rom": 0
    },
    "toes": {
        "pcapsule_ir_rom": 0,
        "pcapsule_er_rom": 0,
        "acapsule_ir_rom": 0,
        "acapsule_er_rom": 0
    },
    "scapular-thoracic": {
        "pcapsule_ir_rom": 0,
        "pcapsule_er_rom": 0,
        "acapsule_ir_rom": 0,
        "acapsule_er_rom": 0
    },
    ## need to update for following joints:
    # - AO
    # - TC
    # - LT
    # - SI
    # - illiac
    # - scapular-thoracic
    #each spine section corresponds to the ROTATION of the bony body
    "spine": {
        "AO": {},
        "TC": {},
        "LT": {},
        "SI": {},
        "specific_segment_values" :{
        "c1": {"flexion": 7.5,"extension": 7.5},
        "c2": {"flexion": 5.6,"extension": 5.6},
        "c3": {"flexion": 8.8,"extension": 8.8},
        "c4": {"flexion": 11.0,"extension": 11.0},
        "c5": {"flexion": 11.0,"extension": 11.0},
        "c6": {"flexion": 16.5,"extension": 16.5},
        "c7": {"flexion": 4.9,"extension": 4.9},
        "t1": {"flexion": 1.9,"extension": 2.3},
        "t2": {"flexion": 1.5,"extension": 2.2},
        "t3": {"flexion": 1.4,"extension": 2.1},
        "t4": {"flexion": 1.5,"extension": 1.9},
        "t5": {"flexion": 1.6,"extension": 1.6},
        "t6": {"flexion": 1.7,"extension": 1.5},
        "t7": {"flexion": 1.8,"extension": 1.4},
        "t8": {"flexion": 2.0,"extension": 1.4},
        "t9": {"flexion": 2.2,"extension": 1.5},
        "t10": {"flexion": 2.5,"extension": 1.7},
        "t11": {"flexion": 3.4,"extension": 2.0},
        "t12": {"flexion": 4.5,"extension": 2.4},
        "l1": {"flexion": 2.6,"extension": 2.6},
        "l2": {"flexion": 2.6,"extension": 2.6},
        "l3": {"flexion": 2.6,"extension": 2.6},
        "l4": {"flexion": 2.6,"extension": 2.6},
        "l5": {"flexion": 2.3,"extension": 2.3},
        "s1": {"flexion": 2.3,"extension": 2.3},
        }}
    }

def default_joint_dict():
    """this just makes a user-generic dict of joints, zones from the def_vals and *_zone_relations_list's"""
    res = defaultdict(list)
    for joint in def_values.keys():
        if joint == "spine":
            continue
        elif joint == "scapular-thoracic":
            zone_list = sesamoid_zone_relations_list
        else:
            zone_list = syn_zone_relations_list
        res["R "+joint].extend(zone_list)
        res["L "+joint].extend(zone_list)
    return res



bones = {
    "cranium": {"bone_ends": [0], "joints": ["AO"]},
    "cervical": {"bone_ends": [0,1], "joints": ["AO", "TC"]},
    "thoracic": {"bone_ends": [0,1,2,3], "joints": ["TC", "LT", "R scapular-thoracic", "L scapular-thoracic"]},
    "scapula": {"bone_ends": [0,1], "joints": ["scapular-thoracic", "GH"]},
    "humerus": {"bone_ends": [0,1], "joints": ["GH", "elbow"]},
    "ul_rad": {"bone_ends": [0,1], "joints": ["elbow", "wrist"]},
    "hand": {"bone_ends": [0], "joints": ["wrist"]},
    "lumbar": {"bone_ends": [0,1], "joints": ["LT", "SI"]},
    "pelvis": {"bone_ends": [0,1,2], "joints": ["SI", "iliac", "hip"]},
    "femur": {"bone_ends": [0,1], "joints": ["hip", "knee"]},
    "fib_tib": {"bone_ends": [0,1], "joints": ["knee", "ankle"]},
    "foot": {"bone_ends": [0,1,2], "joints": ["ankle", "toes", "hallux"]},
    "toes": {"bone_ends": [0], "joints": ["toes"]},
    "big_toe": {"bone_ends": [0], "joints": ["hallux"]}
}

def build_ref_bone_end_vals(db):
    curs = db.cursor()
    bone_ends_to_add = []
    qmarks = ["?" for i in range(3)]
    for bone in bones.keys():
        if bone not in ["cervical", "thoracic", "lumbar", "cranium"]:
            for end in bones[bone]["bone_ends"]:
                bone_end_field_vals_r = [bone, end, "R"]
                bone_end_field_vals_l = [bone, end, "L"]
                bone_ends_to_add.append(bone_end_field_vals_r)
                bone_ends_to_add.append(bone_end_field_vals_l)
        else:
            for end in bones[bone]["bone_ends"]:
                bone_end_field_vals = [bone, end, "mid"]
                bone_ends_to_add.append(bone_end_field_vals)

    curs.executemany(f'INSERT INTO ref_bone_end (bone_name, end, side) VALUES ({",".join(qmarks)})', 
        bone_ends_to_add)
    db.commit()
    print("added the BONE END reference values!")
    # builds in bone_ends (1-2+ per "bone")

def build_joint_ref_vals(db):
    # add ref_joints (ref vals), ref_zones, bone_anchor (*8 per)
    # create db cnx from PASSED in db
    curs = db.cursor()
    bone_ends = curs.execute('SELECT * FROM ref_bone_end').fetchall()
    ## below updates the ref_bone_dict with actual be_ids and adds each side
    bone_joint_table = copy.deepcopy(bones)
    bone_list = list(bone_joint_table.keys())
    for bone in bone_list:
        number_of_ids = len(bone_joint_table[bone]["bone_ends"])
        bone_joint_table[bone]["be_ids"] = [None for i in range(number_of_ids)]
        if bone not in ["cervical", "thoracic", "lumbar", "cranium"]:
            bone_r_side = copy.deepcopy(bone_joint_table[bone])
            bone_r_side["side"] = "R"
            bone_l_side = copy.deepcopy(bone_joint_table[bone])
            bone_l_side["side"] = "L"
            bone_joint_table.pop(bone)
            bone_joint_table[f"R {bone}"] = bone_r_side
            bone_joint_table[f"L {bone}"] = bone_l_side
        else:
            bone_joint_table[bone]["side"] = "mid"
    for be in bone_ends:
        # unpack be for id!
        be_id, be_bone_name, end, side = be
        if be_bone_name not in ["cervical", "thoracic", "lumbar", "cranium"]:
            bone_joint_table[f"{side} {be_bone_name}"]["be_ids"][end] = be_id
        else:
            bone_joint_table[be_bone_name]["be_ids"][end] = be_id

    joint_dict = defaultdict(list)
    # ^ this should result in a single-item/joint dictionary that gives a 2_id list for each that can be used as primary keys! 
    for bone in bone_joint_table.keys():
        side = bone_joint_table[bone]["side"]
        for i, joint in enumerate(bone_joint_table[bone]["joints"]):
            if side != "mid":
                joint_dict[f"{side} {joint}"].append(bone_joint_table[bone]["be_ids"][i])
                #joint_dict[f"{side} {joint}"] = side
            else:
                joint_dict[joint].append(bone_joint_table[bone]["be_ids"][i])
                #joint_dict[joint] = side
    joints_to_add = []
    date = datetime.now().strftime("%Y-%m-%d")
    qmarks = ["?" for i in range(10)]

    for joint in joint_dict.keys():
        if "SI" in joint or "iliac" in joint:
            # for now, just skipping this issue so I can unpack the bone_ends to build joints
            continue
        bone_end_id_a, bone_end_id_b = joint_dict[joint]
        if "R" in joint:
            side = "R"
            joint_name = joint[2:]
            if "scapula" in joint_name:
                joint_type = "sesamoid"
            else:
                joint_type = "synovial"
        elif "L" in joint and joint != "LT":
            side = "L"
            joint_name = joint[2:]
            if "scapula" in joint_name:
                joint_type = "sesamoid"
            else:
                joint_type = "synovial"
        else: 
            joint_name = joint
            side = "mid"
            joint_type = "spinal"
        if joint_name in def_values.keys():
            caps_vals = copy.copy(def_values[joint_name])
            ref_pcapsule_ir_rom = caps_vals["pcapsule_ir_rom"]
            ref_pcapsule_er_rom = caps_vals["pcapsule_er_rom"]
            ref_acapsule_ir_rom = caps_vals["acapsule_ir_rom"]
            ref_acapsule_er_rom = caps_vals["acapsule_er_rom"]
        else:
            ref_pcapsule_ir_rom = None
            ref_pcapsule_er_rom = None
            ref_acapsule_ir_rom = None
            ref_acapsule_er_rom = None
            caps_vals = {
                "pcapsule_ir_rom": ref_pcapsule_ir_rom,
                "pcapsule_er_rom": ref_pcapsule_er_rom,
                "acapsule_ir_rom": ref_acapsule_ir_rom,
                "acapsule_er_rom": ref_acapsule_er_rom,
            }
        joint_values = [
            date, 
            bone_end_id_a, 
            bone_end_id_b, 
            joint_name, 
            side, 
            joint_type, 
            ref_pcapsule_ir_rom, 
            ref_pcapsule_er_rom, 
            ref_acapsule_ir_rom, 
            ref_acapsule_er_rom
            ]
        joints_to_add.append(joint_values)
    # executemany to "joint_reference", commit to db
    curs.executemany(f'INSERT INTO ref_joints (date_updated, bone_end_id_a, bone_end_id_b, joint_name, side, joint_type, ref_pcapsule_ir_rom, ref_pcapsule_er_rom, ref_acapsule_ir_rom, ref_acapsule_er_rom) VALUES ({",".join(qmarks)})', 
        joints_to_add)
    db.commit()
    print("added the JOINT reference values!")
    
def build_zone_ref_vals(db):
    # select ref_joints from db (to get joint_id, side)
    curs = db.cursor()
    joints = curs.execute('SELECT rowid, * FROM ref_joints').fetchall()
    # `joints` is a list
    zones_to_add = []
    date = datetime.now().strftime("%Y-%m-%d")
    for joint in joints:
        joint_ref_id, date_updated, bone_end_id_a, bone_end_id_b, joint_name, side, joint_type, ref_pcapsule_ir_rom, ref_pcapsule_er_rom, ref_acapsule_ir_rom, ref_acapsule_er_rom = joint
        zone_ref_vals = [date, joint_ref_id, "", side, None, None, None, None]
        qmarks = ["?" for i in range(8)]
    # generate zones programatically into sql-ready format
    # --spine joints should generate 4 (flex, ext, r_rotate, l_rotate); this can map with the positionality); 
    # --HOWEVER zones with spine as joint-type should NOT be triplicated in tissue_status table
    # ---scapula should generate 4 (pro, re, elev, dep), 
    # -all other joints get 8
        if joint_type == "spinal":
            for z in spinal_zone_relations_list:
                spine_zone_ref_vals = zone_ref_vals.copy()
                spine_zone_ref_vals[2] = z
                zones_to_add.append(spine_zone_ref_vals)
        elif joint_type == "sesamoid":
            for z in sesamoid_zone_relations_list:
                sesamoid_zone_ref_vals = zone_ref_vals.copy()
                sesamoid_zone_ref_vals[2] = z
                zones_to_add.append(sesamoid_zone_ref_vals)
        else:
            for z in syn_zone_relations_list:
                synovial_zone_ref_vals = zone_ref_vals.copy()
                synovial_zone_ref_vals[2] = z
                zones_to_add.append(synovial_zone_ref_vals)
    # executemany to "zone_reference", commit to db
    curs.executemany(f'INSERT INTO ref_zones (date_updated, ref_joints_id, zone_name, side, reference_progressive_p_rom, reference_progressive_a_rom, reference_regressive_p_rom, reference_regressive_a_rom) VALUES ({",".join(qmarks)})', 
        zones_to_add)
    db.commit()
    print("added the ZONE reference values!")

def build_anchors(db):
    # each bone-end gets 1 anchor per zone
    anchors_to_add = []
    curs = db.cursor()
    anchor_sites = curs.execute('''SELECT ref_joints.rowid, 
                    ref_joints.bone_end_id_a, 
                    ref_joints.bone_end_id_b, 
                    ref_zones.id, 
                    ref_zones.zone_name 
                    FROM ref_joints 
                    INNER JOIN ref_zones 
                    ON ref_zones.ref_joints_id = ref_joints.rowid''').fetchall()
    for anchor in anchor_sites:
        ref_joint_id, ref_bone_end_id_a, ref_bone_end_id_b, ref_zones_id, zone_name = anchor
        anchor_vals_proximal = [ref_bone_end_id_a, ref_zones_id]
        anchors_to_add.append(anchor_vals_proximal)
        anchor_vals_distal = [ref_bone_end_id_b, ref_zones_id]
        anchors_to_add.append(anchor_vals_distal)
    curs.executemany(f'INSERT INTO ref_anchor (bone_end_id, ref_zones_id) VALUES (?, ?)', 
        anchors_to_add)
    db.commit()
    print("added the ANCHOR reference values!")

def build_adj(db):
    # need: joint_id, zone_id
    curs = db.cursor()
    anchors = curs.execute('''SELECT ref_anchor.id,
                ref_anchor.bone_end_id, 
                ref_anchor.ref_zones_id,
                ref_zones.ref_joints_id,
                ref_zones.zone_name,
                ref_joints.joint_type,
                ref_joints.joint_name
                FROM ref_anchor 
                LEFT JOIN ref_zones ON ref_zones.id = ref_zones_id
                LEFT JOIN ref_joints ON ref_joints.rowid = ref_zones.ref_joints_id''').fetchall()
    
    # this gives me a dict of joints:zones:anchor_ids@each zone
    def make_zone_lib():
        joint_dict = {
            "name": "",
            "type": "",
            "zones": defaultdict(list)
        }
        return joint_dict
    joints = defaultdict(make_zone_lib)
    for anchor in anchors:
        anchor_id, bone_end_id, ref_zones_id, ref_joints_id, zone_name, joint_type, joint_name = anchor
        joints[ref_joints_id]["name"] = joint_name
        joints[ref_joints_id]["type"] = joint_type
        joints[ref_joints_id]["zones"][zone_name].append(anchor)
    
    ## start here!
    # need to conditionally link anchors
    capsule_adj_to_add = []
    rot_adj_to_add = []
    linear_adj_to_add = []
## USE the zone_deque to rotate to the correct zone!!@!!!!!! then write the adj that way

    for joint in joints.keys():
        rji = joint
        for zone in joints[joint]["zones"].keys():
            anchor_a_pl, anchor_b_pl = joints[joint]["zones"][zone]
            anchor_id_a, bone_end_id_a, ref_zones_id, ref_joints_id, zone_name, joint_type, joint_name = anchor_a_pl
            anchor_id_b, bone_end_id_b, ref_zones_id, ref_joints_id, zone_name, joint_type, joint_name = anchor_b_pl
            rzi = ref_zones_id
            # handling rotational_adj connection...
            if joint_type == "synovial":
                zone_ind = syn_zone_deque.index(zone_name)
                syn_zone_deque.rotate(-2)
                rot_adj_anchor_b_name = syn_zone_deque[zone_ind]
                syn_zone_deque.rotate(4)
                bkwd_rot_adj_anchor_b_name = syn_zone_deque[zone_ind]
                for anchor in joints[joint]["zones"][rot_adj_anchor_b_name]:
                    if anchor[1] == bone_end_id_b:
                        rot_adj_anchor_b_id = anchor[0]
                for anchor in joints[joint]["zones"][bkwd_rot_adj_anchor_b_name]:
                    if anchor[1] == bone_end_id_b:
                        bkwd_rot_adj_anchor_b_id = anchor[0]

                fwd_rot_tissue = [None, None, rji, anchor_id_a, rot_adj_anchor_b_id, "ER"]
                bkwd_rot_tissue = [None, None, rji, anchor_id_a, bkwd_rot_adj_anchor_b_id, "IR"]
                rot_adj_to_add.append(fwd_rot_tissue)
                rot_adj_to_add.append(bkwd_rot_tissue)
            
            elif joint_type == "spinal":
                zone_ind = spine_zone_deque.index(zone_name)
                spine_zone_deque.rotate(-1)
                rot_adj_anchor_b_name = spine_zone_deque[zone_ind]
                spine_zone_deque.rotate(2)
                bkwd_rot_adj_anchor_b_name = spine_zone_deque[zone_ind]
                for anchor in joints[joint]["zones"][rot_adj_anchor_b_name]:
                    if anchor[1] == bone_end_id_b:
                        rot_adj_anchor_b_id = anchor[0]
                for anchor in joints[joint]["zones"][bkwd_rot_adj_anchor_b_name]:
                    if anchor[1] == bone_end_id_b:
                        bkwd_rot_adj_anchor_b_id = anchor[0]
                
                fwd_rot_tissue = [None, None, rji, anchor_id_a, rot_adj_anchor_b_id, "Rt"]
                bkwd_rot_tissue = [None, None, rji, anchor_id_a, bkwd_rot_adj_anchor_b_id, "Lf"]
                rot_adj_to_add.append(fwd_rot_tissue)
                rot_adj_to_add.append(bkwd_rot_tissue)
            else:
                zone_ind = ses_zone_deque.index(zone_name)
                ses_zone_deque.rotate(-1)
                rot_adj_anchor_b_name = ses_zone_deque[zone_ind]
                ses_zone_deque.rotate(2)
                bkwd_rot_adj_anchor_b_name = ses_zone_deque[zone_ind]
                for anchor in joints[joint]["zones"][rot_adj_anchor_b_name]:
                    if anchor[1] == bone_end_id_b:
                        rot_adj_anchor_b_id = anchor[0]
                for anchor in joints[joint]["zones"][bkwd_rot_adj_anchor_b_name]:
                    if anchor[1] == bone_end_id_b:
                        bkwd_rot_adj_anchor_b_id = anchor[0]

                fwd_rot_tissue = [None, None, rji, anchor_id_a, rot_adj_anchor_b_id, "Uh"]
                bkwd_rot_tissue = [None, None, rji, anchor_id_a, bkwd_rot_adj_anchor_b_id, "Oh"]
                rot_adj_to_add.append(fwd_rot_tissue)
                rot_adj_to_add.append(bkwd_rot_tissue)
                
            caps_tiss = [rji, rzi, None, anchor_id_a, anchor_id_b]
            linear_tiss = [rji, rzi, None, None, anchor_id_a, anchor_id_b]
            capsule_adj_to_add.append(caps_tiss)
            linear_adj_to_add.append(linear_tiss)
    curs.executemany(f'INSERT INTO ref_capsule_adj (ref_joints_id, ref_zones_id, ref_ct_training_status, ref_anchor_id_a, ref_anchor_id_b) VALUES (?, ?, ?, ?, ?)', 
        capsule_adj_to_add)
    db.commit()
    curs.executemany(f'INSERT INTO ref_rotational_adj (ref_musc_training_status, ref_ct_training_status, ref_joints_id, ref_anchor_id_a, ref_anchor_id_b, rotational_bias) VALUES (?, ?, ?, ?, ?, ?)', 
        rot_adj_to_add)
    db.commit()
    curs.executemany(f'INSERT INTO ref_linear_adj (ref_joints_id, ref_zones_id, ref_musc_training_status, ref_ct_training_status, ref_anchor_id_a, ref_anchor_id_b) VALUES (?, ?, ?, ?, ?, ?)', 
        linear_adj_to_add)
    db.commit()
    print("added the ADJ reference values (caps, rot, lin)!")

if __name__=="__main__":
    db = sqlite3.connect('/Users/williamhbelew/Hacking/MSWN/instance/mswnapp.sqlite')
    #build_joint_ref_vals(db)
    build_adj(db)
    #pp = pprint.PrettyPrinter()
    #pp.pprint(joint_zone_lookup_table)

    # eventually I want to harvest all this DB data into a dict, ala below...
"""     joint_zone_lookup_table[joint] = {
        "bone_end_ids": [bone_end_id_a, bone_end_id_b],
        "side": side,
        "joint_name": joint_name,
        "joint_type": joint_type,
        "ref_capsule_values": caps_vals
        } """