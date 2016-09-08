import logging

from flask import jsonify, request
from flask_login import current_user
from flask_security.utils import encrypt_password
from webapp import app, user_datastore, db, User

logger = logging.getLogger(__name__)


@app.route('/api/users')
def get_users():
    if not current_user.has_role('admin'):
        return jsonify({'error': 'User unauthorized'})
    try:
        users = db.session.query(User).all()
        admin_role = user_datastore.find_role('admin')
        table_data = []
        for user in users:
            item = {'id': user.id, 'values': {}}
            item['values']['email'] = user.email
            item['values']['active'] = user.active
            item['values']['admin'] = admin_role in user.roles

            table_data.append(item)

        js = jsonify({'data': table_data})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/users', methods=['POST', ])
def new_user():
    if not current_user.has_role('admin'):
        return jsonify({'error': 'User unauthorized'})
    try:
        email = request.values.get('user-email')
        active = request.values.get('user-active') == 'active'
        admin = request.values.get('user-admin') == 'admin'
        password = request.values.get('user-pass1')
        user = user_datastore.find_user(email=email)
        if user is not None:
            raise Exception('User %s exists' % email)
        enc_password = encrypt_password(password)
        new_user = user_datastore.create_user(email=email, active=active, password=enc_password)
        if admin:
            admin_role = user_datastore.find_role('admin')
            user_datastore.add_role_to_user(new_user, admin_role)
        db.session.commit()
        js = jsonify({'data': new_user.id})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/users/<uid>', methods=['PUT', ])
def modify_user(uid):
    if not current_user.has_role('admin'):
        return jsonify({'error': 'User unauthorized'})
    try:
        key = request.values.get('key')
        value = request.values.get('value')
        user = user_datastore.find_user(id=uid)
        if user is None:
            raise Exception('User %s not found' % uid)
        if key == 'email':
            user.email = value
            db.session.commit()
        elif key == 'active':
            if value == 'true':
                user.active = True
                db.session.commit()
            elif value == 'false':
                user.active = False
                db.session.commit()
            else:
                raise Exception('Value %s not allowed' % value)
        elif key == 'admin':
            admin_role = user_datastore.find_role('admin')
            if value == 'true':
                user_datastore.add_role_to_user(user, admin_role)
                db.session.commit()
            elif value == 'false':
                user_datastore.remove_role_from_user(user, admin_role)
                db.session.commit()
            else:
                raise Exception('Value %s not allowed' % value)
        elif key == 'password':
            user.password = encrypt_password(value)
            db.session.commit()
        else:
            raise Exception('Unknown %s' % key)

        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/users/<uid>', methods=['DELETE', ])
def remove_user(uid):
    if not current_user.has_role('admin'):
        return jsonify({'error': 'User unauthorized'})
    try:
        user = user_datastore.find_user(id=uid)
        if user is None:
            raise Exception('User %s not found' % uid)
        user_datastore.delete_user(user)
        db.session.commit()
        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js
