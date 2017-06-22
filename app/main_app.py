import jwt
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from string import ascii_lowercase, ascii_uppercase, digits
from instance.config import app_config
from flask import request, jsonify, abort, g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from instance import config
from flask_bcrypt import Bcrypt




# initialize sql-alchemy

db = SQLAlchemy()

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)

#  username and password verification
from .models import User

@basic_auth.verify_password
def verify_password(user_email, user_password):
    '''
    Checks user provide password against its hash to confirm validity
    :param user_password: User supplied password
    :return: True if provided password is valid against the hash
    '''
    user = User.query.filter_by(user_email=user_email).first()

    if user and Bcrypt().check_password_hash(user.user_password, user_password):
        g.user_id = user.id
        return True
    else:
        return False

# Token Authentication
@token_auth.verify_token
def verify_token(access_token):
    '''Verifies the user token for expiration time, invalid token and sets user id if valid'''
    user_id = decode_token(access_token)
    if not isinstance(user_id, str):
        g.user_id = user_id
        return True

    else:
        return False


def decode_token(token):
    '''
    method to decode the access token during authorization
    :param token: User token from authorization header
    :return: the decoded token
    '''
    try:
        payload = jwt.decode(token, config.Config.SECRET, algorithm='HS256')
        return payload['sub']

    except jwt.ExpiredSignatureError: # when token is expired
        return 'Expired token. Please login again to get a new token'

    except jwt.InvalidTokenError:  # When token is invalid
        return 'Invalid token. Register or Login to access the service'


def create_app(config_name):
    from app.models import Bucketlists, BucketListItems

    # from .models import User

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():  # Bind the app to current context
        db.create_all()  # create the tables

    @app.route('/api/v1/auth/register', methods=['POST'])
    def auth_register():
        '''Method to create a new user'''

        user_email = str(request.data.get('user_email', ''))
        user_password = str(request.data.get('user_password', ''))
        confirm_password = str(request.data.get('confirm_password', ''))

        if not user_email or not user_password:
            response = jsonify({
                'message': 'Email or password cannot be blank'
            })
            response.status_code = 401
            return response

        user = User.query.filter_by(user_email=user_email).first()

        if user:
            response = jsonify({
                'message': 'Registration Failure. User {} already registered'.format(user_email)
            })
            response.status_code = 202
            return response
        # User does not exist, create one
        else:

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


    @app.route('/api/v1/auth/login', methods=['POST'])
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
                            'access_token': access_token.decode(),
                        })
                        response.status_code = 200
                        return response

                else:
                    response = jsonify({
                        'message': 'Invalid email or password'
                    })
                    response.status_code = 401
                    return response
        # To return any uncaught server errors
        except Exception as error:
            response = jsonify({
                'message': str(error)
            })
            response.status_code = 500
            return response

    @app.route('/api/v1/bucketlists/', methods=['GET', 'POST'])
    @multi_auth.login_required
    def bucketlists():
        '''method to create or return list of bucketlist items'''

        if request.method == 'POST':
            name = str(request.data.get('name', ''))

            if name:
                all_user_bucketlists = Bucketlists.query.filter_by(owner_id=g.user_id)
                bucketlist_names = [x.name for x in all_user_bucketlists]

                if name in bucketlist_names:
                    response = jsonify({
                        'message': 'Bucketlist item already exists'
                    })
                    response.status_code = 201
                    return response

                bucketlist = Bucketlists(name=name, owner_id=g.user_id)
                bucketlist.save()
                response = jsonify({
                    'id': bucketlist.id,
                    'name': bucketlist.name,
                    'date_posted': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified
                })
                response.status_code = 201
                return response

            else:  # No name for bucketlist name specified
                response = jsonify({
                    'message': 'Error. No bucketlist name specified'
                })
                response.status_code = 401
                return response

        elif request.method == 'GET':

            bucketlists = Bucketlists.get(g.user_id)

            bucketlists_details = []
            for bucketlist in bucketlists:
                list_items = []
                items = BucketListItems.query.filter_by(item_id=bucketlist.id)

                if items:
                    for item in items:
                        obj = {
                            'list_item': item.list_item_name,
                            'date_created': item.date_created,
                            'date_modified': item.date_modified,
                            'done': item.done
                        }
                        list_items.append(obj)

                bucketlist_data = {
                    'id': bucketlist.id,
                    'name': bucketlist.name,
                    'items': list_items,
                    'date_created': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified
                }
                bucketlists_details.append(bucketlist_data)

            if bucketlists_details:
                response = jsonify({
                    'bucketlists': bucketlists_details
                })
                response.status_code = 200
            else:
                response = jsonify({
                    'message': 'No bucketlists available'
                })
                response.status_code = 200

            return response

    @app.route('/api/v1/bucketlists/<int:bucketlist_id>', methods=['GET', 'PUT', 'DELETE'])
    @multi_auth.login_required
    def bucketlist_manipulations(bucketlist_id, **kwargs):
        '''Route for getting a specific bucketlist item specified by the integer id argument'''

        bucketlist = Bucketlists.query.filter_by(id=bucketlist_id).first()  # retrieve the list item by id

        if not bucketlist:
            response = jsonify({
                'message': 'That bucketlist item does not exist'
            })
            response.status_code = 404
            return response

        if request.method == 'DELETE':
            bucketlist.delete()
            bucketlist.update()

            response = jsonify({
                'message': 'Bucketlist item No {} deleted successfully'.format(bucketlist.id)
            })
            response.status_code = 200
            return response

        elif request.method == 'PUT':
            name = str(request.data.get('list_item_name', ''))

            current_list_items = BucketListItems.query.filter_by(item_id=bucketlist_id)
            list_item_names = [x.list_item_name for x in current_list_items]

            # Code for when there is no name
            if name in list_item_names:
                response = jsonify({
                    'message': 'Item already in bucketlist.'
                })
                response.status_code = 409
                return response
            elif not name:
                response = jsonify({
                    'message': 'Bucketlist list item name not given.'
                })
                response.status_code = 400
                return response

            bucketlist_item = BucketListItems(name=name, bucketlist_id=bucketlist_id)
            bucketlist_item.save()

            response = jsonify({
                'id': bucketlist_item.id,
                'bucketlist': Bucketlists.query.filter_by(owner_id=g.user_id).first().name,
                'new_item': bucketlist_item.list_item_name,
                'date_posted': bucketlist_item.date_created,
                'date_modified': bucketlist_item.date_modified,
                'created_by': g.user_id
            })
            response.status_code = 201
            return response

        elif request.method == 'GET':

            bucketlist = Bucketlists.query.filter_by(id=bucketlist_id).first()  # retrieve the list item by id

            if not bucketlist:
                abort(404)  # When buckelist item not found, HTTP status code of 404

            items = BucketListItems.query.filter_by(item_id=bucketlist_id)
            list_items = []
            if items:
                for item in items:
                    obj = {
                        'list_item': item.list_item_name,
                        'date_created': item.date_created,
                        'date_modified': item.date_modified,
                        'done': item.done
                    }
                    list_items.append(obj)

            response = jsonify({
                'id': bucketlist.id,
                'name': bucketlist.name,
                'items': list_items,
                'date_posted': bucketlist.date_created,
                'date_modified': bucketlist.date_modified,
                'created_by': g.user_id
            })

            response.status_code = 200
            return response


    return app
