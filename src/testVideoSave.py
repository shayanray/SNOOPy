import cv2
import numpy
from imutils.video import VideoStream

vs = VideoStream(src=0).start()
writer = cv2.VideoWriter("output12.avi", cv2.VideoWriter_fourcc(*"MJPG"), 30,(640,480))


while True:
	frame = vs.read()
	writer.write(frame)
	#for frame in range(1000):
	#    writer.write(numpy.random.randint(0, 255, (480,640,3)).astype('uint8'))

	key = cv2.waitKey(1) & 0xFF
	print("key .... ",key)
	# if the `q` key is pressed, break from the loop
	if key == ord("q"):
		print("Breaking.......")
		break

vs.stop() if args.get("video", None) is None else vs.release()
writer.release()