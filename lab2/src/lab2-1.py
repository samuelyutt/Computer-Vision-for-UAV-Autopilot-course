import cv2
import numpy as np
import math

def calc_histogram(img):
    hist = [0] * 256
    for row in img:
        for pixel in row:
            hist[pixel] += 1
    return hist

def equalized_histogram(hist):
    pixel_num = sum(hist)
    accu_pixel_num = 0
    accu_pr = [0.0] * 256
    for i in range(256):
        accu_pixel_num += hist[i]
        accu_pr[i] = accu_pixel_num / pixel_num
    quantized_output = [math.floor(i * 256) for i in accu_pr]
    return quantized_output

def transform_img(img, eq_grey):
    new_img = np.zeros((len(img[0]),len(img), 1), np.uint8)
    for i in range(len(new_img[0])):
        for j in range(len(new_img[i])):
            new_img[i, j] = eq_grey[img[i, j]]
    return new_img


if __name__ == '__main__':    
    img = cv2.imread('../img/mj.tif', cv2.IMREAD_GRAYSCALE)
    hist = calc_histogram(img)
    eq_grey = equalized_histogram(hist)
    new_img = transform_img(img, eq_grey)
    cv2.imshow('trans_img', img)
    cv2.waitKey(0)
