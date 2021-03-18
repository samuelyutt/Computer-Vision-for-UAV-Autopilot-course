import numpy as np
import cv2

filename = '../video/vtest.avi'

cap = cv2.VideoCapture(filename)
frame_idx = 0
backSub = cv2.createBackgroundSubtractorMOG2()
shadowval = backSub.getShadowValue()

while cap.isOpened():
    # Read the frame
    ret, frame = cap.read()

    # Background Subtraction
    fgmask = backSub.apply(frame)

    # Threshold
    ret, nmask = cv2.threshold(fgmask, shadowval, 255, cv2.THRESH_BINARY)
    
    # Connected Component
    # TODO: Seed Filling Algorithm
    if frame_idx == 0:
        print(nmask.shape)
    cc = np.zeros(nmask.shape)

    map_dict = {}
    label = 1
    i = 0
    for row in nmask:
        j = 0
        for pixel in row:
            if pixel:
                if i and j and cc[i][j-1] and cc[i-1][j]:
                    if cc[i][j-1] > cc[i-1][j]:
                        cc[i][j] = cc[i-1][j]
                        map_dict[ cc[i][j-1] ] = cc[i-1][j]
                    elif cc[i][j-1] < cc[i-1][j]:
                        cc[i][j] = cc[i][j-1]
                        map_dict[ cc[i-1][j] ] = cc[i][j-1]

                elif j and cc[i][j-1]:
                    cc[i][j] = cc[i][j-1]
                
                elif i and cc[i-1][j]:
                    cc[i][j] = cc[i-1][j]

                else:
                    cc[i][j] = label
                    label += 1
            j += 1
        i += 1

    my_dict = {'rectangles': {}, 'stats': {}}
    i = 0
    for row in cc:
        j = 0
        for pixel in row:
            if pixel:
                if pixel in map_dict:
                    cc[i][j] = map_dict[pixel]

                if pixel not in my_dict['stats']:
                    my_dict['stats'][ pixel ] = 0
                    my_dict['rectangles'][pixel] = [[j, i], [j, i]]
                else:
                    rec_1_x = my_dict['rectangles'][pixel][0][0]
                    rec_1_y = my_dict['rectangles'][pixel][0][1]
                    rec_2_x = my_dict['rectangles'][pixel][1][0]
                    rec_2_y = my_dict['rectangles'][pixel][1][1]

                    if j < rec_1_x:
                        my_dict['rectangles'][pixel][0][0] = j
                    if i < rec_1_y:
                        my_dict['rectangles'][pixel][0][1] = i
                    if j > rec_2_x:
                        my_dict['rectangles'][pixel][1][0] = j
                    if i > rec_2_y:
                        my_dict['rectangles'][pixel][1][1] = i
                
                my_dict['stats'][ pixel ] += 1
                
            j += 1
        i += 1

    # Rectangle
    for label in my_dict['rectangles']:
        if label in my_dict['stats'] and my_dict['stats'][label] > 180:
            ptr1 = my_dict['rectangles'][label][0]
            ptr2 = my_dict['rectangles'][label][1]
            cv2.rectangle(frame, (ptr1[0], ptr1[1]), (ptr2[0], ptr2[1]), (0, 255, 0), 2)


    # Display the frame
    cv2.imshow("frame", frame)
    cv2.waitKey(33)

    frame_idx += 1

cv2.destroyAllWindows()