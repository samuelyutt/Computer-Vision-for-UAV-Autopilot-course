import math
import cv2
import numpy as np
import dlib

# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # 0 for camera, second arg for solving warning
cap = cv2.VideoCapture(0)

# filename = '../../lab3/video/vtest.avi'
#cap = cv2.VideoCapture(filename)

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
detector = dlib.get_frontal_face_detector()

while(True):
    
    # Read frame
    ret, frame = cap.read()
    
    # Detect body
    rects, weights = hog.detectMultiScale(frame, winStride=(4,4), scale=1.1, useMeanshiftGrouping=False)
    
    # Detect face
    face_rects = detector(frame, 0)
    
    # Draw body rectangles in yellow
    try:
        for rect in rects:
            cv2.rectangle(frame, (rect[0], rect[1]), 
                                 (rect[0] + rect[2], rect[1] + rect[3]), 
                                 (0, 255, 255), 2)
            height = rect[3]
            dist = 156000 / height
            cv2.putText(frame, f'{dist}cm', (rect[0], rect[1] + rect[3]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
    except:
        print("No body detected.")

    # Draw face rectangles in green
    try:
        for i, d in enumerate(face_rects):
            cv2.rectangle(frame, (d.left(), d.top()), 
                                 (d.right(), d.bottom()), 
                                 (0, 255, 0), 2)
            
            height = d.bottom() - d.top()
            dist = 15000 / height
            cv2.putText(frame, f'{dist}cm', (d.left(), d.top()), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
    except:
        print("No face detected.")

    # Show frame
    cv2.imshow('frame', frame)
    
    key = cv2.waitKey(33)
    if key == ord('q') or key == 27: # Esc
        break

cap.release()
cv2.destroyAllWindows()