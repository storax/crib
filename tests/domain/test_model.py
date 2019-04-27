"""Test basic model functionality."""
from datetime import datetime

import attr
import pytest  # type: ignore

from crib import exceptions
from crib.domain import model


@attr.s
class Component:
    string: str = attr.ib()
    floating: float = attr.ib()


@attr.s
class SomeModel(model.Model):
    dt: datetime = attr.ib()
    integer: int = attr.ib()
    component: Component = attr.ib()


@pytest.fixture
def dt():
    return datetime.now()


@pytest.fixture
def testdata(dt):
    data = {"dt": dt, "integer": 42, "component": {"string": "test", "floating": 0.12}}
    return data


@pytest.fixture
def testmodel(testdata):
    return SomeModel.fromdict(testdata)


def test_fromdict(testmodel, dt):
    """Test creating a model from unstructured data."""
    assert testmodel.dt == dt
    assert testmodel.integer == 42
    assert testmodel.component.string == "test"
    assert pytest.approx(0.12, 0.001) == testmodel.component.floating


def test_fromdict_validation(testdata):
    """Test creating a model from unstructured data."""
    testdata["integer"] = "asdfasdf"
    with pytest.raises(exceptions.InvalidData) as ctx:
        SomeModel.fromdict(testdata)

    assert ctx.value.args == (
        "Invalid data",
        {"unknown": "invalid literal for int() with base 10: 'asdfasdf'"},
    )


def test_asdict(testmodel, testdata):
    """Test converting a model to a dictionary."""
    result = testmodel.asdict()

    assert result == testdata


def test_replace(testmodel):
    new = testmodel.replace(integer=43)
    assert new is not testmodel
    assert new.integer == 43
    assert testmodel.integer == 42
