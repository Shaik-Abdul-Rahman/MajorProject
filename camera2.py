import cv2

camera = cv2.VideoCapture(0)

ret,frame = cap.read()

cv2.imshow('Video',frame)
