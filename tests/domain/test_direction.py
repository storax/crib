"""Tests for the direction model.
"""
import json
import pathlib

import attr
import pytest

from crib.domain import Direction


@pytest.fixture(scope="session")
def directions_full():
    from .resources.direction_full import data

    return data


@pytest.fixture(scope="session")
def directions_minimal():
    from .resources.direction_minimal import data, initialized

    return data, initialized


def test_round_trip_full(directions_full):
    """Test roundtrip serialization with all attributes."""
    direction = Direction.fromdict(directions_full)
    result = direction.asdict()
    assert result == directions_full


def test_frozen(directions_full):
    """Test direction object is frozen."""
    direction = Direction.fromdict(directions_full)
    with pytest.raises(attr.exceptions.FrozenInstanceError):
        direction.duration = "foo"


def test_round_trip_minimal(directions_minimal):
    """Test that defaults are initialized."""
    data, initialized = directions_minimal
    direction = Direction.fromdict(data)
    result = direction.asdict()
    assert result == initialized
