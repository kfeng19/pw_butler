import logging
from getpass import getpass

import click

from butler.app import Butler
from butler.authentication import authenticate, initialize
from butler.database import DBCat


def request_pw():
    """Request and authenticate a password"""
    password = getpass("Please enter root password: ").encode()
    if not authenticate(password):
        logging.error("Wrong password :(")
        return None
    logging.info("Authenticated")
    return password


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
def ls():
    """List all apps / sites"""
    password = request_pw()
    if password is not None:
        with Butler(DBCat.Prod, password) as app:
            all_sites = app.retrieve_all()
            for site in all_sites:
                print(site)


cli.add_command(init)
cli.add_command(ls)
