# cv2geojson
cv2geojson is an open-source project to export annotation contours extracted using [OpenCV-python](https://github.com/opencv/opencv-python) package to [GeoJSON](https://pypi.org/project/geojson/) format.

## Contents
- [Introduction](#introduction)
  - [Example 1](#example-1)
  - [Example 2](#example-2)
- [Installation](#installation)
- [Main Methods](#main-methods)
  - [find_geocontours](#find_geocontoursmask-modeopencv)
  - [draw_geocontours](#draw_geocontoursmask-geocontours-scale1-offset0-0-modeopencv)
  - [export_annotations](#export_annotationsfeatures-path_to_geojson)
  - [load_annotations](#load_annotationspath_to_geojson)
- [class GeoContour](#class-geocontour)
  - [Attributes](#attributes)
    - [contours](#contours)
    - [type](#type)
  - [Methods](#methods)
    - [get_contours](#get_contoursself-scale1-offset0-0)
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
    - [scale_up](#scale_upself-ratio1-offset0-0)
    - [scale_down](#scale_downself-ratio1-offset0-0)
    - [copy](#copyself)

## Introduction
Contours can be defined as continuous curves that connect points of the same color or intensity along a boundary. They are commonly used for shape analysis, object detection, and recognition. For instance, in liver pathology, fat vacuoles can be identified as circular white blobs (check out this [link](https://github.com/mfarzi/liverquant#example-1-detect-fat-globules) for an example). The traditional method to extract contours in `OpenCV` is by utilizing `cv2.findContours`. However, these extracted contours are not easily visualized in third-party software tools such as [QuPath](https://qupath.github.io/). To overcome this limitation, the `cv2geojson` Python package provides a seamless bridge between the contours extracted using `OpenCV` and the geometries represented as [GeoJSON](https://pypi.org/project/geojson/) objects. By converting the extracted contours to the `GeoJSON` format, they can be easily visualized and utilized in various software tools.

### Example 1
In digital pathology, images can be quite large. For example, download the whole slide image with tissue sample ID _GTEX-12584-1526_ from [histology page](https://gtexportal.org/home/histologyPage). This image has 45,815x38,091 pixels which requires about 5GB of storage uncompressed. Rather than storing a binary mask for the foreground segmentation, the mask can be converted to polygons and stored as a geojson file. The image below shows a snapshot from the QuPath software. The foreground contour is blue.
<figure>
  <img src="https://github.com/mfarzi/cv2geojson/raw/main/example/GTEX-12584-1526-snapshot.png" alt="QuPath Snapshot 2" style="width:50%; margin-right:10px;" />
  <figcaption>Snapshot from QuPath software visualising foreground segmentation</figcaption>
</figure>

### Example 2
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

## Installation
The recommended way to install is via pip:

`pip install cv2geojson`

## Main Methods

### <code>find_geocontours(mask, mode='opencv')</code>
This function, similar to `cv2.findContours`, retrieves contours from the binary mask and grouped them as geometries similar to `GeoJSON` objects. The geometries are a useful tool for shape analysis or object detection.
- Parameters:
  - mask: {numpy.ndarray}: binary mask of value 255 or 0
  - mode: {str}: the contour represetnation method; either 'imagej' or 'opencv'
- Returns:
  - geocontours: {cv2geojson.geocontours}: a list of detected  geomtries: Polgy, Point, or LineString
> Note: `OpenCV` contours are based on pixel centers whereas `imagej` contours are based on pixel edges. Both methods are plausible options but `imagej` method is recommended for visualisation in [QuPath](https://qupath.github.io/). Here is a short script to demonstrate the differences between the two methods.
```
import numpy as np
from cv2geojson import find_geocontours

# define a binary mask
mask = np.array([[0,   0, 0, 0, 0],
                 [0,   0, 0, 0, 0],
                 [0, 255, 0, 0, 0],
                 [0,   0, 0, 0, 0],
                 [0,   0, 0, 0, 0]], dtype=np.uint8)

# extract geocontours
geocontour_opencv = find_geocontours(mask, mode='opencv')[0]
geocontour_imagej = find_geocontours(mask, mode='imagej')[0]

print(f'Poplygon Coordinates using OpenCV method: {geocontour_opencv.export_geometry()}')
print(f'Poplygon Coordinates using ImageJ method: {geocontour_imagej.export_geometry()}')
```
The following result is printed:
```
Poplygon Coordinates using OpenCV method: {"coordinates": [1, 2], "type": "Point"}
Poplygon Coordinates using ImageJ method: {"coordinates": [[[1, 2], [1, 3], [2, 3], [2, 2], [1, 2]]], "type": "Polygon"}
```

### <code>draw_geocontours(mask, geocontours, scale=1, offset=(0, 0), mode='opencv')</code>
This function, similar to `cv2.drawContours`, draw geocontours to the corresponding binary mask.
- Parameters:
  - mask: {numpy.ndarray}: binary mask of value 255 or 0
  - goecontours: {list: cv2geojson.GeoContour}
  - scale: {int}: downsampling ratio
  - offset: {tuple: 2}: offset displacement
  - mode: {str}: either 'imagej' or 'opencv'

### <code>export_annotations(features, path_to_geojson)</code>
This function write `GeoJSON.Feature` objects to a file.
- Parameters:
  - features: {list: geojson.feature.Feature}
  - path_to_geojson: {str}

> Here is a short script to demonstrate its usage. Also see [export_feature](#export_featureself-colornone-labelnone-namenone)
```
import numpy as np
from cv2geojson import find_geocontours, export_annotations

# define a binary mask
mask = np.array([[0,   0,   0,   0, 0],
                 [0,   0,   0,   0, 0],
                 [0, 255, 255, 255, 0],
                 [0, 255, 255, 255, 0],
                 [0,   0,   0,   0, 0],
                 [0,   0,   0,   0, 0]], dtype=np.uint8)

# extract geocontours
geocontours = find_geocontours(mask, mode='imagej')

# export features
features = []
for geocontour in geocontours:
    features.append(geocontour.export_feature(color=(255, 0, 0),
                                              label='rectangle',
                                              name='ID1'))
export_annotations(features, 'test.geojson')
```

### <code>load_annotations(path_to_geojson)</code>
This function read `GeoJSON` objects from a file and convert them to `cv2geojson.GeoContour`.
- Parameters:path_to_geojson: {str}
- Returns: geocontours: {list: cv2geojson.GeoContour}

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
#### <code>get_contours(self, scale=1, offset=(0, 0))</code>
- Parameters:
  - scale: {int}: the down-scaling ratio
  - offset: {tuple: 2}
- Returns: contours: {list of numpy.ndarray}: (contours - offset)/scale

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


