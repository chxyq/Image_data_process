 #*- coding: UTF-8 -*-
 #encoding:utf-8
import numpy as np
import cv2
import math
import os
import demosaic
import matplotlib.pyplot as plt
# DRANGE = 23.5
# MAX_BIN = 256
# MAX_CP = 1024
DRANGE = 24.0
MAX_BIN = 384
MAX_CP = 1536
MAX_MID_OCP = 130
MIN_MID_OCP = 50
MIN_MID_LOG = 10
MID_OCP_STEP = 8

def tonemapping_fpga(size, raw24, pedestal, CPs, method, wb):
    height = size[0]
    width = size[1]
    HIST = [0 for x in range(0, MAX_BIN)]
    ACC_HIST = [0 for x in range(0, MAX_BIN)]
    CP = [0 for x in range(0, MAX_CP)]
    tmo_raw = np.zeros(size, dtype=np.float32)
    #raw24 = raw24_to_int32(size, raw24)
    raw24 = raw24.astype(np.float32)
    print(np.max(raw24))
    raw24 -= pedestal
    raw24[raw24 < 1] = 1
    raw24[raw24 > math.pow(2, DRANGE)] = math.pow(2, DRANGE)
    if method == 0:
        rgb = demosaic.demosaic_bilinear3(raw24)
        Y = (rgb[:, :, 1]*2 + rgb[:, :, 0] + rgb[:, :, 2])/4
        Y[Y < 1] = 1
    elif method == 1:
        rgb = demosaic.demosaic_bilinear3(raw24)
        Y = rgb[:, :, 1]
        Y[Y < 1] = 1
    elif method == 2:
        Y = raw24
    if wb == 0:
        r, g1, g2, b = demosaic.awb_gain_cal(raw24, 0)
        
        Y[::2, ::2] *= 4
        Y[1::2, ::2] *= 4
        Y[::2, 1::2] *= 4
        Y[1::2, 1::2] *= 1
        Y[Y < 1] = 1
    Y[Y > math.pow(2, DRANGE)] = math.pow(2, DRANGE)
    avg = []
    ori_ratio = raw24/Y
    ori_ratio[ori_ratio > 1] = 1
    log_raw = Y.astype(np.float32)
    log_raw_ori = raw24.astype(np.float32)
    log_raw = np.log2(log_raw)
    log_raw_ori = np.log2(log_raw_ori)
    tmp = log_raw.copy()
    tmp = np.uint32(tmp * (MAX_BIN - 1) / DRANGE)
    luma_target = np.mean(Y)
    s = 0.0
    for index in range(MAX_BIN):
        k = np.sum(tmp == index)
        HIST[index] = float(k)
        s += k
    ACC_HIST[0] = HIST[0]
    ACC_HIST[1] = HIST[0] + HIST[1]
    for i in range(1, MAX_BIN):
        if i >= 2 and i <= (MAX_BIN - 2):
            ACC_HIST[i] = ACC_HIST[i - 1] + HIST[i]
        else:
            ACC_HIST[i] = ACC_HIST[i - 1]

    ###########################################################
    #base_ratio = [0.005, 0.01,   0.3, 0.9999, 0.99999]
    base_ratio = [0.005, 0.01,   0.5, 0.9999, 0.99999]
    #print(HIST[374])
    print(ACC_HIST[(MAX_BIN - 1)])
    #[0.001, 0.005,   0.5, 0.9999, 0.99999]
    o_base =     [0,        4,   130,  245,   250  ]
    base = []
    #print(ACC_HIST[(MAX_BIN - 1)])
    for i in range(CPs):
        base.append(np.int32((ACC_HIST[(MAX_BIN - 1)] * base_ratio[i]) + 0.5))

    i_base = []
    #o_base = [0, 4, 130, 245]
        
    bin_step = DRANGE / MAX_BIN
    for n in range(CPs):
        pos = 0
        for i in range(MAX_BIN):
            pos = i
            if ACC_HIST[i] >= base[n]:
                break
        i_base.append(pos * bin_step) 

    o_base[3] = i_base[3]/DRANGE * 256
    o_base[4] = i_base[4]/DRANGE * 256

    i_cp = i_base
    o_cp = o_base
    if(i_cp[2] <= MIN_MID_LOG):
        o_cp[2] = MIN_MID_OCP
    else:
        o_cp[2] = (i_cp[2] - MIN_MID_LOG) * MID_OCP_STEP + MIN_MID_OCP
    if(o_cp[2] >= MAX_MID_OCP):
        o_cp[2] = MAX_MID_OCP
    print('i_base:'+str(i_base))
    print('o_base:'+str(o_base))
    N = CPs
    step = DRANGE / MAX_CP
    for i in range(MAX_CP):
        in_pos = i * step
        in_pos = i_cp[0] if i_cp[0] > in_pos else in_pos
        in_pos = i_cp[N - 1] if i_cp[N - 1] < in_pos else in_pos
        for j in range(N):
            i_h = i_cp[j]
            o_h = o_cp[j]
            i_l = i_cp[0] if j < 2 else i_cp[j - 1]
            o_l = o_cp[0] if j < 2 else o_cp[j - 1]
            if in_pos < i_cp[j]:
                break
        ratio = (in_pos - i_l) / float(i_h - i_l + 0.00000001)
        CP[i] = int(o_l + (o_h - o_l) * ratio)

    index = np.int32(log_raw / step)
    index[index >= MAX_CP] = MAX_CP - 1
    for h in range(height):
        for w in range(width):
            t = index[h, w]
            tmo_raw[h, w] = CP[t]
    tmo_raw *= ori_ratio
    return tmo_raw, luma_target




