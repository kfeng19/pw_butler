import click
from butler.authentication import initialize


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "--password",
    hide_input=True,
    prompt="Your root password",
    help="This will be used for encrypting your secrets.",
)
def init(password):
    """Initialize a root password for authentication"""
    initialize(str.encode(password))


cli.add_command(init)
