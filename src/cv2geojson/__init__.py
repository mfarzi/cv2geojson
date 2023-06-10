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
import math


class GeoContour:
    """
    A class to accommodate working with contours extracted using opencv.findContours and geometries defined using
    geojson python package.

    Attributes:
        - contours (numpy.ndarray): the coordinates of the geometry
        - type (str): the geometry of interest, e.g., Point, LineString, or Polygon

    Methods:
        - export_geometry: return the geometry using geojson format
        - export_feature: return the geometry as a feature object using geojson format
        - scale_up: return a new GeoContour instance with new_coords = old_coords * ratio + offset
        - scale_down: return a new GeoContour instance with new_coords = (old_coords - offset) / ratio
        - area: return the contour area
        - min_enclosing_circle: similar to cv.minEnclosingCircle
        - circularity: return the circularity of a polygon defined as (math.pi * 4 * area) / perimeter ** 2
        - solidity: return the solidity of a polygon defined as area / convex_hull_area
        - aspect_ratio: return the aspect ratio of the polygon between 0 and 1
        - holes_num: return the number of holes in a polygon
    """

    def __init__(self, contours=None, geometry=None):
        if contours is not None:
            self.contours = contours
            self.type = self._get_geometry_type(contours)

        elif geometry is not None:
            self.contours = self._geometry_to_contour(geometry)
            self.type = geometry['type']
        else:
            raise ValueError("Either contour or geometry must be provided.")

    def __repr__(self):
        return 'cv2geojson.GeoContour.{}'.format(self.type)

    @staticmethod
    def _get_geometry_type(contours):
        # define the geometry type
        area = cv.contourArea(contours[0])
        if len(contours) > 1 or area > 0:
            # this is a Polygon
            return 'Polygon'
        elif len(contours[0]) == 1:
            # this is a Point
            return 'Point'
        else:
            # this is a LineString
            return 'LineString'

    @staticmethod
    def _geometry_to_contour(geometry):
        # convert geometry to contours compatible with OpenCV
        if geometry['type'] == 'Polygon':
            contours = [np.array(coordinates[0:-1], dtype=np.int32) for coordinates in geometry['coordinates']]
        elif geometry['type'] == 'LineString':
            contours = [np.array(geometry['coordinates'], dtype=np.int32)]
        elif geometry['type'] == 'Point':
            contours = [np.array(geometry['coordinates'], dtype=np.int32)]
        else:
            raise ValueError('Input geometry must be either Polygon, LineString, or Point. Use cv2geojson.simplify to '
                             'brake complex geometries into basic compartments')
        return contours

    def export_geometry(self):
        # convert contour coordinates to geometry using geojson package
        if self.type == 'Polygon':
            coordinates = [contour.squeeze().tolist() for contour in self.contours]
            # each ring must end where it starts
            for coord in coordinates:
                coord.append(coord[0])
            geometry = geojson.Polygon(coordinates)
        elif self.type == 'Point':
            coordinates = self.contours[0].squeeze().tolist()
            geometry = geojson.Point(coordinates)
        elif self.type == 'LineString':
            coordinates = self.contours[0].squeeze().tolist()
            geometry = geojson.LineString(coordinates)
        else:
            raise ValueError('The object type must be either Point, LineString, or Polygon.')

        assert geometry.is_valid, f'Input geometry is not valid: {geometry.errors()}.'
        return geometry

    def export_feature(self, color=None, label=None, name=None):
        geometry = self.export_geometry()
        properties = {'object_type': 'annotation'}
        classification = {}
        if color is not None:
            classification['colorRGB'] = pack_rgb(color)
        if label is not None:
            classification['name'] = label
        if len(classification) > 0:
            properties['classification'] = classification
        if name is not None:
            properties['name'] = name
        feature = geojson.Feature(geometry=geometry, properties=properties)
        return feature

    def scale_down(self, ratio=1, offset=(0, 0)):
        # return a new GeoContour instance with the coordinates being downsampled
        contours = []
        for contour in self.contours:
            contour = np.ndarray.astype(np.round((contour - offset) / ratio), dtype=np.int32)
            contours.append(contour)
        # return scaled geocontour
        return GeoContour(contours=contours)

    def scale_up(self, ratio=1, offset=(0, 0)):
        # return a new GeoContour instance with the coordinates being upsampled
        contours = []
        for contour in self.contours:
            contour = np.ndarray.astype(np.round((contour * ratio) + offset), dtype=np.int32)
            contours.append(contour)
        # return scaled geocontour
        return GeoContour(contours=contours)

    def area(self, resolution=1.0):
        if self.type in ['Point', 'LineString']:
            return 0
        else:
            area_list = [cv.contourArea(contour) for contour in self.contours]
            area = area_list[0] - np.sum(area_list[1:])
            return area * resolution * resolution

    def min_enclosing_circle(self):
        center, radius = cv.minEnclosingCircle(self.contours[0])
        return center, radius

    def circularity(self):
        if self.type == 'Polygon':
            area = cv.contourArea(self.contours[0])
            perimeter = cv.arcLength(self.contours[0], closed=True)
            circularity = (math.pi * 4 * area) / perimeter ** 2
        else:
            circularity = 0
        return circularity

    def solidity(self):
        if self.type == 'Polygon':
            hull = cv.convexHull(self.contours[0])
            hull_area = cv.contourArea(hull)
            area = cv.contourArea(self.contours[0])
            solidity = float(area) / hull_area
        else:
            solidity = 0
        return solidity

    def aspect_ratio(self):
        if self.type == 'Polygon':
            rect = cv.minAreaRect(self.contours[0])
            rect_width = rect[1][0]
            rect_height = rect[1][1]
            if rect_width < rect_height:
                aspect_ratio = float(rect_width) / rect_height
            else:
                aspect_ratio = float(rect_height) / rect_width
        else:
            aspect_ratio = 0
        return aspect_ratio

    def elongation(self):
        moments = cv.moments(self.contours[0])
        x = moments['mu20'] + moments['mu02']
        y = np.sqrt(4 * moments['mu11']**2 + (moments['mu20'] - moments['mu02'])**2)
        elongation = (x - y) / (x + y)
        return elongation

    def holes_num(self):
        return len(self.contours) - 1

    def fill_hole(self, resolution=1, hole_size=None):
        # check if any holes exist
        if self.holes_num() > 0:
            if hole_size is None:
                # Remove all holes
                self.contours = [self.contours[0]]
            elif hole_size > 0:
                # all holes smaller than hole_size will be removed
                contours = [self.contours[0]]
                for hole in self.contours[1:]:
                    hole_area = cv.contourArea(hole) * resolution * resolution
                    if hole_area > hole_size:
                        contours.append(hole)
                # update the contours
                self.contours = contours
            # otherwise do nothing

    def copy(self):
        return GeoContour(contours=self.contours)

def simplify(obj):
    """
    Convert a geojson object to a list of geometries with types Polygon, Point, or LineString

    :param obj: A geojson object
    :return geometries: A list of geometries of type geojson.Point or geojson.Polygon, or geojson.LineString
    """
    assert obj.is_valid, f'Input geometry is not valid: {obj.errors()}.'
    if obj['type'] in ['Polygon', 'LineString', 'Point']:
        return obj

    if obj['type'] == 'MultiPolygon':
        geometries = [geojson.Polygon(coordinates) for coordinates in obj['coordinates']]
        return geometries

    if obj['type'] == 'MultiPoint':
        geometries = [geojson.Point(coordinates) for coordinates in obj['coordinates']]
        return geometries

    if obj['type'] == 'MultiLineString':
        geometries = [geojson.LineString(coordinates) for coordinates in obj['coordinates']]
        return geometries

    if obj['type'] == 'GeometryCollection':
        geometries = []
        for geometry in obj['geometries']:
            g = simplify(geometry)
            if type(g) == list:
                geometries.extend(g)
            else:
                geometries.append(g)
        return geometries

    if obj['type'] == 'Feature':
        return simplify(obj['geometry'])

    if obj['type'] == 'FeatureCollection':
        geometries = []
        for feature in obj['features']:
            g = simplify(feature['geometry'])
            if type(g) == list:
                geometries.extend(g)
            else:
                geometries.append(g)
        return geometries


def contour_to_geocontour(contours, hierarchy):
    """
    Convert contours extracted using cv.findCountours to cv2geojson.GeoContours
    """
    geocontours = []
    for index, contour in enumerate(contours):
        # Check if this contour has no parents
        if hierarchy[0, index, 3] == -1:
            cnt = [contour]
            # find children for this contour
            children = np.where(hierarchy[0, :, 3] == index)[0]
            for child in children:
                cnt.append(contours[child])
            geocontours.append(GeoContour(contours=cnt))

    return geocontours


def load_annotations(path_to_file):
    """
    return a list of geocontours from a geojson file
    """
    with open(path_to_file, 'r') as reader:
        annotations = geojson.load(reader)

    geometries = simplify(annotations)
    geocontours = [GeoContour(geometry=geometry) for geometry in geometries]
    return geocontours


def export_annotations(features, path_to_file):
    """
    Export features formatted by geojson python package
    :param features: a list of 'geojson.Feature' objects
    :param path_to_file:
    """
    # check the validity of the feature list
    for feature in features:
        assert feature.is_valid, f'Input feature is not valid: {feature.errors()}.'

    annotations = geojson.FeatureCollection(features=features)
    with open(path_to_file, 'w') as writer:
        geojson.dump(annotations, writer)


def find_geocontours(mask, mode='opencv'):
    """
    Return GeoContours from input binary mask
    :param mask: A numpy array of selected ROI [either 255 or 0]
    :param mode: either 'opencv' or 'imagej'

    :return geocontours:
    """
    if mode == 'opencv':
        contours, hierarchy = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
    elif mode == 'imagej':
        mask_upsampled = cv.resize(mask, dsize=(mask.shape[1]*2, mask.shape[0]*2), interpolation=cv.INTER_NEAREST)
        contours_upsampled, hierarchy = cv.findContours(mask_upsampled, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
        contours = []
        for contour in contours_upsampled:
            contour = np.ndarray.astype(np.round((contour + [0.5, 0.5]) / 2), dtype=np.int32)
            contours.append(contour)
    else:
        raise ValueError('Invalid value for mode:.must be either opencv or imagej')

    geocontours = contour_to_geocontour(contours, hierarchy)
    return geocontours


def draw_geocontours(mask, geocontours, mode='opencv'):
    """
    Draw geocontours into the mask and return a new binary mask
    """
    assert mode == 'opencv' or mode == 'imagej', 'Invalid value for mode:.must be either opencv or imagej'

    if mode == 'opencv':
        for geometry in geocontours:
            cv.drawContours(mask, geometry.contours, -1, 255, -1)
        return mask

    if mode == 'imagej':
        mask2 = cv.resize(mask, dsize=(mask.shape[1]*2, mask.shape[0]*2), interpolation=cv.INTER_NEAREST)
        for geometry in geocontours:
            contours = [np.ndarray.astype(np.round(cnt * 2 - [1, 1]), dtype=np.int32) for cnt in geometry.contours]
            cv.drawContours(mask2, contours, -1, 255, -1)
        mask = cv.resize(mask2, dsize=(mask.shape[1], mask.shape[0]), interpolation=cv.INTER_NEAREST)
        return mask


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


