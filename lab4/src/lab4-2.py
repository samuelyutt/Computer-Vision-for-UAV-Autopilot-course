import numpy as np
import cv2

frame = cv2.imread('../../lab1/img/IU.png')
background = cv2.imread('../img/warp.jpg')

background_size = (background.shape[1], background.shape[0])

dst = np.float32([[464, 250],
                    [246, 205],
                    [261, 634],
                    [433, 762]])

cap = cv2.VideoCapture(0)

while(True):
    ret, frame = cap.read()
    #ret is True if read() successed
    
    frame_size = (frame.shape[1], frame.shape[0])

    src = np.float32([[0, 0], 
                    [frame_size[0], 0], 
                    [frame_size[0], frame_size[1]],
                    [0, frame_size[1]]])

    M = cv2.getPerspectiveTransform(src, dst)

    for y in range(frame_size[1]-1):
        for x in range(frame_size[0]-1):
            s = np.float32([x, y, 1])
            d = np.matmul(M, s)
            # print(d)
            i = d[0] / d[2]
            j = d[1] / d[2]
            # print(i, j)
            pixel = background[int(j)][int(i)]
            for p in range(3):
                pixel[p] = (i-int(i)) * frame[y+1][x][p] + (i-int(i)+1) * frame[y][x][p] + (j-int(j)) * frame[y][x+1][p] + (j-int(j)+1) * frame[y][x][p]
            background[int(j)][int(i)] = pixel

    # warped = cv2.warpPerspective(frame, M, background_size)
    cv2.imshow('frame', background)
    cv2.waitKey(60)



# cap = cv2.VideoCapture(0)

# while(True):
#     ret, frame = cap.read()
#     #ret is True if read() successed
#     cv2.imshow('frame', frame)
#     cv2.waitKey(33)