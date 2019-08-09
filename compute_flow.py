# Author: Deepak Pathak (c) 2016

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from PIL import Image
import time
import argparse
import pyflow
from ipdb import set_trace as st
import sys
from glob import glob
from os.path import join
from natsort import natsorted
from imageio import imread, imsave

pth = sys.argv[1]
offset = int(sys.argv[2])

fns = natsorted(glob(join(pth,'*.png')))
idx_to_img = lambda x: imread(fns[x]).astype(np.float64)/255.0

base = idx_to_img(0)
other = idx_to_img(offset)

print('job %d loaded both images' % offset)

# Flow Options:
alpha = 0.012
ratio = 0.75
minWidth = 20
nOuterFPIterations = 7
nInnerFPIterations = 1
nSORIterations = 30
colType = 0  # 0 or default:RGB, 1:GRAY (but pass gray image with shape (h,w,1))

args = [alpha, ratio, minWidth, nOuterFPIterations, nInnerFPIterations, nSORIterations, colType]

u, v, warped = pyflow.coarse2fine_flow(base, other, *args)

flow = np.concatenate((u[..., None], v[..., None]), axis=2)
np.save(join(pth, '%d.npy' % (offset+1)), flow)
