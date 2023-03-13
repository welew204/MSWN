from ..workout_recorder import unpack_workout, unpack_inputs, prep_bouts_for_insertion, workout_recorder
import pytest

# should I use simulate_workout to generate these?
# if so, should I write tests for that first?

# Seems that a major outcome of these tests will be
# to ADD raiseError to


# input, output tuples
unpack_workout_test_results = [("1989/4/20", 34),
                               ("1991/8/3", 32),
                               ("1981/4/18", 42),
                               ("1954/1/11", 69)]

# I want to test:
# - incoming workout request has moverid, workout_id, date_done in valid
#   formats
#


# @pytest.mark.parametrize("test_input, expected_output", unpack_workout_test_results)
def test_unpack_workout():
    pass
