import tello
import cv2
from time import sleep
import numpy as np
import math
from collections import Counter

# Load the predefined dictionary
dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
# Initialize the detector parameters using default values
parameters = cv2.aruco.DetectorParameters_create()

blue_lb = np.array([100, 70, 70])
blue_hb = np.array([170, 255, 255])

ignore_dir_dict = {
    'l': 'r',
    'r': 'l',
    'u': 'd',
    'd': 'u'
}

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

def move2Aruco(drone, tvec, margin, s_t=0.5):
    DIST = 80 # Fixed distance to Aruco
    distance = 0.3
    '''
    if tvec[0][0][2] > DIST + margin[2]:
        drone.move_forward(distance)
        #sleep(s_t)
    elif tvec[0][0][2] < DIST - margin[2]/2:
        drone.move_backward(distance)
        #sleep(s_t)
    '''
    
    if tvec[0][0][1] < 0 - margin[1]:
        drone.move_up(distance)
        #sleep(s_t)
    elif tvec[0][0][1] > 0 + margin[1]:
        drone.move_down(distance)
        #sleep(s_t)
        
    if tvec[0][0][0] < 0 - margin[0]:
        drone.move_left(distance)
        #sleep(s_t)
    elif tvec[0][0][0] > 0 + margin[0]:
        drone.move_right(distance)
        #sleep(s_t)
    
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
    
def inBound(px):
    for i in range(3):
        if px[i] < blue_lb[i] or px[i] > blue_hb[i]:
            return False
    return True

def readBlue(frame, ignore_dir):
    margin_y = 180
    margin_x = 300
    center_y = len(frame) // 2
    center_x = len(frame[0]) // 2
    
    cnt_dict = {
        'u': 0,
        'l': 0,
        'd': 0,
        'r': 0
    }
    cnt_dict = Counter(cnt_dict)
    
    bf = np.zeros(frame.shape)
    sp = 8
    for i in range(0, len(frame), sp):
        for j in range(0, len(frame[0]), sp):
            if inBound(frame[i][j]):
                bf[i][j] = np.array([255, 255, 255])
                if i < center_y - margin_y :
                    cnt_dict['u'] += 1
                elif i > center_y + margin_y:
                    cnt_dict['d'] += 1
                if j < center_x - margin_x:
                    cnt_dict['l'] += 1
                elif j > center_x + margin_x:
                    cnt_dict['r'] += 1
    
    _max = cnt_dict.most_common(2)
    if _max[0][0] == ignore_dir:
        return _max[1][0], bf
    return _max[0][0], bf

def main():
    drone = tello.Tello('', 8889)
    sleep(10)

    #drone_calibrate(drone)
    intrinsic, distortion = drone_calibrate_read()

    move_sensitivity = [15, 13, 50] # left/right, up/down, forward/backward
    rot_sensitivity = 10
    rotCount = 0
    
    ready2Land = 0
    
    state = 0
    ignore_dir = 'l'
    
    # Detect line param
    kernel_size = 5 # 3, 5, 7
    low_threshold = 40
    high_threshold = 120
    vote = {'u':0, 'd':0, 'l':0, 'r':0}
    vote_cnt = 6

    # Before catch Aruco
    count = 0
    while True:
        frame = drone.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)
        frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)
        rvec, tvec, _objPoints = cv2.aruco.estimatePoseSingleMarkers(markerCorners, 15, intrinsic, distortion)
        
        if count == 0:
            drone.move_up(0.2)
            sleep(1)
        
        try:
            if int(markerIds[0][0]) == 4:
                count += 1
                move2Aruco(drone, tvec, move_sensitivity)
                if count > 200:
                    break
        except:
            if count > 0:
                count -= 5
            else:
                 count = 0
            pass
        print(count)
        
        cv2.imshow("Drone", frame)

        drone_keyboard_control(drone) 

    drone.move_right(0.5)
    sleep(2)
    print("move right")

    offset_cnt = 0
    while(True):
        frame = drone.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        #blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
        #edges_frame = cv2.Canny(blur_gray, low_threshold, high_threshold)
        
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        tmp_dir, bf = readBlue(hsv_frame, ignore_dir)
        vote[tmp_dir] += 1
        if vote_cnt == 0:
            ignore_dir = ignore_dir_dict[tmp_dir]
            next_dir = Counter(vote).most_common(1)[0][0]
            vote = {'u':0, 'd':0, 'l':0, 'r':0}
            
            dis = 0.3
            if next_dir == 'u':
                drone.move_up(dis)
            elif next_dir == 'd':
                drone.move_down(0.5)
            elif next_dir == 'l':
                drone.move_left(dis)
            elif next_dir == 'r':
                drone.move_right(dis)
            print(next_dir)
            sleep(2)
            vote_cnt = 6
        else:
            vote_cnt -= 1
        
        if offset_cnt == 60:
            #drone.move_forward(dis)
            #sleep(2)
            offset_cnt = 0
        else:
            offset_cnt += 1
        
        # Detect the markers in the image
        markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)
        frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)
        rvec, tvec, _objPoints = cv2.aruco.estimatePoseSingleMarkers(markerCorners, 15, intrinsic, distortion)
        
        try:
            if int(markerIds[0][0]) == 4:
                drone.land()
                sleep(4)
                break
        except:
            
            pass
        
        cv2.imshow("Drone", frame)

        drone_keyboard_control(drone)    

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()