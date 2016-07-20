import logging

from flask import Flask, jsonify
from flask_bootstrap import Bootstrap
from flask_environments import Environments
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
from flask_security import RoleMixin, UserMixin, SQLAlchemyUserDatastore, Security

app = Flask(__name__, template_folder='templates', static_folder='static')
Bootstrap(app)

# Load configuration depending on FLASK_ENV environment variable
env = Environments(app)
env.from_yaml('config.yml')

# Create database connection object
db = SQLAlchemy(app)

from webapp.wu_client import WuClient

wuclient = WuClient()

try:
    with open('gmap_api_key') as f:
        gmap_api_key = f.read().strip()
except Exception, e:
    logging.warning('Google map API key not found: %s', e)

import models

# Define security models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return '<User id=%s email=%s>' % (self.id, self.email)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.before_first_request
def init_db():
    db.create_all()
    # Create admin user if doesn't exist
    admin_role = user_datastore.find_or_create_role('admin')
    admin_user = user_datastore.find_user(email=app.config['ADMIN_EMAIL'])
    if admin_user is None:
        user_datastore.create_user(email=app.config['ADMIN_EMAIL'],
                                   password=app.config['ADMIN_PASSWORD'],
                                   roles=[admin_role, ])
    db.session.commit()


@app.errorhandler(404)
@app.errorhandler(500)
def missing_resource(ex):
    response = jsonify(error=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


import page
import api
