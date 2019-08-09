import cv2
from imageio import imread, imsave
import numpy as np
import sys
from os.path import join

pth = sys.argv[1]
offset = int(sys.argv[2])
factor = 2

im_path = join(pth, 'tiffs', '%d.tiff' % (offset))
flow_path = join(pth, 'pngs', '%d.npy' % (offset))
out_path = join(pth, 'warps', '%d.tiff' % (offset))

im = imread(im_path).astype(np.float32)
h, w, _ = im.shape
im_big = cv2.resize(im, (w*factor, h*factor), interpolation = cv2.INTER_LINEAR)

if offset > 1:
    # if offset == 1:    
    #     flow = np.zeros_like(np.load(join(pth, 'pngs', '2.npy')))
    # else:
    
    flow = np.load(flow_path)
        
    flow_big = cv2.resize(flow, (w*factor, h*factor), interpolation = cv2.INTER_LINEAR) * factor

    flow_big[...,0] += np.arange(w*factor)
    flow_big[...,1] += np.arange(h*factor)[:,np.newaxis]
    flow_big = flow_big.astype(np.float32)

    warp = cv2.remap(im_big, flow_big, None, interpolation=cv2.INTER_LINEAR)
else:
    warp = im_big
    
warp = cv2.cvtColor(warp,cv2.COLOR_BGR2RGB)
cv2.imwrite(out_path, warp.astype(np.uint16))
