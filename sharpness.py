#!/usr/bin/env python

from imageio import imread
from PIL import Image
import numpy as np
import sys

filename = sys.argv[1]

im = Image.open(filename).convert('L') # to grayscale
array = np.asarray(im, dtype=np.int32)

gy, gx = np.gradient(array)
gnorm = np.sqrt(gx**2 + gy**2)
sharpness = np.average(gnorm)

print(sharpness)
