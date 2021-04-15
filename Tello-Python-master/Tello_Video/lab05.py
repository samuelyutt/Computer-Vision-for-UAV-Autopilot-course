import tello
import cv2
import time
import numpy as np

# Load the predefined dictionary
dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
# Initialize the detector parameters using default values
parameters = cv2.aruco.DetectorParameters_create()

w = 9
h = 6
objp = np.zeros((w*h,3), np.float32)
objp[:,:2] = np.mgrid[0:w,0:h].T.reshape(-1,2)
objpoints = []
imgpoints = []
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

def drone_calibrate(drone, filename='./calibrate.xml'):
    cnt = 0
    while cnt <= 50:
        print(cnt)
        frame = drone.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
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

    f = cv2.FileStorage(filename, cv2.FILE_STORAGE_WRITE)
    f.write('intrinsic', mtx)
    f.write('distortion', dist)
    print(mtx)
    print(dist)


def drone_calibrate_read(filename='./calibrate.xml'):
    f = cv2.FileStorage(filename, cv2.FILE_STORAGE_READ)

    intrinsic_node = f.getNode('intrinsic')
    distortion_node = f.getNode('distortion')

    intrinsic = intrinsic_node.mat()
    distortion = distortion_node.mat()

    return intrinsic, distortion

def drone_keyboard_control(drone):
    key = cv2.waitKey(1)
    if key != -1:
        drone.keyboard(key)


def main():
    drone = tello.Tello('', 8889)
    time.sleep(10)

    # drone_calibrate(drone)
    intrinsic, distortion = drone_calibrate_read()

    while(True):
        frame = drone.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Detect the markers in the image
        markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)
        frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)

        rvec, tvec, _objPoints = cv2.aruco.estimatePoseSingleMarkers(markerCorners, 15, intrinsic, distortion)
        
        try:
            frame = cv2.aruco.drawAxis(frame, intrinsic, distortion, rvec, tvec, 8)
            print(tvec)
            print('x: ' + str(tvec[0][0][0]) + ' y: ' + str(tvec[0][0][1]) + ' z: ' + str(tvec[0][0][2]))
            frame = cv2.putText(frame, 'x: ' + str(tvec[0][0][0]) + ' y: ' + str(tvec[0][0][1]) + ' z: ' + str(tvec[0][0][2]), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
            print('drawAxis')
        except:
            pass
        
        cv2.imshow("findCorners", frame)

        drone_keyboard_control(drone)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()