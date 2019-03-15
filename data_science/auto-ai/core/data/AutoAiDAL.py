#!/usr/bin/env python3

import pandas as pd

from core.utils.AutoAiLogger import AutoAiLogger

# Title: Auto-AI DAL (Data Access Layer)
#
# Description: abstraction for reading/writing data
#
# Notes: just does CSV read for now, and the file needs to have column names
#
# TODO:
#


class AutoAiDAL(object):

    log = AutoAiLogger('AutoAiDAL')

    def __init__(self, project_name, home_dir):
        self.project_name = project_name
        self.home_dir = home_dir
        self.log.debug(f"AutoAiDAL initialized, name={self.project_name}, home dir={self.home_dir}")

    def load_csv_file(self, file_path):
        return pd.read_csv(self.home_dir + '/' + file_path)


if __name__ == '__main__':      # simple test

    import os

    project_dir = os.path.abspath(os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)))
    )
    dal = AutoAiDAL(
        'Titanic',
        os.path.join(project_dir, 'test', 'datasets'))

    df = dal.load_csv_file('titanic_train.csv')
    print(f'df={df}')
