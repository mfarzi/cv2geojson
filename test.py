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
