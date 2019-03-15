import numpy as np
import cv2


class Utils(Exception):
    """
        From Jon Powell @ jonpowell60@gmail.com

        Utility class for common methods used finding a specific image in an RGB pixel array
    """

    @staticmethod
    def calc_mse(rx, ry, x, y):
        return (rx - x) ** 2 + (ry - y) ** 2

    @staticmethod
    def quarter_array(arr):
        by_y = np.split(arr, 2)
        top_y = np.split(by_y[0], 2, axis=1)
        bot_y = np.split(by_y[1], 2, axis=1)
        return top_y[0], top_y[1], bot_y[1], bot_y[0]  # quadrants from top left, clockwise direction

    @staticmethod
    def non_empty_cols_rows(arr, lim):
        non_empty_x = np.where(arr.max(axis=0) > lim)[0]
        non_empty_y = np.where(arr.max(axis=1) > lim)[0]
        return non_empty_x, non_empty_y

    @staticmethod
    def bounding_box(arr, low_lim, x_max, y_max):
        non_empty_x, non_empty_y = Utils.non_empty_cols_rows(arr, low_lim)
        if len(non_empty_x) > 0 and len(non_empty_y) > 0:
            x_left, x_right, y_top, y_bot = (min(non_empty_x), max(non_empty_x), min(non_empty_y), max(non_empty_y))
            width = x_right - x_left
            height = y_bot - y_top
            center_x = (x_right + x_left) / (2.0 * x_max)
            center_y = (y_top + y_bot) / (2.0 * y_max)
            on_edge = True if x_left < 1 or x_right >= x_max or y_top < 1 or y_bot >= y_max else False
        else:
            width = height = 0.0
            center_x = 0.5
            center_y = 0.5
            on_edge = False
        return center_x, center_y, width, height, on_edge

    @staticmethod
    def filter_image(img, low_lim, high_lim):

        inv_img = cv2.bitwise_not(img)
        ret, thresh = cv2.threshold(inv_img, low_lim, high_lim, cv2.THRESH_TOZERO)

        # Blurring open/close helps; too many contours
        inv_img = cv2.bitwise_not(thresh)

        # remove edges, smooth internally
        median = cv2.medianBlur(inv_img, 5)
        kernel = np.ones((5, 5), np.uint8)
        closed = cv2.morphologyEx(median, cv2.MORPH_CLOSE, kernel)
        inv_closed_img = cv2.bitwise_not(closed)

        x_max = float(img.shape[1])
        y_max = float(img.shape[0])
        return inv_closed_img, x_max, y_max

