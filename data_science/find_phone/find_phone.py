import sys
import cv2
from utils import Utils


class PhoneFinder(Exception):
    """
    From Jon Powell @ jonpowell60@gmail.com

    Take a single command line arg 'path' which is path of jpeg image to be tested.
    Output is normalized (x,y) coordinates separated by a space.
    Orientation: (0,0) is top left, (1,1) is bottom right

    Initial ideas:
        1. Use threshold detection to convert everything to either white or black
        2. Look for black bounded by white
        3. Each point has probability of being center
        4. Convert image to List(x,y, probability) for each center point for desired image
        5. Center has equal number of black in each direction along axis of phone (unless phone is angled/tilted)
        6. Convert to chord file: hold x fixed and give y range
        7. Subsample for speed - start @ point and traverse both x & y looking for white. Result is 2 chords (x,y w probability)
        8. Method that returns probability that point is in phone perimeter
        9. Window: slide a * b size window over array, setting boolean
        10. Boolean 2D bit array of True if black; false otherwise
        11. Only need to keep indices of qualifying pixels
        12. Use numPy step to work window function

    """

    @staticmethod
    def filter_with_adj(img, max_img_size):
        """
            Locate the desire image using the following steps:
                1. Filter, blur and otherwise process the original image to make the desired image "pop".
                2. Check for a simple bounding box the size of the image; if there, done.
                3. If no bounding box, increase filtering sensitivity and try again.
                4. If too many bounding boxes, divide image into quadrants and check for simple bounding box

            Use numpy for reasonable efficiency vs. loops.

        :param
            img: detect the object in this RGB image
            max_img_size: size in pixels of object we're looking for, independent of orientation
        :return: tuple of filtered image, success boolean, x, y as normalized center coordinates
            (0,0) is top left, (x_max, y_max) is bottom right
        """

        high_lim = 255
        low_lim = 210
        while low_lim > 140:

            filtered_img, x_max, y_max = Utils.filter_image(img, low_lim, high_lim)
            ctr_x, ctr_y, width, height, on_edge = Utils.bounding_box(filtered_img, low_lim, x_max, y_max)

            if width < 1 and height < 1:   # increase sensitivity
                low_lim -= 20
            elif width < max_img_size and height < max_img_size:
                return filtered_img, True, ctr_x, ctr_y
            else:
                # divide image into quadrants and look for most likely one (could be recursive)
                quad_idx = 0
                for quadrant_img in Utils.quarter_array(filtered_img):
                    ctr_x, ctr_y, w, h, on_edge = Utils.bounding_box(quadrant_img, low_lim, x_max, y_max)
                    if not on_edge and 0 < w < max_img_size and 0 < h < max_img_size:
                        if quad_idx == 1 or quad_idx == 2:      # adjust x & y depended on quadrant
                            ctr_x += 0.5
                        if quad_idx == 2 or quad_idx == 3:
                            ctr_y += 0.5
                        return filtered_img, True, ctr_x, ctr_y
                    quad_idx += 1
                return filtered_img, False, 0.5, 0.5

        return filtered_img, False, 0.5, 0.5

    @staticmethod
    def nominal_center(iar, max_img_size):
        return iar, True, 0.5, 0.5

    @staticmethod
    def nominal_zero(iar, max_img_size):
        return iar, True, 0.0, 0.0


if __name__ == '__main__':

    max_image_size = 50     # max expected size of object to look for

    # set to chosen one or make configurable w/command line parms...
    alg = PhoneFinder.filter_with_adj

    if len(sys.argv) < 2:
        print('Usage: find_phone.py <image_path>')
    else:
        image = cv2.imread(sys.argv[1], 0)
        iar, success, x, y = alg(image, max_image_size)
        print '{0:.4f} {1:.4f}'.format(x, y)
