from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from string import ascii_lowercase, ascii_uppercase, digits
from instance.config import app_config
from flask import request, jsonify, abort
# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    from app.models import BucketList
    from .models import User

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/api/v1/auth/register/', methods=['POST'])
    def auth_register():
        '''Method to create a new user'''

        user_email = str(request.data.get('user_email', ''))
        user_password = str(request.data.get('user_password', ''))
        confirm_password = str(request.data.get('confirm_password', ''))

        user = User.query.filter_by(user_email=user_email).first()

        if user:
            response = jsonify({
                'message': 'Registration Failure. User {} already registered'.format(user_email)
            })
            response.status_code = 202
            return response
        # User does not exist, create one
        else:
            if not user_email or not user_password:
                response = jsonify({
                    'message': 'Email or password cannot be blank'
                })
                response.status_code = 401
                return response

            if user_password != confirm_password:
                response = jsonify({
                    'message': 'Password fields do not match'
                })
                response.status_code = 401
                return response

            if not strong_password(user_password):
                response = jsonify({
                    'message': 'Weak password. Make sure password contains at least 8 characters, an uppercase letter, and a digit'
                })
                response.status_code = 401
                return response

            try:
                new_user = User(user_email=user_email, user_password=user_password)
                new_user.save()

                response = jsonify({
                    'message': 'Registration successful, welcome to Bucketlist'
                })
                response.status_code = 201

                return response

            except Exception as error: # When an error occurs
                response = jsonify({
                    'meesage': str(error)
                })
                response.status_code = 401
                return response

    def strong_password(password):
        return len(password) >= 8 and \
               any(upper in password for upper in ascii_uppercase) and \
               any(lower in password for lower in ascii_lowercase) and \
               any(digit in password for digit in digits)


    @app.route('/api/v1/auth/login/', methods=['POST'])
    def auth_login():
        '''Login an existing user'''
        try:
            user_email = str(request.data.get('user_email', ''))
            user_password = str(request.data.get('user_password', ''))

            if not user_email or not user_password:
                response = jsonify({
                    'message': 'Email or password cannot be blank'
                })
                response.status_code = 401
                return response

            user = User.query.filter_by(user_email=user_email).first()

            if not user:
                response = jsonify({
                    'message': 'User {} does not exist. Register to access the service'.format(user_email)
                })
                response.status_code = 401
                return response
            else:
                if user and user.password_validity(user_password):
                    access_token = user.generate_user_token(user.id)
                    if access_token:
                        response = jsonify({
                            'message': 'Login successful',
                            'access_token': access_token.decode()
                        })
                        response.status_code = 200
                        return response

                else:
                    response = jsonify({
                        'message': 'Invalid email or password'
                    })
                    response.status_code = 401
                    return response
        except Exception as error:
            response = jsonify({
                'message': str(error)
            })
            response.status_code = 500
            return response

    @app.route('/api/v1/bucketlists/', methods=['GET', 'POST'])
    def bucketlists():
        '''method to create or return list of bucketlist items'''
        if request.method == 'POST':
            name = str(request.data.get('list_item_name', ''))
            if name:
                bucketlist = BucketList(list_item_name=name)
                bucketlist.save()
                response = jsonify({
                    'id': bucketlist.id,
                    'list_item_name': bucketlist.list_item_name,
                    'date_posted': bucketlist.date_posted,
                    'date_modified': bucketlist.date_modified
                })
                response.status_code = 201
                return response

        elif request.method == 'GET':
            bucketlists = BucketList.get_all()
            results = []

            for bucketlist in bucketlists:
                obj = {
                'id': bucketlist.id,
                'list_item_name': bucketlist.list_item_name,
                'date_posted': bucketlist.date_posted,
                'date_modified': bucketlist.date_modified
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route('/api/v1/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def bucketlist_manipulations(id, **kwargs):
        bucketlist = BucketList.query.filter_by(id=id).first() # retrieve a list item by id

        if not bucketlist:
            abort(404)  # When buckelist item not found, HTTP status code of 404

        if request.method == 'DELETE':
            bucketlist.delete()

            return { 'message': 'Bucketlist item No {} deleted successfully'.format(bucketlist.id)}, 200

        elif request.method == 'PUT':
            name = str(request.data.get('list_item_name', ''))
            bucketlist.list_item_name = name
            bucketlist.save()

            response = jsonify({
                'id': bucketlist.id,
                'list_item_name': bucketlist.list_item_name,
                'date_posted': bucketlist.date_posted,
                'date_modified': bucketlist.date_modified
            })
            response.status_code = 200
            return response

        elif request.method == 'GET':

            response = jsonify({
                'id': bucketlist.id,
                'list_item_name': bucketlist.list_item_name,
                'date_posted': bucketlist.date_posted,
                'date_modified': bucketlist.date_modified
            })

            response.status_code = 200
            return response

    return app
