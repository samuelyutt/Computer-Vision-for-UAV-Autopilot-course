import numpy as np
import cv2

def fourPoints(img, ti, tj):
    pts = []
    lt_pti, lt_ptj = int(ti), int(tj) # left-top point
    
    lt_pti = lt_pti if lt_pti<len(img)-1 else len(img)-2
    lt_ptj = lt_ptj if lt_ptj<len(img[0])-1 else len(img[0])-2
    
    for m in range(2):
        for n in range(2):
            pts.append([lt_pti+m,lt_ptj+n])
    relativeI = ti - int(ti)
    relativeJ = tj - int(tj)
    
    return pts, relativeI, relativeJ

cap = cv2.VideoCapture(0)
img_TV = cv2.imread('../img/warp.jpg')

doOnce = False

while(True):
    ret, frame = cap.read()
    if not doOnce:
        doOnce = True
        print('Frame size ixj:',len(frame), len(frame[0]))

        # left-top, right-top, left-bottom, right-bottom 
        # in (i, j) order
        src_co = np.array([[0, 0], [0, len(frame[0])], [len(frame), 0], [len(frame), len(frame[0])]], dtype = "float32")    
        dest_co = np.array([[205, 246], [250, 464], [634, 261], [762, 433]], dtype = "float32")

        proj = cv2.getPerspectiveTransform(src_co, dest_co)
        proj_inv = cv2.getPerspectiveTransform(dest_co, src_co)
    
    # loop through maximum TV frame
    for i in range(205, 763): # can replace by parameter
        for j in range(246, 465):
            ta = np.array([i, j, 1], dtype="float32")
            ta = np.matmul(proj_inv, ta)
            ta = ta / ta[2]
            
            # not in TV frame
            if ta[0]<0.0 or ta[1]<0.0 or ta[0]>len(frame) or ta[1]>len(frame[0]):
                continue
            
            # bilinear interpolation
            pts, ri, rj = fourPoints(frame, ta[0], ta[1])

            pA = rj * frame[pts[1][0],pts[1][1]] + (1-rj) * frame[pts[0][0],pts[0][1]]
            pB = rj * frame[pts[3][0],pts[3][1]] + (1-rj) * frame[pts[2][0],pts[2][1]]
            pC = ri * pB + (1-ri) * pA
            
            img_TV[i, j] = pC

    cv2.imshow('frame', img_TV)
    cv2.waitKey(33)