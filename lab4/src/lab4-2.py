import numpy as np
import cv2

img_cont = cv2.imread('../img/IU.png')
img_TV = cv2.imread('../img/warp.jpg')

def multi(a,b): #a*b
    if len(a[0])!=len(b):
        print('Error: matrix multiple, wrong size of matrix')
        return
    re = np.zeros((len(a),len(b[0])))
    for i in range(len(re)):
        for j in range(len(re[i])):
            for k in range(len(a[0])):
                re[i][j] += a[i][k]*b[k][j]
    return re

#左上，右上，左下，右下
src_co = np.array([[0, 0], [0, len(img_cont[0])], [len(img_cont), 0], [len(img_cont), len(img_cont[0])]], dtype = "float32")
dest_co = np.array([[246, 205], [464, 250], [261, 634], [433, 762]], dtype = "float32")
print(len(img_TV))
proj = cv2.getPerspectiveTransform(src_co, dest_co)
proj_inv = cv2.getPerspectiveTransform(dest_co, src_co)

ta = np.array([433, 762, 1], dtype="float32")
ta = np.matmul(proj, ta)
ta = ta / ta[2]
print(ta)

for i 

cv2.imshow('Flipped image', img_TV)
cv2.waitKey(0)
cv2.destroyAllWindows()
