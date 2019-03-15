
import category_encoders as ce
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn import preprocessing
from sklearn.impute import SimpleImputer, MissingIndicator
from sklearn.pipeline import FeatureUnion, make_pipeline
from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import PolynomialFeatures
from sklearn.feature_selection import RFECV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import numpy as np
from sklearn.pipeline import Pipeline
import random
import sys


class Transformation:

    ENCODERS = {
        'BackwardDifferenceEncoder': ce.BackwardDifferenceEncoder(),
        'BinaryEncoder': ce.BinaryEncoder(),
        'HashingEncoder': ce.HashingEncoder(),
        'HelmertEncoder': ce.HelmertEncoder(),
        'OneHotEncoder': ce.OneHotEncoder(),
        'OrdinalEncoder': ce.OrdinalEncoder(),
        'SumEncoder': ce.SumEncoder(),
        'PolynomialEncoder': ce.PolynomialEncoder(),
        'BaseNEncoder': ce.BaseNEncoder(),
        'TargetEncoder': ce.TargetEncoder(),
        'LeaveOneOutEncoder': ce.LeaveOneOutEncoder()
    }

    SCALERS = {
        'MaxAbsScaler': preprocessing.MaxAbsScaler(),
        'MinMaxScaler': preprocessing.MinMaxScaler(),
        'Normalizer': preprocessing.Normalizer(),
        'StandardScaler': preprocessing.StandardScaler(),
    }

    CONTINOUS_PROCESSORS = {
        'PowerTransformer': preprocessing.PowerTransformer(),
        'QuantileTransformer': preprocessing.QuantileTransformer()
    }

    OUTLIER_REMOVERS = {
        'RobustScaler': preprocessing.RobustScaler(),
    }

    def __init__(self, classification=True, random_state=123):

        np.random.seed(random_state)
        random.seed(random_state)
        self.random_state = random_state

        self.classification = classification

        self.pipeline = Pipeline([
            # self.get_object(),
            self.get_encoder(),
            self.get_imputer(),
            self.get_continuous_processor(),
            self.get_new_features(),
            self.get_variance_reduction(),
            self.get_dimension_reduction(),
            self.get_scaler()
        ])

    def get_object(self):
        return "ObjectTypeTransformer", ToObject()

    def get_encoder(self):
        return random.choice(list(self.ENCODERS.items()))

    def get_scaler(self):
        return random.choice(list(self.SCALERS.items()))

    def get_continuous_processor(self):
        return random.choice(list(self.CONTINOUS_PROCESSORS.items()))

    def get_outliers_remover(self):
        return random.choice(list(self.OUTLIER_REMOVERS.items()))

    def get_imputer(self):

        return 'Median_impute', FeatureUnion(
            transformer_list=[
                ('features', SimpleImputer(strategy='median')),
                ('indicators', MissingIndicator())
            ])

    def get_variance_reduction(self):
        variance_reduction = "VarianceThreshold", VarianceThreshold(0.05)
        return variance_reduction

    def get_dimension_reduction(self):
        return "RFECV", DimensionReductor(self.classification, self.random_state)

    def get_new_features(self):
        return "PolynomialFeatures", PolynomialFeatures(interaction_only=True)


class ToObject(TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y):
        self.cols = X.select_dtypes(exclude=["float64", "int64"]).columns.tolist()
        return self

    def transform(self, X):
        X[self.cols] = X[self.cols].astype(object)
        return X


class DimensionReductor(TransformerMixin):

    def __init__(self, classification, random_state):
        self.classification = classification
        self.random_state = random_state
        self.rfe = None

    def fit(self, X, y):
        if self.classification:
            rf = RandomForestClassifier(10, random_state=self.random_state)
        else:
            rf = RandomForestRegressor(10, random_state=self.random_state)

        self.rfe = RFECV(rf, 0.1)

        return self.rfe.fit(X, y)

    def transform(self, X):
        return self.rfe.transform(X)


if __name__ == '__main__':      # simple test

    tr = Transformation()

