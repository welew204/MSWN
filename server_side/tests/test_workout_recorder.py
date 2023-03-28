from ..workout_recorder import unpack_workout, unpack_inputs, prep_bouts_for_insertion, workout_recorder
import pytest
import json
from pprint import pprint

# should I use simulate_workout to generate these?
# if so, should I write tests for that first?

# Seems that a major outcome of these tests will be
# to ADD raiseError to source code....?
with open('/Users/williamhbelew/Hacking/MSWN/server_side/tests/record_tests.json') as json_workouts:
    tester_records = json.load(json_workouts)

# input, output tuples
unpack_workout_test_results = [
    # moverid, workout_id, date_done
    # each of these test records are from the same workout (id: 1)
    (tester_records[0], ("1", "1", "2023-03-13T21:27:32.025Z")),
    (tester_records[1], ("1", "1", "2023-03-13T21:27:32.025Z")),
    (tester_records[2], ("1", "1", "2023-03-13T21:27:32.025Z")),
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
    # if given the wrong number of args
    # if date is wrong format
    # if joint motion is NOT one of the three types
    # if tissue_type is NOT one of the three types
    pass
