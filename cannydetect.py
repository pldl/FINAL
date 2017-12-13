# USAGE
# python detect_color.py --image example_shapes.png

# import the necessary packages
from pyimagesearch.shapedetector import ShapeDetector
from pyimagesearch.colorlabeler import ColorLabeler
import numpy as np
import argparse
import glob
import imutils
import cv2
import socket
def checkEqual1(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == rest for rest in iterator)
def auto_canny(image, sigma=0.33):
	v=np.median(image)
	lower = int(max(0,(1.0-sigma)*v))
	upper = int(min(255,(1.0+sigma)*v))
	edged=cv2.Canny(image,lower,upper)
	return edged
host=''
port=50007
size=1024
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((host,port))
s.listen(5)
dup=[]
Quit=0
cap = cv2.VideoCapture(0)
while(True):
	client,address=s.accept()
	while(True):
		
		B=0
		ret,image=cap.read()
		if image is None:
			break
		resized = imutils.resize(image, width=300)
		ratio = image.shape[0] / float(resized.shape[0])

# blur the resized image slightly, then convert it to both
# grayscale and the L*a*b* color spaces
		blurred = cv2.GaussianBlur(resized, (5, 5), 0)
		gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
		auto= auto_canny(blurred)
		lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
		thresh = cv2.threshold(auto, 100, 255, cv2.THRESH_BINARY)[1]
		cv2.imshow("Thresh", thresh)
	

# find contours in the thresholded image
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	
        
# initialize the shape detector and color labeler
		sd = ShapeDetector()
		cl = ColorLabeler()
		Output=""
# loop over the contours
		for c in cnts:
	# compute the center of the contour
			M = cv2.moments(c)
			if M["m00"]!=0:
				cX = int((M["m10"] / M["m00"]) * ratio)
				cY = int((M["m01"] / M["m00"]) * ratio)
			else:
				cX,cY=0,0

	# detect the shape of the contour and label the color
			shape = sd.detect(c)
			color = cl.label(lab, c)

	# multiply the contour (x, y)-coordinates by the resize ratio,
	# then draw the contours and the name of the shape and labeled
	# color on the image
			c = c.astype("float")
			c *= ratio
			c = c.astype("int")
			text = "{} {}".format(color, shape)
                #change into specific color shape combinations.
			if text=="yellow circle" or text=="red pentagon" or text=="green rectangle" or text=="orange triangle":
				if Output!="":
					Output+=" "
				Output+=text
		cv2.imshow("Image",image)
		if cv2.waitKey(1)& 0xFF == ord('q'):
			Quit=1
			break
		if Output!="":
			dup.append(Output)
			if len(dup)==10:
				if checkEqual1(dup)==True:
					client.send(Output+"\n")
					print Output
					client.close()
					B=1
					Quit=1
				dup=[]
		if B==1:
			break
	if Quit==1:
		break
cap.release()		
cv2.destroyAllWindows()
