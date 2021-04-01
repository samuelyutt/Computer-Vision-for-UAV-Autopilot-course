import tello
import cv2
import time
import numpy as np

w = 9
h = 6
objp = np.zeros((w*h,3), np.float32)
objp[:,:2] = np.mgrid[0:w,0:h].T.reshape(-1,2)
objpoints = []
imgpoints = []
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

cnt = 0

drone = tello.Tello('', 8889)
time.sleep(10)
while cnt <= 50:
    frame = drone.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    # cv2.imshow("drone", frame)
    print(cnt)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (w, h), None)

    if ret == True:
        cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        objpoints.append(objp)
        imgpoints.append(corners)
        cnt += 1
        cv2.drawChessboardCorners(frame, (w,h), corners, ret)
        cv2.imshow('findCorners',frame)
        cv2.waitKey(15)

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print("mtx:", mtx)
print()
print("dist:", dist)


# f = cv2.FileStorage('c:\\Users\\happy\\Downloads\\無人機\\Computer-Vision-for-UAV-Autopilot-course\\lab5\\src\\part1.xml', cv2.FILE_STORAGE_WRITE)
# f.write('intrinsic', mtx)
# f.write('distortion', dist)

#     key = cv2.waitKey(1)
#     if key!= -1:
#         # drone.keyboard(key)
#         pass
# cv2.destroyAllWindows()
