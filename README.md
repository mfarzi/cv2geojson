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
    - [area](#areaself-resolution10)
    - [min_enclosing_circle](#min_enclosing_circleself)
    - [circularity](#circularityself)
    - [solidity](#solidityself)
    - [aspect_ratio](#aspect_ratioself)
    - [elongation](#elongationself)
    - [holes_num](#holes_numself)
    - [fill_hole](#fill_holeself-resolution10-hole_size-10)
    - [scale_up](#scale_upself-ratio1-offset00)
    - [scale_down](#scale_downself-ratio1-offset00)
    - [copy](#copyself)
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
The library implements a new class, `cv2geojson.GeoContour`, which facilitates the seamless integration of contours extracted using `cv2.findContours` and geometries defined as GeoJSON objects. An instance of this class can be initialized by providing either contours or GeoJSON objects. Here is an example of how to initialize the class using both a GeoJSON object and NumPy contours:
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
&nbsp;list of numpy.ndarray: the coordinates of the geometry

#### <code>type</code>
&nbsp;str: Point, LineString, or Polygon

### Methods:
#### <code>export_geometry(self)</code>
- Returns: {geojson.Point, geojson.LineString, geojson.Polgyon}

#### <code>export_feature(self, color=None, label=None, name=None)</code>
- Parameters:
  - color: {tuple: 3}: (r, g, b) in range 0 to 255
  - label: {str}: the class name for the identified geometry
  - name: {str}: the unique ID given to the identified geometry
- Returns: {geojson.Feature}: append provided properties to the geometry

#### <code>area(self, resolution=1.0)</code>
- Parameters:
  - resolution: {float}: the pixel size in micro-meter
- Returns: {float}: the total area of polygon in micro-meter-squared

#### <code>min_enclosing_circle(self)</code>
- Returns:
  - center: {tuple: 2}: (x, y) coordinates 
  - radius: {float}: radius in pixels

#### <code>circularity(self)</code> 
- Returns: {float}: $4\pi \text{Area}/\text{Perimeter}^2$

#### <code>solidity(self)</code> 
- Returns: {float}: the polygon area divided by its convex hull area

#### <code>aspect_ratio(self)</code> 
- Returns: {float}: the width of the enclosing rectangle divided by its height

#### <code>elongation(self)</code> 
- Returns: {float}: the minor to major diameter of the enclosing oval

#### <code>holes_num(self)</code> 
- Returns: {int}: the number of holes in the polygon

#### <code>fill_hole(self, resolution=1.0, hole_size=-1.0)</code> 
Remove any holes in the polygon larger than hole_size
- Parameters:
  - resolution: {float}: the pixel size in micro-meter
  - hole_size: {float}: the hole area in micro-meter-squared. If -1, all holes will be filled.

#### <code>scale_up(self, ratio=1, offset=(0, 0))</code>
Scale up the coodinates: x_new = (ratio * x_old) + offset
- Parameters:
  - ratio: {int}
  - offset: {tuple: 2}

#### <code>scale_down(self, ratio=1, offset=(0, 0))</code>
Scale down the coodinates: x_new = (x_old - offset) / ratio
- Parameters:
  - ratio: {int}
  - offset: {tuple: 2}

#### <code>copy(self)</code>
- Returns: {cv2geojson.GeoContour}

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
