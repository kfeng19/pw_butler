import functools
import logging
from getpass import getpass

import click

from butler.app import Butler
from butler.authentication import initialize, verify_password
from butler.database import DBCat


def authenticate(func):
    """A decorator to request and authenticate a password"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        password = getpass("Please enter root password: ").encode()
        if verify_password(password):
            logging.info("Authenticated")
            return func(password, *args, **kwargs)
        else:
            logging.error("Wrong password :(")

    return wrapper


@click.group()
def cli():
    pass


@click.command()
def init():
    """Initialize a root password for authentication and encryption"""
    password = getpass("Please enter root password: ").encode()
    pw2 = getpass(prompt="Please type your password again: ").encode()
    if password != pw2:
        logging.error("Passwords don't match!")
        return
    initialize(password)


@click.command()
@authenticate
def ls(password):
    """List all apps / sites"""
    with Butler(DBCat.Prod, password) as app:
        all_sites = app.retrieve_all()
        for site in all_sites:
            print(site)


cli.add_command(init)
cli.add_command(ls)
