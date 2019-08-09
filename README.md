# More pixels, less noise

Below is a small crop of a larger image taken in relatively low light. There is a lot of noise in the top image -- however the top image is just the first of 12 which I took and fused together to create the bottom image, which is twice the resolution (80 MP) and much cleaner. No tripod was used, and I deliberately shook my hands more than usual while taking the photographs.

![Test Image 4](https://github.com/ricsonc/more-pixels-less-noise/blob/master/comparison.jpg?raw=true)

This project has no original ideas and is a custom synthesis/recombination of previous research:

https://dl.acm.org/citation.cfm?id=2980254

https://arxiv.org/abs/1905.03277

The basic components are 1. estimating optical flow to align the images, 2. misalignment robust block merging a la Hasinoff et al., 3. a naive superres approach by upsampling images *before* warping/aligning with subpixel accurate flow.

The dependencies are dcraw, for demosaicking, pyflow, which is a wrapper on Ce Liu's implementation of coarse to fine flow estimation, and cv2, imagemagick, and some python libraries, for some image processing tasks.

The code isn't really plug-and-play yet, so I won't bother writing how-to-use documentation. All of the steps are implemented as a function in cmds.sh, and merge.py is used as the last step. The output is 16 bit linear RGB.
