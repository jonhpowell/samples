import os
import sys
import cv2
from find_phone import PhoneFinder
from utils import Utils


class PhoneFinderTrainer(Exception):

    """
    From Jon Powell @ jonpowell60@gmail.com

    Take a single command line arg 'path' which is path of directory of labeled jpeg images
     and the expected results in labels.txt in the format {image_name, norm_x, norm_y} to be tested.
    Coordinates are normalized (x,y) and orientation as (0,0) = top left, (1,1) = bottom right.

    - Iterate over possible find functions, accumulating MSE, which will be the model's score. Minimize
        this score over the supervised training set w/o over-training.

    - The function with the lowest MSE will be the function that is called when the command-line version
        of the program executes.

    Assumptions:
        1. Simple supervised learning with training set as ~130 images of Phone as a black rectangle w/white edges.
            Solution is pretty specialized (overtrained?) and builds in the shape/color features into
            code. A more general model might take a more generalized template as input.
        2. Algorithms assume general limits on phone size, its color and and that it's not on edge of overall image.
        3. Final algorithm used: see PhoneFinder.filter_with_adj()

    Next steps to improve finder algorithm:
        1. Image should not be w/in 1/4 image size to edge.
        2. Consider generalizing for other image types.
        3. Consider full image recognition service such as AWS "Rekognition".

    To improve data collection:
        1. Want background contrast!
        2. Eliminate reflections as much as possible.
        3. Diagonal orientation is less desirable.

    Training Loop:
        1. Pass in candidate function that will look for the phone in each image, computing the difference from
            expected and computing each image's MSE. The "quality" of each algorithm will be SUM(MSE).
        2. Develop N candidate functions using above assumptions and rank by simple SUM(MSE).

    """

    base_path = ''

    labels_file_name = 'labels.txt'
    training_dict = {}

    def __init__(self, base_path):
        self.base_path = base_path
        self.training_dict = self.get_training_dict(base_path + os.sep + self.labels_file_name)
#        print('training_dict:\n{0}'.format(self.training_dict))
        print('\nRead {0} entries into training set...'.format(len(self.training_dict)))

    def get_training_dict(self, labels_file_path):

        dict = {}
        with open(labels_file_path) as fp:
            for line in fp:
                fields = line.strip('\n').split(' ')
#                print('{0:8} {1:.4f} {2:.4f}'.format(fields[0], float(fields[1]), float(fields[2])))
                dict[fields[0]] = float(fields[1]), float(fields[2])
        return dict

    def num_training_samples(self):
        return len(self.training_dict)

    def train(self, algorithms, max_img_size):

        acc_mse = {}    # accumulated MSE
        details = []    # stats by algorithm for tabular comparision
        for img_name, xy in trainer.training_dict.iteritems():
            img = cv2.imread(base_path + img_name, 0)  # only load image once, run all algorithms
            for alg in algorithms:
                filtered_img, success, x, y = alg(img, max_img_size)
                mse = Utils.calc_mse(xy[0], xy[1], x, y)
                details.append((mse, img_name, xy[0], xy[1], x, y))
#                print("img={0} mse={1:.4f} ref=({2:.4f},{3:.4f}) alg=({4:.4f},{5:.4f})".format(img, mse, xy[0], xy[1], x, y))
                acc_mse[alg] = acc_mse.get(alg, 0.0) + mse
        print('Find results sorted by worst MSE descending...\n')
        print('idx\tmse\timg\t\tref(x,y)\talg(x,y)\n{0}'.format(65 * '-'))
        count = 0
        for res in sorted(details, reverse=True):
            print("{0}\t{1:.4f}\t{2:10s}\t({3:.4f},{4:.4f})\t({5:.4f},{6:.4f})"
                .format(count, res[0], res[1], res[2], res[3], res[4], res[5]))
            count += 1
        return acc_mse


if __name__ == '__main__':

    ACCEPTABLE_MSE = 0.05
    MAX_IMAGE_SIZE = 50

    find_phone_algorithms = [
#        PhoneFinder.nominal_zero,
#        PhoneFinder.nominal_center,
        PhoneFinder.filter_with_adj,
    ]
    if len(sys.argv) < 2:
        print('Usage: train_phone_finder <training_dir>')
        sys.exit(1)
    base_path = sys.argv[1]

    trainer = PhoneFinderTrainer(base_path)
    accum_mse = trainer.train(find_phone_algorithms, MAX_IMAGE_SIZE)

    print('\nAlgorithm\t\tAccum MSE\n{0}'.format(34 * '-'))
    count = 0
    for alg in find_phone_algorithms:
        print('{0}\t\t{1:.4f}'.format(alg.func_name, accum_mse[alg]))

