import tello
import cv2
import time
import numpy as np
import math


def drone_start_up(port=8889):
    drone = tello.Tello('', port)
    time.sleep(10)
    return drone


def main():
    drone = drone_start_up()

    # drone.calibrate()
    intrinsic, distortion = drone.calibrate_read()

    rotCount = 0

    while(True):
        # Read the frame
        frame = drone.frame_read()
        
        # Detect the markers in the image
        rvec, tvec, _objPoints = drone.detect_aruco(frame, intrinsic, distortion)
        
        try:
            # Move the drone to Aruco
            drone.move_to_aruco(drone, tvec)
            
            # Rotate the drone by Aruco
            if rotCount % 10 == 0:
                drone.rotate_by_aruco(drone, rvec)
            rotCount += 1
        
        except:
            pass
        
        # Show the frame
        cv2.imshow("Drone", frame)

        # Keyboard control
        drone.keyboard_control()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()