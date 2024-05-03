import cv2
face_detect=cv2.CascadeClassifier('C:/Users/3rdLABSYSTEM01/Downloads/haarcascade_frontalface_default.xml')
img=cv2.imread('img3.jpg')
gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
faces=face_detect.detectMultiScale(gray,1.2,5)
for (x,y,w,h) in faces:
    cv2.rectangle(img,(x,y),(x+w,y+h),(160,130,200),2)
cv2.imshow('img',img)
cv2.waitKey()