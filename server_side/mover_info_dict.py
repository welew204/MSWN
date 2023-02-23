from collections import defaultdict


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
