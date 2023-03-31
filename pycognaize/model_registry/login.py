from pathlib import Path

import click
import yaml


def login(email):
    credentials_path = Path.home() / '.pycognaize_auth'

    if credentials_path.exists() and not click.confirm(
            'There is an account already logged in do you want to '
            'override the info?'):
        return

    password = click.prompt('Please specify password',
                            type=click.STRING,
                            hide_input=True)

    credentials = {'email': email, 'password': password}

    with open(credentials_path, 'w') as file:
        file.write(yaml.dump(credentials))
