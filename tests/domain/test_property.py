"""Tests for the property model.
"""
import attr
import pytest  # type: ignore

from crib.domain import Property


@pytest.fixture(scope="session")
def property_full():
    from .resources.property_full import data

    return data


@pytest.fixture(scope="session")
def property_minimal():
    from .resources.property_minimal import data, initialized

    return data, initialized


def test_round_trip_full(property_full):
    """Test roundtrip serialization with all attributes."""
    prop = Property.fromdict(property_full)
    result = prop.asdict()
    assert result == property_full


def test_frozen(property_full):
    """Test Property object is frozen."""
    prop = Property.fromdict(property_full)
    with pytest.raises(attr.exceptions.FrozenInstanceError):
        prop.price = "foo"


def test_round_trip_minimal(property_minimal):
    """Test that defaults are initialized."""
    data, initialized = property_minimal
    prop = Property.fromdict(data)
    result = prop.asdict()
    assert result == initialized
