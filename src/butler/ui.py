import click

from butler.authentication import initialize, authenticate


@click.group()
def cli():
    pass


def str2bytes(ctx, param, value):
    if isinstance(value, str):
        return str.encode(value)
    else:
        return value


def pw_option(func):
    return click.option(
        "--password",
        hide_input=True,
        prompt="Your root password",
        callback=str2bytes,
        help="This is used for secret encryption.",
    )(func)


@click.command()
@pw_option
def init(password):
    """Initialize a root password for authentication"""
    initialize(password)


@click.command()
@pw_option
def ls(password):
    if authenticate(password):
        print("Hooray!")
    else:
        print("Wrong password :(")


cli.add_command(init)
cli.add_command(ls)
