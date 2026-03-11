import pytest
from pureenv import Env


def test_str_returns_value():
    env = Env(environ={"NAME": "alice"})
    assert env.str("NAME") == "alice"

def test_str_returns_default():
    env = Env(environ={})
    assert env.str("MISSING", default="fallback") == "fallback"

def test_str_returns_none_when_no_default():
    env = Env(environ={})
    assert env.str("MISSING") is None

def test_str_raises_when_required():
    env = Env(environ={})

    with pytest.raises(ValueError, match="MISSING"):
        env.str("MISSING", required=True)


def test_int_returns_value():
    env = Env(environ={"PORT": "8080"})
    assert env.int("PORT") == 8080

def test_int_returns_default():
    env = Env(environ={})
    assert env.int("MISSING", default=3306) == 3306

def test_int_raises_on_invalid_value():
    env = Env(environ={"PORT": "not_a_number"})

    with pytest.raises(ValueError, match="PORT"):
        env.int("PORT")

def test_int_raises_when_required():
    env = Env(environ={})

    with pytest.raises(ValueError, match="PORT"):
        env.int("PORT", required=True)

def test_float_returns_value():
    env = Env(environ={"PI": "3.14"})
    assert env.float("PI") == 3.14

def test_float_returns_default():
    env = Env(environ={})
    assert env.float("MISSING", default=3.14) == 3.14

def test_float_raises_on_invalid_value():
    env = Env(environ={"PI": "not_a_number"})

    with pytest.raises(ValueError, match="PI"):
        env.float("PI")

def test_float_raises_when_required():
    env = Env(environ={})

    with pytest.raises(ValueError, match="PI"):
        env.float("PI", required=True)


@pytest.mark.parametrize("value", ("true", "1", "yes", "y", "on"))
def test_bool_truthy_values(value):
    env = Env(environ={"DEBUG": value})
    assert env.bool("DEBUG") is True

@pytest.mark.parametrize("value", ("false", "0", "no", "n", "off"))
def test_bool_falsy_values(value):
    env = Env(environ={"DEBUG": value})
    assert env.bool("DEBUG") is False

def test_bool_returns_default():
    env = Env(environ={})
    assert env.bool("MISSING", default=False) is False

def test_bool_raises_on_invalid_value():
    env = Env(environ={"DEBUG": "maybe"})

    with pytest.raises(ValueError, match="DEBUG"):
        env.bool("DEBUG")

def test_bool_raises_when_required():
    env = Env(environ={})

    with pytest.raises(ValueError, match="MISSING"):
        env.bool("MISSING", required=True)