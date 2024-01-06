import functools
import logging
import secrets
import string
from getpass import getpass

import click

from butler.app import Butler
from butler.authentication import initialize, verify_password
from butler.database import config_db


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
    logging.basicConfig(level=logging.INFO)


@click.command()
def init():
    """Initialize a root password for authentication / encryption and configure database credentials"""
    password = getpass("Please enter root password: ").encode()
    pw2 = getpass(prompt="Please type your password again: ").encode()
    if password != pw2:
        logging.error("Passwords don't match!")
        return
    initialize(password)
    db_name = "".join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    user = "".join(secrets.choice(string.ascii_lowercase) for _ in range(6))
    db_pw = "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(10)
    )
    if config_db(db_name=db_name, user=user, password=db_pw):
        logging.info("Database configured")
    else:
        logging.error("Failed to configure database")


@click.command()
@authenticate
def ls(password):
    """List all apps / sites"""
    with Butler(password) as app:
        all_sites = app.retrieve_all()
        print("All entries:")
        for site in all_sites:
            print(site)


@click.command()
@authenticate
def add(password):
    """Add a new credential"""
    site_name = input("App / site name: ")
    username = input("Username: ")
    user_pw = getpass("Password: ")
    with Butler(password) as app:
        app.add(site_name, username, user_pw)


cli.add_command(add)
cli.add_command(init)
cli.add_command(ls)
