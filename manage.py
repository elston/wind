#!/usr/bin/env python

import argparse
import getpass
import logging

from webapp import app, user_datastore
from flask_security.utils import encrypt_password


def add_user(args):
    email = args.args[0]
    user = user_datastore.find_user(email=email)
    if user is not None:
        logging.error('User %s already exists', email)
        return
    while True:
        pass1 = getpass.getpass('New password:')
        pass2 = getpass.getpass('New password again:')
        if pass1 == pass2:
            break
        print "Passwords doesn't match"
    admin = args.admin
    with app.app_context():
        if admin:
            admin_role = user_datastore.find_or_create_role('admin')
            roles = [admin_role, ]
        else:
            roles = []
        user_datastore.create_user(email=email,
                                   password=encrypt_password(pass1),
                                   roles=roles)
        user_datastore.commit()
        logging.info('User %s created', email)


def remove_user(args):
    email = args.args[0]
    with app.app_context():
        user = user_datastore.find_user(email=email)
        if user is None:
            logging.error("User %s doesn't exist", email)
        else:
            user_datastore.delete_user(user)
            logging.info('User %s removed', email)


def encrypt():
    with app.app_context():
        password = getpass.getpass('New password:')
        print(encrypt_password(password))


def main(args, loglevel, parser):
    logging.basicConfig(format='%(levelname)s: %(message)s', level=loglevel)

    if args.command == 'add_user':
        add_user(args)
    elif args.command == 'remove_user':
        remove_user(args)
    elif args.command == 'encrypt_password':
        encrypt()
    else:
        parser.print_help()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Executes action.',
    )

    parser.add_argument(
        'command',
        help='command to execute')
    parser.add_argument(
        'args',
        nargs='*',
        help='arguments for command')
    parser.add_argument(
        '-v',
        '--verbose',
        help='increase output verbosity',
        action='store_true')
    parser.add_argument(
        '--admin',
        action='store_true')
    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    main(args, loglevel, parser)
