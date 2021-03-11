import numpy as np
import cv2


def histogram(img):
    inten = np.zeros(256, np.uint8)
    for i in range(len(img)):
        for j in range(len(img[i])):
            inten[img[i,j,0]] += 1
    total = sum(inten)
    accSum = np.zeros(256)
    accSum[0] = inten[0]
    for i in range(1, 256):
        accSum[i] = accSum[i-1] + inten[i]
    for i in range(256):
        accSum[i] = accSum[i]/total
    return accSum

def enhance(img, accSUm, SCALE):
    for i in range(256):
        accSum[i] = int(accSum[i] * SCALE)
    tmp_img = img.copy()
    for i in range(len(tmp_img)):
        for j in range(len(tmp_img[i])):
            tmp_img[i,j] = accSum[img[i,j,0]]
            #print(img[i,j])
            #print(accSum[img[i,j,0]])
            #print(tmp_img[i,j])
            #input()
    return tmp_img

SCALE = 255
img = cv2.imread('../img/mj.tif')

accSum = histogram(img)
img_enhan = enhance(img, accSum, SCALE)

cv2.imshow('before', img)
cv2.imshow('after', img_enhan)
cv2.waitKey(0)
cv2.destroyAllWindows()