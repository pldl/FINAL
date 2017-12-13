import numpy as np
import argparse
import imutils
import cv2
import socket


cap = cv2.VideoCapture(0)
def reject_outliers(data, m = 2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]
def avg(l):
    return sum(l)/float(len(l))

distance=[]
adistance=0
q=0

host=''
port=50000
size=1024
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((host,port))
s.listen(5)

while(True):
	client,address=s.accept()
	while(True):
		ret,image=cap.read()
		if image is None:
			break
		output=image.copy()
		hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
		lower_red=np.array([0,140,125])
		upper_red=np.array([10,255,255])
		maskO = cv2.inRange(hsv, lower_red,upper_red)
		oRes=cv2.bitwise_and(image,image,mask=maskO)
		cv2.imshow("mask",oRes)
	# find contours in the mask and initialize the current
	# (x, y) center of the ball
		cnts = cv2.findContours(maskO.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
		center = None
 
	# only proceed if at least one contour was found
		if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			if M["m00"]!=0:
				center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			else:
				center = (0,0)
			# only proceed if the radius meets a minimum size
			if True:
				# draw the circle and centroid on the frame,
				# then update the liqst of tracked points
				cv2.circle(image, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(image, center, 5, (0, 0, 255), -1)
				if (33/radius < 15):
					distance.append(33/radius)
		cv2.imshow("frame", image)
		if cv2.waitKey(1)& 0xFF == ord('q'):
			q=1
			break		
		if len(distance)==25:
			adistance=avg(distance)
			client.send(str(adistance)+"\n")
			print(str(adistance))
			distance=[]
			client.close()
			break

	if q==1:
		break
cap.release()		
cv2.destroyAllWindows()
