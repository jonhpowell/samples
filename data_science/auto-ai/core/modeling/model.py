
import random
import numpy as np
from sklearn.model_selection import RandomizedSearchCV
import scipy.stats as stats

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from xgboost.sklearn import XGBClassifier
from catboost import CatBoostClassifier


from sklearn.linear_model import ElasticNet
from xgboost.sklearn import XGBRegressor
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.neighbors import KNeighborsRegressor



class Model:

    REGRESSORS = {
        ElasticNet: {
            'alpha': [[1e-4, 1e4], 'range', 'float'],
            'l1_ratio': [[0., 1.], 'range', 'float'],
        },
        XGBRegressor: {
            'max_depth': [list(range(2, 30)), 'discrete', 'integer'],
            'learning_rate': [[1e-5, 1.], 'range', 'float'],
            'gamma': [[1e-5, 10.], 'range', 'float'],
            'min_child_weight': [list(range(1, 30)), 'discrete', 'integer'],
            'max_delta_step': [list(range(1, 100)), 'discrete', 'integer'],
            'subsample': [[0.5, 1.], 'range', 'float'],
            'colsample_bytree': [[0.1, 1.], 'range', 'float'],
            'colsample_bylevel': [[0.1, 1.], 'range', 'float'],
            'reg_alpha': [[1e-5, 10.], 'range', 'float'],
            'reg_lambda': [[1e-5, 10.], 'range', 'float'],
            'scale_pos_weight': [[1e-5, 100.], 'range', 'float']
        },
        CatBoostRegressor: {
            'learning_rate': [[1e-5, 1.], 'range', 'float'],
            'l2_leaf_reg': [[1e-5, 10.], 'range', 'float'],
            'bagging_temperature': [[1e-5, 1e5], 'range', 'float'],
            'sampling_frequency': [['PerTree', 'PerTreeLevel'], 'discrete', 'string'],
            'random_strength': [[0.5, 1.5], 'range', 'float'],
            'depth': [list(range(2, 16)), 'discrete', 'integer'],
            'one_hot_max_size': [list(range(2, 10)), 'discrete', 'integer'],
            'rsm': [[0.1, 1.], 'range', 'float'],
            'nan_mode': [['Min', 'Max'], 'discrete', 'string'],
            'fold_permutation_block_size': [list(range(1, 11)), 'discrete', 'integer'],
            # 'approx_on_full_history': [[False], 'discrete', 'bool'],
            'boosting_type': [['Ordered', 'Plain'], 'discrete', 'string'],
            'border_count': [[50, 254], 'range', 'integer'],
            'feature_border_type': [
                ['Median', 'Uniform', 'UniformAndQuantiles', 'MaxLogSum', 'MinEntropy', 'GreedyLogSum'], 'discrete',
                'string']
        },
        RandomForestRegressor: {
            'criterion': [['mse', 'mae'], 'discrete', 'string'],
            'max_depth': [[1, None], 'range', 'integer'],
            'max_leaf_nodes': [[2, 1000], 'range', 'integer'],
            'max_features': [['sqrt', 'log2', None], 'discrete', 'string'],
            'min_impurity_decrease': [[0., 1.], 'range', 'float'],
            'min_samples_leaf': [[1, 1000], 'range', 'integer'],
            'min_samples_split': [[2, 1000], 'range', 'integer'],
            'min_weight_fraction_leaf': [[0., 0.5], 'range', 'float']
        },
        MLPRegressor: {
            'activation': [['logistic', 'tanh', 'relu'], 'discrete', 'string'],
            'alpha': [[1e-4, 1e4], 'range', 'float'],
            'batch_size': [[32, 64, 128, 256], 'discrete', 'integer'],
            'hidden_layer_sizes': [
                [tuple([random.randint(3, 129) for _ in range(random.randint(1, 11))]) for _ in range(100)],
                'discrete', 'integer']
        },
        KNeighborsRegressor: {
            'weights': [['uniform', 'distance'], 'discrete', 'string'],
            'n_neighbors': [list(range(1, 30, 2)), 'discrete', 'integer'],
            'p': [list(range(1, 11)), 'discrete', 'integer']
        }
    }

    CLASSIFIERS = {
        LogisticRegression: {
            'penalty': [['l1', 'l2'], 'discrete', 'string'],
            'C': [[1e-4, 1e4], 'range', 'float'],
        },
        XGBClassifier: {
            'max_depth': [list(range(2, 30)), 'discrete', 'integer'],
            'learning_rate': [[1e-5, 1.], 'range', 'float'],
            'gamma': [[1e-5, 10.], 'range', 'float'],
            'min_child_weight': [list(range(1, 30)), 'discrete', 'integer'],
            'max_delta_step': [list(range(1, 100)), 'discrete', 'integer'],
            'subsample': [[0.5, 1.], 'range', 'float'],
            'colsample_bytree': [[0.1, 1.], 'range', 'float'],
            'colsample_bylevel': [[0.1, 1.], 'range', 'float'],
            'reg_alpha': [[1e-5, 10.], 'range', 'float'],
            'reg_lambda': [[1e-5, 10.], 'range', 'float'],
            'scale_pos_weight': [[1e-5, 100.], 'range', 'float']
        },
        CatBoostClassifier: {
            'n_estimators': [[10], 'discrete', 'integer'],
            'learning_rate': [[1e-5, 1.], 'range', 'float'],
            'l2_leaf_reg': [[1e-5, 10.], 'range', 'float'],
            'bagging_temperature': [[1e-5, 1e5], 'range', 'float'],
            'sampling_frequency': [['PerTree', 'PerTreeLevel'], 'discrete', 'string'],
            'random_strength': [[0.5, 1.5], 'range', 'float'],
            'depth': [list(range(2, 16)), 'discrete', 'integer'],
            'one_hot_max_size': [list(range(2, 10)), 'discrete', 'integer'],
            'rsm': [[0.1, 1.], 'range', 'float'],
            'nan_mode': [['Min', 'Max'], 'discrete', 'string'],
            'fold_permutation_block_size': [list(range(1, 11)), 'discrete', 'integer'],
            # 'approx_on_full_history': [[True, False], 'discrete', 'bool'],
            'boosting_type': [['Ordered', 'Plain'], 'discrete', 'string'],
            'border_count': [[50, 254], 'range', 'integer'],
            'feature_border_type': [
                ['Median', 'Uniform', 'UniformAndQuantiles', 'MaxLogSum', 'MinEntropy', 'GreedyLogSum'], 'discrete', 'string']
        },
        RandomForestClassifier: {
            'criterion': [['gini', 'entropy'], 'discrete', 'string'],
            'max_depth': [[1, 40], 'range', 'integer'],
            'max_leaf_nodes': [[2, 1000], 'range', 'integer'],
            'max_features': [['sqrt', 'log2', None], 'discrete', 'string'],
            'min_impurity_decrease': [[0., 1e-3], 'range', 'float'],
            'min_samples_leaf': [[1, 1000], 'range', 'integer'],
            'min_samples_split': [[2, 1000], 'range', 'integer'],
            'min_weight_fraction_leaf': [[0., 0.5], 'range', 'float']
        },
        MLPClassifier: {
            'activation': [['logistic', 'tanh', 'relu'], 'discrete', 'string'],
            'alpha': [[1e-4, 1e4], 'range', 'float'],
            'batch_size': [[32, 64, 128, 256, 512], 'discrete', 'integer'],
            'hidden_layer_sizes': [
                [tuple([random.randint(3, 129) for _ in range(random.randint(1, 11))]) for _ in range(100)],
                'discrete', 'integer']
        },
        KNeighborsClassifier: {
            'weights': [['uniform', 'distance'], 'discrete', 'string'],
            'n_neighbors': [list(range(1, 30, 2)), 'discrete', 'integer'],
            'p': [list(range(1, 11)), 'discrete', 'integer']
        }
    }

    def __init__(self, model_selection_metrics, n_iter_search, classification=True, random_state=123):

        np.random.seed(random_state)
        random.seed(random_state)

        self.model_selection_metrics = model_selection_metrics
        self.n_iter_search = n_iter_search
        self.classification = classification
        self.model_class, self.params = self.get_model()
        self.model = self.model_class()

        self.random_search = RandomizedSearchCV(
            self.model,
            param_distributions=self.get_param_distribution(self.params),
            n_iter=self.n_iter_search,
            scoring=self.model_selection_metrics,
            cv=3
        )

        self.best_params = None

    def train(self, X, y):
        self.best_params = self.crossvalidate(X, y)
        self.model.set_params(**self.best_params)

        if self.model_class in [XGBRegressor, XGBClassifier, RandomForestClassifier,
                                RandomForestRegressor, CatBoostClassifier, CatBoostRegressor]:
            self.model.set_params(n_estimators=1000)

        self.model.fit(X, y)

    def crossvalidate(self, X, y):

        self.random_search.fit(X, y)
        return self.random_search.best_params_

    def get_param_distribution(self, params):

        param_dist = {}

        for k, v in params.items():

            if v[1] == 'range':
                if v[2] == 'integer':
                    param_dist[k] = stats.randint(v[0][0], v[0][1])
                else:
                    param_dist[k] = stats.uniform(v[0][0], v[0][1] - v[0][0])
            else:
                param_dist[k] = v[0]

        return param_dist

    def predict(self, X):
        return self.model.predict_proba(X)[:, 1]

    def predict_one(self):
        return

    def get_model(self):
        if self.classification:
            return random.choice(list(self.CLASSIFIERS.items()))
        else:
            return random.choice(list(self.REGRESSORS.items()))



