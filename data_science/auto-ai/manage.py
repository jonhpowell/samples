#!/usr/bin/env python

import os

from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean

from jinja2 import Environment, FileSystemLoader

from shell.webinterface.controllers.main import current_ui_state
from shell import create_app

# default to dev config because no one should use this in
# production anyway
env = os.environ.get('AUTO_AI_ENV', 'dev')
app = create_app('shell.webinterface.settings.%sConfig' % env.capitalize(),
                 env=env)


manager = Manager(app)
manager.add_command("runserver", Server())
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())


#===============================================================================
# @manager.shell
# def make_shell_context():
#     """ Creates a python REPL with several default imports
#         in the context of the app
#     """
#
#     return dict(app=app, db=db, User=User)
#===============================================================================

PROJECT_DIR = os.path.dirname(__file__)


@manager.command
def init_project(project_name="your_flask_project_name"):
    """ Initialize your flask project. right now it does following:
           1. Give it your project name
           2. ... (more ? Welcome your ideas)
    """
    # 1. Give it a project name, save it to your __init__.py file
    env = Environment(loader=FileSystemLoader(
        os.path.join(PROJECT_DIR, 'shell')))
    template = env.get_template('__init__.py')
    output_from_parsed_template = template.render(project_name=project_name)
    #print(output_from_parsed_template)

    with open(os.path.join(PROJECT_DIR, 'shell', "__init__.py"), "wb") as fh:
        fh.write(output_from_parsed_template)


if __name__ == "__main__":
    try:
        manager.run()
    finally:
        current_ui_state.job_runner.kill()
        # current_ui_state.job_runner.shutdown()
