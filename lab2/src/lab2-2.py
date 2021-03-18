import cv2
import numpy as np

def histogram(img):
    inten = np.zeros(256, np.uint32)
    for i in range(len(img)):
        for j in range(len(img[i])):
            inten[img[i,j,0]] += 1
    return inten

def threshold(_sum):
    T = 0
    maxmi = -999
    nB, nO = 0, sum(_sum)
    muB = 0
    muO = sum([i*_sum[i] for i in range(256)]) / sum(_sum)
    for i in range(256):
        muB = (muB*nB + (_sum[i]*i)) / (nB + _sum[i])
        muO = (muO*nO - (_sum[i]*i)) / (nO - _sum[i])
        nB += _sum[i]
        nO -= _sum[i]
        var_bet = nB * nO * ((muB - muO)**2)
        if var_bet>maxmi:
            maxmi = var_bet
            T = i
    print('Threshold:', T)
    return T

def OtsuProcess(img, T):
    tmp_img = img.copy()
    for i in range(len(img)):
        for j in range(len(img[i])):
            tmp_img[i,j] = 255 if img[i,j,0]>T else 0
    return tmp_img

img = cv2.imread('../img/input.jpg')

intensity = histogram(img)
T = threshold(intensity)
img_thre = OtsuProcess(img, T)

cv2.imshow('before', img)
cv2.imshow('after', img_thre)
cv2.waitKey(0)
cv2.destroyAllWindows()