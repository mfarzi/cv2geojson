# cv2geojson
cv2geojson is an open-source project to export annotation contours extracted using [OpenCV-python](https://github.com/opencv/opencv-python) package to [GeoJSON](https://pypi.org/project/geojson/) format.

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [class GeoContour](#class-geocontour)
  - [Attributes](#attributes)
    - [contours](#contours)
    - [type](#type)
  - [Methods](#methods)
    - [export_geometry](#export_geometryself)
    - [export_feature](#export_featureself-colornone-labelnone-namenone)
    - [area](#areaself-resolution1.0)
    - [min_enclosing_circle](#min_enclosing_circleself)
- [Examples](#examples)

## Introduction
In digital pathology, images are often quite large and dedicated software tools like [QuPath](https://qupath.github.io/) are required to aid visualisation. The python package cv2geojson export contours detected using `cv2.findContours` as polygons using GeoJSON format for visualisation in QuPath. For example, download the whole slide image with tissue sample ID _GTEX-12584-1526_ from [histology page](https://gtexportal.org/home/histologyPage). This image has 45,815x38,091 pixels which requires about 5GB of storage uncompressed. Rather than storing a binary mask for the foreground segmentation, the mask can be converted to polygons and stored as a geojson file. The image below shows a snapshot from the QuPath software. The foreground contour is blue.
<figure>
  <img src="https://github.com/mfarzi/cv2geojson/raw/main/example/GTEX-12584-1526-snapshot.png" alt="QuPath Snapshot 2" style="width:50%; margin-right:10px;" />
  <figcaption>Snapshot from QuPath software visualising foreground segmentation</figcaption>
</figure>

## Installation
The recommended way to install is via pip:

`pip install cv2geojson`

## class GeoContour
The libarary implements a new class `cv2geojson.GeoContour` to accommodate bridging between contours extracted using `cv2.findContours` and geometries defined as geojson objects. To initialise a class instance, either contours or geojson objects can be provided. Below, an example for initialsing the class with both a geojson object and numpy contours are provided.
```
import numpy as np
from geojson import LineString
from cv2geojson import GeoContour

# initialise GeoContour class with a geojson LineString object
geometry = LineString([(1, 2), (5, 15)])
geocontour_1 = GeoContour(geometry=geometry)

# initialise GeoContour class with contours
geocontour_2 = GeoContour(contours=[np.array([[1, 2], [5, 15]])]) 
```

### Attributes:

#### <code>contours</code> 
list of numpy.ndarray: the coordinates of the geometry

#### <code>type</code>
str: Point, LineString, or Polygon

### Methods:
#### <code>export_geometry(self)</code>
- Returns
  - geometry: {geojson.Point, geojson.LineString, geojson.Polgyon}

#### <code>export_feature(self, color=None, label=None, name=None)</code>
- Parameters:
  - color: {tuple: 3}: (r, g, b) in range 0 to 255
  - label: {str}: the class name for the identified geometry
  - name: {str}: the unique ID given to the identified geometry
- Returns: 
  - feature: {geojson.Feature}: append provided properties to the geometry

#### <code>area(self, resolution=1.0)</code>
- Parameters:
  - resolution: {float}: the pixel size in micro-meter
- Returns:
  - area: {float}: the total area of geometry in micro-meter-squared

#### <code>min_enclosing_circle(self)</code>
- Returns:
  - center: {tuple: 2}: (x, y) coordinates 
  - radius: {float}: radius in pixels

## Examples
Here is a dummy example to demonstrate the utility of cv2geojson package.
```
import cv2 as cv
from cv2geojson import find_geocontours, export_annotations

# read sample image
img = cv.imread('./example/img_01.png')
mask = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Extract annotation contours
geocontours = find_geocontours(mask, mode='imagej')

# convert geocontours to geojson.Feature format
features = [contour.export_feature(color=(0, 255, 0), label='roi') for contour in geocontours]
export_annotations(features, './example/img_01.geojson')
```

<figure>
  <img src="https://github.com/mfarzi/cv2geojson/raw/main/example/img_01_snapshot.png" alt="QuPath Snapshot 2" style="width:70%; margin-right:10px;" />
</figure>
