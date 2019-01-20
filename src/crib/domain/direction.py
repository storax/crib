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


class Direction(Model):
    schema: Dict[str, Dict[str, Union[str, bool, Dict]]] = {
        "overview_polyline": _polyline,
        "duration": _duration,
        "steps": vlist(
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
                        "line": vdict(
                            {
                                "vehicle": vdict(
                                    {"type": vstr(), "name": vstr(), "icon": vstr()}
                                ),
                                "text_color": vstr(),
                                "short_name": vstr(),
                                "color": vstr(),
                            }
                        ),
                    },
                    False,
                ),
            }
        ),
    }
