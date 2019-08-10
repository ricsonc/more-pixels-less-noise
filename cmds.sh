#!/usr/bin/env bash

relabel() {
    ls -v *.ARW | cat -n | while read n f; do mv -n "$f" "$n.ARW"; done 
}

to_png() {
    find *.ARW | xargs -n 1 -P 8 dcraw -w -q 3 -C 0.999 1.001
    find *.ppm | xargs -I{} basename {} .ppm | xargs -n 1 -P 8 -I{} convert {}.ppm {}.png
    rm -f *.ppm
    mkdir pngs
    mv *.png pngs
}

to_tiff() {
    find *.ARW | xargs -n 1 -P 8 dcraw -4 -T -q 3 -C 0.999 1.001
    mkdir tiffs
    mv *.tiff tiffs
}

# swap_sharpest() {
#     fn="$(find *.png | sort -V | xargs -n 1 python /home/ricson/code/compho/sharpness.py | cat -n | sort -nk +2 | tail -n 1 | awk '{ print $1 }').png"
#     echo "swapping with $fn"
    
#     cp 1.png tmp
#     cp $fn 1.png
#     cp tmp $fn
#     rm -f tmp
# }

run_flow() {
    for i in $(seq 1 $(ls -1q $1/*.png | wc -l)); do echo $i; done | head -n -1 | xargs -n 1 -I{} python compute_flow.py $1 {}
}

make_warps() {
    mkdir $1/warps
    for i in $(seq 1 $(ls -1q $1/*.ARW | wc -l)); do echo $i; done | xargs -n 1 -P 4 -I{} python2.7 warp.py $1 {}
}


copyexif() {
    exiftool -all= -tagsfromfile tiffs/1.tiff -exif:all out.tiff
    exiftool -tagsfromfile tiffs/1.tiff -icc_profile out.tiff
}



