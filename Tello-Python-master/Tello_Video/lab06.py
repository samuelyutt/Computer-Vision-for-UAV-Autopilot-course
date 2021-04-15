import tello
import cv2
import time
import numpy as np
import math

# Load the predefined dictionary
dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
# Initialize the detector parameters using default values
parameters = cv2.aruco.DetectorParameters_create()


def drone_calibrate(drone, filename='./calibrate.xml'):
    w = 9
    h = 6
    objp = np.zeros((w*h,3), np.float32)
    objp[:,:2] = np.mgrid[0:w,0:h].T.reshape(-1,2)
    objpoints = []
    imgpoints = []
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
    
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

def move2Aruco(drone, tvec, margin):
    DIST = 130 # Fixed distance to Aruco
    distance = 0.3
    if tvec[0][0][2] > DIST + margin[2]:
        drone.move_forward(distance)
    elif tvec[0][0][2] < DIST - margin[2]:
        drone.move_backward(distance)
    
    if tvec[0][0][1] < 0 - margin[1] :
        drone.move_up(distance)
    elif tvec[0][0][1] > 0 + margin[1]:
        drone.move_down(distance)
        
    if tvec[0][0][0] < 0 - margin[0]:
        drone.move_left(distance)
    elif tvec[0][0][0] > 0 + margin[0]:
        drone.move_right(distance)

def rotAruco(drone, rvec, margin):
    rmat = cv2.Rodrigues(rvec)  #rmat is a tuple of (3*3 mat, 9*3 mat)
    Zprime = np.matmul(rmat[0], np.array([[0, 0, 1]]).T)
    Zprime[1] = 0 # project onto X-Z plane
    V = Zprime
    rad = math.atan2(V[2], V[0])
    deg = math.degrees(rad)
    deg += 90 # adjusting
    
    if deg > 0 + margin:
        drone.rotate_ccw(deg)
    elif deg < 0 - margin:
        drone.rotate_cw(-deg)

def main():
    drone = tello.Tello('', 8889)
    time.sleep(10)

    # drone_calibrate(drone)
    intrinsic, distortion = drone_calibrate_read()

    rotCount = 0
    move_sensitivity = [15, 15, 50] # up/down, left/right, forward/backward
    rot_sensitivity = 10

    while(True):
        frame = drone.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Detect the markers in the image
        markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)
        frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)
        rvec, tvec, _objPoints = cv2.aruco.estimatePoseSingleMarkers(markerCorners, 15, intrinsic, distortion)
        
        try:
            #frame = cv2.aruco.drawAxis(frame, intrinsic, distortion, rvec, tvec, 8)
            move2Aruco(drone, tvec, move_sensitivity)
            
            if rotCount % 10 == 0:
                rotAruco(drone, rvec, rot_sensitivity)
            rotCount += 1
        except:
            pass
        
        cv2.imshow("Drone", frame)

        drone_keyboard_control(drone)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()