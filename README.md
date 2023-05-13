# cv2geojson
cv2geojson is an open-source project to export annotation contours extracted using [OpenCV-python](https://github.com/opencv/opencv-python) package to [GeoJSON](https://pypi.org/project/geojson/) format.

## Introduction
In digital pathology, images are often quite large and dedicated software tools like [QuPath](https://qupath.github.io/) are required to aid visualisation. The python package cv2geojson export contours detected using `cv2.findContours` as polygons using GeoJSON format for visualisation in QuPath. For example, download the whole slide image with tissue sample ID _GTEX-12584-1526_ from [histology page](https://gtexportal.org/home/histologyPage). This image has 45,815x38,091 pixels which requires about 5GB of storage uncompressed. Rather than storing a binary mask for the foreground segmentation, the mask can be converted to polygons and stored as a geojson file. The image below shows a snapshot from the QuPath software. The foreground contour is blue.
<figure style="margin:0; padding:0;">
  <img src="https://github.com/mfarzi/cv2geojson/blob/main/example/GTEX-12584-1526-snapshot.png" alt="Image 1" style="width:30%; margin-right:10px;" />
  <figcaption>Snapshot from QuPath software visualising foreground segmentation</figcaption>
</figure>

## Installation
The recommended way to install is via pip:

`pip install cv2geojson`

## Example
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

<figure style="margin:0; padding:0;">
  <img src="https://github.com/mfarzi/cv2geojson/blob/main/example/img_01_snapshot.png" alt="Image 1" style="width:30%; margin-right:10px;" />
  <figcaption>Snapshot from QuPath software visualising foreground segmentation</figcaption>
</figure>