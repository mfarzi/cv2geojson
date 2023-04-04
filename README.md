# cv2geojson
cv2geojson is an open source project to export annotation contours extracted using [OpenCV-python](https://github.com/opencv/opencv-python) package to [GeoJSON](https://pypi.org/project/geojson/) format.

## Introduction
In digital pathology, images are often quite large and dedicated software tools like [QuPath](https://qupath.github.io/) are required to aid visualisation. The python package cv2geojson export contours detected using `cv2.findContours` as polygons using GeoJSON format for visualisation in QuPath.

## Installation
The recommended way to install is via pip:

`pip install cv2geojson`

## Example

```
import cv2 as cv
import geojson
import cv2geojson

# read sample image
img = cv.imread('./example/img_01.png')
img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Extract annotation contours
contours, hierarchy = cv.findContours(img, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

# convert contours to geojson format
geometries = cv2geojson.contour2geometry(contours, hierarchy)
features = [cv2geojson.geometry2feature(geometry) for geometry in geometries]
annotation = geojson.FeatureCollection(features)

# export annotation
with open('./example/geocontours_01.geojson', 'w') as writer:
    geojson.dump(annotation, writer)
```
