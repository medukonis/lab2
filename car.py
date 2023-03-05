##################################################
# Name:         Michael Edukonis
# UIN:          677141300
# email:        meduk2@illinois.edu
# class:        CS437
# assignment:   Lab2
# date:         3/3/2023
##################################################

import picar_4wd as fc
import time
import cv2
import os
#from tflite_support.task import core
#from tflite_support.task import processor
#from tflite_support.task import vision
import utils
from picamera2 import Picamera2, MappedArray
import json
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

class Car:

    def __init__(self):

        #Set some global variables for oepration
        self.speed = 1                                              #motor speed
        self.scan_result = [0,0,0,0,0,0,0,0,0]                      #list of scan results - measurements to objects
        self.scan_angles = [90, 60, 45, 20, 0, -20, -45, -60, -90]  #preset list of scan angles for the servo.  180 degree sweep
        self.radius = 0
        self.orientation = 'N'                                      #car always starts in an noth orientation.  This was to demonstrate A* routing
        self.location = (0,0)                                       #car always start at 0,0 on the cartesian grid.  This was to demonstrate A* routing

        #Set opencv font parameters for text overlay on picam photo
        self.colour = (0, 255, 0)
        self.origin = (0, 30)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.scale = 1
        self.thickness = 2

        #Set picam initialization and parameters.  Get it setup and running.  Other function will take/store photo
        self.camera = Picamera2()
        self.camera.set_logging(Picamera2.WARNING)
        self.camera.configure(self.camera.create_still_configuration())
        self.camera.pre_callback = self.apply_timestamp
        self.camera.start()

        #Start capturing video input from the camera               #commented out for lab3.  Could not get a video stream going to web front end
        #self.cap = cv2.VideoCapture(0)                             #takes cameraID 0 for pi cam
        #self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        #self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Initialize the object detection model
        #self.base_options = core.BaseOptions(file_name='efficientdet_lite0.tflite', #use_coral=False, num_threads=1)
        #self.detection_options = processor.DetectionOptions(max_results=3, #score_threshold=0.3)
        #self.options = vision.ObjectDetectorOptions(base_options=self.base_options, #detection_options=self.detection_options)
        #self.detector = vision.ObjectDetector.create_from_options(self.options)

##################################################
# Function: plot_scan_results()
# Inputs:   none
# Outputs:  none
# notes:    writes a jpg file of a polar plot of
#           nearby objects based on ultrasonic
#           scan results
##################################################
    def plot_scan_results(self):
        now = datetime.now()
        date_string = now.strftime("%m/%d/%Y")
        time_string = now.strftime("%H:%M:%S")
        r_max = 50.0  #y axis limit that can change this based on range of sensor
        #The scan angles above must be converted into radians as expected by matplotlib.  Since the angles are the same each scan, all are hard coded.
        scan_radians = [3.141592653589793, 2.6179938779914944, 2.356194490192345, 1.9198621771937625, 1.5707963267948966, 1.2217304763960306, 0.7853981633974483, 0.5235987755982988, 0.0]

        #below are parameters for the plot photo.
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='polar')  #represents 180 degree sweep
        ax.set_thetamin(0)
        ax.set_thetamax(180)
        ax.set_ylim([0.0,r_max]) # range of distances to show
        ax.set_xlim([0.0,np.pi]) # limited by the servo span (0-180 deg)
        plt.title("Scan Results " + date_string + " " + time_string, size=20)
        ax.set_xlabel('Distance (cm)', fontsize=15)
        ax.set_ylabel('Angle', fontsize=15, labelpad=30)
        ax.scatter(scan_radians,self.scan_result)

        #save the figure and then make a copy to the webserver directory
        plt.savefig("/home/pi/picar-4wd/examples/scan_result.jpg", facecolor="#849BC1")
        os.system('cp /home/pi/picar-4wd/examples/scan_result.jpg /var/www/html/scan_result.jpg')


##################################################
# Function: get_car_readings()
# Inputs:   none
# Outputs:  dictionary
# notes:    returns a dictionary of timestamp and
#           various car readings such as temp
#           battery level, etc. convert to json
#           object for transport over network
##################################################
    def get_car_readings(self):
        now = datetime.now()
        date_string = now.strftime("%m/%d/%Y")
        time_string = now.strftime("%H:%M:%S")
        result = {"date":date_string,"time":time_string}
        result.update(fc.pi_read())
        #print(result)
        json_object = json.dumps(result, indent=2)
        #print(json_object)
        with open("car_readings.json", "w") as outfile:
            json.dump(result, outfile)
        #making a copy of the json file to the webserver directory however it is not utilized for lab3
        os.system('cp /home/pi/picar-4wd/examples/car_readings.json /var/www/html/car_readings.json')
        #for lab 3 json results are returned to the calling method and the data is sent over the socket.
        return json_object

##################################################
# Function: apply_timestamp()
# Inputs:   none
# Outputs:  none
# notes:    OpenCV applies a date time stamp to
#           picam photos
##################################################
    def apply_timestamp(self, request):
        ts = time.strftime("%Y-%m-%d %X")
        with MappedArray(request, "main") as m:
            cv2.putText(m.array, "meduk2 picar", (5, 50),cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            cv2.putText(m.array, ts, (5, 125),cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)


##################################################
# Function: take_pic()
# Inputs:   none
# Outputs:  none
# notes:    takes a photo from the car's picam
##################################################
    def take_pic(self):
        #save the photo and then make a copy to the webserver directory
        self.camera.capture_file("/home/pi/picar-4wd/examples/img.jpg")
        os.system('cp /home/pi/picar-4wd/examples/img.jpg /var/www/html/img.jpg')
        print('photo captured')

#End new functions for lab3
#######################################################################################################################
##################################################
# Function: scan()
# Inputs:   none
# Outputs:  none
# notes:    calls the set_angle() method from servo
#           object.  Stores the results to the
#           scan_result[] list and prints result
#           to standard output for debug.
##################################################
    def scan(self):
        for x in range(len(self.scan_angles)):
            fc.servo.set_angle(self.scan_angles[x])
            time.sleep(0.1)                                     #decreased from 0.5 to 0.3 to 0.1 - faster scanning
            self.scan_result[x] = int(fc.us.get_distance())
        print("plotting ultrasonic scan results")
        self.plot_scan_results()
        print("done plotting")

##################################################
# Function: move_forward()
# Inputs:   integer
# Outputs:  none
# notes:    takes an integer for power setting and
#           applies to the 4 wheel motors.  Sleep
#           instruction allows car travel time and
#           then stops all motors.
##################################################
    def move_forward(self):
        fc.forward(self.speed)
        print("moving forward") #debug
        time.sleep(0.5)
        self.stop()

##################################################
# Function: handle_video_object()
# Inputs:   string
# Outputs:  none
# Notes:    takes an string from tensorflow image
#           category and acts on the type.
#           only one for now - stop sign
###################################################
    def handle_video_object(self, category):
        #print("handling video")  #debug
        print("Object detected by cam: %s" % category)

        if category == 'stop sign':
            print("stop sign detected - stopping")
            time.sleep(5)
            print("resuming")


##################################################
# Function: turn_right()
# Inputs:   integer
# Outputs:  none
# Notes:    takes an integer for power setting and
#           applies to the 2 left wheel motors
#           forward and 2 right wheels backward
#           effecting a turn right motion on the
#           car. Sleep instruction gives enough
#           time for 90 degree turn and then stops
#           all motors.
###################################################
    def turn_right(self, radius):
        fc.turn_right(self.speed)
        #print("turning right") #debug
        if radius < 90:
            time.sleep(0.5)             #Will give a 45 degree turn
            print("turning right 45 degrees")
        else:
            time.sleep(1.2)             #else 90 degree turn.
            print("turning right 90 degrees")
        self.stop()

###################################################
# Function: turn_left()
# Inputs:   integer
# Outputs:  none
# Notes:    takes an integer for power setting and
#           applies to the 2 right wheel motors
#           forward and 2 left wheels backward
#           effecting a turn left motion on the
#           car. Sleep time gives enough time for
#           90 degree turn and then stops all motors.
###################################################
    def turn_left(self, radius):
        fc.turn_left(self.speed)
        #print("turning left") #debug
        if radius < 90:
            time.sleep(0.5)             #Will give a 45 degree turn
            print("turning left 45 degrees")
        else:                           #Else 90 degree turn
            time.sleep(1.2)
            print("turning left 90 degrees")
        self.stop()

###################################################
# Function: back_up()
# Inputs:   integer
# Outputs:  none
# Notes:    takes an integer for power setting and
#           applies to the 4 wheel motors in
#           reverse.  Sleep instruction allows for
#           travel time and then stop all motors.
###################################################
    def back_up(self):
        fc.backward(self.speed)
        print("backing up") #debug
        time.sleep(0.5)
        self.stop()

###################################################
# Function: stop()
# Inputs:   none
# Outputs:  none
# Notes:    calls the picar object stop method which
#           issues the command to stop all motors.
###################################################
    def stop(self):
        print("stop") #debug
        fc.stop()


    def set_direction(self, currentx, currenty, nextx, nexty):
        if nexty < currenty and nextx < currentx:
            direction = 'NW'
        elif nexty < currenty and nextx == currentx:
            direction = 'N'
        elif nexty < currenty and nextx > currentx:
            direction = 'NE'
        elif nexty == currenty and nextx < currentx:
            direction = 'W'
        elif nexty > currenty and nextx < currentx:
            direction = 'SW'
        elif nexty > currenty and nextx == currentx:
            direction = 'S'
        elif nexty > currenty and nextx > currentx:
            direction = 'SE'
        elif nexty == currenty and nextx > currentx:
            direction = 'E'
        else:
            return "error in set_direction"
        return direction

    def set_orientation(self, current_orientation, direction):
        if current_orientation == direction:
            print("no change in direction")


        #Orientation is North
        elif current_orientation == 'N' and direction == 'NE':
            self.turn_right(45)
            self.orientation = 'NE'
        elif current_orientation == 'N' and direction == 'E':
            self.turn_right(90)
            self.orientation = 'E'
        elif current_orientation == 'N' and direction == 'SE':
            self.turn_right(90)
            self.turn_right(45)
            self.orientation = 'SE'
        elif current_orientation =='N' and direction == 'S':
            self.turn_right(90)
            self.turn_right(90)
            self.orientation = 'S'
        elif current_orientation =='N' and direction == 'SW':
            self.turn_left(90)
            self.turn_left(45)
            self.orientation = 'SW'
        elif current_orientation == 'N' and direction == 'W':
            self.turn_left(90)
            self.orientation = 'W'
        elif current_orientation =='N' and direction == 'NW':
            self.turn_left(45)
            self.orientation = 'NW'


        #Orientation is Northeast
        elif current_orientation == 'NE' and direction == 'N':
            self.turn_left(45)
            self.orientation = 'N'
        elif current_orientation == 'NE' and direction == 'E':
            self.turn_right(45)
            self.orientation = 'E'
        elif current_orientation == 'NE' and direction == 'SE':
            self.turn_right(90)
            self.orientation = 'SE'
        elif current_orientation =='NE' and direction == 'S':
            self.turn_right(90)
            self.turn_right(45)
            self.orientation = 'S'
        elif current_orientation =='NE' and direction == 'SW':
            self.turn_right(90)
            self.turn_right(90)
            self.orientation = 'SW'
        elif current_orientation == 'NE' and direction == 'W':
            self.turn_left(90)
            self.turn_left(45)
            self.orientation = 'W'
        elif current_orientation =='NE' and direction == 'NW':
            self.turn_left(90)
            self.turn_left(90)
            self.orientation = 'NW'

        #Orientation is East
        elif current_orientation == 'E' and direction == 'SE':
            self.turn_right(45)
            self.orientation = 'SE'
        elif current_orientation == 'E' and direction == 'S':
            self.turn_right(90)
            self.orientation = 'S'
        elif current_orientation == 'E' and direction == 'SW':
            self.turn_right(90)
            self.turn_right(45)
            self.orientation = 'SW'
        elif current_orientation =='E' and direction == 'W':
            self.turn_right(90)
            self.turn_right(90)
            self.orientation = 'W'
        elif current_orientation =='E' and direction == 'NW':
            self.turn_left(90)
            self.turn_left(45)
            self.orientation = 'NW'
        elif current_orientation == 'E' and direction == 'N':
            self.turn_left(45)
            self.orientation = 'N'
        elif current_orientation =='E' and direction == 'NE':
            self.turn_left(45)
            self.orientation = 'NE'

        #Orientation is Southeast
        elif current_orientation =='SE' and direction == 'S':
            self.turn_right(45)
            self.orientation = 'S'
        elif current_orientation =='SE' and direction == 'SW':
            self.turn_right(90)
            self.orientation = 'SW'
        elif current_orientation =='SE' and direction == 'W':
            self.turn_right(90)
            self.turn_right(45)
            self.orientation = 'W'
        elif current_orientation =='SE' and direction == 'NW':
            self.turn_right(90)
            self.turn_right(90)
            self.orientation = 'NW'
        elif current_orientation =='SE' and direction == 'N':
            self.turn_left(90)
            self.turn_left(45)
            self.orientation = 'N'
        elif current_orientation =='SE' and direction == 'NE':
            self.turn_left(90)
            self.orientation = 'NE'
        elif current_orientation =='SE' and direction == 'E':
            self.turn_left(45)
            self.orientation = 'E'

        #Orientation is South
        elif current_orientation =='S' and direction == 'SW':
            self.turn_right(45)
            self.orientation = 'SW'
        elif current_orientation =='S' and direction == 'W':
            self.turn_right(90)
            self.orientation = 'W'
        elif current_orientation =='S' and direction == 'NW':
            self.turn_right(90)
            self.turn_right(45)
            self.orientation = 'NW'
        elif current_orientation =='S' and direction == 'N':
            self.turn_right(90)
            self.turn_right(90)
            self.orientation = 'N'
        elif current_orientation =='S' and direction == 'NE':
            self.turn_left(90)
            self.turn_left(45)
            self.orientation = 'NE'
        elif current_orientation =='S' and direction == 'E':
            self.turn_left(90)
            self.orientation = 'E'
        elif current_orientation =='S' and direction == 'SE':
            self.turn_left(45)
            self.orientation = 'SE'

        #Orientation is Southwest
        elif current_orientation =='SW' and direction == 'W':
            self.turn_right(45)
            self.orientation = 'W'
        elif current_orientation =='SW' and direction == 'NW':
            self.turn_right(90)
            self.orientation = 'NW'
        elif current_orientation =='SW' and direction == 'N':
            self.turn_right(90)
            self.turn_right(45)
            self.orientation = 'N'
        elif current_orientation =='SW' and direction == 'NE':
            self.turn_right(90)
            self.turn_right(90)
            self.orientation = 'NE'
        elif current_orientation =='SW' and direction == 'E':
            self.turn_left(90)
            self.turn_left(45)
            self.orientation = 'E'
        elif current_orientation =='SW' and direction == 'SE':
            self.turn_left(90)
            self.orientation = 'SE'
        elif current_orientation =='SW' and direction == 'S':
            self.turn_left(45)
            self.orientation = 'S'

        #Orientation is West
        elif current_orientation =='W' and direction == 'NW':
            self.turn_right(45)
            self.orientation = 'NW'
        elif current_orientation =='W' and direction == 'N':
            self.turn_right(90)
            self.orientation = 'N'
        elif current_orientation =='W' and direction == 'NE':
            self.turn_right(90)
            self.turn_right(45)
            self.orientation = 'NE'
        elif current_orientation =='W' and direction == 'E':
            self.turn_right(90)
            self.turn_right(90)
            self.orientation = 'NE'
        elif current_orientation =='W' and direction == 'SE':
            self.turn_left(90)
            self.turn_left(45)
            self.orientation = 'SE'
        elif current_orientation =='W' and direction == 'S':
            self.turn_left(90)
            self.orientation = 'S'
        elif current_orientation =='W' and direction == 'SW':
            self.turn_left(45)
            self.orientation = 'SW'

        #Orientation is Northwest
        elif current_orientation =='NW' and direction == 'N':
            self.turn_right(45)
            self.orientation = 'N'
        elif current_orientation =='NW' and direction == 'NE':
            self.turn_right(90)
            self.orientation = 'NE'
        elif current_orientation =='NW' and direction == 'E':
            self.turn_right(90)
            self.turn_right(45)
            self.orientation = 'E'
        elif current_orientation =='NW' and direction == 'SE':
            self.turn_right(90)
            self.turn_right(90)
            self.orientation = 'SE'
        elif current_orientation =='NW' and direction == 'S':
            self.turn_left(90)
            self.turn_left(45)
            self.orientation = 'S'
        elif current_orientation =='NW' and direction == 'SW':
            self.turn_left(90)
            self.orientation = 'SW'
        elif current_orientation =='NW' and direction == 'W':
            self.turn_left(45)
            self.orientation = 'W'
        else:
            print("error in set_orientation")

    def cleanup(self):
        self.stop()
        self.cap.release()
        cv2.destroyAllWindows()
        self.camera.close()

