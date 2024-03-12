import numpy as np
#from PIL import Image
import cv2
from numpy import *

def nearest(img, size):
    height, width= img.shape
    n_height = size[0]
    n_width = size[1]
    n_img = np.zeros((n_height, n_width), dtype = float32)
    count = 0
    for i in range(n_height):
        for j in range(n_width):
            #print(i, j, k)
            x = float(i) * height / n_height
            y = float(j) * width / n_width
            n_img[i, j] = img[int(np.floor(x)), int(np.floor(y))]
        if count <= 30:
            print((np.floor(x), np.floor(y)))
            count += 1
    return np.uint8(n_img)

def double_linear(img, size):
    height, width= img.shape
    n_height = size[0]
    n_width = size[1]
    n_img = np.zeros(size, dtype = np.float32)
    for i in range(n_height):
        for j in range(n_width):
            src_x = (float(i) + 0.5) * height / n_height - 0.5
            src_y = (float(j) + 0.5) * width / n_width - 0.5
            src_x_0 = int(np.floor(src_x))
            src_y_0 = int(np.floor(src_y))
            src_x_1 = min(src_x_0 + 1, height - 1)
            src_y_1 = min(src_y_0 + 1, width - 1)
            #print(src_x, src_y, src_x_0, src_y_0, src_x_1, src_y_1)
            value0 = (src_x_1 - src_x) * img[src_x_0, src_y_0] + (src_x - src_x_0) * img[src_x_1, src_y_0]
            value1 = (src_x_1 - src_x) * img[src_x_0, src_y_1] + (src_x - src_x_0) * img[src_x_1, src_y_1]
            n_img[i, j] = int((src_y_1 - src_y) * value0 + (src_y - src_y_0) * value1)
    return np.uint8(n_img)

def demosaic_bilinear1(raw):
    pass
    rgb = np.zeros((raw.shape[0], raw.shape[1], 3), dtype=raw.dtype)
    for h in range(1, raw.shape[0] - 1):
        for w in range(1, raw.shape[1] - 1):
            p = (h % 2) * 2 + (w % 2)
            if p == 3:
                rgb[h, w, 0] = (raw[h - 1, w - 1] + raw[h - 1, w + 1] +
                                raw[h + 1, w - 1] + raw[h + 1, w + 1]) / 4
                rgb[h, w, 1] = (raw[h - 1, w] + raw[h, w - 1] + raw[h, w + 1] +
                                raw[h + 1, w]) / 4
                rgb[h, w, 2] = raw[h, w]
            elif p == 2:
                rgb[h, w, 0] = (raw[h - 1, w] + raw[h + 1, w]) / 2
                rgb[h, w, 1] = raw[h, w]
                rgb[h, w, 2] = (raw[h, w - 1] + raw[h, w + 1]) / 2
            elif p == 1:
                rgb[h, w, 0] = (raw[h, w - 1] + raw[h, w + 1]) / 2
                rgb[h, w, 1] = raw[h, w]
                rgb[h, w, 2] = (raw[h - 1, w] + raw[h + 1, w]) / 2
            elif p == 0:
                rgb[h, w, 0] = raw[h, w]
                rgb[h, w, 1] = (raw[h - 1, w] + raw[h, w - 1] + raw[h, w + 1] +
                                raw[h + 1, w]) / 4
                rgb[h, w, 2] = (raw[h - 1, w - 1] + raw[h - 1, w + 1] +
                                raw[h + 1, w - 1] + raw[h + 1, w + 1]) / 4
    return rgb

def bilinear_demosaic_fpga(raw8, height, width):
    #height, width = raw8.shape
    tmp8 = np.zeros((height+2, width+2), 'uint8')
    img  = np.zeros((height, width, 3), 'uint8')
    
    fd   = open('..\\py_img_demosaic.txt', 'w')

    for i in range(height):
        for j in range(width):
            tmp8[i+1][j+1]  = raw8[i][j]
    
    for j in range(width):
        tmp8[0][j+1]        = raw8[1][j]
        tmp8[height+1][j+1] = raw8[height-2][j]
        
    for j in range(height+2):
        tmp8[j][0]        = tmp8[j][2]
        tmp8[j][width+1]  = tmp8[j][width-1]

    for i in range(1, height+1):
        for j in range(1, width+1):
            if(i%2 == 1):
                if(j%2 == 1):
                    img[i-1][j-1][2] = tmp8[i][j]  #R
                    #img[i-1][j-1][1] = int(round(tmp8[i-1][j]/4.0 + tmp8[i][j-1]/4.0 + tmp8[i+1][j]/4.0 + tmp8[i][j+1]/4.0))  #G
                    #img[i-1][j-1][0] = int(round(tmp8[i-1][j-1]/4.0 + tmp8[i+1][j-1]/4.0 + tmp8[i-1][j+1]/4.0 + tmp8[i+1][j+1]/4.0))  #B
                    img[i-1][j-1][1] = int(round(tmp8[i-1][j]/4.0)) + int(round(tmp8[i][j-1]/4.0)) + int(round(tmp8[i+1][j]/4.0)) + int(round(tmp8[i][j+1]/4.0))  #G
                    img[i-1][j-1][0] = int(round(tmp8[i-1][j-1]/4.0)) + int(round(tmp8[i+1][j-1]/4.0)) + int(round(tmp8[i-1][j+1]/4.0)) + int(round(tmp8[i+1][j+1]/4.0))  #B
                else:
                    #img[i-1][j-1][2] = int(round(tmp8[i][j-1]/2.0 + tmp8[i][j+1]/2.0)) #R
                    img[i-1][j-1][2] = int(round(tmp8[i][j-1]/2.0)) + int(round(tmp8[i][j+1]/2.0)) #R
                    img[i-1][j-1][1] = tmp8[i][j] #G
                    #img[i-1][j-1][0] = int(round(tmp8[i-1][j]/2.0 + tmp8[i+1][j]/2.0)) #B
                    img[i-1][j-1][0] = int(round(tmp8[i-1][j]/2.0)) + int(round(tmp8[i+1][j]/2.0)) #B
            else:
                if(j%2 == 1):
                    #img[i-1][j-1][2] = int(round(tmp8[i-1][j]/2.0 + tmp8[i+1][j]/2.0)) #R
                    img[i-1][j-1][2] = int(round(tmp8[i-1][j]/2.0)) + int(round(tmp8[i+1][j]/2.0)) #R
                    img[i-1][j-1][1] = tmp8[i][j] #G
                    #img[i-1][j-1][0] = int(round(tmp8[i][j-1]/2.0 + tmp8[i][j+1]/2.0)) #B
                    img[i-1][j-1][0] = int(round(tmp8[i][j-1]/2.0)) + int(round(tmp8[i][j+1]/2.0)) #B
                else:
                    #img[i-1][j-1][2] = int(round(tmp8[i-1][j-1]/4.0 + tmp8[i+1][j-1]/4.0 + tmp8[i-1][j+1]/4.0 + tmp8[i+1][j+1]/4.0))  #R
                    #img[i-1][j-1][1] = int(round(tmp8[i-1][j]/4.0 + tmp8[i][j-1]/4.0 + tmp8[i+1][j]/4.0 + tmp8[i][j+1]/4.0))  #G
                    img[i-1][j-1][2] = int(round(tmp8[i-1][j-1]/4.0)) + int(round(tmp8[i+1][j-1]/4.0)) + int(round(tmp8[i-1][j+1]/4.0)) + int(round(tmp8[i+1][j+1]/4.0))  #R
                    img[i-1][j-1][1] = int(round(tmp8[i-1][j]/4.0)) + int(round(tmp8[i][j-1]/4.0)) + int(round(tmp8[i+1][j]/4.0)) + int(round(tmp8[i][j+1]/4.0))  #G
                    img[i-1][j-1][0] = tmp8[i][j] #B
    
    for i in range(height):        
        for j in range(width):   
            fd.write(str(img[i][j][2]))
            fd.write("\n")
            fd.write(str(img[i][j][1]))
            fd.write("\n")
            fd.write(str(img[i][j][0]))
            fd.write("\n")
                        
            #if(i == 0 and j < 32):
            #    print "img_r: %d, img_g: %d, img_b: %d," %(img[i][j][2], img[i][j][1], img[i][j][0])
    fd.close()
    return img

def gradient_correct_demosaic(raw):
    rgb = np.zeros((raw.shape[0], raw.shape[1], 3), dtype=np.float32)
    h = raw.shape[0]
    w = raw.shape[1]
    raw = raw.astype(np.float32)
    #raw = awb_gain_cal(raw)
    '''raw[::2, ::2] = cv2.bilateralFilter(raw[::2, ::2], 10, 7, 10)
    raw[1::2, 1::2] = cv2.bilateralFilter(raw[1::2, 1::2], 10, 7, 10)
    raw[1::2, ::2] = cv2.bilateralFilter(raw[1::2, ::2], 10, 7, 10)
    raw[::2, 1::2] = cv2.bilateralFilter(raw[::2, 1::2], 10, 7, 10)'''
    '''denoise = np.zeros((raw.shape[0], raw.shape[1]), dtype=np.float32)
    a = cv2.bilateralFilter(r, 10, 10, 100)
    b = cv2.bilateralFilter(r, 10, 10, 50)
    c = cv2.bilateralFilter(r, 10, 10, 25) '''
    '''d = r
    denoise[:540, :960] = a 
    denoise[:540, 960:] = b 
    denoise[540:, :960] = c 
    denoise[540:, 960:] = d'''

    '''for i in range(1080):
        for j in range(1920):
            if i > 1 and i < 1078 and j > 1 and j < 1918:
                g_B = 0
                g_R = 0
                g_Gb = 0
                g_Gr = 0
                if i % 2 != 0 and j % 2 != 0:
                    rgb[i, j, 2] = raw[i, j]
                    g_B = raw[i, j] - (raw[i - 2, j] + raw[i, j + 2] + raw[i + 2, j] + raw[i, j - 2]) / 4.0
                    rgb[i, j, 1] = (raw[i - 1, j] + raw[i, j + 1] + raw[i + 1, j] + raw[i, j - 1]) / 4.0 + g_B / 2.0 + 0.5
                    rgb[i, j, 0] = (raw[i - 1, j - 1] + raw[i + 1, j + 1] + raw[i + 1, j - 1] + raw[i - 1, j + 1]) / 4.0 + g_B * 0.75 + 0.5
                elif i % 2 == 0 and j % 2 == 0:
                    rgb[i, j, 0] = raw[i, j]
                    g_R = raw[i, j] - (raw[i - 2, j] + raw[i, j + 2] + raw[i + 2, j] + raw[i, j - 2]) / 4.0
                    rgb[i, j, 1] = (raw[i - 1, j] + raw[i, j + 1] + raw[i + 1, j] + raw[i, j - 1]) / 4.0 + g_R / 2.0 + 0.5
                    rgb[i, j, 2] = (raw[i - 1, j - 1] + raw[i + 1, j + 1] + raw[i + 1, j - 1] + raw[i - 1, j + 1]) / 4.0 + g_R * 0.75 + 0.5
                elif i % 2 != 0 and j % 2 == 0:
                    rgb[i, j, 1] = raw[i, j]
                    g_Gb = raw[i, j] - (raw[i - 1, j - 1] + raw[i + 1, j + 1] + raw[i + 1, j - 1] + raw[i - 1, j + 1] + raw[i, j - 2] + raw[i, j + 2] - (raw[i - 2, j] + raw[i + 2, j]) / 2.0) / 5.0
                    rgb[i, j, 2] = (raw[i, j - 1] + raw[i, j + 1]) / 2.0 + g_Gb * 0.625 + 0.5
                    g_Gr = raw[i, j] - (raw[i - 1, j - 1] + raw[i + 1, j + 1] + raw[i + 1, j - 1] + raw[i - 1, j + 1] + raw[i + 2, j] + raw[i - 2, j] - (raw[i, j - 2] + raw[i, j + 2]) / 2.0) / 5.0
                    rgb[i, j, 0] = (raw[i - 1, j] + raw[i + 1, j]) / 2.0 + g_Gr * 0.625 + 0.5
                elif i % 2 == 0 and j % 2 != 0:
                    rgb[i, j, 1] = raw[i, j]
                    g_Gr = raw[i, j] - (raw[i - 1, j - 1] + raw[i + 1, j + 1] + raw[i + 1, j - 1] + raw[i - 1, j + 1] + raw[i, j - 2] + raw[i, j + 2] - (raw[i - 2, j] + raw[i + 2, j]) / 2.0) / 5.0
                    rgb[i, j, 0] = (raw[i, j - 1] + raw[i, j + 1]) / 2.0 + g_Gr * 0.625 + 0.5
                    g_Gb = raw[i, j] - (raw[i - 1, j - 1] + raw[i + 1, j + 1] + raw[i + 1, j - 1] + raw[i - 1, j + 1] + raw[i + 2, j] + raw[i - 2, j] - (raw[i, j - 2] + raw[i, j + 2]) / 2.0) / 5.0
                    rgb[i, j, 2] = (raw[i - 1, j] + raw[i + 1, j]) / 2.0 + g_Gb * 0.625 + 0.5
            else:
                pass'''

    '''#padding
    new_raw = np.zeros((raw.shape[0] + 4, raw.shape[1] + 4), dtype=np.float32)
    new_raw[2:1082, 2:1922] = raw
    new_raw[:2, 2:1922] = raw[:2,:]
    new_raw[-2:, 2:1922] = raw[-2:,:]
    new_raw[2:1082, :2] = raw[:,:2]
    new_raw[2:1082, -2:] = raw[:,-2:]

    rgb[0:1080:2, 0:1920:2, 0] = new_raw[2:1082:2, 2:1922:2]
    g_R = new_raw[2:1082:2, 2:1922:2] - (new_raw[0:1080:2, 2:1922:2] + new_raw[4:1084:2, 2:1922:2] + new_raw[2:1082:2, 0:1920:2] + new_raw[2:1082:2, 4:1924:2]) / 4.0
    rgb[0:1080:2, 0:1920:2, 1] = (new_raw[1:1081:2, 2:1922:2] + new_raw[3:1083:2, 2:1922:2] + new_raw[2:1082:2, 1:1921:2] + new_raw[2:1082:2, 3:1923:2]) / 4.0 + g_R * 0.5 + 0.5
    rgb[0:1080:2, 0:1920:2, 2] = (new_raw[1:1081:2, 1:1921:2] + new_raw[3:1083:2, 3:1923:2] + new_raw[3:1083:2, 1:1921:2] + new_raw[1:1081:2, 3:1923:2]) / 4.0 + g_R * 0.75 + 0.5

    rgb[1:1081:2, 1:1921:2, 2] = new_raw[3:1083:2, 3:1923:2]
    g_B = new_raw[3:1083:2, 3:1923:2] - (new_raw[1:1081:2, 3:1923:2] + new_raw[5:1084:2, 3:1923:2] + new_raw[3:1083:2, 1:1921:2] + new_raw[3:1083:2, 5:1924:2]) / 4.0
    rgb[1:1081:2, 1:1921:2, 1] = (new_raw[2:1082:2, 3:1923:2] + new_raw[4:1084:2, 3:1923:2] + new_raw[3:1083:2, 2:1922:2] + new_raw[3:1083:2, 4:1924:2]) / 4.0 + g_B * 0.5 + 0.5
    rgb[1:1081:2, 1:1921:2, 0] = (new_raw[2:1082:2, 2:1922:2] + new_raw[4:1084:2, 4:1924:2] + new_raw[4:1084:2, 2:1922:2] + new_raw[2:1082:2, 4:1924:2]) / 4.0 + g_B * 0.75 + 0.5

    rgb[0:1080:2, 1:1921:2, 1] = new_raw[2:1082:2, 3:1923:2]
    g_Gr = new_raw[2:1082:2, 3:1923:2] - (new_raw[1:1081:2, 2:1922:2] + new_raw[3:1083:2, 4:1924:2] + new_raw[1:1081:2, 4:1924:2] + new_raw[3:1083:2, 2:1922:2] + new_raw[2:1082:2, 1:1921:2] + new_raw[2:1082:2, 5:1924:2] - (new_raw[0:1080:2, 3:1923:2] + new_raw[4:1084:2, 3:1923:2]) * 0.5 ) * 0.2
    rgb[0:1080:2, 1:1921:2, 0] = (new_raw[2:1082:2, 2:1922:2] + new_raw[2:1082:2, 4:1924:2]) * 0.5 + g_Gr * 0.625 + 0.5
    g_Gb = new_raw[2:1082:2, 3:1923:2] - (new_raw[1:1081:2, 2:1922:2] + new_raw[3:1083:2, 4:1924:2] + new_raw[1:1081:2, 4:1924:2] + new_raw[3:1083:2, 2:1922:2] + new_raw[0:1080:2, 3:1923:2] + new_raw[4:1084:2, 3:1923:2] - (new_raw[2:1082:2, 1:1921:2] + new_raw[2:1082:2, 5:1924:2]) * 0.5 ) * 0.2
    rgb[0:1080:2, 1:1921:2, 2] = (new_raw[1:1081:2, 3:1923:2] + new_raw[3:1083:2, 3:1923:2]) * 0.5 + g_Gb * 0.625 + 0.5

    rgb[1:1081:2, 0:1920:2, 1] = new_raw[3:1083:2, 2:1922:2]
    g_gB = new_raw[3:1083:2, 2:1922:2] - (new_raw[2:1082:2, 1:1921:2] + new_raw[4:1084:2, 3:1923:2] + new_raw[2:1082:2, 3:1923:2] + new_raw[4:1084:2, 1:1921:2] + new_raw[3:1083:2, 0:1920:2] + new_raw[3:1083:2, 4:1924:2] - (new_raw[1:1081:2, 2:1922:2] + new_raw[5:1084:2, 2:1922:2]) * 0.5 ) * 0.2
    rgb[1:1081:2, 0:1920:2, 2] = (new_raw[3:1083:2, 1:1921:2] + new_raw[3:1083:2, 3:1923:2]) * 0.5 + g_gB * 0.625 + 0.5
    g_gR = new_raw[3:1083:2, 2:1922:2] - (new_raw[2:1082:2, 1:1921:2] + new_raw[4:1084:2, 3:1923:2] + new_raw[2:1082:2, 3:1923:2] + new_raw[4:1084:2, 1:1921:2] + new_raw[1:1081:2, 2:1922:2] + new_raw[5:1084:2, 2:1922:2] - (new_raw[3:1083:2, 0:1920:2] + new_raw[3:1083:2, 4:1924:2]) * 0.5 ) * 0.2
    rgb[1:1081:2, 0:1920:2, 0] = (new_raw[4:1084:2, 2:1922:2] + new_raw[2:1082:2, 2:1922:2]) * 0.5 + g_gR * 0.625 + 0.5

    #all
    rgb[0:1080:2, 0:1920:2, 0] = raw[0:1080:2, 0:1920:2]
    g_R = raw[0:1080:2, 0:1920:2] - (raw[-2:1078:2, 0:1920:2] + raw[2:1082:2, 0:1920:2] + raw[0:1080:2, -2:1918:2] + raw[0:1080:2, 2:1922:2]) / 4.0
    rgb[0:1080:2, 0:1920:2, 1] = (raw[-1:1079:2, 0:1920:2] + raw[1:1081:2, 0:1920:2] + raw[0:1080:2, -1:1919:2] + raw[0:1080:2, 1:1921:2]) / 4.0 + g_R * 0.5 + 0.5
    rgb[0:1080:2, 0:1920:2, 2] = (raw[-1:1079:2, -1:1919:2] + raw[1:1081:2, 1:1921:2] + raw[1:1081:2, -1:1919:2] + raw[-1:1079:2, 1:1921:2]) / 4.0 + g_R * 0.75 + 0.5

    rgb[1:1081:2, 1:1921:2, 2] = raw[1:1081:2, 1:1921:2]
    g_B = raw[1:1081:2, 1:1921:2] - (raw[-1:1079:2, 1:1921:2] + raw[3:1082:2, 1:1921:2] + raw[1:1081:2, -1:1919:2] + raw[1:1081:2, 3:1922:2]) / 4.0
    rgb[1:1081:2, 1:1921:2, 1] = (raw[0:1080:2, 1:1921:2] + raw[2:1082:2, 1:1921:2] + raw[1:1081:2, 0:1920:2] + raw[1:1081:2, 2:1922:2]) / 4.0 + g_B * 0.5 + 0.5
    rgb[1:1081:2, 1:1921:2, 0] = (raw[0:1080:2, 0:1920:2] + raw[2:1082:2, 2:1922:2] + raw[2:1082:2, 0:1920:2] + raw[0:1080:2, 2:1922:2]) / 4.0 + g_B * 0.75 + 0.5

    rgb[0:1080:2, 1:1921:2, 1] = raw[0:1080:2, 1:1921:2]
    g_Gr = raw[0:1080:2, 1:1921:2] - (raw[-1:1079:2, 0:1920:2] + raw[1:1081:2, 2:1922:2] + raw[-1:1079:2, 2:1922:2] + raw[1:1081:2, 0:1920:2] + raw[0:1080:2, -1:1919:2] + raw[0:1080:2, 3:1922:2] - (raw[-2:1078:2, 1:1921:2] + raw[2:1082:2, 1:1921:2]) * 0.5 ) * 0.2
    rgb[0:1080:2, 1:1921:2, 0] = (raw[0:1080:2, 0:1920:2] + raw[0:1080:2, 2:1922:2]) * 0.5 + g_Gr * 0.625 + 0.5
    g_Gb = raw[0:1080:2, 1:1921:2] - (raw[-1:1079:2, 0:1920:2] + raw[1:1081:2, 2:1922:2] + raw[-1:1079:2, 2:1922:2] + raw[1:1081:2, 0:1920:2] + raw[-2:1078:2, 1:1921:2] + raw[2:1082:2, 1:1921:2] - (raw[0:1080:2, -1:1919:2] + raw[0:1080:2, 3:1922:2]) * 0.5 ) * 0.2
    rgb[0:1080:2, 1:1921:2] = (raw[-1:1079:2, 1:1921:2] + raw[1:1081:2, 1:1921:2]) * 0.5 + g_Gb * 0.625 + 0.5

    rgb[1:1081:2, 0:1920:2, 1] = raw[1:1081:2, 0:1920:2]
    g_gB = raw[1:1081:2, 0:1920:2] - (raw[0:1080:2, -1:1919:2] + raw[2:1082:2, 1:1921:2] + raw[0:1080:2, 1:1921:2] + raw[2:1082:2, -1:1919:2] + raw[1:1081:2, -2:1918:2] + raw[1:1081:2, 2:1922:2] - (raw[-1:1079:2, 0:1920:2] + raw[3:1082:2, 0:1920:2]) * 0.5 ) * 0.2
    rgb[1:1081:2, 0:1920:2, 2] = (raw[1:1081:2, -1:1919:2] + raw[1:1081:2, 1:1921:2]) * 0.5 + g_gB * 0.625 + 0.5
    g_gR = raw[1:1081:2, 0:1920:2] - (raw[0:1080:2, -1:1919:2] + raw[2:1082:2, 1:1921:2] + raw[0:1080:2, 1:1921:2] + raw[2:1082:2, -1:1919:2] + raw[-1:1079:2, 0:1920:2] + raw[3:1082:2, 0:1920:2] - (raw[1:1081:2, -2:1918:2] + raw[1:1081:2, 2:1922:2]) * 0.5 ) * 0.2
    rgb[1:1081:2, 0:1920:2] = (raw[2:1082:2, 0:1920:2] + raw[0:1080:2, 0:1920:2]) * 0.5 + g_gR * 0.625 + 0.5'''
    #body
    rgb[2:h-2:2, 2:w-2:2, 0] = raw[2:h-2:2, 2:w-2:2]
    g_R = raw[2:h-2:2, 2:w-2:2] - (raw[0:h-4:2, 2:w-2:2] + raw[4:h:2, 2:w-2:2] + raw[2:h-2:2, 0:w-4:2] + raw[2:h-2:2, 4:w:2]) / 4.0
    rgb[2:h-2:2, 2:w-2:2, 1] = (raw[1:h-3:2, 2:w-2:2] + raw[3:h-1:2, 2:w-2:2] + raw[2:h-2:2, 1:w-3:2] + raw[2:h-2:2, 3:w-1:2]) / 4.0 + g_R * 0.5 + 0.5
    rgb[2:h-2:2, 2:w-2:2, 2] = (raw[1:h-3:2, 1:w-3:2] + raw[3:h-1:2, 3:w-1:2] + raw[3:h-1:2, 1:w-3:2] + raw[1:h-3:2, 3:w-1:2]) / 4.0 + g_R * 0.75 + 0.5

    rgb[3:h-1:2, 3:w-1:2, 2] = raw[3:h-1:2, 3:w-1:2]
    g_B = raw[3:h-1:2, 3:w-1:2] - (raw[1:h-3:2, 3:w-1:2] + raw[5:h:2, 3:w-1:2] + raw[3:h-1:2, 1:w-3:2] + raw[3:h-1:2, 5:w:2]) / 4.0
    rgb[3:h-1:2, 3:w-1:2, 1] = (raw[2:h-2:2, 3:w-1:2] + raw[4:h:2, 3:w-1:2] + raw[3:h-1:2, 2:w-2:2] + raw[3:h-1:2, 4:w:2]) / 4.0 + g_B * 0.5 + 0.5
    rgb[3:h-1:2, 3:w-1:2, 0] = (raw[2:h-2:2, 2:w-2:2] + raw[4:h:2, 4:w:2] + raw[4:h:2, 2:w-2:2] + raw[2:h-2:2, 4:w:2]) / 4.0 + g_B * 0.75 + 0.5

    rgb[2:h-2:2, 3:w-1:2, 1] = raw[2:h-2:2, 3:w-1:2]
    g_Gr = raw[2:h-2:2, 3:w-1:2] - (raw[1:h-3:2, 2:w-2:2] + raw[3:h-1:2, 4:w:2] + raw[1:h-3:2, 4:w:2] + raw[3:h-1:2, 2:w-2:2] + raw[2:h-2:2, 1:w-3:2] + raw[2:h-2:2, 5:w:2] - (raw[0:h-4:2, 3:w-1:2] + raw[4:h:2, 3:w-1:2]) * 0.5 ) * 0.2
    rgb[2:h-2:2, 3:w-1:2, 0] = (raw[2:h-2:2, 2:w-2:2] + raw[2:h-2:2, 4:w:2]) * 0.5 + g_Gr * 0.625 + 0.5
    g_Gb = raw[2:h-2:2, 3:w-1:2] - (raw[1:h-3:2, 2:w-2:2] + raw[3:h-1:2, 4:w:2] + raw[1:h-3:2, 4:w:2] + raw[3:h-1:2, 2:w-2:2] + raw[0:h-4:2, 3:w-1:2] + raw[4:h:2, 3:w-1:2] - (raw[2:h-2:2, 1:w-3:2] + raw[2:h-2:2, 5:w:2]) * 0.5 ) * 0.2
    rgb[2:h-2:2, 3:w-1:2, 2] = (raw[1:h-3:2, 3:w-1:2] + raw[3:h-1:2, 3:w-1:2]) * 0.5 + g_Gb * 0.625 + 0.5

    rgb[3:h-1:2, 2:w-2:2, 1] = raw[3:h-1:2, 2:w-2:2]
    g_gB = raw[3:h-1:2, 2:w-2:2] - (raw[2:h-2:2, 1:w-3:2] + raw[4:h:2, 3:w-1:2] + raw[2:h-2:2, 3:w-1:2] + raw[4:h:2, 1:w-3:2] + raw[3:h-1:2, 0:w-4:2] + raw[3:h-1:2, 4:w:2] - (raw[1:h-3:2, 2:w-2:2] + raw[5:h:2, 2:w-2:2]) * 0.5 ) * 0.2
    rgb[3:h-1:2, 2:w-2:2, 2] = (raw[3:h-1:2, 1:w-3:2] + raw[3:h-1:2, 3:w-1:2]) * 0.5 + g_gB * 0.625 + 0.5
    g_gR = raw[3:h-1:2, 2:w-2:2] - (raw[2:h-2:2, 1:w-3:2] + raw[4:h:2, 3:w-1:2] + raw[2:h-2:2, 3:w-1:2] + raw[4:h:2, 1:w-3:2] + raw[1:h-3:2, 2:w-2:2] + raw[5:h:2, 2:w-2:2] - (raw[3:h-1:2, 0:w-4:2] + raw[3:h-1:2, 4:w:2]) * 0.5 ) * 0.2
    rgb[3:h-1:2, 2:w-2:2, 0] = (raw[4:h:2, 2:w-2:2] + raw[2:h-2:2, 2:w-2:2]) * 0.5 + g_gR * 0.625 + 0.5

    #top
    rgb[0, 2:w-2:2, 0] = raw[0, 2:w-2:2]
    g_R0 = raw[0, 2:w-2:2] - (raw[0, 0:w-4:2] + raw[0, 4:w:2] + raw[2, 2:w-2:2]) / 3.0
    rgb[0, 2:w-2:2, 1] = (raw[0, 1:w-3:2] + raw[1, 2:w-2:2] + raw[0, 3:w-1:2]) / 3.0 + g_R0 * 0.5 + 0.5
    rgb[0, 2:w-2:2, 2] = (raw[1, 1:w-3:2] + raw[1, 3:w-1:2]) / 2.0 + g_R0 * 0.75 + 0.5

    rgb[1, 3:w-1:2, 2] = raw[1, 3:w-1:2]
    g_B0 = raw[1, 3:w-1:2] - (raw[1, 1:w-3:2] + raw[1, 5:w:2] + raw[3, 3:w-1:2]) / 3.0
    rgb[1, 3:w-1:2, 1] = (raw[0, 3:w-1:2] + raw[1, 2:w-2:2] + raw[1, 4:w:2] + raw[2, 3:w-1:2]) / 4.0 + g_B0 * 0.5 + 0.5
    rgb[1, 3:w-1:2, 0] = (raw[0, 2:w-2:2] + raw[2, 2:w-2:2] + raw[0, 4:w:2] + raw[2, 4:w:2]) / 4.0 + g_B0 * 0.75 + 0.5

    rgb[0, 3:w-1:2, 1] = raw[0, 3:w-1:2]
    g_Gr0 = raw[0, 3:w-1:2] - (raw[0, 1:w-3:2] + raw[0, 5:w:2] + raw[1, 2:w-2:2] + raw[1, 4:w:2] - 0.5 * raw[2, 3:w-1:2]) / 3.5
    rgb[0, 3:w-1:2, 0] = (raw[0, 2:w-2:2] + raw[0, 4:w:2]) * 0.5 + g_Gr0 * 0.625 + 0.5
    g_Gb0 = raw[0, 3:w-1:2] - (raw[2, 3:w-1:2] + raw[1, 2:w-2:2] + raw[1, 4:w:2] - 0.5 * (raw[0, 1:w-3:2] + raw[0, 5:w:2])) / 2.0
    rgb[0, 3:w-1:2, 2] = raw[1, 3:w-1:2] + g_Gb0 * 0.625 + 0.5

    rgb[1, 2:w-2:2, 1] = raw[1, 2:w-2:2]
    g_gB0 = raw[1, 2:w-2:2] - (raw[0, 1:w-3:2] + raw[2, 3:w-1:2] + raw[0, 3:w-1:2] + raw[2, 1:w-3:2] + raw[1, 0:w-4:2] + raw[1, 4:w:2] - 0.5 * raw[3, 2:w-2:2]) / 5.5
    rgb[1, 2:w-2:2, 2] = (raw[1, 1:w-3:2] + raw[1, 3:w-1:2]) * 0.5 + g_gB0 * 0.625 + 0.5
    g_gR0 = raw[1, 2:w-2:2] - (raw[0, 1:w-3:2] + raw[2, 3:w-1:2] + raw[0, 3:w-1:2] + raw[2, 1:w-3:2] + raw[3, 2:w-2:2] - 0.5 * (raw[1, 0:w-4:2] + raw[1, 4:w:2])) / 4.0
    rgb[1, 2:w-2:2, 0] = (raw[0, 2:w-2:2] + raw[3, 2:w-2:2]) * 0.5 + g_gR0 * 0.625 + 0.5

    #down
    rgb[h-2, 2:w-2:2, 0] = raw[h-2, 2:w-2:2]
    g_R1 = raw[h-2, 2:w-2:2] - (raw[h-2, 0:w-4:2] + raw[h-2, 4:w:2] + raw[h-4, 2:w-2:2]) / 3.0
    rgb[h-2, 2:w-2:2, 1] = (raw[h-2, 1:w-3:2] + raw[h-3, 2:w-2:2] + raw[h-2, 3:w-1:2] + raw[h-1, 2:w-2:2]) / 4.0 + g_R1 * 0.5 + 0.5
    rgb[h-2, 2:w-2:2, 2] = (raw[h-3, 1:w-3:2] + raw[h-3, 3:w-1:2] + raw[h-1, 1:w-3:2] + raw[h-1, 3:w-1:2]) / 4.0 + g_R1 * 0.75 + 0.5

    rgb[h-1, 3:w-1:2, 2] = raw[h-1, 3:w-1:2]
    g_B1 = raw[h-1, 3:w-1:2] - (raw[h-1, 1:w-3:2] + raw[h-1, 5:w:2] + raw[h-3, 3:w-1:2]) / 3.0
    rgb[h-1, 3:w-1:2, 1] = (raw[h-2, 3:w-1:2] + raw[h-1, 2:w-2:2] + raw[h-1, 4:w:2]) / 3.0 + g_B1 * 0.5 + 0.5
    rgb[h-1, 3:w-1:2, 0] = (raw[h-2, 2:w-2:2] + raw[h-2, 4:w:2]) / 2.0 + g_B1 * 0.75 + 0.5

    rgb[h-2, 3:w-1:2, 1] = raw[h-2, 3:w-1:2]
    g_Gr1 = raw[h-2, 3:w-1:2] - (raw[h-2, 1:w-3:2] + raw[h-2, 5:w:2] + raw[h-3, 2:w-2:2] + raw[h-1, 4:w:2] + raw[h-3, 4:w:2] + raw[h-1, 2:w-2:2] - 0.5 * raw[h-4, 3:w-1:2]) / 5.5
    rgb[h-2, 3:w-1:2, 0] = (raw[h-2, 2:w-2:2] + raw[h-2, 4:w:2]) * 0.5 + g_Gr1 * 0.625 + 0.5
    g_Gb1 = raw[h-2, 3:w-1:2] - (raw[h-3, 2:w-2:2] + raw[h-1, 4:w:2] + raw[h-3, 4:w:2] + raw[h-1, 2:w-2:2] + raw[h-4, 3:w-1:2] - 0.5 * (raw[h-2, 1:w-3:2] + raw[h-2, 5:w:2])) / 4.0
    rgb[h-2, 3:w-1:2, 2] = (raw[h-3, 3:w-1:2] + raw[h-1, 3:w-1:2]) * 0.5 + g_Gb1 * 0.625 + 0.5

    rgb[h-1, 2:w-2:2, 1] = raw[h-1, 2:w-2:2]
    g_gB1 = raw[h-1, 2:w-2:2] - (raw[h-2, 1:w-3:2] + raw[h-2, 3:w-1:2] + raw[h-1, 0:w-4:2] + raw[h-1, 4:w:2] - 0.5 * raw[h-3, 2:w-2:2]) / 3.5
    rgb[h-1, 2:w-2:2, 2] = (raw[h-1, 1:w-3:2] + raw[h-1, 3:w-1:2]) * 0.5 + g_gB1 * 0.625 + 0.5
    g_gR1 = raw[h-1, 2:w-2:2] - (raw[h-2, 1:w-3:2] + raw[h-2, 3:w-1:2] + raw[h-3, 2:w-2:2] - 0.5 * (raw[h-1, 0:w-4:2] + raw[h-1, 4:w:2])) / 2.0
    rgb[h-1, 2:w-2:2, 0] = raw[h-2, 2:w-2:2] + g_gR1 * 0.625 + 0.5

    #left
    rgb[2:h-2:2, 0, 0] = raw[2:h-2:2, 0]
    g_R2 = raw[2:h-2:2, 0] - (raw[0:h-4:2, 0] + raw[4:h:2, 0] + raw[2:h-2:2, 2]) / 3.0
    rgb[2:h-2:2, 0, 1] = (raw[1:h-3:2, 0] + raw[3:h-1:2, 0] + raw[2:h-2:2, 1]) / 3.0 + g_R2 * 0.5 + 0.5
    rgb[2:h-2:2, 0, 2] = (raw[1:h-3:2, 1] + raw[3:h-1:2, 1]) / 2.0 + g_R2 * 0.75 + 0.5

    rgb[3:h-1:2, 1, 2] = raw[3:h-1:2, 1]
    g_B2 = raw[3:h-1:2, 1] - (raw[1:h-3:2, 1] + raw[5:h:2, 1] + raw[3:h-1:2, 3]) / 3.0
    rgb[3:h-1:2, 1, 1] = (raw[3:h-1:2, 0] + raw[3:h-1:2, 2] + raw[4:h:2, 1] + raw[2:h-2:2, 1]) / 4.0 + g_B2 * 0.5 + 0.5
    rgb[3:h-1:2, 1, 0] = (raw[2:h-2:2, 0] + raw[4:h:2, 2] + raw[4:h:2, 0] + raw[2:h-2:2, 2]) / 4.0 + g_B2 * 0.75 + 0.5

    rgb[2:h-2:2, 1, 1] = raw[2:h-2:2, 1]
    g_Gr2 = raw[2:h-2:2, 1] - (raw[1:h-3:2, 0] + raw[1:h-3:2, 2] + raw[3:h-1:2, 0] + raw[3:h-1:2, 2] + raw[2:h-2:2, 3] - 0.5 * (raw[4:h:2, 1] + raw[0:h-4:2, 1])) / 4.0
    rgb[2:h-2:2, 1, 0] = (raw[2:h-2:2, 0] + raw[2:h-2:2, 2]) * 0.5 + g_Gr2 * 0.625 + 0.5
    g_Gb2 = raw[2:h-2:2, 1] - (raw[1:h-3:2, 0] + raw[1:h-3:2, 2] + raw[3:h-1:2, 0] + raw[3:h-1:2, 2] + raw[4:h:2, 1] + raw[0:h-4:2, 1] - 0.5 * raw[2:h-2:2, 3]) / 5.5
    rgb[2:h-2:2, 1, 2] = (raw[3:h-1:2, 1] + raw[1:h-3:2, 1]) * 0.5 + g_Gb2 * 0.625 + 0.5

    rgb[3:h-1:2, 0, 1] = raw[3:h-1:2, 0]
    g_gB2 = raw[3:h-1:2, 0] - (raw[2:h-2:2, 1] + raw[4:h:2, 1] + raw[3:h-1:2, 2] - 0.5 * (raw[4:h:2, 0] + raw[0:h-4:2, 0])) / 4.0
    rgb[3:h-1:2, 0, 2] = raw[3:h-1:2, 1] + g_gB2 * 0.625 + 0.5
    g_gR2 = raw[3:h-1:2, 0] - (raw[2:h-2:2, 1] + raw[4:h:2, 1] + raw[4:h:2, 0] + raw[0:h-4:2, 0] - 0.5 * raw[3:h-1:2, 2]) / 3.5
    rgb[3:h-1:2, 0, 0] = (raw[2:h-2:2, 0] + raw[4:h:2, 0]) * 0.5 + g_gR2 * 0.625 + 0.5

    #right
    rgb[2:h-2:2, w-2, 0] = raw[2:h-2:2, w-2]
    g_R3 = raw[2:h-2:2, w-2] - (raw[0:h-4:2, w-2] + raw[4:h:2, w-2] + raw[2:h-2:2, w-4]) / 3.0
    rgb[2:h-2:2, w-2, 1] = (raw[1:h-3:2, w-2] + raw[2:h-2:2, w-1] + raw[3:h-1:2, w-2] + raw[2:h-2:2, w-3]) / 4.0 + g_R3 * 0.5 + 0.5
    rgb[2:h-2:2, w-2, 2] = (raw[1:h-3:2, w-3] + raw[1:h-3:2, w-1] + raw[3:h-1:2, w-3] + raw[3:h-1:2, w-1]) / 4.0 + g_R3 * 0.75 + 0.5

    rgb[3:h-1:2, w-1, 2] = raw[3:h-1:2, w-1]
    g_B3 = raw[3:h-1:2, w-1] - (raw[1:h-3:2, w-1] + raw[5:h:2, w-1] + raw[3:h-1:2, w-3]) / 3.0
    rgb[3:h-1:2, w-1, 1] = (raw[3:h-1:2, w-2] + raw[2:h-2:2, w-1] + raw[4:h:2, w-1]) / 3.0 + g_B3 * 0.5 + 0.5
    rgb[3:h-1:2, w-1, 0] = (raw[2:h-2:2, w-2] + raw[2:h-2:2, w-2]) / 2.0 + g_B3 * 0.75 + 0.5

    rgb[2:h-2:2, w-1, 1] = raw[2:h-2:2, w-1]
    g_Gr3 = raw[2:h-2:2, w-1] - (raw[1:h-3:2, w-2] + raw[3:h-1:2, w-2] + raw[2:h-2:2, w-3] - 0.5 * (raw[0:h-4:2, w-1] + raw[4:h:2, w-1])) / 2.0
    rgb[2:h-2:2, w-1, 0] = raw[2:h-2:2, w-2] + g_Gr3 * 0.625 + 0.5
    g_Gb3 = raw[2:h-2:2, w-1] - (raw[1:h-3:2, w-2] + raw[3:h-1:2, w-2] + raw[0:h-4:2, w-1] + raw[4:h:2, w-1] - 0.5 * raw[2:h-2:2, w-3]) / 3.5
    rgb[2:h-2:2, w-1, 2] = (raw[3:h-1:2, w-1] + raw[1:h-3:2, w-1]) * 0.5 + g_Gb3 * 0.625 + 0.5

    rgb[3:h-1:2, w-2, 1] = raw[3:h-1:2, w-2]
    g_gB3 = raw[3:h-1:2, w-2] - (raw[2:h-2:2, w-3] + raw[2:h-2:2, w-1] + raw[4:h:2, w-3] + raw[4:h:2, w-1] + raw[3:h-1:2, w-4] - 0.5 * (raw[1:h-3:2, w-2] + raw[5:h:2, w-2])) / 4.0
    rgb[3:h-1:2, w-2, 2] = (raw[3:h-1:2, w-3] + raw[3:h-1:2, w-1]) * 0.5 + g_gB3 * 0.625 + 0.5
    g_gR3 = raw[3:h-1:2, w-2] - (raw[2:h-2:2, w-3] + raw[2:h-2:2, w-1] + raw[4:h:2, w-3] + raw[4:h:2, w-1] + raw[1:h-3:2, w-2] + raw[5:h:2, w-2] - 0.5 * raw[3:h-1:2, w-4]) / 5.5
    rgb[3:h-1:2, w-2, 0] = (raw[2:h-2:2, w-2] + raw[4:h:2, w-2]) * 0.5 + g_gR3 * 0.625 + 0.5

    '''#body bggr
    rgb[2:h-2:2, 2:w-2:2, 2] = raw[2:h-2:2, 2:w-2:2]
    g_R = raw[2:h-2:2, 2:w-2:2] - (raw[0:h-4:2, 2:w-2:2] + raw[4:h:2, 2:w-2:2] + raw[2:h-2:2, 0:w-4:2] + raw[2:h-2:2, 4:w:2]) / 4.0
    rgb[2:h-2:2, 2:w-2:2, 1] = (raw[1:h-3:2, 2:w-2:2] + raw[3:h-1:2, 2:w-2:2] + raw[2:h-2:2, 1:w-3:2] + raw[2:h-2:2, 3:w-1:2]) / 4.0 + g_R * 0.5 + 0.5
    rgb[2:h-2:2, 2:w-2:2, 0] = (raw[1:h-3:2, 1:w-3:2] + raw[3:h-1:2, 3:w-1:2] + raw[3:h-1:2, 1:w-3:2] + raw[1:h-3:2, 3:w-1:2]) / 4.0 + g_R * 0.75 + 0.5

    rgb[3:h-1:2, 3:w-1:2, 0] = raw[3:h-1:2, 3:w-1:2]
    g_B = raw[3:h-1:2, 3:w-1:2] - (raw[1:h-3:2, 3:w-1:2] + raw[5:h:2, 3:w-1:2] + raw[3:h-1:2, 1:w-3:2] + raw[3:h-1:2, 5:w:2]) / 4.0
    rgb[3:h-1:2, 3:w-1:2, 1] = (raw[2:h-2:2, 3:w-1:2] + raw[4:h:2, 3:w-1:2] + raw[3:h-1:2, 2:w-2:2] + raw[3:h-1:2, 4:w:2]) / 4.0 + g_B * 0.5 + 0.5
    rgb[3:h-1:2, 3:w-1:2, 2] = (raw[2:h-2:2, 2:w-2:2] + raw[4:h:2, 4:w:2] + raw[4:h:2, 2:w-2:2] + raw[2:h-2:2, 4:w:2]) / 4.0 + g_B * 0.75 + 0.5

    rgb[2:h-2:2, 3:w-1:2, 1] = raw[2:h-2:2, 3:w-1:2]
    g_Gr = raw[2:h-2:2, 3:w-1:2] - (raw[1:h-3:2, 2:w-2:2] + raw[3:h-1:2, 4:w:2] + raw[1:h-3:2, 4:w:2] + raw[3:h-1:2, 2:w-2:2] + raw[2:h-2:2, 1:w-3:2] + raw[2:h-2:2, 5:w:2] - (raw[0:h-4:2, 3:w-1:2] + raw[4:h:2, 3:w-1:2]) * 0.5 ) * 0.2
    rgb[2:h-2:2, 3:w-1:2, 2] = (raw[2:h-2:2, 2:w-2:2] + raw[2:h-2:2, 4:w:2]) * 0.5 + g_Gr * 0.625 + 0.5
    g_Gb = raw[2:h-2:2, 3:w-1:2] - (raw[1:h-3:2, 2:w-2:2] + raw[3:h-1:2, 4:w:2] + raw[1:h-3:2, 4:w:2] + raw[3:h-1:2, 2:w-2:2] + raw[0:h-4:2, 3:w-1:2] + raw[4:h:2, 3:w-1:2] - (raw[2:h-2:2, 1:w-3:2] + raw[2:h-2:2, 5:w:2]) * 0.5 ) * 0.2
    rgb[2:h-2:2, 3:w-1:2, 0] = (raw[1:h-3:2, 3:w-1:2] + raw[3:h-1:2, 3:w-1:2]) * 0.5 + g_Gb * 0.625 + 0.5

    rgb[3:h-1:2, 2:w-2:2, 1] = raw[3:h-1:2, 2:w-2:2]
    g_gB = raw[3:h-1:2, 2:w-2:2] - (raw[2:h-2:2, 1:w-3:2] + raw[4:h:2, 3:w-1:2] + raw[2:h-2:2, 3:w-1:2] + raw[4:h:2, 1:w-3:2] + raw[3:h-1:2, 0:w-4:2] + raw[3:h-1:2, 4:w:2] - (raw[1:h-3:2, 2:w-2:2] + raw[5:h:2, 2:w-2:2]) * 0.5 ) * 0.2
    rgb[3:h-1:2, 2:w-2:2, 0] = (raw[3:h-1:2, 1:w-3:2] + raw[3:h-1:2, 3:w-1:2]) * 0.5 + g_gB * 0.625 + 0.5
    g_gR = raw[3:h-1:2, 2:w-2:2] - (raw[2:h-2:2, 1:w-3:2] + raw[4:h:2, 3:w-1:2] + raw[2:h-2:2, 3:w-1:2] + raw[4:h:2, 1:w-3:2] + raw[1:h-3:2, 2:w-2:2] + raw[5:h:2, 2:w-2:2] - (raw[3:h-1:2, 0:w-4:2] + raw[3:h-1:2, 4:w:2]) * 0.5 ) * 0.2
    rgb[3:h-1:2, 2:w-2:2, 2] = (raw[4:h:2, 2:w-2:2] + raw[2:h-2:2, 2:w-2:2]) * 0.5 + g_gR * 0.625 + 0.5

    #top
    rgb[0, 2:w-2:2, 2] = raw[0, 2:w-2:2]
    g_R0 = raw[0, 2:w-2:2] - (raw[0, 0:w-4:2] + raw[0, 4:w:2] + raw[2, 2:w-2:2]) / 3.0
    rgb[0, 2:w-2:2, 1] = (raw[0, 1:w-3:2] + raw[1, 2:w-2:2] + raw[0, 3:w-1:2]) / 3.0 + g_R0 * 0.5 + 0.5
    rgb[0, 2:w-2:2, 0] = (raw[1, 1:w-3:2] + raw[1, 3:w-1:2]) / 2.0 + g_R0 * 0.75 + 0.5

    rgb[1, 3:w-1:2, 0] = raw[1, 3:w-1:2]
    g_B0 = raw[1, 3:w-1:2] - (raw[1, 1:w-3:2] + raw[1, 5:w:2] + raw[3, 3:w-1:2]) / 3.0
    rgb[1, 3:w-1:2, 1] = (raw[0, 3:w-1:2] + raw[1, 2:w-2:2] + raw[1, 4:w:2] + raw[2, 3:w-1:2]) / 4.0 + g_B0 * 0.5 + 0.5
    rgb[1, 3:w-1:2, 2] = (raw[0, 2:w-2:2] + raw[2, 2:w-2:2] + raw[0, 4:w:2] + raw[2, 4:w:2]) / 4.0 + g_B0 * 0.75 + 0.5

    rgb[0, 3:w-1:2, 1] = raw[0, 3:w-1:2]
    g_Gr0 = raw[0, 3:w-1:2] - (raw[0, 1:w-3:2] + raw[0, 5:w:2] + raw[1, 2:w-2:2] + raw[1, 4:w:2] - 0.5 * raw[2, 3:w-1:2]) / 3.5
    rgb[0, 3:w-1:2, 2] = (raw[0, 2:w-2:2] + raw[0, 4:w:2]) * 0.5 + g_Gr0 * 0.625 + 0.5
    g_Gb0 = raw[0, 3:w-1:2] - (raw[2, 3:w-1:2] + raw[1, 2:w-2:2] + raw[1, 4:w:2] - 0.5 * (raw[0, 1:w-3:2] + raw[0, 5:w:2])) / 2.0
    rgb[0, 3:w-1:2, 0] = raw[1, 3:w-1:2] + g_Gb0 * 0.625 + 0.5

    rgb[1, 2:w-2:2, 1] = raw[1, 2:w-2:2]
    g_gB0 = raw[1, 2:w-2:2] - (raw[0, 1:w-3:2] + raw[2, 3:w-1:2] + raw[0, 3:w-1:2] + raw[2, 1:w-3:2] + raw[1, 0:w-4:2] + raw[1, 4:w:2] - 0.5 * raw[3, 2:w-2:2]) / 5.5
    rgb[1, 2:w-2:2, 0] = (raw[1, 1:w-3:2] + raw[1, 3:w-1:2]) * 0.5 + g_gB0 * 0.625 + 0.5
    g_gR0 = raw[1, 2:w-2:2] - (raw[0, 1:w-3:2] + raw[2, 3:w-1:2] + raw[0, 3:w-1:2] + raw[2, 1:w-3:2] + raw[3, 2:w-2:2] - 0.5 * (raw[1, 0:w-4:2] + raw[1, 4:w:2])) / 4.0
    rgb[1, 2:w-2:2, 2] = (raw[0, 2:w-2:2] + raw[3, 2:w-2:2]) * 0.5 + g_gR0 * 0.625 + 0.5

    #down
    rgb[h-2, 2:w-2:2, 2] = raw[h-2, 2:w-2:2]
    g_R1 = raw[h-2, 2:w-2:2] - (raw[h-2, 0:w-4:2] + raw[h-2, 4:w:2] + raw[h-4, 2:w-2:2]) / 3.0
    rgb[h-2, 2:w-2:2, 1] = (raw[h-2, 1:w-3:2] + raw[h-3, 2:w-2:2] + raw[h-2, 3:w-1:2] + raw[h-1, 2:w-2:2]) / 4.0 + g_R1 * 0.5 + 0.5
    rgb[h-2, 2:w-2:2, 0] = (raw[h-3, 1:w-3:2] + raw[h-3, 3:w-1:2] + raw[h-1, 1:w-3:2] + raw[h-1, 3:w-1:2]) / 4.0 + g_R1 * 0.75 + 0.5

    rgb[h-1, 3:w-1:2, 0] = raw[h-1, 3:w-1:2]
    g_B1 = raw[h-1, 3:w-1:2] - (raw[h-1, 1:w-3:2] + raw[h-1, 5:w:2] + raw[h-3, 3:w-1:2]) / 3.0
    rgb[h-1, 3:w-1:2, 1] = (raw[h-2, 3:w-1:2] + raw[h-1, 2:w-2:2] + raw[h-1, 4:w:2]) / 3.0 + g_B1 * 0.5 + 0.5
    rgb[h-1, 3:w-1:2, 2] = (raw[h-2, 2:w-2:2] + raw[h-2, 4:w:2]) / 2.0 + g_B1 * 0.75 + 0.5

    rgb[h-2, 3:w-1:2, 1] = raw[h-2, 3:w-1:2]
    g_Gr1 = raw[h-2, 3:w-1:2] - (raw[h-2, 1:w-3:2] + raw[h-2, 5:w:2] + raw[h-3, 2:w-2:2] + raw[h-1, 4:w:2] + raw[h-3, 4:w:2] + raw[h-1, 2:w-2:2] - 0.5 * raw[h-4, 3:w-1:2]) / 5.5
    rgb[h-2, 3:w-1:2, 2] = (raw[h-2, 2:w-2:2] + raw[h-2, 4:w:2]) * 0.5 + g_Gr1 * 0.625 + 0.5
    g_Gb1 = raw[h-2, 3:w-1:2] - (raw[h-3, 2:w-2:2] + raw[h-1, 4:w:2] + raw[h-3, 4:w:2] + raw[h-1, 2:w-2:2] + raw[h-4, 3:w-1:2] - 0.5 * (raw[h-2, 1:w-3:2] + raw[h-2, 5:w:2])) / 4.0
    rgb[h-2, 3:w-1:2, 0] = (raw[h-3, 3:w-1:2] + raw[h-1, 3:w-1:2]) * 0.5 + g_Gb1 * 0.625 + 0.5

    rgb[h-1, 2:w-2:2, 1] = raw[h-1, 2:w-2:2]
    g_gB1 = raw[h-1, 2:w-2:2] - (raw[h-2, 1:w-3:2] + raw[h-2, 3:w-1:2] + raw[h-1, 0:w-4:2] + raw[h-1, 4:w:2] - 0.5 * raw[h-3, 2:w-2:2]) / 3.5
    rgb[h-1, 2:w-2:2, 0] = (raw[h-1, 1:w-3:2] + raw[h-1, 3:w-1:2]) * 0.5 + g_gB1 * 0.625 + 0.5
    g_gR1 = raw[h-1, 2:w-2:2] - (raw[h-2, 1:w-3:2] + raw[h-2, 3:w-1:2] + raw[h-3, 2:w-2:2] - 0.5 * (raw[h-1, 0:w-4:2] + raw[h-1, 4:w:2])) / 2.0
    rgb[h-1, 2:w-2:2, 2] = raw[h-2, 2:w-2:2] + g_gR1 * 0.625 + 0.5

    #left
    rgb[2:h-2:2, 0, 2] = raw[2:h-2:2, 0]
    g_R2 = raw[2:h-2:2, 0] - (raw[0:h-4:2, 0] + raw[4:h:2, 0] + raw[2:h-2:2, 2]) / 3.0
    rgb[2:h-2:2, 0, 1] = (raw[1:h-3:2, 0] + raw[3:h-1:2, 0] + raw[2:h-2:2, 1]) / 3.0 + g_R2 * 0.5 + 0.5
    rgb[2:h-2:2, 0, 0] = (raw[1:h-3:2, 1] + raw[3:h-1:2, 1]) / 2.0 + g_R2 * 0.75 + 0.5

    rgb[3:h-1:2, 1, 0] = raw[3:h-1:2, 1]
    g_B2 = raw[3:h-1:2, 1] - (raw[1:h-3:2, 1] + raw[5:h:2, 1] + raw[3:h-1:2, 3]) / 3.0
    rgb[3:h-1:2, 1, 1] = (raw[3:h-1:2, 0] + raw[3:h-1:2, 2] + raw[4:h:2, 1] + raw[2:h-2:2, 1]) / 4.0 + g_B2 * 0.5 + 0.5
    rgb[3:h-1:2, 1, 2] = (raw[2:h-2:2, 0] + raw[4:h:2, 2] + raw[4:h:2, 0] + raw[2:h-2:2, 2]) / 4.0 + g_B2 * 0.75 + 0.5

    rgb[2:h-2:2, 1, 1] = raw[2:h-2:2, 1]
    g_Gr2 = raw[2:h-2:2, 1] - (raw[1:h-3:2, 0] + raw[1:h-3:2, 2] + raw[3:h-1:2, 0] + raw[3:h-1:2, 2] + raw[2:h-2:2, 3] - 0.5 * (raw[4:h:2, 1] + raw[0:h-4:2, 1])) / 4.0
    rgb[2:h-2:2, 1, 2] = (raw[2:h-2:2, 0] + raw[2:h-2:2, 2]) * 0.5 + g_Gr2 * 0.625 + 0.5
    g_Gb2 = raw[2:h-2:2, 1] - (raw[1:h-3:2, 0] + raw[1:h-3:2, 2] + raw[3:h-1:2, 0] + raw[3:h-1:2, 2] + raw[4:h:2, 1] + raw[0:h-4:2, 1] - 0.5 * raw[2:h-2:2, 3]) / 5.5
    rgb[2:h-2:2, 1, 0] = (raw[3:h-1:2, 1] + raw[1:h-3:2, 1]) * 0.5 + g_Gb2 * 0.625 + 0.5

    rgb[3:h-1:2, 0, 1] = raw[3:h-1:2, 0]
    g_gB2 = raw[3:h-1:2, 0] - (raw[2:h-2:2, 1] + raw[4:h:2, 1] + raw[3:h-1:2, 2] - 0.5 * (raw[4:h:2, 0] + raw[0:h-4:2, 0])) / 4.0
    rgb[3:h-1:2, 0, 0] = raw[3:h-1:2, 1] + g_gB2 * 0.625 + 0.5
    g_gR2 = raw[3:h-1:2, 0] - (raw[2:h-2:2, 1] + raw[4:h:2, 1] + raw[4:h:2, 0] + raw[0:h-4:2, 0] - 0.5 * raw[3:h-1:2, 2]) / 3.5
    rgb[3:h-1:2, 0, 2] = (raw[2:h-2:2, 0] + raw[4:h:2, 0]) * 0.5 + g_gR2 * 0.625 + 0.5

    #right
    rgb[2:h-2:2, w-2, 2] = raw[2:h-2:2, w-2]
    g_R3 = raw[2:h-2:2, w-2] - (raw[0:h-4:2, w-2] + raw[4:h:2, w-2] + raw[2:h-2:2, w-4]) / 3.0
    rgb[2:h-2:2, w-2, 1] = (raw[1:h-3:2, w-2] + raw[2:h-2:2, w-1] + raw[3:h-1:2, w-2] + raw[2:h-2:2, w-3]) / 4.0 + g_R3 * 0.5 + 0.5
    rgb[2:h-2:2, w-2, 0] = (raw[1:h-3:2, w-3] + raw[1:h-3:2, w-1] + raw[3:h-1:2, w-3] + raw[3:h-1:2, w-1]) / 4.0 + g_R3 * 0.75 + 0.5

    rgb[3:h-1:2, w-1, 0] = raw[3:h-1:2, w-1]
    g_B3 = raw[3:h-1:2, w-1] - (raw[1:h-3:2, w-1] + raw[5:h:2, w-1] + raw[3:h-1:2, w-3]) / 3.0
    rgb[3:h-1:2, w-1, 1] = (raw[3:h-1:2, w-2] + raw[2:h-2:2, w-1] + raw[4:h:2, w-1]) / 3.0 + g_B3 * 0.5 + 0.5
    rgb[3:h-1:2, w-1, 2] = (raw[2:h-2:2, w-2] + raw[2:h-2:2, w-2]) / 2.0 + g_B3 * 0.75 + 0.5

    rgb[2:h-2:2, w-1, 1] = raw[2:h-2:2, w-1]
    g_Gr3 = raw[2:h-2:2, w-1] - (raw[1:h-3:2, w-2] + raw[3:h-1:2, w-2] + raw[2:h-2:2, w-3] - 0.5 * (raw[0:h-4:2, w-1] + raw[4:h:2, w-1])) / 2.0
    rgb[2:h-2:2, w-1, 2] = raw[2:h-2:2, w-2] + g_Gr3 * 0.625 + 0.5
    g_Gb3 = raw[2:h-2:2, w-1] - (raw[1:h-3:2, w-2] + raw[3:h-1:2, w-2] + raw[0:h-4:2, w-1] + raw[4:h:2, w-1] - 0.5 * raw[2:h-2:2, w-3]) / 3.5
    rgb[2:h-2:2, w-1, 0] = (raw[3:h-1:2, w-1] + raw[1:h-3:2, w-1]) * 0.5 + g_Gb3 * 0.625 + 0.5

    rgb[3:h-1:2, w-2, 1] = raw[3:h-1:2, w-2]
    g_gB3 = raw[3:h-1:2, w-2] - (raw[2:h-2:2, w-3] + raw[2:h-2:2, w-1] + raw[4:h:2, w-3] + raw[4:h:2, w-1] + raw[3:h-1:2, w-4] - 0.5 * (raw[1:h-3:2, w-2] + raw[5:h:2, w-2])) / 4.0
    rgb[3:h-1:2, w-2, 0] = (raw[3:h-1:2, w-3] + raw[3:h-1:2, w-1]) * 0.5 + g_gB3 * 0.625 + 0.5
    g_gR3 = raw[3:h-1:2, w-2] - (raw[2:h-2:2, w-3] + raw[2:h-2:2, w-1] + raw[4:h:2, w-3] + raw[4:h:2, w-1] + raw[1:h-3:2, w-2] + raw[5:h:2, w-2] - 0.5 * raw[3:h-1:2, w-4]) / 5.5
    rgb[3:h-1:2, w-2, 2] = (raw[2:h-2:2, w-2] + raw[4:h:2, w-2]) * 0.5 + g_gR3 * 0.625 + 0.5'''


    rgb[rgb > 255] = 255
    rgb[rgb < 0] = 0
    raw_img = np.zeros((raw.shape[0], raw.shape[1], 3), dtype=np.float32)
    '''raw_img[:,:,0] = rgb[:,:,2] * 0.72716749 - rgb[:,:,0] * 0.07907599 + rgb[:,:,1] * 0.3519085
    raw_img[:,:,1] = rgb[:,:,1] * 1.26974485 - rgb[:,:,0] * 0.11506455 - rgb[:,:,2] * 0.1546803
    raw_img[:,:,2] = rgb[:,:,0] * 0.66678476 + rgb[:,:,1] * 0.49068153 - rgb[:,:,2] * 0.15746629
    raw_img[raw_img > 255] = 255
    raw_img[raw_img < 0] = 0'''
    raw_img[:,:,0] = rgb[:,:,2]
    raw_img[:,:,1] = rgb[:,:,1]
    raw_img[:,:,2] = rgb[:,:,0]
    #a = raw_img[540,1000]
    #img = Image.fromarray(np.uint8(rgb))
    #img.save('/home/tusimple/workspace/20210412/390_color/20210412_165548/0.png')
    return raw_img
