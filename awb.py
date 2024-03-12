 #*- coding: UTF-8 -*-
 #encoding:utf-8
import numpy as np
import cv2
import data_parse
import tonemapping as tm
import os
import pwl
import demosaic

def awb_gain_cal(raw, method):
    r = raw[::2, ::2]
    b = raw[1::2, 1::2]
    g1 = raw[1::2, ::2]
    g2 = raw[::2, 1::2]
    g = (g1 + g2)/ 2.0
    r_mean = np.mean(r)
    b_mean = np.mean(b)
    g1_mean = np.mean(g1)
    g2_mean = np.mean(g2)

    #grey world
    if method == 0:
        k = (r_mean + b_mean + g2_mean + g1_mean) / 4
        kr = k / r_mean
        kb = k / b_mean
        kg1 = k / g1_mean
        kg2 = k / g2_mean
        #kg = k / g_mean
    elif method == 1:
        #perfect reflect
        max_r = np.max(r)
        max_b = np.max(b)
        max_g1 = np.max(g1)
        max_g2 = np.max(g2)
        kr = max_r / r_mean
        kb = max_b / b_mean
        kg1 = max_g1 / g1_mean
        kg2 = max_g2 / g2_mean
    raw[::2, ::2] = raw[::2, ::2] * kr
    raw[1::2, 1::2] = raw[1::2, 1::2] * kb
    raw[1::2, ::2] = raw[1::2, ::2] * kg1
    raw[::2, 1::2] = raw[::2, 1::2] * kg2
    #raw[raw > 255] = 255
    return raw

