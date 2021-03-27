"""
Direction model
"""
from typing import Dict, Optional, Tuple

import attr

from .model import Model


@attr.s(frozen=True)
class Location:
    latitude: float = attr.ib()
    longitude: float = attr.ib()


@attr.s(frozen=True)
class Polyline:
    points: str = attr.ib()


@attr.s(frozen=True)
class Distance:
    value: str = attr.ib()
    text: str = attr.ib()


@attr.s(frozen=True)
class Duration:
    value: int = attr.ib()
    text: str = attr.ib()


@attr.s(frozen=True)
class LatLng:
    lat: float = attr.ib()
    lng: float = attr.ib()


@attr.s(frozen=True)
class Time:
    text: str = attr.ib()
    time_zone: str = attr.ib()
    value: int = attr.ib()


@attr.s(frozen=True)
class Stop:
    location: LatLng = attr.ib()
    name: str = attr.ib()


@attr.s(frozen=True)
class Vehicle:
    type: str = attr.ib()
    name: str = attr.ib()
    icon: str = attr.ib()
    local_icon: Optional[str] = attr.ib(default=None)


@attr.s(frozen=True)
class Line:
    vehicle: Vehicle = attr.ib()
    url: Optional[str] = attr.ib(default=None)
    name: Optional[str] = attr.ib(default=None)
    text_color: Optional[str] = attr.ib(default=None)
    short_name: Optional[str] = attr.ib(default=None)
    color: Optional[str] = attr.ib(default=None)
    agencies: Tuple[Dict, ...] = attr.ib(default=())


@attr.s(frozen=True)
class TransitDetails:
    num_stops: int = attr.ib()
    headsign: str = attr.ib()
    line: Line = attr.ib()
    arrival_stop: Optional[Stop] = attr.ib(default=None)
    arrival_time: Optional[Time] = attr.ib(default=None)
    departure_stop: Optional[Stop] = attr.ib(default=None)
    departure_time: Optional[Time] = attr.ib(default=None)


@attr.s(frozen=True)
class Step:
    html_instructions: str = attr.ib()
    polyline: Polyline = attr.ib()
    travel_mode: str = attr.ib()
    start_location: LatLng = attr.ib()
    end_location: LatLng = attr.ib()
    duration: Duration = attr.ib()
    distance: Distance = attr.ib()
    transit_details: Optional[TransitDetails] = attr.ib(default=None)
    steps: Tuple[Dict, ...] = attr.ib(default=())


@attr.s(frozen=True)
class Direction(Model):
    overview_polyline: Polyline = attr.ib()
    duration: Duration = attr.ib()
    distance: Distance = attr.ib()
    end_address: str = attr.ib()
    end_location: LatLng = attr.ib()
    start_address: str = attr.ib()
    start_location: LatLng = attr.ib()
    steps: Tuple[Step, ...] = attr.ib()
    arrival_time: Optional[Time] = attr.ib(default=None)
    departure_time: Optional[Time] = attr.ib(default=None)
    via_waypoint: Tuple = attr.ib(default=())
    traffic_speed_entry: Tuple = attr.ib(default=())
