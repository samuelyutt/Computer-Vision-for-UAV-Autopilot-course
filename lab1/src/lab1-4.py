import numpy as np
import cv2


def fourPoints(img,i,j,magni):
    points = []
    mid = 0.5
    ti, tj = i/magni, j/magni
    
    
    #Find left-top point and some debugging
    pti = int(ti)-1 if ti<=int(ti)+mid else int(ti)
    pti = pti if pti>=0 else 0
    pti = pti if pti<len(img)-1 else len(img)-2
    
    ptj = int(tj)-1 if tj<=int(tj)+mid else int(tj)
    ptj = ptj if ptj>=0 else 0
    ptj = ptj if ptj<len(img[0])-1 else len(img[0])-2
    
    #points save in the order of:top-left, top-right, botton-left, bottom-right
    for m in range(2):
        for n in range(2):
            points.append([pti+m,ptj+n])
    
    #Interpolation distance
    relativeX = tj - (points[0][1]+mid)
    relativeY = ti - (points[0][0]+mid)
    
    return points,relativeX,relativeY

def bilinearInterpolation(img,magni):
    img_tmp = np.zeros((magni*len(img),magni*len(img[0]),3), np.uint8)
    for i in range(len(img_tmp)):
        for j in range(len(img_tmp[i])):
            pts,rx,ry = fourPoints(img,i,j,magni)
            
            #Interpolation
            pA = rx * img[pts[1][0],pts[1][1]] + (1-rx) * img[pts[0][0],pts[0][1]]
            pB = rx * img[pts[3][0],pts[3][1]] + (1-rx) * img[pts[2][0],pts[2][1]]
            pC = ry * pB + (1-ry) * pA
            
            img_tmp[i,j] = pC

    return img_tmp

#Bilinear Interpolate
MAGNI = 3
img_IU = cv2.imread('../img/IU.png')

cv2.imshow('Before bilinear interpolate',img_IU)
img_biInterpol = bilinearInterpolation(img_IU, MAGNI)
cv2.imshow('After bilinear interpolate',img_biInterpol)
#cv2.imwrite('IU_bi.png',img_biInterpol)

cv2.waitKey(0)
cv2.destroyAllWindows()
