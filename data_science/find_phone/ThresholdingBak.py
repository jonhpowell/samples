import cv2
import numpy as np
#from matplotlib import pyplot as plt
import sys
import os
import time
from train_phone_finder import PhoneFinderTrainer

low_lim = 150
high_lim = 255

base_path = '/Users/jonpowell/find_phone_task/find_phone/'
trainer = PhoneFinderTrainer(base_path)
for img_name, value in trainer.training_dict.iteritems():

    #img_name = '84.jpg'
    img = cv2.imread(base_path+img_name, 0)
    print('image {0}'.format(img_name))
    inv_img = cv2.bitwise_not(img)
    ret, thresh4 = cv2.threshold(inv_img, low_lim, high_lim, cv2.THRESH_TOZERO)

    #cv2.imshow('original', img)
    #cv2.imshow(img_name + '_inverted', inv_img)

    #ret, thresh1 = cv2.threshold(inv_img, low_lim, high_lim, cv2.THRESH_BINARY)
    #cv2.imshow(img_name + '_THRESH_BINARY', thresh1)

    #ret, thresh4 = cv2.threshold(inv_img, low_lim, high_lim, cv2.THRESH_TOZERO)
    #cv2.imshow(img_name + '_THRESH_TOZERO', thresh4)

    # Blurring open/close helps; too many contours
    thresh6 = cv2.adaptiveThreshold(img, low_lim, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 71, 51)
    inv_img = cv2.bitwise_not(thresh4)
    median = cv2.medianBlur(inv_img, 5)
    kernel = np.ones((5, 5), np.uint8)
    closing = cv2.morphologyEx(median, cv2.MORPH_CLOSE, kernel)
    inv_closed_img = cv2.bitwise_not(closing)
    cv2.imshow(img_name + '_ADAPTIVE_THRESH_MEAN_C', inv_closed_img)

    #Z = np.float32(inv_img)
    #criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    #ret, label, center = cv2.kmeans(Z, 2, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    #print center[:, 0], center[:, 1]

    #x, y, w, h = cv2.boundingRect(closing)
    #img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255), 4)
    #contours, hierarchy = cv2.findContours(closing, 1, 2)
    #cnt = contours[0]
    #M = cv2.moments(cnt)
    #print M

    thresh7 = cv2.adaptiveThreshold(img, low_lim, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 71, 71)
    #cv2.imshow(img_name + '_ADAPTIVE_THRESH_GAUSSIAN_C', thresh7)

    ret2, threshold8 = cv2.threshold(img, low_lim, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # no real help
    #cv2.imshow(img_name + '_ADAPTIVE_THRESH_MEAN_C', threshold8)

# to try: OTSU & others on inversion?
#    time.sleep(2)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()

sys.exit(0)


ret, thresh1 = cv2.threshold(inv_img, low_lim, high_lim, cv2.THRESH_BINARY)  # YES
cv2.imshow('THRESH_BINARY', thresh1)

ret, thresh2 = cv2.threshold(inv_img, low_lim, high_lim, cv2.THRESH_BINARY_INV)
#cv2.imshow('THRESH_BINARY_INV', thresh2)

ret, thresh3 = cv2.threshold(inv_img, low_lim, high_lim, cv2.THRESH_TRUNC)
#cv2.imshow('THRESH_TRUNC', thresh3)

ret, thresh4 = cv2.threshold(inv_img, low_lim, high_lim, cv2.THRESH_TOZERO)  # YES
cv2.imshow('THRESH_TOZERO', thresh4)

ret, thresh5 = cv2.threshold(inv_img, low_lim, high_lim, cv2.THRESH_TOZERO_INV)
#cv2.imshow('THRESH_TOZERO_INV', thresh5)

cv2.waitKey(0)
cv2.destroyAllWindows()

path = '/Users/jonpowell/Downloads/conic-gradient-color-wheel.png'

titles = ['Original Image','BINARY','BINARY_INV','TRUNC','TOZERO','TOZERO_INV']
images = [img0, thresh1, thresh2, thresh3, thresh4, thresh5]

'''
for i in xrange(6):
    plt.subplot(2,3,i+1),plt.imshow(images[i],'gray')
    plt.title(titles[i])
    plt.xticks([]),plt.yticks([])

plt.show()
'''