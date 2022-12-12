from collections import defaultdict
import sqlite3
from flask import g, current_app
from datetime import datetime
import copy


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
    "scapula": {
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
        }
    }

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

# start here!!!!!!!

    for joint in joint_dict.keys():
        if "SI" in joint or "iliac" in joint:
            # for now, just skipping this issue so I can unpack the bone_ends to build joints
            continue
        bone_end_id_a, bone_end_id_b = joint_dict[joint]
        if side == "mid":
            joint_name = joint
            joint_type = "spinal"
        else: # need to cut off the side from the joint name <eye roll>
            joint_name = joint[2:]
            if joint_name == "scapula":
                joint_type = "sesamoid"
            else:
                joint_type = "synovial"
        if joint_name in def_values.keys():
            caps_vals = copy.copy(def_values[joint])
            ref_pcapsule_ir_rom = caps_vals["ref_pcapsule_ir_rom"]
            ref_pcapsule_er_rom = caps_vals["ref_pcapsule_er_rom"]
            ref_acapsule_ir_rom = caps_vals["ref_acapsule_ir_rom"]
            ref_acapsule_er_rom = caps_vals["ref_acapsule_er_rom"]
        else:
            ref_pcapsule_ir_rom = None
            ref_pcapsule_er_rom = None
            ref_acapsule_ir_rom = None
            ref_acapsule_er_rom = None
        joint_values = [
            date, 
            bone_end_id_a, 
            bone_end_id_b, 
            joint_name, 
            side, joint_type, 
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
    
def add_zone_ref_values(db):
    # select ref_joints from db (to get joint_id, side)
    curs = db.cursor()
    joints = curs.execute('SELECT * FROM joint_reference').fetchall()
    # `joints` is a list
    zones_to_add = []
    date = datetime.now().strftime("%Y-%m-%d")
    for joint in joints:
        joint_ref_id, date_updated, joint_name, side, joint_type, ref_pcapsule_ir_rom, ref_pcapsule_er_rom, ref_acapsule_ir_rom, ref_acapsule_er_rom = joint
        zone_ref_vals = [date, joint_ref_id, joint_name, side, ""]
        qmarks = ["?" for i in range(5)]
    # generate zones programatically into sql-ready format
    # --spine joints should generate 4 (flex, ext, r_rotate, l_rotate); this can map with the positionality); 
    # --HOWEVER zones with spine as joint-type should NOT be triplicated in tissue_status table
    # ---scapula should generate 4 (pro, re, elev, dep), 
    # -all other joints get 8
        if joint_type == "spinal":
            for z in ["flexion", "extension", "r_rotation", "l_rotation"]:
                spinal_joint_zone_ref_vals = zone_ref_vals.copy()
                spinal_joint_zone_ref_vals[4] = z
                zones_to_add.append(spinal_joint_zone_ref_vals)
        elif joint_type == "sesamoid":
            for z in ["retraction", "protraction", "elevation", "depression"]:
                sesamoid_joint_zone_ref_vals = zone_ref_vals.copy()
                sesamoid_joint_zone_ref_vals[4] = z
                zones_to_add.append(sesamoid_joint_zone_ref_vals)
        else:
            for z in ["flexion", "flex-abd", "abduction", "extend-abd", "extension", "extend-add", "adduction", "flex-add"]:
                synovial_joint_zone_ref_vals = zone_ref_vals.copy()
                synovial_joint_zone_ref_vals[4] = z
                zones_to_add.append(synovial_joint_zone_ref_vals)
    # executemany to "zone_reference", commit to db
    curs.executemany(f'INSERT INTO zones_reference (date_updated, joint_id, joint_name, side, zname) VALUES ({",".join(qmarks)})', 
        zones_to_add)
    db.commit()
    print("added the ZONE reference values!")

if __name__=="__main__":
    db = sqlite3.connect('/Users/williamhbelew/Hacking/MSWN/instance/mswnapp.sqlite')
    build_joint_ref_vals(db)