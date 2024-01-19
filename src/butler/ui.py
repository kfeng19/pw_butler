import functools
import logging
import os
import secrets
import string
from getpass import getpass
from importlib import resources

import click
import pyperclip  # type: ignore
from python_on_whales import DockerClient, docker
from python_on_whales.exceptions import NoSuchVolume

from butler.app import Butler
from butler.authentication import AUTH_PATH, initialize, verify_password
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


def get_docker():
    return DockerClient(compose_files=[resources.files() / "docker-compose.yml"])


@click.group()
def cli():
    logging.basicConfig(level=logging.INFO)


@click.command()
def init():
    """Initialize a root password for authentication / encryption and initialize database"""
    if os.path.isfile(AUTH_PATH):
        logging.warning("Authentication file already exists.")
        go = input("Overwrite? (this would erase any old password data) (y/n): ")
        if go.lower() != "y":
            print("Canceling")
            return
    password = getpass("Please enter root password: ").encode()
    pw2 = getpass(prompt="Please type your password again: ").encode()
    if password != pw2:
        logging.error("Passwords don't match!")
        return
    initialize(password)
    # Drop any existing db volume
    try:
        db_vol = docker.volume.inspect("butler_db")
        logging.info("Erasing old data.")
        db_vol.remove()
    except NoSuchVolume:
        pass
    # Config new db
    db_pw = "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(10)
    )
    if config_db(password=db_pw):
        logging.info("Database configured")
    else:
        logging.error("Failed to configure database")


@click.command
def up():
    """Start up backend services for CLI"""
    docker = get_docker()
    docker.compose.up(detach=True)


@click.command
def down():
    """Stop backend services"""
    docker = get_docker()
    docker.compose.down()


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
    pw2 = getpass("Please type in the password again: ")
    if pw2 != user_pw:
        logging.error("Passwords don't match!")
        return
    with Butler(password) as app:
        app.add(site_name, username, user_pw)


@cli.group()
def get():
    """Retrieve credentials for a site / app"""
    pass


@get.command()
@click.argument("site")
@authenticate
def uname(password, site):
    """Retrieve username"""
    with Butler(password) as app:
        unames = app.retrieve_uname(site)
    if not unames:
        logging.error(f"No entry found for {site}")
    else:
        logging.info(f"Usernames for {site}")
        for name in unames:
            print(name)


@get.command()
@click.argument("site")
@click.argument("username")
@authenticate
def pword(password, site, username):
    """Retrieve password for a site and username"""
    with Butler(password) as app:
        site_pword = app.retrieve_pword(site, username)
    pyperclip.copy(site_pword)
    logging.info("Password copied to clip board!")


cli.add_command(add)
cli.add_command(init)
cli.add_command(ls)
cli.add_command(up)
cli.add_command(down)
