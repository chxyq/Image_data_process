 #*- coding: UTF-8 -*-
 #encoding:utf-8
import numpy as np
import cv2
import data_parse
import tonemapping as tm
import os
import pwl
import demosaic
import awb

def findAllFile(filepath):
    filelist = []
    for root, ds, fs in os.walk(filepath):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname

def main(path):
    for i in findAllFile(path):
        print(i)
        if i.split(".")[-1] == "jpg":
            continue
        raw_img,raw_img1 = data_parse.load_raw12(i)
        hdr = (raw_img1* 16. + raw_img/16.)
        upwl = pwl.pwl12_decompress((2160, 3840), hdr[1:2161,:], 0, 5, 1)
        ldr, luma_target = tm.tonemapping_fpga((2160, 3840), awb.awb_gain_cal(upwl, 0), 0, 5, 2, 1)
        #full_rgb888 = cv2.cvtColor(np.uint8(ldr), cv2.COLOR_BAYER_RG2RGB)
        full_rgb888 = demosaic.gradient_correct_demosaic(np.uint8(ldr))
        cv2.imwrite(i + ".jpg", full_rgb888)

main("/home/tusimple/newdisk4t/workspace/20230215/a")

