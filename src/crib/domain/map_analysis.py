import math

import geopandas  # type: ignore
import numpy as np  # type: ignore
from scipy.spatial import Delaunay  # type: ignore
from shapely import geometry  # type: ignore
from shapely.ops import polygonize, unary_union  # type: ignore


def get_area(directions, alpha=None, hullbuffer=None):
    if not directions:
        return None

    alpha = alpha or 450

    if hullbuffer is None:
        hullbuffer = 0.0014

    directions = np.array(directions)

    polys = alpha_shape(directions, alpha)
    polys = unary_union([p.buffer(hullbuffer) for p in polys])
    return geopandas.GeoSeries(polys).to_json()


def alpha_shape(points, alpha):
    """Compute the alpha shape (concave hull) of a set of points.

    Credits: http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/

    Args:
        points: Iterable container of coordinate pairs.
        alpha: The higher the value, the less big areas between points are
        allowed.
    """
    if len(points) < 4:
        # When you have a triangle, there is no sense
        # in computing an alpha shape.
        return geometry.MultiPoint(list(points)).convex_hull

    def add_edge(edges, edge_points, coords, i, j):
        """
        Add a line between the i-th and j-th points,
        if not in the list already
        """
        if (i, j) in edges or (j, i) in edges:
            # already added
            return
        edges.add((i, j))
        edge_points.append(coords[[i, j]])

    coords = points
    tri = Delaunay(coords)
    edges = set()
    edge_points = []
    # loop over triangles:
    # ia, ib, ic = indices of corner points of the
    # triangle
    for ia, ib, ic in tri.vertices:
        pa = coords[ia]
        pb = coords[ib]
        pc = coords[ic]
        # Lengths of sides of triangle
        a = math.sqrt((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2)
        b = math.sqrt((pb[0] - pc[0]) ** 2 + (pb[1] - pc[1]) ** 2)
        c = math.sqrt((pc[0] - pa[0]) ** 2 + (pc[1] - pa[1]) ** 2)
        # Semiperimeter of triangle
        s = (a + b + c) / 2.0
        # Area of triangle by Heron's formula
        area = math.sqrt(s * (s - a) * (s - b) * (s - c))
        circum_r = a * b * c / (4.0 * area)
        # Here's the radius filter.
        if circum_r < 1.0 / alpha:
            add_edge(edges, edge_points, coords, ia, ib)
            add_edge(edges, edge_points, coords, ib, ic)
            add_edge(edges, edge_points, coords, ic, ia)
    m = geometry.MultiLineString(edge_points)
    triangles = list(polygonize(m))
    return unary_union(triangles)
