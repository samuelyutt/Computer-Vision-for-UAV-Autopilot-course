import cv2
import numpy as np

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # 0 for camera, second arg for solving warning

filename = '../../lab3/video/vtest.avi'
#cap = cv2.VideoCapture(filename)

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

while(True):
    
    ret, frame = cap.read()
    
    rects, weights = hog.detectMultiScale(frame, winStride=(4,4), scale=1.1, useMeanshiftGrouping=False)
    try:
        for rect in rects:
            cv2.rectangle(frame, (rect[0], rect[1]), 
                                 (rect[0] + rect[2], rect[1] + rect[3]), 
                                 (0, 255, 0), 2)
            height = rect[3]
            dist = 15000 / height
            cv2.putText(frame, f'{dist}cm', (rect[0], rect[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
    except:
        print("Not detected.")
        pass
    
    cv2.imshow('frame', frame)
    
    key = cv2.waitKey(33)
    if key == ord('q') or key == 27: # Esc
        break

cap.release()
cv2.destroyAllWindows()