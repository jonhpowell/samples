import cv2
import numpy as np

flags = [i for i in dir(cv2) if i.startswith('COLOR_RGB2')] # and 'RGB' in i and 'BAYER' not in i and '2RGB' not in i]
print flags

green = np.uint8([[[0,255,0 ]]])
hsv_green = cv2.cvtColor(green,cv2.COLOR_BGR2HSV)
print hsv_green

black = np.uint8([[[0,0,0 ]]])
hsv_black = cv2.cvtColor(black,cv2.COLOR_BGR2HSV)
print hsv_black

# Load a color image
base_path = "/Users/jonpowell/find_phone_task/find_phone/84.jpg"  # 51
img = cv2.imread(base_path, 1)

#convert RGB image to Gray
#gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
#gray=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
#iar = np.asarray(gray)
#print("gray shape={0}".format(iar.shape))

#Display the color image
cv2.imshow('color_image', img)

# TRY: numpy.nonzero(arr)


gray = cv2.cvtColor(img, cv2.COLOR_RGB2BGRA)
imagem = cv2.bitwise_not(gray)

lower_black = np.array([0, 0, 0])
upper_black = np.array([55, 55, 55])
#lower_white = np.array([200])
#upper_white = np.array([255])
mask = cv2.inRange(img, lower_black, upper_black)
res = cv2.bitwise_and(img, img, mask=mask)  # INVERT Bitwise-AND mask and original image

cv2.imshow(str(type) + '_inverted_image', imagem)

cv2.waitKey(0)
cv2.destroyAllWindows()