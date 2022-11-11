import argparse

from src.model import CurrentModel as GenieModel

parser = argparse.ArgumentParser(description='Execute and'
                                 ' evaluate genie models')
parser.add_argument('action', metavar='action', type=str,
                    help='an action to be run on the task'
                         ' [execute | evaluate]')
parser.add_argument('--task_id', type=str, required=True, nargs='*')
parser.add_argument('--base_doc_task_id', type=str)
parser.add_argument('--token', type=str, required=True)
parser.add_argument('--url', type=str, required=True)
parser.add_argument('--model_version', type=str)

parser.add_argument('-bulk', '--bulk',  action='store_true')
parser.add_argument('-based_on_match', '--based_on_match', action='store_true')


def main():
    """Argparser for pycognaize"""
    args = parser.parse_args()

    action = args.action
    task_ids, token, url = args.task_id, args.token, args.url
    base_doc_task_id = args.base_doc_task_id
    print(base_doc_task_id)

    if action == 'execute':
        run_model(task_ids, token, url, base_doc_task_id, args.based_on_match)
    elif action == 'evaluate':
        model_version = args.base_doc_task_id
        evaluate_model(model_version, token, url)
    else:
        print('Unknown action')


def run_model(task_ids, token, url, base_doc_task_id, based_on_match):
    """Execute model given parameters from cli"""
    for task_id in task_ids:
        if based_on_match:
            if base_doc_task_id is None:
                raise ValueError('base_doc_task_id is required when'
                                 ' based_on_match is True')
            GenieModel().execute_based_on_match(task_id,
                                                base_doc_task_id,
                                                token, url)
        else:
            GenieModel().execute_genie_v2(task_id, token, url)


def evaluate_model(token, url, model_version):
    """Run Model evaluation given parameters from cli"""
    if model_version is None:
        raise ValueError('model_version is required when action is evaluate')
    GenieModel().evaluate(token, url, model_version)
