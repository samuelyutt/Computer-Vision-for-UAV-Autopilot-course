import socket
import threading
import time
import numpy as np
import cv2
# import libh264decoder

class Tello:
    """Wrapper class to interact with the Tello drone."""

    def __init__(self, local_ip, local_port, imperial=False, command_timeout=.3, tello_ip='192.168.10.1',
                 tello_port=8889):
        """
        Binds to the local IP/port and puts the Tello into command mode.

        :param local_ip (str): Local IP address to bind.
        :param local_port (int): Local port to bind.
        :param imperial (bool): If True, speed is MPH and distance is feet.
                             If False, speed is KPH and distance is meters.
        :param command_timeout (int|float): Number of seconds to wait for a response to a command.
        :param tello_ip (str): Tello IP.
        :param tello_port (int): Tello port.
        """

        self.abort_flag = False
        # self.decoder = libh264decoder.H264Decoder()
        self.command_timeout = command_timeout
        self.imperial = imperial
        self.response = None  
        self.frame = None  # numpy array BGR -- current camera output frame
        self.is_freeze = False  # freeze current camera output
        self.last_frame = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for receiving video stream
        self.tello_address = (tello_ip, tello_port)
        self.local_video_port = 11111  # port for receiving video stream
        self.last_height = 0
        self.socket.bind((local_ip, local_port))

        # thread for receiving cmd ack
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True

        self.receive_thread.start()

        # to receive video -- send cmd: command, streamon
        self.socket.sendto(b'command', self.tello_address)
        print('sent: command')
        self.socket.sendto(b'streamon', self.tello_address)
        print('sent: streamon')

        # self.socket_video.bind((local_ip, self.local_video_port))

        # thread for receiving video
        self.receive_video_thread = threading.Thread(target=self._receive_video_thread)
        self.receive_video_thread.daemon = True

        self.receive_video_thread.start()

        #### ADDED PARAMS ####
        # About Aruco
        # Load the predefined dictionary
        self.aruco_dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        # Initialize the detector parameters using default values
        self.aruco_parameters = cv2.aruco.DetectorParameters_create()
        
        # Above moving and rotating
        self.DIST = 130 # Fixed distance to Aruco
        self.move_sensitivity = [15, 15, 50] # up/down, left/right, forward/backward
        self.rot_sensitivity = 10
        


    def __del__(self):
        """Closes the local socket."""

        self.socket.close()
        self.socket_video.close()

    def keyboard(self, key):
        print("key:", key)
        distance = 0.9
        degree = 30
        
        if key == ord('1'):
            self.takeoff()
        if key == ord('2'):
            self.land()
        if key == ord('i'):
            self.move_forward(distance)
            print("forward!!!!")
        if key == ord('k'):
            self.move_backward(distance)
            print("backward!!!!")
        if key == ord('j'):
            self.move_left(distance)
            print("left!!!!")
        if key == ord('l'):
            self.move_right(distance)
            print("right!!!!")
        if key == ord('s'):
            self.move_down(distance)
            print("down!!!!")
        if key == ord('w'):
            self.move_up(distance)
            print("up!!!!")
        if key == ord('a'):
            self.rotate_cw(degree)
            print("rotate!!!!")
        if key == ord('d'):
            self.rotate_ccw(degree)
            print("counter rotate!!!!")
        if key == ord('5'):
            height = self.get_height()
            print(height)
        if key == ord('6'):
            battery = self.get_battery()
            print(battery)
    
    def read(self):
        """Return the last frame from camera."""
        if self.is_freeze:
            return self.last_frame
        else:
            return self.frame

    def video_freeze(self, is_freeze=True):
        """Pause video output -- set is_freeze to True"""
        self.is_freeze = is_freeze
        if is_freeze:
            self.last_frame = self.frame

    def _receive_thread(self):
        """Listen to responses from the Tello.

        Runs as a thread, sets self.response to whatever the Tello last returned.

        """
        while True:
            try:
                self.response, ip = self.socket.recvfrom(3000)
                #print(self.response)
            except socket.error as exc:
                print("Caught exception socket.error : %s" % exc)

    def _receive_video_thread(self):
        video_ip = "udp://{}:{}".format("0.0.0.0", 11111)
        video_capture = cv2.VideoCapture(video_ip)
        retval, self.frame = video_capture.read()
        while retval:
            retval, frame = video_capture.read()
            self.frame = frame[..., ::-1] # From BGR to RGB

    # def _receive_video_thread(self):
    #     """
    #     Listens for video streaming (raw h264) from the Tello.

    #     Runs as a thread, sets self.frame to the most recent frame Tello captured.

    #     """
    #     packet_data = ""
    #     while True:
    #         try:
    #             res_string, ip = self.socket_video.recvfrom(2048)
    #             packet_data += res_string
    #             # end of frame
    #             if len(res_string) != 1460:
    #                 for frame in self._h264_decode(packet_data):
    #                     self.frame = frame
    #                 packet_data = ""

    #         except socket.error as exc:
    #             print("Caught exception socket.error : %s" % exc)
    
    # def _h264_decode(self, packet_data):
    #     """
    #     decode raw h264 format data from Tello
        
    #     :param packet_data: raw h264 data array
       
    #     :return: a list of decoded frame
    #     """
    #     res_frame_list = []
    #     frames = self.decoder.decode(packet_data)
    #     for framedata in frames:
    #         (frame, w, h, ls) = framedata
    #         if frame is not None:
    #             # print'frame size %i bytes, w %i, h %i, linesize %i' % (len(frame), w, h, ls)

    #             frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
    #             frame = (frame.reshape((h, ls / 3, 3)))
    #             frame = frame[:, :w, :]
    #             res_frame_list.append(frame)

    #     return res_frame_list

    def send_command(self, command):
        """
        Send a command to the Tello and wait for a response.

        :param command: Command to send.
        :return (str): Response from Tello.

        """

        print(">> send cmd: {}".format(command))
        self.abort_flag = False
        timer = threading.Timer(self.command_timeout, self.set_abort_flag)

        self.socket.sendto(command.encode('utf-8'), self.tello_address)

        timer.start()
        while self.response is None:
            if self.abort_flag is True:
                break
        timer.cancel()
        
        if self.response is None:
            response = 'none_response'
        else:
            response = self.response.decode('utf-8')

        self.response = None

        return response
    
    def set_abort_flag(self):
        """
        Sets self.abort_flag to True.

        Used by the timer in Tello.send_command() to indicate to that a response
        
        timeout has occurred.

        """

        self.abort_flag = True

    def takeoff(self):
        """
        Initiates take-off.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.send_command('takeoff')

    def set_speed(self, speed):
        """
        Sets speed.

        This method expects KPH or MPH. The Tello API expects speeds from
        1 to 100 centimeters/second.

        Metric: .1 to 3.6 KPH
        Imperial: .1 to 2.2 MPH

        Args:
            speed (int|float): Speed.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        speed = float(speed)

        if self.imperial is True:
            speed = int(round(speed * 44.704))
        else:
            speed = int(round(speed * 27.7778))

        return self.send_command('speed %s' % speed)

    def rotate_cw(self, degrees):
        """
        Rotates clockwise.

        Args:
            degrees (int): Degrees to rotate, 1 to 360.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.send_command('cw %s' % degrees)

    def rotate_ccw(self, degrees):
        """
        Rotates counter-clockwise.

        Args:
            degrees (int): Degrees to rotate, 1 to 360.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """
        return self.send_command('ccw %s' % degrees)

    def flip(self, direction):
        """
        Flips.

        Args:
            direction (str): Direction to flip, 'l', 'r', 'f', 'b'.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.send_command('flip %s' % direction)

    def get_response(self):
        """
        Returns response of tello.

        Returns:
            int: response of tello.

        """
        response = self.response
        return response

    def get_height(self):
        """Returns height(dm) of tello.

        Returns:
            int: Height(dm) of tello.

        """
        height = self.send_command('height?')
        height = str(height)
        height = filter(str.isdigit, height)
        try:
            height = int(height)
            self.last_height = height
        except:
            height = self.last_height
            pass
        return height

    def get_battery(self):
        """Returns percent battery life remaining.

        Returns:
            int: Percent battery life remaining.

        """
        
        battery = self.send_command('battery?')

        try:
            battery = int(battery)
        except:
            pass

        return battery

    def get_flight_time(self):
        """Returns the number of seconds elapsed during flight.

        Returns:
            int: Seconds elapsed during flight.

        """

        flight_time = self.send_command('time?')

        try:
            flight_time = int(flight_time)
        except:
            pass

        return flight_time

    def get_speed(self):
        """Returns the current speed.

        Returns:
            int: Current speed in KPH or MPH.

        """

        speed = self.send_command('speed?')

        try:
            speed = float(speed)

            if self.imperial is True:
                speed = round((speed / 44.704), 1)
            else:
                speed = round((speed / 27.7778), 1)
        except:
            pass

        return speed

    def land(self):
        """Initiates landing.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.send_command('land')

    def move(self, direction, distance):
        """Moves in a direction for a distance.

        This method expects meters or feet. The Tello API expects distances
        from 20 to 500 centimeters.

        Metric: .02 to 5 meters
        Imperial: .7 to 16.4 feet

        Args:
            direction (str): Direction to move, 'forward', 'back', 'right' or 'left'.
            distance (int|float): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        distance = float(distance)

        if self.imperial is True:
            distance = int(round(distance * 30.48))
        else:
            distance = int(round(distance * 100))

        return self.send_command('%s %s' % (direction, distance))

    def move_backward(self, distance):
        """Moves backward for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.move('back', distance)

    def move_down(self, distance):
        """Moves down for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.move('down', distance)

    def move_forward(self, distance):
        """Moves forward for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """
        return self.move('forward', distance)

    def move_left(self, distance):
        """Moves left for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """
        return self.move('left', distance)

    def move_right(self, distance):
        """Moves right for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        """
        return self.move('right', distance)

    def move_up(self, distance):
        """Moves up for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.move('up', distance)

    #### ADDED FUNCTIONS ####
    def keyboard_control(self):
        key = cv2.waitKey(1)
        if key != -1:
            self.keyboard(key)

    def frame_read(self):
        frame = self.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    def calibrate(self, filename='./calibrate.xml'):
        cnt = 0
        while cnt <= 50:
            print(cnt)
            frame = self.read()
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


    def calibrate_read(self, filename='./calibrate.xml'):
        f = cv2.FileStorage(filename, cv2.FILE_STORAGE_READ)

        intrinsic_node = f.getNode('intrinsic')
        distortion_node = f.getNode('distortion')

        intrinsic = intrinsic_node.mat()
        distortion = distortion_node.mat()

        return intrinsic, distortion

    def detect_aruco(self, frame, intrinsic, distortion, debug=False):
        # Detect the markers in the image
        markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(frame, self.aruco_dictionary, parameters=self.aruco_parameters)
        frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)

        rvec, tvec, _objPoints = cv2.aruco.estimatePoseSingleMarkers(markerCorners, 15, intrinsic, distortion)
        
        if debug:
            try:
                frame = cv2.aruco.drawAxis(frame, intrinsic, distortion, rvec, tvec, 8)
                print(tvec)
                print('x: ' + str(tvec[0][0][0]) + ' y: ' + str(tvec[0][0][1]) + ' z: ' + str(tvec[0][0][2]))
                frame = cv2.putText(frame, 'x: ' + str(tvec[0][0][0]) + ' y: ' + str(tvec[0][0][1]) + ' z: ' + str(tvec[0][0][2]), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
                print('drawAxis')
            except:
                pass

            cv2.imshow("findCorners", frame)
            # cv2.waitKey(15)
        
        return rvec, tvec, _objPoints

    def move_to_aruco(self, tvec, margin=self.move_sensitivity, DIST=self.DIST):
        distance = 0.3
        if tvec[0][0][2] > DIST + margin[2]:
            self.move_forward(distance)
        elif tvec[0][0][2] < DIST - margin[2]:
            self.move_backward(distance)
        
        if tvec[0][0][1] < 0 - margin[1] :
            self.move_up(distance)
        elif tvec[0][0][1] > 0 + margin[1]:
            self.move_down(distance)
            
        if tvec[0][0][0] < 0 - margin[0]:
            self.move_left(distance)
        elif tvec[0][0][0] > 0 + margin[0]:
            self.move_right(distance)

    def rotate_by_aruco(self, rvec, margin=self.rot_sensitivity):
        rmat = cv2.Rodrigues(rvec)  #rmat is a tuple of (3*3 mat, 9*3 mat)
        Zprime = np.matmul(rmat[0], np.array([[0, 0, 1]]).T)
        Zprime[1] = 0 # project onto X-Z plane
        V = Zprime
        rad = math.atan2(V[2], V[0])
        deg = math.degrees(rad)
        deg += 90 # adjusting
        
        if deg > 0 + margin:
            self.rotate_ccw(deg)
        elif deg < 0 - margin:
            self.rotate_cw(-deg)