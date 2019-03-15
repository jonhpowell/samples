import os

from flask import (
    Blueprint, current_app, jsonify, render_template, abort, request)
from werkzeug.utils import secure_filename

from core.data import AutoAiDAL, AutoAiDataExplorer
from core.jobs.AutoAiJobRunner import AutoAiJobRunner
from core.modeling.ModelTrainingGenerator import ModelTrainingGenerator
from core.utils.AutoAiLogger import AutoAiLogger

main = Blueprint('main', __name__)


class UiState(object):
    logger = AutoAiLogger('UI')
    dal = None
    data_explorer = None
    model_gen = None
    job_runner = AutoAiJobRunner()


current_ui_state = UiState()

INITIAL_PROJECTS = [
    { 'id': 0,
      'name': 'Ticket Routing'
    },{ 'id': 1,
      'name': 'Failure Detection'
    },{ 'id': 2,
      'name': 'Churn Prediction'
    },
]


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/projects')
def projects():
    return render_template('main/projects.html',
                           projects=INITIAL_PROJECTS)


@main.route('/add_project', methods=['POST'])
def add_project():
    new_project = dict(
        id=request.form.get('id', type=int),
        name=request.form.get('name')
    )
    INITIAL_PROJECTS.append(new_project)
    return "Success"


@main.route('/upload_data/')
@main.route('/upload_data/<int:project_id>')
def upload_data(project_id=None):
    if project_id is not None:
        the_project = next(p for p in INITIAL_PROJECTS
                           if p["id"] == project_id)
        return render_template('main/upload_data.html',
                               current_project=the_project)
    else:
        abort(404)


@main.route('/project_config/')
@main.route('/project_config/<int:project_id>', methods=['GET', 'POST'])
def project_config(project_id=None):
    if project_id is not None:
        the_project = next(p for p in INITIAL_PROJECTS
                           if p["id"] == project_id)
        # project_name = the_project['name']
        # dal = AutoAiDAL(
        #    project_name,
        #    os.path.join(project_dir, 'test', 'datasets'))

        project_home_dir = '/tmp'
        project_name = the_project['name']
        if the_project['name'].lower() == 'titanic':
            project_home_dir = current_app.config['DEV_TEST_DS_DIR']
            current_ui_state.dal = AutoAiDAL.AutoAiDAL(
                project_name, project_home_dir)
            # (NOTE:tonytan4ever) for now hardcode to load up titanic's
            # dataframe
            df = current_ui_state.dal.load_csv_file('titanic_train.csv')
            current_ui_state.data_explorer = AutoAiDataExplorer.AutoAiDataExplorer(
                project_name, df)
        else:
            # save the file
            data_file = request.files['data_file']
            filename = secure_filename(data_file.filename)
            file_dst_path = os.path.join(project_home_dir, filename)
            data_file.save(file_dst_path)

            current_ui_state.dal = AutoAiDAL.AutoAiDAL(
                project_name, project_home_dir)
            df = current_ui_state.dal.load_csv_file(filename)
            current_ui_state.data_explorer = (
                AutoAiDataExplorer.AutoAiDataExplorer(project_name, df))

        return render_template('main/project_config.html',
                               current_project=the_project,
                               data_explorer=current_ui_state.data_explorer
                               )
    else:
        abort(404)


@main.route('/start_training/<int:project_id>')
@main.route('/start_training/<int:project_id>', methods=['GET', 'POST'])
def start_training(project_id=None):
    if project_id is not None:
        the_project = next(p for p in INITIAL_PROJECTS if p["id"] == project_id)
        if request.method.lower() == "post":
            form_items = dict(request.form.items())
            current_ui_state.logger.debug(f'start_training form_items={form_items}')
            training_cfg = dict()
            training_cfg['model_selection_metric'] = form_items['model_selection_metric']
            training_cfg['training_type'] = form_items['training_type']
            training_cfg['training_number'] = 20    # advanced options later in UI
            training_cfg['n_iter_search'] = 200     # advanced options later in UI
            training_cfg['validation_size'] = 0.20  # advanced options later in UI
            training_cfg['simulate_jobs'] = True    # set to false to run real jobs (not test UI)
            current_ui_state.logger.debug(f'training_cfg={training_cfg}')

            current_ui_state.data_explorer.set_as_target(form_items['target_row'])
            current_ui_state.data_explorer.set_as_index(form_items['index_row'])
            current_ui_state.data_explorer.set_as_weight(form_items['weight_row'])
            current_ui_state.logger.debug(
                f'training target/index/weight columns: {form_items["target_row"]}/{form_items["index_row"]}/{form_items["weight_row"]}')

            current_ui_state.model_gen = ModelTrainingGenerator(
                current_ui_state.data_explorer, training_cfg,
                current_ui_state.job_runner, random_state=123)
            current_ui_state.model_gen.run_jobs()

        return "Okay"
    else:
        abort(404)


@main.route('/start_testing/<int:project_id>')
@main.route('/start_testing/<int:project_id>', methods=['GET', 'POST'])
def start_testing(project_id=None):
    if project_id is not None:
        the_project = next(p for p
                           in INITIAL_PROJECTS if p["id"] == project_id)
        return render_template('main/start_testing.html',
                               current_project=the_project)
    else:
        abort(404)


@main.route('/training_summary/')
@main.route('/training_summary/<int:project_id>')
def training_summary(
        project_id=None,
):
    if project_id is not None:
        the_project = next(p for p in INITIAL_PROJECTS if p["id"] == project_id)
        current_job_runner_progress = current_ui_state.job_runner.get_status()
        current_job_runner_results = current_ui_state.job_runner.get_results()
        return render_template('main/training_summary.html',
                               current_job_runner_progress=current_job_runner_progress,
                               current_job_runner_results=current_job_runner_results,
                               current_project=the_project)
    else:
        abort(404)


@main.route('/training_job_update')
def training_job_update():

    current_job_runner_progress = current_ui_state.job_runner.get_status()
    current_job_runner_results = current_ui_state.job_runner.get_results()

    print(f'###### JobRunner status={current_job_runner_progress}')
    print(f'###### JobRunner results={current_job_runner_results}')

    return jsonify({
        'status': 'success',
        'training_job_status': current_job_runner_progress,
        'training_job_results': current_job_runner_results
    })


@main.route('/predict/')
@main.route('/predict/<int:project_id>')
def predict(project_id=None):
    if project_id is not None:
        the_project = next(p for p in INITIAL_PROJECTS
                           if p["id"] == project_id)
        return render_template('main/upload_test_data.html',
                               current_project=the_project)
    else:
        abort(404)
