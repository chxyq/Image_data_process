 #*- coding: UTF-8 -*-
 #encoding:utf-8
import numpy as np
import math

def pwl12_compress(size, raw24, pedestal, CPs, method):
    height = size[0]
    width = size[1]
    pwl_comress = np.zeros(size, dtype=np.float32)
    raw24 = raw24_to_int32(size, raw24)
    raw24 = raw24.astype(np.float32)
    #print(np.max(raw24))
    #raw24 += 240
    raw24[raw24 < 1] = 1
    
    raw24[raw24 > math.pow(2, DRANGE)] = math.pow(2, DRANGE)

    for h in range(height):
        for w in range(width):
            t = raw24[h, w]
            if t < 384:
                pwl_comress[h, w] = int(t)
            elif t < 1600:
                pwl_comress[h, w] = int(384 + (t - 384) * 0.333333313)
            elif t < 3700:
                pwl_comress[h, w] = int(789 + (t - 1600) * 0.111111104)
            elif t < 24000:
                pwl_comress[h, w] = int(1022 + (t - 3700) * 0.012595475)
            elif t < 73000:
                pwl_comress[h, w] = int(1278 + (t - 24000) * 0.006297708)
            elif t < 210392:
                pwl_comress[h, w] = int(1586 + (t - 73000) * 0.003148854)
            elif t < 1500000:
                pwl_comress[h, w] = int(2019 + (t - 210392) * 0.000306666)
            elif t < 5000000:
                pwl_comress[h, w] = int(2415 + (t - 1500000) * 0.000153303)
            elif t < 16777215:
                pwl_comress[h, w] = int(2951 + (t - 5000000) * 0.000076652)
            else:
                pwl_comress[h, w] = int(3854)

    return pwl_comress

def pwl12_decompress(size, pwl_comress, pedestal, CPs, method):
    height = size[0]
    width = size[1]
    pwl_decomress = np.zeros(size, dtype=np.float32)
    for h in range(height):
        for w in range(width):
            t = pwl_comress[h, w]
            #y = [0., 512., 767., 1023., 1279., 1535., 1663., 1791., 1919., 2047., 2175., 2303., 2431., 2559., 2687., 2815., 2943., 3071., 3135., 3199., 3263., 3327., 3391., 3455., 3519., 3583., 3647., 3711., 3775., 3839., 3903., 3967., 4031., 4095.]
            #x = [0., 511., 1023., 2047., 3071., 4095., 6143., 8191., 12287., 16383., 24575., 32767., 49151., 65535., 98303., 131071., 196607., 262143., 393215., 524287., 786431., 1048575., 1310719., 1572863., 2097151., 2621439., 3145727., 4194303., 5242879., 6291455., 8388607., 10485759., 12582911., 16777215.]
            y = [0., 100., 175., 308., 423., 624., 762., 1000., 1167., 1456., 1652., 1998., 2233., 2646., 2928., 3423., 3759., 4095.]
            x = [0., 100., 212., 450., 954., 2024., 4293., 9106., 19313., 40963., 86883., 184279., 390856., 829005., 1758320., 3729396., 7910050., 16777215.]
            '''if t < 384:
                pwl_decomress[h, w] = int(t)
            elif t < 789:
                pwl_decomress[h, w] = int(384 + (t - 384) / 0.333333313)
            elif t < 1022:
                pwl_decomress[h, w] = int(1600 + (t - 789) / 0.111111104)
            elif t < 1278:
                pwl_decomress[h, w] = int(3700 + (t - 1022) / 0.012595475)
            elif t < 1586:
                pwl_decomress[h, w] = int(24000 + (t - 1278) / 0.006297708)
            elif t < 2019:
                pwl_decomress[h, w] = int(73000 + (t - 1586) / 0.003148854)
            elif t < 2415:
                pwl_decomress[h, w] = int(210392 + (t - 2019) / 0.000306666)
            elif t < 2951:
                pwl_decomress[h, w] = int(1500000 + (t - 2415) / 0.000153303)
            elif t < 3854:
                pwl_decomress[h, w] = int(5000000 + (t - 2951) / 0.000076652)
            else:
                pwl_decomress[h, w] = int(16777215)'''
            #pwl = 0.
            if t < y[1]:
                    pwl_decomress[h, w] = int(x[0] + (t - y[0]) * (x[1] - x[0]) / (y[1] - y[0]) + 0.5)
            elif t < y[2]:
                    pwl_decomress[h, w] = int(x[1] + (t - y[1]) * (x[2] - x[1]) / (y[2] - y[1]) + 0.5)
            elif t < y[3]:
                    pwl_decomress[h, w] = int(x[2] + (t - y[2]) * (x[3] - x[2]) / (y[3] - y[2]) + 0.5)
            elif t < y[4]:
                    pwl_decomress[h, w] = int(x[3] + (t - y[3]) * (x[4] - x[3]) / (y[4] - y[3]) + 0.5)
            elif t < y[5]:
                    pwl_decomress[h, w] = int(x[4] + (t - y[4]) * (x[5] - x[4]) / (y[5] - y[4]) + 0.5)
            elif t < y[6]:
                    pwl_decomress[h, w] = int(x[5] + (t - y[5]) * (x[6] - x[5]) / (y[6] - y[5]) + 0.5)
            elif t < y[7]:
                    pwl_decomress[h, w] = int(x[6] + (t - y[6]) * (x[7] - x[6]) / (y[7] - y[6]) + 0.5)
            elif t < y[8]:
                    pwl_decomress[h, w] = int(x[7] + (t - y[7]) * (x[8] - x[7]) / (y[8] - y[7]) + 0.5)
            elif t < y[9]:
                    pwl_decomress[h, w] = int(x[8] + (t - y[8]) * (x[9] - x[8]) / (y[9] - y[8]) + 0.5)
            elif t < y[10]:
                    pwl_decomress[h, w] = int(x[9] + (t - y[9]) * (x[10] - x[9]) / (y[10] - y[9]) + 0.5)
            elif t < y[11]:
                    pwl_decomress[h, w] = int(x[10] + (t - y[10]) * (x[11] - x[10]) / (y[11] - y[10]) + 0.5)
            elif t < y[12]:
                    pwl_decomress[h, w] = int(x[11] + (t - y[11]) * (x[12] - x[11]) / (y[12] - y[11]) + 0.5)
            elif t < y[13]:
                    pwl_decomress[h, w] = int(x[12] + (t - y[12]) * (x[13] - x[12]) / (y[13] - y[12]) + 0.5)
            elif t < y[14]:
                    pwl_decomress[h, w] = int(x[13] + (t - y[13]) * (x[14] - x[13]) / (y[14] - y[13]) + 0.5)
            elif t < y[15]:
                    pwl_decomress[h, w] = int(x[14] + (t - y[14]) * (x[15] - x[14]) / (y[15] - y[14]) + 0.5)
            elif t < y[16]:
                    pwl_decomress[h, w] = int(x[15] + (t - y[15]) * (x[16] - x[15]) / (y[16] - y[15]) + 0.5)
            elif t < y[17]:
                    pwl_decomress[h, w] = int(x[16] + (t - y[16]) * (x[17] - x[16]) / (y[17] - y[16]) + 0.5)
            else:
                    pwl_decomress[h, w] = x[17]
                #print(hex(int(pwl)))

            '''if t < y[1]:
                pwl_decomress[h, w] = int(x[0] + (t - y[0]) * (x[1] - x[0]) / (y[1] - y[0]))
            elif t < y[2]:
                pwl_decomress[h, w] = int(x[1] + (t - y[1]) * (x[2] - x[1]) / (y[2] - y[1]))
            elif t < y[3]:
                pwl_decomress[h, w] = int(x[2] + (t - y[2]) * (x[3] - x[2]) / (y[3] - y[2]))
            elif t < y[4]:
                pwl_decomress[h, w] = int(x[3] + (t - y[3]) * (x[4] - x[3]) / (y[4] - y[3]))
            elif t < y[5]:
                pwl_decomress[h, w] = int(x[4] + (t - y[4]) * (x[5] - x[4]) / (y[5] - y[4]))
            elif t < y[6]:
                pwl_decomress[h, w] = int(x[5] + (t - y[5]) * (x[6] - x[5]) / (y[6] - y[5]))
            elif t < y[7]:
                pwl_decomress[h, w] = int(x[6] + (t - y[6]) * (x[7] - x[6]) / (y[7] - y[6]))
            elif t < y[8]:
                pwl_decomress[h, w] = int(x[7] + (t - y[7]) * (x[8] - x[7]) / (y[8] - y[7]))
            elif t < y[9]:
                pwl_decomress[h, w] = int(x[8] + (t - y[8]) * (x[9] - x[8]) / (y[9] - y[8]))
            elif t < y[10]:
                pwl_decomress[h, w] = int(x[9] + (t - y[9]) * (x[10] - x[9]) / (y[10] - y[9]))
            elif t < y[11]:
                pwl_decomress[h, w] = int(x[10] + (t - y[10]) * (x[11] - x[10]) / (y[11] - y[10]))
            elif t < y[12]:
                pwl_decomress[h, w] = int(x[11] + (t - y[11]) * (x[12] - x[11]) / (y[12] - y[11]))
            elif t < y[13]:
                pwl_decomress[h, w] = int(x[12] + (t - y[12]) * (x[13] - x[12]) / (y[13] - y[12]))
            elif t < y[14]:
                pwl_decomress[h, w] = int(x[13] + (t - y[13]) * (x[14] - x[13]) / (y[14] - y[13]))
            elif t < y[15]:
                pwl_decomress[h, w] = int(x[14] + (t - y[14]) * (x[15] - x[14]) / (y[15] - y[14]))
            elif t < y[16]:
                pwl_decomress[h, w] = int(x[15] + (t - y[15]) * (x[16] - x[15]) / (y[16] - y[15]))
            elif t < y[17]:
                pwl_decomress[h, w] = int(x[16] + (t - y[16]) * (x[17] - x[16]) / (y[17] - y[16]))
            elif t < y[18]:
                pwl_decomress[h, w] = int(x[17] + (t - y[17]) * (x[18] - x[17]) / (y[18] - y[17]))
            elif t < y[19]:
                pwl_decomress[h, w] = int(x[18] + (t - y[18]) * (x[19] - x[18]) / (y[19] - y[18]))
            elif t < y[20]:
                pwl_decomress[h, w] = int(x[19] + (t - y[19]) * (x[20] - x[19]) / (y[20] - y[19]))
            elif t < y[21]:
                pwl_decomress[h, w] = int(x[20] + (t - y[20]) * (x[21] - x[20]) / (y[21] - y[20]))
            elif t < y[22]:
                pwl_decomress[h, w] = int(x[21] + (t - y[21]) * (x[22] - x[21]) / (y[22] - y[21]))
            elif t < y[23]:
                pwl_decomress[h, w] = int(x[22] + (t - y[21]) * (x[23] - x[22]) / (y[23] - y[22]))
            elif t < y[24]:
                pwl_decomress[h, w] = int(x[23] + (t - y[21]) * (x[24] - x[23]) / (y[24] - y[23]))
            elif t < y[25]:
                pwl_decomress[h, w] = int(x[24] + (t - y[21]) * (x[25] - x[24]) / (y[25] - y[24]))
            elif t < y[26]:
                pwl_decomress[h, w] = int(x[25] + (t - y[21]) * (x[26] - x[25]) / (y[26] - y[25]))
            elif t < y[27]:
                pwl_decomress[h, w] = int(x[26] + (t - y[21]) * (x[27] - x[26]) / (y[27] - y[26]))
            elif t < y[28]:
                pwl_decomress[h, w] = int(x[27] + (t - y[27]) * (x[28] - x[27]) / (y[28] - y[27]))
            elif t < y[29]:
                pwl_decomress[h, w] = int(x[28] + (t - y[28]) * (x[29] - x[28]) / (y[29] - y[28]))
            elif t < y[30]:
                pwl_decomress[h, w] = int(x[29] + (t - y[29]) * (x[30] - x[29]) / (y[30] - y[29]))
            elif t < y[31]:
                pwl_decomress[h, w] = int(x[30] + (t - y[30]) * (x[31] - x[30]) / (y[31] - y[30]))
            elif t < y[32]:
                pwl_decomress[h, w] = int(x[31] + (t - y[31]) * (x[32] - x[31]) / (y[32] - y[31]))
            elif t < y[33]:
                pwl_decomress[h, w] = int(x[32] + (t - y[32]) * (x[33] - x[32]) / (y[33] - y[32]))
            else:
                pwl_decomress[h, w] = int(16777215)'''

    return pwl_decomress