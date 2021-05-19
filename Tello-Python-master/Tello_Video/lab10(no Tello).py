import math
import cv2
import numpy as np
from collections import Counter
from time import sleep

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
url = "http://192.168.0.3:4747/video"
#cap = cv2.VideoCapture(url)

calibrate_file_name = './webCamCalibrate.xml'

# Aruco related
dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters_create()


blue_lb = np.array([60, 10, 10])
blue_hb = np.array([150, 60, 70])
#blue_lb = np.array([100, 70, 70])
#blue_hb = np.array([170, 255, 255])

ignore_dir_dict = {
    'l': 'r',
    'r': 'l',
    'u': 'd',
    'd': 'u'
}

dir_name_dict = {
    'l': 'left',
    'r': 'right',
    'u': 'up',
    'd': 'down'
}

def inBound(px):
    for i in range(3):
        if px[i] < blue_lb[i] or px[i] > blue_hb[i]:
            return False
    return True

def readBlue(frame, ignore_dir):
    margin_y = 80
    margin_x = 80
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
    sp = 6
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

def beforeStart():
    # Before catch Aruco
    count = 0
    while True:
        ret, frame = cap.read()        
        markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)
        frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)
        
        # Take off higher
        if count == 0:
            #drone.move_up(0.2)
            #sleep(1)
            pass
        
        try:
            if int(markerIds[0][0]) == 4:
                count += 1
                #move2Aruco(drone, tvec, move_sensitivity)
                if count > 50:
                    break
        except:
            count = count - 5 if count > 0 else 0
        print(count)
        
        cv2.imshow("Drone", frame)
        #drone_keyboard_control(drone) 
        
        key = cv2.waitKey(33)
        if key == ord('q') or key == 27: # Esc
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    
    ignore_dir = 'l'
    next_dir = 'r'
    
    vote = {'u':0, 'd':0, 'l':0, 'r':0}
    vote_cnt = 6
    landFlag = False
    debugFlag = False
    
    # Detect Aruco #4
    beforeStart()
    
    # After detected, move a little bit
    #drone.move_right(0.5)
    sleep(3)
    
    while(True):
        # Read frame
        ret, frame = cap.read()
        BGR_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Detect Aruco
        markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)
        frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)
        
        # Detect line
        hsv_frame = cv2.cvtColor(BGR_frame, cv2.COLOR_BGR2HSV)
        tmp_dir, bf = readBlue(hsv_frame, ignore_dir)
        vote[tmp_dir] += 1
        if vote_cnt == 0:
            ignore_dir = ignore_dir_dict[tmp_dir]
            next_dir = Counter(vote).most_common(1)[0][0]
            vote = {'u':0, 'd':0, 'l':0, 'r':0}
            
            '''
            dis = 0.3
            if next_dir == 'u':
                drone.move_up(dis)
            elif next_dir == 'd':
                drone.move_down(0.5)
            elif next_dir == 'l':
                drone.move_left(dis)
            elif next_dir == 'r':
                drone.move_right(dis)
            '''
            print(f'Move {dir_name_dict[next_dir]}')
            #sleep(2)
            vote_cnt = 6
            debugFlag = True
        else:
            vote_cnt -= 1
        
        # Show frame
        frame_show = frame
        try:
            if int(markerIds[0][0]) == 4 and debugFlag:
                # Landing
                landFlag = True
                print("Detected marker #4, ready to land.")
                cv2.putText(frame_show, "Detected marker #4, ready to land.", (0, frame.shape[1]//2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA) 
                cv2.imshow('frame', frame_show)
                #drone.land()
                sleep(3)
                break
        except:
            landFlag = False
            pass
        
        if not landFlag:
            cv2.putText(frame_show, f'Move {dir_name_dict[next_dir]}', (frame.shape[0]//2, frame.shape[1]//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.imshow('frame', frame_show)
    
        key = cv2.waitKey(33)
        if key == ord('q') or key == 27: # Esc
            tmp_frame = hsv_frame
            break
    
    cap.release()
    cv2.destroyAllWindows()
