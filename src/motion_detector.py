# USAGE
# python motion_detector.py
# python motion_detector.py --video videos/example_01.mp4

# import the necessary packages
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import math
import serial
import time

ser = serial.Serial('COM3')

## constants
motion_disp_threshold = 5	

output_file = 'output_'+ str(time.time()) + '.avi'

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
#outV = cv2.VideoWriter(output_file,fourcc, 20.0, (640,480))
outV = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*"MJPG"), 30,(640,480))

def resetArd(ser):
	ser.write(bytes(int(90))) # reset home

def checkDeviation(disparr):
	'''
		check if the last value is deviating from the last 4 values then return true
		else false
	'''
	lastValue = disparr[4]

	for i in range(3,0,-1):
		if abs(lastValue - disparr[i]) > motion_disp_threshold:
			return True

	return False

def getRotation(displacement, imgcx):

	'''
	
	0-180
	0-90 = -ve
	91-180 = +ve

	'''

	print("displacement ", displacement)
	rotation = 90.0/imgcx * displacement

	if rotation < 0:
		rotation *= -1.0 
	else:
		rotation += 90
	
	print("Rotation ", rotation)
	return rotation

def calculateDisplacement(imgcx, imgcy, bbcx, bbcy):
	'''
		cartesian product
		right +ve
		left -ve
	'''
	sign = 1.0
	## TODO figure outV why arduino does not take -ve count
	if bbcx < imgcx:
		sign = -1.0

	disp = math.sqrt(pow(abs(imgcx - bbcx), 2) + pow(abs(imgcy - bbcy), 2))
	#print(" displacement .. ",disp)
	return getRotation(sign * disp, imgcx)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())
imgcx = 0
imgcy = 0

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
	vs = VideoStream(src=0).start()
	imgcx = vs.stream.get(3)/2
	imgcy = vs.stream.get(4)/2
	print("streaming video frame center .. ", imgcx, imgcy)
	time.sleep(2.0)

# otherwise, we are reading from a video file
else:
	vs = cv2.VideoCapture(args["video"])
	imgcx = vs.get(3)/2
	imgcy = vs.get(4)/2
	print("video file frame center .. ", imgcx, imgcy)

# initialize the first frame in the video stream
firstFrame = None

disparr = [0.0,0.0,0.0,0.0,0.0]
index = 0 # only 5
# loop over the frames of the video
while True:
	# grab the current frame and initialize the occupied/unoccupied
	# text
	frame1 = vs.read()
	
	frame = frame1 if args.get("video", None) is None else frame1[1]
	text = "Unoccupied"

	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if frame is None:
		break

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	#flippedframe = cv2.flip(frame,180)
	# write the useful frame
	#outV.write(flippedframe)
	#outV.write(frame)

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = gray
		continue

	# compute the absolute difference between the current frame and
	# first frame
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	print("cnts.size() ", len(cnts))

	resetBtn = False
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)

		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

		## get center of these bounding boxes
		M = cv2.moments(c)
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])

		print("Bounding Box center :: ", cx, cy)

		disp = calculateDisplacement(imgcx, imgcy, cx, cy);
		disparr[index] = disp

		isUseful = checkDeviation(disparr)
		index +=1
		if index >= 5:
			index = 0

		if isUseful == True:

			print("final displacement .. ",disp)
			print("----------------------------")
			# write the useful frame
			outV.write(frame1)

			ser.write(bytes(int(disp)))
			resetBtn = True

			#ser.close
			#time.sleep(5)

		else:
			print("No Movement !!")
			if resetBtn:
				resetArd(ser)
				resetBtn = False # reset once for no movement
			

		text = "Occupied"

	# draw the text and timestamp on the frame
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# show the frame and record if the user presses a key
	cv2.imshow("Security Feed", frame)
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF
	print("key .... ",key)
	# if the `q` key is pressed, break from the loop
	if key == ord("q"):
		print("Breaking.......")
		break


# Release everything if job is finished
# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
outV.release()
cv2.destroyAllWindows()