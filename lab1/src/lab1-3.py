import numpy as np
import cv2

def neighborInterpolation(img, magni):
    img_tmp = np.zeros((magni*len(img),magni*len(img[0]),3), np.uint8)
    for i in  range(len(img_tmp)):
        for j in range(len(img_tmp[i])):
            img_tmp[i, j] = img[i//magni, j//magni]
    return img_tmp

#Neighbor Interpolate
MAGNI = 3
img_IU = cv2.imread('../img/IU.png')

cv2.imshow('Before neighbor interpolate',img_IU)
img_neInterpol = neighborInterpolation(img_IU, MAGNI)
cv2.imshow('After neighbor interpolate',img_neInterpol)
#cv2.imwrite('IU_ne.png',img_neInterpol)

cv2.waitKey(0)
cv2.destroyAllWindows()