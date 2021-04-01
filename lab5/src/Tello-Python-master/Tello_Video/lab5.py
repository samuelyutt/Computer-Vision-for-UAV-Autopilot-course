import tello
import cv2
import time
import numpy as np

# intrinsic = cv2.UMat(np.array([[1.31239836e3, 0.00000000, 1.38727107e2],
#     [0.00000000, 1.36448029e3, 1.33259206e2],
#     [0.00000000, 0.00000000, 1.00000000]]))

# distortion = cv2.UMat(np.array([[ 0.22502296, -0.37829631, -0.01676715, -0.05744351,  0.28779467]]))


dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters_create()

def main():

    drone = tello.Tello('', 8889)
    time.sleep(10)

    w = 9
    h = 6
    objp = np.zeros((w*h,3), np.float32)
    objp[:,:2] = np.mgrid[0:w,0:h].T.reshape(-1,2)
    objpoints = []
    imgpoints = []
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

    cnt = 0

    # drone = tello.Tello('', 8889)
    # time.sleep(10)
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

    intrinsic = mtx
    distortion = dist

    while(True):
        frame = drone.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow("drone", frame)
        markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)

        # frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)
        rvec, tvec, _objPoints = cv2.aruco.estimatePoseSingleMarkers(markerCorners, 15 , intrinsic, distortion)
        if rvec is not None and tvec is not None:
            print("tvec:", tvec)
            frame = cv2.aruco.drawAxis(frame, intrinsic, distortion, rvec, tvec, 20)
        else:
            print("rvec:", rvec)
            print("tvec:", tvec)

        frame = cv2.putText(frame, str("z: " + str(tvec[0][0][2])), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("drone", frame)
        key = cv2.waitKey(1)
        # if key!= -1:
        #     drone.keyboard(key)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()