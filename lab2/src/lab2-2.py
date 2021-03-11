import cv2
import numpy as np

def histogram(img):
    inten = np.zeros(256, np.uint8)
    for i in range(len(img)):
        for j in range(len(img[i])):
            inten[img[i,j,0]] += 1
    print(inten)
    return inten

def threshold(_sum):
    T = 0
    maxmi = -999
    nB, nO = 0, 256
    muB, muO = 0, np.average(_sum)
    print(muB,muO)
    for i in range(256):
        muB = (muB*nB + _sum[i]) / (nB + 1)
        muO = (muO*nO - _sum[i]) / (nO - 1)
        nB = i + 1
        nO = 255 - i
        var_bet = nB * nO * ((muB - muO)**2)
        if var_bet>maxmi:
            maxmi = var_bet
            T = i
        print(T, var_bet)
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