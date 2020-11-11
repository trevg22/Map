#Map Viewer
# helpers.py
#contains helper functions not specific to a class
import random
import math
import matplotlib.pyplot as plt
import numpy as np
from descartes import PolygonPatch
from scipy.spatial import Voronoi
from shapely.geometry import Polygon

# return a random rgba list
def random_color(as_str=False, alpha=0.5):
    rgb = [random.randint(0, 255),
           random.randint(0, 255),
           random.randint(0, 255)]
    if as_str:
        return "rgba"+str(tuple(rgb+[alpha]))
    else:
        # Normalize & listify
        return list(np.array(rgb)/255) + [alpha]

# take scipy vor and bound infinite regions
def voronoi_finite_polygons_2d(vor, radius=None):

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()*2

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1]  # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)

# make up data points
# compute Voronoi tesselation

# return voronoi cell bounded by boundpoints
def get_vorPolys(vorPoints, boundPoints):
    vor = Voronoi(vorPoints)

    min_x = vor.min_bound[0] - 0.1
    max_x = vor.max_bound[0] + 0.1
    min_y = vor.min_bound[1] - 0.1
    max_y = vor.max_bound[1] + 0.1
    boundPoly = Polygon([p[0], p[1]] for p in boundPoints)

    # if no bounPoints draw rectantle as bounding polygon
    if not boundPoints:
        boundPoly = Polygon([[min_x, min_y], [max_x, min_y], [
                            max_x, max_y], [min_x, max_y]])

    regions, vertices = voronoi_finite_polygons_2d(vor)

    polygons = []

    for region in regions:
        polygon = vertices[region]
        # Clipping polygon
        poly = Polygon(polygon)
        if poly.intersects(boundPoly):
            poly = poly.intersection(boundPoly)
        polygons.append(poly)

    return polygons, boundPoly

def wgs84_toMercator(lon,lat):
    x=lon
    radLat=(lat/360)*2*math.pi
    y=math.tan(radLat)

    return (x,y)

def wgs84_toMercater_coords(coords):

    return [wgs84_toMercator(coord[0],coord[1]) for coord in coords]

def wgs84_toMercater_poly(poly):
    x,y=poly.exterior.coords.xy
    coords=zip(x,y)
    merc_coords=[wgs84_toMercator(coord[0],coord[1]) for coord in tuple(coords)]
    return Polygon(merc_coords)

def convPolygs84_toMerc(polygons):
        
    return [wgs84_toMercater_poly(poly) for poly in polygons]

def wgs84_toCart_coords(lon,lat):
        r=6371 #km
        c=2*math.pi*r
        x = lon*c/360
        y=lat*c/180
        return(x,y)

def wgs84_toCartesion_poly(poly):

    x,y=poly.exterior.coords.xy
    coords=zip(x,y)
    cart_coords=[wgs84_toCart_coords(coord[0],coord[1]) for coord in tuple(coords)]
    return Polygon(cart_coords)


def convPolygons84_toCart(polygons):
    return [wgs84_toCartesion_poly(poly) for poly in polygons]

def get_area_wgs84(poly):
    areaPoly=wgs84_toCartesion_poly(poly)
    return areaPoly.area # area in km^2

def moveCoords(lon_offset,lat_offset,coords):
    
    for coord in coords:
        newLon=coord[0]+lon_offset

        if newLon>180:
            newLon=newLon-360

        elif newLon <-180:
            newLon=newLon+360


        coord[0]=newLon
        # coord[0]=coord[0]+lon_offset
        coord[1]=coord[1]+lat_offset