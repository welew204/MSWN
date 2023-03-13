import pytest
from .testing_sandbox import get_age


@pytest.mark.skip(reason="this is literally a test of pytest, so....")
@pytest.mark.parametrize("test_input, expected_output", [("1989/4/20", 34), ("1991/8/3", 32), ("1981/4/18", 42), ("1954/1/11", 69)])
def test_get_age(test_input, expected_output):
    # given...
    yyyy, mm, dd = map(int, test_input.split("/"))
    # ... when ...
    age = get_age(yyyy, mm, dd)
    # ... then ...
    assert age == expected_output
