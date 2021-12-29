from picamera import PiCamera
from time import sleep
from datetime import datetime, timedelta
from ephem import readtle, degree
from sense_hat import SenseHat
import reverse_geocoder as rg
from logzero import logger, logfile
import os
import csv

#we will update the senseHat to show that the program is running
#this will light up green if all is working as expected
#otherwise it will light up red
sense = SenseHat()

#we will use these variables to stop right before the 3 hours mark
current_time = datetime.now()
final_time = current_time + timedelta(hours = 3)

#initiating the camera and setting the resolution of 5MP
camera = PiCamera()
camera.resolution = (2592, 1944)

#we will count the number of photos taken
k_photo = 0

#creating the directory paths of our data file and log file
dir_path = os.path.dirname(os.path.realpath(__file__))
data_file = dir_path + "/data.csv"
logfile(dir_path + "/errors.log")

#set up latest TLE data for ISS location
name  = "ISS (ZARYA)"
line1 = "1 25544U 98067A   20011.25516102  .00000195  00000-0  11565-4 0  9993"
line2 = "2 25544  51.6455  49.9243 0005192 121.3003 338.9406 15.49550468207533"
iss = readtle(name, line1, line2)
   
#write the header of our data file
with open(data_file, 'w') as f:
    writer = csv.writer(f)
    header = ("Name", "Data", "Time", "Latitude", "Longitude");
    writer.writerow(header)
    
#loop running for about 178 minutes
while final_time - current_time > timedelta(minutes = 2):
    #we are trying to avoid any errors
    try:
        sense.show_message("running", text_colour = [0, 255, 0], scroll_speed = 0.1, back_colour = [0, 0, 0])
        
        #we use sleep command to be sure that we don't take more photos than necessary
        #by taking a photo every 9-10 seconds for 178 minutes we end up with 1000 photos
        #1000 5MP photos in memory space usage is roughly 2.7 GB, surely less then 3GB mark
        sleep(9)
        
        #increase the number of photos taken
        #then capture the photo and save it
        k_photo = k_photo + 1
        camera.capture(dir_path + "/image%s.jpg" %k_photo)
        
        #compute the position of ISS and round latitude and longitude to 3 decimal places
        iss.compute()
        pos = (round((iss.sublat / degree), 3), round(iss.sublong / degree, 3))
        
        #create a new variable with the format:
        #name of the photo, data, time, latitude, longitude
        #example
        #image1, 14/02/20, 18:19:03, 18.673, -133.965
        #append the information to data file
        row = ('image%s' %k_photo, datetime.now().strftime("%d/%m/%y %H:%M:%S"), pos[0], pos[1])
        with open(data_file, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        current_time = datetime.now()
    #otherwise log the error encountered in our log file
    except Exception as e:
        sense.show_message("error", text_colour = [255, 0, 0], scroll_speed = 0.1, back_colour = [0, 0, 0])
        logger.error('{}: {})'.format(e.__class__.__name__, e))
camera.close()