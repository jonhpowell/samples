#!/usr/bin/env python3

import pandas as pd

from core.utils.AutoAiLogger import AutoAiLogger
from core.data.AutoAiDAL import AutoAiDAL

# Title: Auto-AI Data Explorer
#
# Description: imports model training data and provides useful statistics on each column needed for
#    later modeling
#
# Notes:
#   1. Utilize mostly powerful pandas DataFrame methods to determine stats. For int64 dtypes it was deemed
#       useful to determine the number of unique values, which helps with index determination as well as if
#       an int variable is actually more categorical in nature.
#
# TODO:
#


class AutoAiDataExplorer(object):

    log = AutoAiLogger('AutoAiDataExplorer')

    def __init__(self, project_name, input_df):

        self.project_name = project_name
        self.input_df = input_df
        (self.num_rows, self.num_cols) = self.input_df.shape

        self.summary = dict()
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
            types = dict(self.input_df.dtypes)
            description = dict(self.input_df.describe(include='all'))
            for key, value in description.items():
                self.summary[key] = dict(value)
                self.summary[key]['count'] = int(self.summary[key]['count'])  # make count type homogeneous
                self.summary[key]['missing'] = int(self.num_rows - self.summary[key]['count'])  # calc missing
                [self.summary[key].pop(x, None) for x in ['top', 'freq', '25%', '50%', '75%']]  # remove unneeded
                self.summary[key]['type'] = 'string' if str(types[key]) == 'object' else str(types[key])
                if self.summary[key]['type'] == 'int64':   # not provided by pandas, but useful, for int64-type columns
                    self.summary[key]['unique'] = len(self.input_df[key].value_counts())
        self.target = None
        self.index = None
        self.weight = None
        self.log.debug(f"{self.project_name} dataset: {self.num_rows} rows x {self.num_cols} columns, summary={self.summary}")

    '''
    Set specified column as training target.
    NOTE: does not yet validate that it is the only column to be set this way.
    '''
    def set_as_target(self, column_name):
        self.target = column_name

    '''
    Set specified column as data index.
    NOTE: does no validation.
    '''
    def set_as_index(self, column_name):
        self.index = column_name

    '''
    Set specified column as training target.
    NOTE: does not yet validate that it is the only column to be set this way.
    '''
    def set_as_weight(self, column_name):
        self.weight = column_name


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
    explorer = AutoAiDataExplorer("Titanic", df)
    explorer.set_as_target('Survived')
    explorer.set_as_index('PassengerId')
    explorer.set_as_weight('Parch')   # may not make sense

    print(f'Titanic dataset summary: {explorer.summary}')
