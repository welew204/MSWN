from ..workout_recorder import unpack_workout, unpack_inputs, prep_bouts_for_insertion, workout_recorder
from ..mover_info_dict import mover_info_dict
import pytest
import json
import sqlite3
from pprint import pprint

# should I use simulate_workout to generate these?
# if so, should I write tests for that first?

# Seems that a major outcome of these tests will be
# to ADD raiseError to source code....?
with open('/Users/williamhbelew/Hacking/MSWN/server_side/tests/record_tests.json') as json_workouts:
    tester_records = json.load(json_workouts)
with open('/Users/williamhbelew/Hacking/MSWN/server_side/test_outputs.json') as json_OUTPUTs:
    tester_outputs = json.load(json_OUTPUTs)

db_to_look_at = db = sqlite3.connect(
    '/Users/williamhbelew/Hacking/MSWN/instance/mswnapp.sqlite')
tester_dict = mover_info_dict(db_to_look_at, 1)


# input, output tuples
unpack_workout_test_results = [
    # moverid, workout_id, date_done
    # each of these test records are from the same workout (id: 1)
    (tester_records[0], ("1", "8", "2023-03-29T21:57:19.336Z")),
    (tester_records[1], ("1", "8", "2023-03-29T21:57:19.336Z")),
    (tester_records[2], ("1", "8", "2023-03-29T21:57:19.336Z")),
]

# I want to test:
# - incoming workout request has moverid, workout_id, date_done in valid
#   formats
# -


@pytest.mark.parametrize("test_input, expected_output", unpack_workout_test_results)
def test_unpack_workout(test_input, expected_output):
    # given... test_input is already looking like a 'req'
    # ... when ...
    moverid, workout_id, date_done = unpack_workout(test_input)
    # ...then...
    assert moverid == expected_output[0]
    assert workout_id == expected_output[1]
    assert date_done == expected_output[2]

    moverid, workout_id, date_done = unpack_workout_test_results


def test_bout_dict_maker() -> None:
    pass
    # NOT doign this now.
    # if given the wrong number of args
    # if date is wrong format
    # if joint motion is NOT one of the three types
    # if tissue_type is NOT one of the three types


def test_unpack_inputs_CARs() -> None:
    # this is to grab an instance of PREPACKED bouts (results)
    inputs = tester_outputs["unpack_inputs"]
    cars_input = inputs["1"]
    first_date = list(cars_input.keys())
    # this is the actual list of bouts to compare...
    cars_bouts_to_test = cars_input[first_date[0]]

    # this generates a list of NEW results to test against the `cars_bouts_to_test`
    testing = unpack_inputs(
        tester_records[0].items(), tester_dict, "2023-04-10T14:44:34.417Z", 1)

    for n, i in enumerate(cars_bouts_to_test):

        assert i["moverid"] == testing[n]["moverid"]
        assert i["joint_id"] == testing[n]["joint_id"]
        assert i["programmed_drills_id"] == testing[n]["programmed_drills_id"]
        assert i["rotational_value"] == testing[n]["rotational_value"]
        assert i["fixed_side_anchor_id"] == testing[n]["fixed_side_anchor_id"]
        assert i["joint_motion"] == testing[n]["joint_motion"]
        assert i["start_coord"] == testing[n]["start_coord"]
        assert i["end_coord"] == testing[n]["end_coord"]
        assert i["passive_duration"] == testing[n]["passive_duration"]
        assert i["duration"] == testing[n]["duration"]
        assert i["rpe"] == testing[n]["rpe"]
        assert i["external_load"] == testing[n]["external_load"]
        assert i["tissue_type"] == testing[n]["tissue_type"]
        assert i["capsular_tissue_id"] == testing[n]["capsular_tissue_id"]
        assert i["rotational_tissue_id"] == testing[n]["rotational_tissue_id"]
        assert i["linear_tissue_id"] == testing[n]["linear_tissue_id"]

    pass
    # a test for top-level conditional --> a test for each branch of conditional
    # seperate tests for each case
    # --> points at needing to refactor the case-switcher component of unpack
