import numpy as np

# first, I need to have (input):
# - joint
# - zone
# - start_position
# - end_position
# - date-timestamp,
# - impact (divided_duration, rpe, load)

def get_tissue(tissue_type, anchor, moverid):
    # needs to do SQL select of adj of type tissue_type, at anchor, from specified mover
    # return the tissue_id
    pass

# these functions recieve a gesture object (unidirectional, can't cross 0!) of following format:
# {   "date": <date-timestamp>,
#     "fixed_side_capsule_anchor": <anchor_id>,
#     "start_position": <either rot_rom% or linear_rom%>,
#     "end_position": <either rot_rom% or linear_rom%; can be NULL>,
#     "duration": <sec, this is often the result of a division of the entire given duration>,
#     "load": <from mover input>,
#     "rpe": <from mover input>
# }
# these two functions return tuples:
# (tissue_id,
# [MUSCULAR np array of 4 vals, plus direction?], [position, duration, rpe, load]
# [CT np array of 4 vals, plus direction?]
# )

def joint_rotation(bout_obj): 
    ## is there a better way to unpack a dictionary?
    fixed_side_capsule_anchor = bout_obj["fixed_side_capsule_anchor"]
    start_position = bout_obj["start_position"] #in format of -deg/+deg
    end_position = bout_obj["end_position"] # if iso, this should be same as start_pos
    moverid = bout_obj["moverid"]
    input_type = ""
    rotation_difference = end_position - start_position
    if rotation_difference == 0:
        input_type = "isometric"
    elif abs(end_position) > abs(start_position):
        input_type = "eccentric"
    else:
        input_type = "concentric"
    if input_type == "isometric":
        # capsular tissue impacted (ct)
        capsule_tissue_id = get_tissue("capsule", fixed_side_capsule_anchor, moverid) # this gives me the TISSUE that flows out of that attachment!
        capsular_training_array = [start_position, ]
        # rotational tissue impacted (musc)

    musc_array = np.array()
    ct_array = np.array()
        



def joint_fe():
    pass

# then I need to compile arrays of these and pass to fncs that will write to bout_log and to the specific adjacencies

def write_to_bout_log(gesture_array):
    pass

def write_to_tissue_status(gesture_array):
    pass