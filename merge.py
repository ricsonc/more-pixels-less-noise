from imageio import imread, imsave
from glob import glob
import sys
from ipdb import set_trace as st
from os.path import join
import numpy as np
import cv2

def pad_to_multiple(img, size = 32):
    H, W, _ = img.shape

    padh = ((H//size)+1) * size - H
    padw = ((W//size)+1) * size - W

    return np.pad(img, ((0, padh), (0, padw), (0,0)), mode = 'constant') #pad w/ 0
    
def extend_borders(img, border = 16):
    return np.pad(img, ((border, border), (border, border), (0,0)), mode = 'constant') #pad w/ 0

def remove_borders(img, border = 16):
    return img[border:-border, border:-border]

def img_to_tiles(img, size = 32):
    H, W, C = img.shape
    
    img = img.transpose((2, 0, 1)) #C x H x W
    img = img.reshape((C, H, W//size, size)) #C x H x WT x S
    img = img.transpose((0, 2, 3, 1)) #C x WT x S x H
    img = img.reshape((C, W//size, size, H//size, size)) #C x WT x S x HT x S
    img = img.transpose((3, 1, 4, 2, 0)) #HT x WT x S x S x C
    img = img.reshape(( (W//size) * (H//size), size, size, C)) #HT*WT x S x S x C
    return img

def tiles_to_img(tiles, shp, size = 32):
    H, W, C = shp
    
    tiles = tiles.reshape(( H//size, W//size, size, size, C)) #HT x WT x S x S x C
    tiles = tiles.transpose((4, 1, 3, 0, 2)) #C x WT x S x HT x S
    tiles = tiles.reshape((C, W//size, size, H)) #C x WT x S x H
    tiles = tiles.transpose((0, 3, 1, 2)) #C x H x WT x S
    tiles = tiles.reshape((C, H, W)) #C, H, W
    tiles = tiles.transpose((1, 2, 0))
    return tiles

def make_tile_weights(size = 32):
    mg = np.meshgrid(np.linspace(-1, 1, size), np.linspace(-1, 1, size))
    dist = np.sqrt(mg[0] * mg[0] + mg[1] * mg[1]) / np.sqrt(1.9) #< 2
    weight = 1 - np.cos( (dist-1) * np.pi )
    return weight / 2.0

def merge(imgs, extend = False):
    padded = map(pad_to_multiple, imgs)
    if extend:
        padded = map(extend_borders, padded)
    tiles = np.stack(list(map(img_to_tiles, padded)), axis = 0)
    base = tiles[0]
    rest = tiles[1:]

    NT = tiles.shape[1]

    weights = [np.ones(NT).astype(np.float32)]
    
    for i, other in enumerate(rest): #this saves on memory...
        diff = np.abs(other.astype(np.float32) - base.astype(np.float32)).sum(axis = 3).mean(axis = (1, 2)) / 65536.0

        numerator = 0.05
        weight = np.maximum(np.minimum(1.0, numerator / (diff + 0.001)), 0.2)
        weights.append(weight)

    weights = np.stack(weights, axis = 0)[...,np.newaxis,np.newaxis,np.newaxis]
        
    merged_tiles = np.sum(tiles * weights, axis = 0) / np.sum(weights, axis = 0)

    out = tiles_to_img(merged_tiles, padded[0].shape)

    spatial_weight = tiles_to_img(
        np.tile(make_tile_weights()[np.newaxis,:,:,np.newaxis], (NT, 1, 1, 3)),
        padded[0].shape
    )

    if extend:
        out = remove_borders(out)
        spatial_weight = remove_borders(spatial_weight)
    
    return out, spatial_weight

def finish(imgs):
    H, W, _ = imgs[0].shape

    print 'first pass'
    out1, sw1 = merge(imgs, extend = False)
    print 'second pass'
    out2, sw2 = merge(imgs, extend = True)

    result = (out1 * sw1 + out2 * sw2) / (sw1+sw2)
    result = result.astype(np.uint16)
    return result[:H,:W]

def ez(imgs):
    return np.stack([img.astype(np.float32) for img in imgs], axis = 0).mean(axis = 0).astype(np.uint16)

if __name__ == '__main__':
    pth = sys.argv[1]

    N = len(glob(join(pth,'warps/*.tiff')))
    fns = [join(pth, 'warps/%d.tiff' % (i+1)) for i in range(N)]

    print('reading images')
    
    def cvread(fn):
        img = cv2.imread(fn, -1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    tiffs = list(map(cvread, fns))

    print 'processing'
    
    out = finish(tiffs)
    imsave(join(pth, 'out.tiff'), out)

    print 'processing 2'

    bad = ez(tiffs)
    imsave(join(pth, 'bad.tiff'), bad)
    
