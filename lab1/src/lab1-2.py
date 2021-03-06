import numpy as np
import cv2

def rotateImg(img):
    img_tmp = np.zeros((len(img[0]),len(img),3), np.uint8)
    for i in range(len(img_tmp)):
        for j in range(len(img_tmp[i])):
            img_tmp[i,j] = img[j,len(img_tmp)-i-1]
    return img_tmp

#Rotate
img_curry = cv2.imread('../img/curry.jpg')
cv2.imshow('Before rotate',img_curry)
img_rotate = rotateImg(img_curry)
cv2.imshow('After rotate',img_rotate)
#cv2.imwrite('curry_ro.jpg',img_rotate)

cv2.waitKey(0)
cv2.destroyAllWindows()