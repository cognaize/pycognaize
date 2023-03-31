import click

from pycognaize import model_registry


@click.group()
def cognaize():
    pass


@cognaize.command()
@click.argument('email', type=click.STRING)
def login(email):
    model_registry.login(email)
