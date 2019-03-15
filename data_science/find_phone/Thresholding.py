import cv2
from train_phone_finder import PhoneFinderTrainer
from find_phone import PhoneFinder
from utils import Utils

'''
    TODO:
        1. Make Utils file for all statics
        2. 
'''


base_path = '/Users/jonpowell/find_phone_task/find_phone/'
do_plot = False

ACCEPTABLE_MSE = 0.05
MAX_IMAGE_SIZE = 50

trainer = PhoneFinderTrainer(base_path)
finder = PhoneFinder(MAX_IMAGE_SIZE)
good_count = 0
bad_count = 0

for img_name, xy in trainer.training_dict.iteritems():

    #img_name = '84.jpg'
    print('image {0}'.format(img_name))

    img = cv2.imread(base_path+img_name, 0)
    filtered_img, success, ctr_x, ctr_y = PhoneFinder.filter_with_adj(img, MAX_IMAGE_SIZE)
    mse = Utils.calc_mse(xy[0], xy[1], ctr_x, ctr_y)
    if mse < ACCEPTABLE_MSE:
        status = 'GOOD'
        good_count += 1
    else:
        status = 'BAD'
        bad_count += 1
    if status is 'BAD':
        title = "{0} center=({1:.2f},{2:.2f}) ref=({3:.2f},{4:.2f})".format(status, ctr_x, ctr_y, xy[0], xy[1])
        print(title)

    if do_plot:
        cv2.imshow(img_name + "_orig", img)
        cv2.moveWindow(img_name + "_orig", 0, 0)
        cv2.imshow(img_name + title, filtered_img)
        cv2.moveWindow(img_name + title, 0, 400)
        cv2.waitKey(1)
        cv2.destroyAllWindows()

print('good_count={0} bad_count={1}'.format(good_count, bad_count))
percent_good = good_count / float(len(trainer.training_dict))
print('{0:.2f}% within {1:.3f} mse (70% good is sufficient)'.format(len(trainer.training_dict)*0.7, ACCEPTABLE_MSE))
