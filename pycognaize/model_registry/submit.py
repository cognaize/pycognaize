import datetime
import json
import os
import subprocess
from pathlib import Path

import click
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from pycognaize.model_registry.db.models import Run, Experiment


class ModelRegistry:

    def __init__(self):
        self.project_path = Path.cwd()

    def submit(self, run_id):
        self._assert_all_changes_committed()

        kedro_metadata = self._get_kedro_metadata(run_id)
        metrics = self._get_kedro_metrics(run_id)
        github_data = self._get_github_data()

        postgres_engine = create_engine(os.getenv('DB_URL'))

        with Session(postgres_engine) as session:
            experiment = Experiment(**kedro_metadata,
                                    metrics=metrics,
                                    **github_data)

            session.add(experiment)
            session.commit()
            run = session.scalars(select(Experiment)).all()

            print(run)

        print(github_data)

    def _assert_all_changes_committed(self):
        try:
            status_process = subprocess.run(['git', 'status', '-s'],
                                            capture_output=True,
                                            check=True,
                                            text=True)

            status_output = status_process.stdout.strip()
        except FileNotFoundError:
            raise click.UsageError('Git should be installed '
                                   'to submit the data.')

        if status_output:
            raise click.UsageError('There are some modifications '
                                   'to the repo. Make sure all changes are'
                                   ' committed.')

    def _get_kedro_metadata(self, run_id):
        db_path = self.project_path / 'data' / 'session_store.db'

        sqlite_engine = create_engine(f'sqlite:///{db_path}')

        with Session(sqlite_engine) as session:
            run = session.scalars(select(Run).where(Run.id == run_id)).first()

            if run is None:
                print('Sorry matching run not found')
                return None

            run.blob = json.loads(run.blob)
            executed_date = datetime.datetime.strptime(run.blob['session_id'],
                                                       '%Y-%m-%dT%H.%M.%S.%fZ')
            return {'executed_at': executed_date,
                    'command': run.blob['cli']['command_path']}

    def _get_kedro_metrics(self, run_id):
        tracking_path = self.project_path / 'data' / '09_tracking'

        metrics = {}

        for metric_dir in tracking_path.iterdir():
            if metric_dir.is_dir():
                metric_dir_name = metric_dir.name

                for run_dir in metric_dir.iterdir():
                    if run_dir.is_dir() and run_dir.name == run_id:
                        file_path = run_dir / metric_dir_name

                        with file_path.open('r') as metric_file:
                            metrics[metric_dir_name] = json.loads(
                                metric_file.read())

        return metrics

    def _get_github_data(self):
        github_data = {}
        try:
            repo_url_command = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'], capture_output=True,
                check=True,
                text=True)
            github_data['git_repo'] = repo_url_command.stdout.strip()

            username_command = subprocess.run(['git', 'config', 'user.name'],
                                              capture_output=True,
                                              check=True,
                                              text=True)
            github_data['github_name'] = username_command.stdout.strip()

            email_command = subprocess.run(['git', 'config', 'user.email'],
                                           capture_output=True,
                                           check=True,
                                           text=True)
            github_data['github_email'] = email_command.stdout.strip()

            commit_hash_command = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                                 capture_output=True,
                                                 check=True,
                                                 text=True)
            github_data['git_commit_hash'] = commit_hash_command.stdout.strip()

        except subprocess.CalledProcessError:
            print('Sorry something went wrong')
        finally:
            return github_data


def submit(run_id):
    registry = ModelRegistry()
    registry.submit(run_id)
