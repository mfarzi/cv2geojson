"""cv2geojson
This module includes helper functions to convert contours estimated using OpenCV python package into geometries
supported by geojson python package.
"""

__author__ = "Mohsen Farzi"
__email__ = "mhnfarzi@gmail.com"
__status__ = "planning"

import cv2 as cv
import geojson
import numpy as np


def geometry2feature(geometry, label=None, color=(255, 0, 0), id=None):
    assert geometry.is_valid, f'Input geometry is not valid: {geometry.errors()}.'
    # set properties
    classification = {"name": label, "colorRGB": pack_rgb(color)}
    properties = {'object_type': 'annotation', 'isLocked': False, "classification": classification}
    feature = geojson.Feature(geometry=geometry)
    return feature


def feature2polygon(feature):
    assert feature.is_valid and feature['type'] == 'Feature', 'Input feature is not a valid geojson object.'
    polygons = []
    if feature['geometry']['type'] == 'Polygon':
        polygons.append(feature['geometry'])
    elif feature['geometry']['type'] == 'MultiPolygon':
        # split it into different polygons
        for coordinates in feature['geometry']['coordinates']:
            polygon = geojson.Polygon(coordinates)
            polygons.append(polygon)
    else:
        raise ValueError(f"Unsupported geometry {feature['geometry']['type']}. Only Polygon or MultiPolygon is "
                         f"supported.")
    return polygons


def pack_rgb(color):
    r, g, b = color
    value = (0xff << 24) + ((r & 0xff) << 16) + ((g & 0xff) << 8) + (b & 0xff)
    return value - 4294967296


def get_rgb(value):
    value += 4294967296
    value -= (0xff << 24)
    b = value % 256
    value -= b
    value = int(value / 256)
    g = value % 256
    value -= g
    r = int(value / 256)
    return r, g, b


def contour2geometry(contours, hierarchy):
    geometries = []
    for counter, contour in enumerate(contours):
        # Check if this contour has no parents
        if hierarchy[0, counter, 3] >= 0:
            continue

        # Determine the geometry type: point, linestring, or polygon
        area = cv.contourArea(contour)
        if len(contour) == 1:
            # This contour is a single point
            geometry = contour2point(contour)
        elif area == 0:
            # This contour is a line string
            geometry = contour2linestring(contour)
        else:
            # This is a polygon
            # Check if any holes exist
            child_index = hierarchy[0, counter, 2]
            holes = []
            while child_index >= 0:
                this_hole = contours[child_index]
                holes.append(this_hole)
                child_index = hierarchy[0, child_index, 0]
            geometry = contour2polygon(contour, holes)
        geometries.append(geometry)
    return geometries


def geometry2contour(geometries):
    contours = []
    for geometry in geometries:
        assert geometry.is_valid, f'Input geometry is not valid: {geometry.errors()}.'
        if geometry['type'] == 'Point':
            contour = [np.array([geometry['coordinates']], dtype=np.int32)]
        elif geometry['type'] == 'LineString':
            contour = [np.array(geometry['coordinates'], dtype=np.int32)]
        else:
            contour = polygon2contour(geometry)
        contours.extend(contour)
    return contours


def contour2polygon(contour, holes=None):
    # check if each point is repeated only once
    polygon_coord = contour.squeeze().tolist()
    # each ring must end where it starts
    polygon_coord.append(polygon_coord[0])
    coordinates = [polygon_coord]
    if holes is not None:
        for hole in holes:
            hole_coord = hole.squeeze().tolist()
            # each ring must end where it starts
            hole_coord.append(hole_coord[0])
            coordinates.append(hole_coord)

    geometry = geojson.Polygon(coordinates)
    return geometry


def contour2linestring(contour):
    coordinates = contour.squeeze().tolist()
    geometry = geojson.LineString(coordinates)
    return geometry


def contour2point(contour):
    coordinates = contour.squeeze().tolist()
    geometry = geojson.Point(coordinates)
    return geometry


def polygon2contour(geometry):
    assert geometry.is_valid and geometry['type'] == 'Polygon'
    contours = [np.array(geometry['coordinates'][0][0:-1], dtype=np.int32)]
    for i in range(1, len(geometry['coordinates'])):
        contours.append(np.array(geometry['coordinates'][i][0:-1], dtype=np.int32))
    return contours




