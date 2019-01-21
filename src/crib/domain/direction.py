"""
Direction model
"""

from typing import Dict, Union

from crib.domain.model import Model
from crib.validation import vdict, vfloat, vint, vlist, vstr

_polyline = vdict({"points": vstr()})
_distance = _duration = vdict({"value": vint(), "text": vstr()})
_latlng = vdict({"lat": vfloat(), "lng": vfloat()})
_location = vdict({"latitude": vfloat(), "longitude": vfloat()})
_time = vdict({"text": vstr(), "time_zone": vstr(), "value": vint()})


class Direction(Model):
    schema: Dict[str, Dict[str, Union[str, bool, Dict]]] = {
        "overview_polyline": _polyline,
        "duration": _duration,
        "distance": _distance,
        "arrival_time": _time,
        "departure_time": _time,
        "end_address": vstr(),
        "end_location": _latlng,
        "start_address": vstr(),
        "via_waypoint": {"type": "list", "required": True},
        "traffic_speed_entry": {"type": "list", "required": True},
        "start_location": _latlng,
        "steps": vlist(
            vdict(
                {
                    "html_instructions": vstr(),
                    "polyline": _polyline,
                    "travel_mode": vstr(),
                    "start_location": _latlng,
                    "end_location": _latlng,
                    "duration": _duration,
                    "distance": _distance,
                    "transit_details": vdict(
                        {
                            "num_stops": vint(),
                            "arrival_stop": vdict(
                                {"location": _latlng, "name": vstr()}, False
                            ),
                            "arrival_time": _time,
                            "departure_time": _time,
                            "departure_stop": vdict(
                                {"location": _latlng, "name": vstr()}, False
                            ),
                            "headsign": vstr(),
                            "line": vdict(
                                {
                                    "vehicle": vdict(
                                        {
                                            "type": vstr(),
                                            "name": vstr(),
                                            "icon": vstr(),
                                            "local_icon": vstr(0),
                                        }
                                    ),
                                    "url": vstr(0),
                                    "name": vstr(0),
                                    "text_color": vstr(),
                                    "short_name": vstr(),
                                    "color": vstr(),
                                    "agencies": vlist({"type": "dict"}),
                                }
                            ),
                        },
                        False,
                    ),
                    "steps": vlist({"type": "dict"}, False),
                },
                False,
            )
        ),
    }
