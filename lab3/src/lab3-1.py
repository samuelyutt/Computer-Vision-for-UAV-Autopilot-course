import numpy as np
import cv2

filename = '../video/vtest.avi'

cap = cv2.VideoCapture(filename)

while cap.isOpened():
    # Read the frame
    ret, frame = cap.read()

    # Background Subtraction
    backSub = cv2.createBackgroundSubtractorMOG2()
    fgmask = backSub.apply(frame)

    # Threshold
    shadowval = backSub.getShadowValue()
    ret, nmask = cv2.threshold(fgmask, shadowval, 255, cv2.THRESH_BINARY)

    # Connected Component
    # TODO: Seed Filling Algorithm

    # Rectangle


    # Display the frame
    cv2.imshow("frame", frame)
    cv2.waitKey(10)

cv2.destroyAllWindows()