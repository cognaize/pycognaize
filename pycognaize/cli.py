import click

from pycognaize import model_registry


@click.group()
def cognaize():
    pass


# @cognaize.command()
# @click.argument('run_id', type=click.DateTime(formats=['%Y-%m-%dT%H.%M.%S.%fZ']))
# def submit(run_id):
#     model_registry.submit(run_id)


@cognaize.command()
@click.argument('email', type=click.STRING)
def login(email):
    model_registry.login(email)
