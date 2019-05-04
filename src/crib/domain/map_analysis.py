import geopandas  # type: ignore
import numpy as np  # type: ignore
from scipy.spatial import Delaunay  # type: ignore
from shapely import geometry  # type: ignore
from shapely.ops import cascaded_union, polygonize  # type: ignore
from sklearn.cluster import DBSCAN  # type: ignore


def get_area(directions, eps=None, min_samples=None, leaf_size=None, alpha=None):
    eps = eps or 0.005
    min_samples = min_samples or 1
    leaf_size = leaf_size or 1
    alpha = alpha or 215

    directions = np.array(directions)

    clusters = get_clusters(
        directions, eps=eps, min_samples=min_samples, leaf_size=leaf_size
    )

    polys = [alpha_shape(m, alpha) for m in clusters]
    polys = [p for p in polys if p and p.geometryType() == "Polygon"]
    return geopandas.GeoSeries(polys).to_json()


def get_clusters(directions, *args, **kwargs):
    c = DBSCAN(*args, **kwargs).fit(directions)
    clusters = [directions[np.where(c.labels_ == i)] for i in np.unique(c.labels_)]
    return clusters


def alpha_shape(points, alpha):
    """
    Compute the alpha shape (concave hull) of a set
    of points.
    @param points: Iterable container of points.
    @param alpha: alpha value to influence the
        gooeyness of the border. Smaller numbers
        don't fall inward as much as larger numbers.
        Too large, and you lose everything!
    """
    if len(points) < 4:
        # When you have a triangle, there is no sense
        # in computing an alpha shape.
        return geometry.MultiPoint(list(points)).convex_hull
    coords = geometry.MultiPoint(points)

    tri = Delaunay(coords)
    triangles = points[tri.vertices]
    a = (
        (triangles[:, 0, 0] - triangles[:, 1, 0]) ** 2
        + (triangles[:, 0, 1] - triangles[:, 1, 1]) ** 2  # noqa: W503
    ) ** 0.5
    b = (
        (triangles[:, 1, 0] - triangles[:, 2, 0]) ** 2
        + (triangles[:, 1, 1] - triangles[:, 2, 1]) ** 2  # noqa: W503
    ) ** 0.5
    c = (
        (triangles[:, 2, 0] - triangles[:, 0, 0]) ** 2
        + (triangles[:, 2, 1] - triangles[:, 0, 1]) ** 2  # noqa: W503
    ) ** 0.5
    s = (a + b + c) / 2.0
    areas = (s * (s - a) * (s - b) * (s - c)) ** 0.5
    circums = a * b * c / (4.0 * areas)
    filtered = triangles[circums < (1.0 / alpha)]
    edge1 = filtered[:, (0, 1)]
    edge2 = filtered[:, (1, 2)]
    edge3 = filtered[:, (2, 0)]
    concat = np.concatenate((edge1, edge2, edge3))
    if len(concat):
        edge_points = np.unique(concat, axis=0).tolist()
        m = geometry.MultiLineString(edge_points)
        triangles = list(polygonize(m))
        return cascaded_union(triangles)
