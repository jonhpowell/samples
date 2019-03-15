
import os
import time
import random
from core.utils.AutoAiLogger import AutoAiLogger
from core.data.AutoAiDAL import AutoAiDAL
from core.data.AutoAiDataExplorer import AutoAiDataExplorer
from core.jobs.AutoAiJobRunner import AutoAiJobRunner
from core.modeling.transformation import Transformation
from core.modeling.model import Model
from sklearn.model_selection import train_test_split
from sklearn import metrics


def simulated_job(args, kwargs):
    wait_secs = random.randint(5, 30)
    print(f'Starting simulated job with wait {wait_secs}')
    time.sleep(wait_secs)
    return random.uniform(0.5, 0.999)


def make_job(args, kwargs):
    transformation = args[0]
    model = args[1]
    X_train = args[2]
    X_val = args[3]
    y_train = args[4]
    y_val = args[5]
    metric_dict = args[6]
    model_selection_metric = args[7]

    X_trans = transformation.pipeline.fit_transform(X_train, y_train)
    model.train(X_trans, y_train)
    X_val_trans = transformation.pipeline.transform(X_val)
    prediction = model.predict(X_val_trans)
    metric = metric_dict[model_selection_metric]

    return metric(y_val, prediction)


class ModelTrainingGenerator:
    
    # TODO: move to utils

    METRIC_DICT = {
        'accuracy':  metrics.accuracy_score,
        'average_precision': metrics.average_precision_score,
        'brier_score_loss': metrics.brier_score_loss,
        'f1': metrics.brier_score_loss,
        'log_loss': metrics.log_loss,
        'precision': metrics.precision_score,
        'roc_auc': metrics.roc_auc_score,
        'explained_variance': metrics.explained_variance_score,
        'mean_absolute_error': metrics.mean_absolute_error,
        'mean_squared_error': metrics.mean_squared_error,
        'mean_squared_log_error': metrics.mean_squared_log_error,
        'median_absolute_error': metrics.median_absolute_error,
        'r2': metrics.r2_score
    }

    def __init__(self, data_explorer, training_config, job_runner, random_state=123):

        self.log = AutoAiLogger('ModelTrainingGenerator')

        self.random_state = random_state
        random.seed(random_state)

        self.data_explorer = data_explorer
        self.training_config = training_config

        self.input_df = self.data_explorer.input_df
        self.target = self.data_explorer.target
        self.weight = self.data_explorer.weight
        self.index = self.data_explorer.index

        msg0 = f'ModelConfig data explorer: target={self.target}, weight={self.weight} index={self.index}, '
        msg0 += 'summary={self.data_explorer.summary}'
        self.log.info(msg0)

        self.model_selection_metric = self.training_config['model_selection_metric']
        self.training_type = self.training_config['training_type']
        self.training_number = self.training_config['training_number']
        self.n_iter_search = self.training_config['n_iter_search']
        self.validation_size = self.training_config['validation_size']
        self.simulated_jobs = self.training_config.get('simulate_jobs', False)

        self.classification = True if self.training_type == 'classification' else False

        msg1 = f'ModelConfig training parms: classification={self.classification}, '
        msg1 += f'selection_metric={self.model_selection_metric}, training_type={self.training_type}, '
        msg1 += f'training_number={self.training_number}, n_iter_search={self.n_iter_search}, '
        msg1 += f'validation_size = {self.validation_size}'
        self.log.info(msg1)

        if self.index is not None:
            self.input_df.set_index(self.index, inplace=True)

        self.train_df, self.val_df = train_test_split(self.input_df, test_size=self.validation_size, random_state=random_state)

        self.tpc = job_runner

        self.models_dictionary = {}

        for i in range(self.training_number):

            transformation = Transformation(
                classification=self.classification,
                random_state=random.randint(1, 1000)
            )
            model = Model(
                self.model_selection_metric,
                n_iter_search=self.n_iter_search,
                classification=self.classification,
                random_state=random.randint(1, 1000)
            )

            model_name = f'model-{i}-{random_state}'
            self.models_dictionary[model_name] = {
                'model': model,
                'transformation': transformation
            }
        self.model_names = self.models_dictionary.keys()

    def run_jobs(self):

        X_train = self.train_df.drop([self.target, self.weight], 1, errors='ignore').copy().values
        X_val = self.val_df.drop([self.target, self.weight], 1, errors='ignore').copy().values
        y_train = self.train_df[self.target].copy().values
        y_val = self.val_df[self.target].copy().values

        # def make_job(transformation, model, X_train, X_val, y_train, y_val):
        #     X_trans = transformation.pipeline.fit_transform(X_train, y_train)
        #     model.train(X_trans, y_train)
        #     X_val_trans = transformation.pipeline.transform(X_val)
        #     prediction = model.predict(X_val_trans)
        #     metric = self.METRIC_DICT[self.model_selection_metric]
        #
        #     return metric(prediction, y_val)

        for model_name, model_config in self.models_dictionary.items():
            res = model_config.get('simulate_jobs', False)
            self.tpc.add_job(
                model_name,
                simulated_job if self.simulated_jobs else make_job,
                model_config['transformation'],
                model_config['model'], X_train, X_val, y_train, y_val, self.METRIC_DICT, self.model_selection_metric)


if __name__ == '__main__':  # simple tests

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

    training_cfg = dict()
    training_cfg['model_selection_metric'] = 'roc_auc'
    training_cfg['training_type'] = 'classification'
    training_cfg['training_number'] = 20
    training_cfg['n_iter_search'] = 20
    training_cfg['validation_size'] = 0.20
    training_cfg['simulate_jobs'] = True  # set to false to run real jobs (not test UI)

    mjr = AutoAiJobRunner()

    tgen = ModelTrainingGenerator(explorer, training_cfg, job_runner=mjr, random_state=123)

    tgen.run_jobs()









