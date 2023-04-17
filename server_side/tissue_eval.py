import sqlite3
from pprint import pprint
from scipy.spatial import ConvexHull

'''this handles "strength" and "health" assessments of tissues (based on bout logs)'''


def calc_CH_vals(coords_array):
    hull = ConvexHull(coords_array)
    vol = hull.volume
    density = (len(coords_array))/vol
    return vol, density


def strength_cloud_dict(db, moverid):
    '''this processes all bouts into a series of points in 4D vector-space, 
    calculates the volume and density of this cloud space 
    and outputs a dictionary of results (keyed by joint_id)'''
    result = {}
    curs = db.cursor()
    all_bouts = curs.execute('''SELECT 
                            joint_id,
                            rotational_value,
                            joint_motion,
                            start_coord,
                            end_coord,
                            capsular_tissue_id, 
                            rotational_tissue_id,
                            linear_tissue_id, 
                            duration,
                            rpe,
                            external_load,
                            tissue_type
                            FROM bout_log 
                            WHERE moverid = (?)''', (moverid,)).fetchall()
    for row in all_bouts:
        tissue_id_to_add = None
        if row["tissue_type"] == "capsular":
            tissue_id_to_add = row["capsular_tissue_id"]
        elif row["tissue_type"] == "linear":
            tissue_id_to_add = row["linear_tissue_id"]
        else:
            tissue_id_to_add = row["rotational_tissue_id"]

        if row["joint_id"] not in result.keys():
            result[row["joint_id"]] = {}
        if tissue_id_to_add not in result[row["joint_id"]]:
            result[row["joint_id"]][tissue_id_to_add] = []

        point = (row["duration"], row["rpe"], row["external_load"],
                 row["start_coord"], row["end_coord"])
        result[row["joint_id"]][tissue_id_to_add].append(point)

    for joint in result:
        for tissue_id, points in result[joint].items():
            ch_volume, ch_density = calc_CH_vals(points)
            result[joint][tissue_id] = {
                "ch_volume": ch_volume, "ch_density": ch_density}
    pprint(result)


if __name__ == "__main__":
    db = sqlite3.connect(
        '/Users/williamhbelew/Hacking/MSWN/instance/mswnapp.sqlite')
    db.row_factory = sqlite3.Row
    strength_cloud_dict(db, 1)
