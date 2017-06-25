import jwt
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from string import ascii_lowercase, ascii_uppercase, digits
from instance.config import app_config
from flask import request, jsonify, abort, g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from instance import config
from flask_bcrypt import Bcrypt
from datetime import datetime

# initialize sql-alchemy
db = SQLAlchemy()

# Authentication declarations
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)

# Local import to avoid circular import nightmare
from .models import User, UserSchema, BuckelistItemsSchema, BucketlistsSchema

# username and password verification
@basic_auth.verify_password
def verify_password(user_email, user_password):
    """
    Checks user provide password against its hash to confirm validity
    :param user_password: User supplied password
    :return: True if provided password is valid against the hash
    """
    user = User.query.filter_by(user_email=user_email).first()

    if user and Bcrypt().check_password_hash(user.user_password, user_password):
        g.user_id = user.id
        return True
    else:
        return False

# Token Authentication
@token_auth.verify_token
def verify_token(access_token):
    """Verifies the user token for expiration time, invalid token and sets user id if valid
    :param access_token from the header
    """
    user_id = decode_token(access_token)
    if not isinstance(user_id, str):
        g.user_id = user_id
        return True

    else:
        return False


def decode_token(token):
    """
    method to decode the access token during authorization
    :param token: User token from authorization header
    :return: the decoded token
    """
    try:
        payload = jwt.decode(token, config.Config.SECRET, algorithm='HS256')
        return payload['sub']

    except jwt.ExpiredSignatureError: # when token is expired
        return 'Expired token. Please login again to get a new token'

    except jwt.InvalidTokenError:  # When token is invalid
        return 'Invalid token. Register or Login to access the service'


def create_app(config_name):
    from app.models import Bucketlists, BucketListItems

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():  # Bind the app to current context
        db.create_all()  # create the tables

    @app.before_request
    def database_check():
        """Method to confirm database tables setup, and provide user friendly information if 
        they dont exist"""
        engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        user_table = engine.dialect.has_table(engine, 'users')
        bucketlist_table = engine.dialect.has_table(engine, 'bucketlists')
        items_table = engine.dialect.has_table(engine, 'bucketlist_items')

        if not user_table or not bucketlist_table or not items_table:
            if app.config['ENV'] == 'testing': #  Dont return error in testing environment
                pass
            else:
                response = ({
                    'message': 'Database not properly setup. Application shall exit'
                })
                return response, 500

    @app.route('/api/v1/auth/register', methods=['POST'])
    def auth_register():
        """Route for creating a user"""

        data, error = UserSchema().load(request.data)

        if error:
            return error, 400

        user_email = data['user_email']
        user_password = data['user_password']
        confirm_password = data['confirm_password']

        user = User.query.filter_by(user_email=user_email).first()

        if user:
            response = jsonify({
                'message': 'Registration Failure. User {} already registered'.format(user_email)
            })
            response.status_code = 409
            return response

        # User does not exist, create one
        else:

            if user_password != confirm_password:
                response = jsonify({
                    'message': 'Password fields do not match'
                })
                response.status_code = 400
                return response

            if not strong_password(user_password):
                response = jsonify({
                    'message': 'Weak password. Make sure password contains at least 8 characters, an uppercase letter, and a digit'
                })
                response.status_code = 400
                return response

            try:
                new_user = User(user_email=user_email, user_password=user_password)
                new_user.save()

                obj = User.query.filter_by(user_email=user_email).first()

                response, error = UserSchema().dump(obj)

                if error:
                    return error, 500

                response.update({'message':'Registration successful, welcome to Bucketlist'})

                return response, 201

            except Exception as error: # When an error occurs
                response = jsonify({
                    'message': str(error)
                })
                response.status_code = 500
                return response

    def strong_password(password):
        """
        Function to evaluate the strenght of a password
        :param password: user proposed password
        :return: True if password is strong, False if not strong
        """
        return len(password) >= 8 and \
               any(upper in password for upper in ascii_uppercase) and \
               any(lower in password for lower in ascii_lowercase) and \
               any(digit in password for digit in digits)

    @app.route('/api/v1/auth/login', methods=['POST'])
    def auth_login():
        """Route for Login"""
        try:
            data, error = UserSchema(partial=('confirm_password',)).load(request.data)
            if error:
                return error, 400

            user_email = data['user_email']
            user_password = data['user_password']

            user = User.query.filter_by(user_email=user_email).first()

            if not user:
                response = jsonify({
                    'message': 'User {} does not exist. Register to access the service'.format(user_email)
                })
                response.status_code = 401
                return response
            else:
                if user and user.password_validator(user_password):
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
                        'message': 'Incorrect email or password'
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
        """Route to create or get list of bucketlist items"""
        if request.method == 'POST':

            data, error = BucketlistsSchema(partial=('owner_id', 'id',)).load(request.data)
            if error:
                return error, 400

            name = data['name']

            all_user_bucketlists = Bucketlists.query.filter_by(owner_id=g.user_id)
            bucketlist_names = [x.name for x in all_user_bucketlists]

            if name in bucketlist_names:
                response = jsonify({
                    'message': 'Bucketlist already exists'
                })
                response.status_code = 409
                return response

            bucketlist = Bucketlists(name=name, owner_id=g.user_id)
            bucketlist.save()

            obj = Bucketlists.query.filter_by(name=name).first()
            response, error = BucketlistsSchema().dumps(obj)

            return response, 201

        elif request.method == 'GET':

            available_bucketlists = Bucketlists.query.filter_by(owner_id=g.user_id)

            if list(available_bucketlists):
                bucketlists_details = {}
                for bucketlist in available_bucketlists:
                    item_details = []
                    items = BucketListItems.query.filter_by(bucketlist_id=bucketlist.id)
                    if list(items):
                        item_data, error = BuckelistItemsSchema(many=True).dump(items)
                        item_details.append(item_data)

                    bucketlist_obj, error = BucketlistsSchema().dump(bucketlist)

                    bucketlist_obj.update({'items': item_details})

                    bucketlists_details.update({bucketlist.name : bucketlist_obj})

                if bucketlists_details:
                    response = bucketlists_details

            else:
                response = jsonify({
                    'message': 'No bucketlists available'
                })

            return response, 200

    @app.route('/api/v1/bucketlists/<int:bucketlist_id>', methods=['GET', 'PUT', 'DELETE'])
    @multi_auth.login_required
    def bucketlist_manipulations(bucketlist_id, **kwargs):
        """Route for operating on a specific bucketlist specified by the integer id argument"""
        # Retrieve the list item by id
        bucketlist = Bucketlists.query.filter_by(id=bucketlist_id).first()

        if not bucketlist:
            response = jsonify({
                'message': 'That bucketlist item does not exist'
            })
            response.status_code = 404
            return response

        if request.method == 'DELETE':
            bucketlist.delete()

            response = jsonify({
                'message': 'Bucketlist No {} deleted successfully'.format(bucketlist.id)
            })
            response.status_code = 200
            return response

        elif request.method == 'PUT':
            # Edit the bucketlist
            data, error = BucketlistsSchema(partial=('owner_id',)).load(request.data)
            if error:
                return error, 400

            name = data['name']

            if name == bucketlist.name:
                response = jsonify({
                    'message': 'No changes made.'
                })
                response.status_code = 409
                return response

            bucketlist.name = name
            bucketlist.date_modified = datetime.utcnow()
            bucketlist.save()

            bucketist_obj = Bucketlists.query.filter_by(id=bucketlist_id).first()
            response, error = BucketlistsSchema().dump(bucketist_obj)
            response.update({'message': 'Bucketlist updated'})

            if error:
                return error, 500

            return response, 200

        elif request.method == 'GET':
            # Retrieve the list item by id
            bucketlist = Bucketlists.query.filter_by(id=bucketlist_id).first()

            if not bucketlist:
                response = jsonify({
                    'message': 'That bucketlist item does not exist'
                })
                response.status_code = 404
                return response

            bucketlists_details = {}
            item_details = []
            items = BucketListItems.query.filter_by(bucketlist_id=bucketlist.id)

            if list(items):
                item_data, error = BuckelistItemsSchema(many=True).dump(items)
                item_details.append(item_data)

            bucketlist_obj, error = BucketlistsSchema().dump(bucketlist)

            bucketlist_obj.update({'items': item_details})

            bucketlists_details.update(bucketlist_obj)

            response = bucketlists_details

            return response, 200

    @app.route('/api/v1/bucketlists/<int:bucketlist_id>/items/', methods=['POST'])
    @multi_auth.login_required
    def bucketlist_items(bucketlist_id):
        """Route to add items to a bucketlist <bucketlist_id>"""
        if not isinstance(bucketlist_id, int):
            response = jsonify({
                'message': 'Bucketlist ID format must be an integer'
            })
            response.status_code = 400
            return response

        bucketlist = Bucketlists.query.filter_by(id=bucketlist_id).first()

        if not bucketlist:
            response = jsonify({
                'message': 'That bucketlist does not exist'
            })
            response.status_code = 404
            return response

        items = BucketListItems.query.filter_by(bucketlist_id=bucketlist_id)

        data, error = BuckelistItemsSchema(partial=('done',)).load(request.data)

        if error:
            return error, 400

        list_name = data['item_name']

        if list(items):
            item_names = [item.item_name for item in items]
            if list_name in item_names:
                response = jsonify({
                    'message':'The item already in list'
                })
                return response, 409

        new_item = BucketListItems(item_name=list_name, bucketlist_id=bucketlist_id)
        new_item.save()

        list_object = BucketListItems.query.filter_by(item_name=list_name).first()

        response, error = BuckelistItemsSchema().dump(list_object)

        if error:
            return error, 500

        return response, 201

    @app.route('/api/v1/bucketlists/<int:bucketlist_id>/items/<item_id>', methods=['PUT',
                                                                                       'DELETE'])
    @multi_auth.login_required
    def bucketlist_edit_items(bucketlist_id, item_id):

        """Route to edit or delete bucketlist items <item_id> of bucketlist <bucketlist_id>"""

        bucketlist = Bucketlists.query.filter_by(id=bucketlist_id).first()

        if not bucketlist:
            response = jsonify({
                'message': 'That bucketlist does not exist'
            })
            response.status_code = 404
            return response

        item = BucketListItems.query.filter_by(bucketlist_id=bucketlist_id, id=item_id).first()

        if not item:
            response = jsonify({
                'message': 'That bucketlist item does not exist'
            })
            response.status_code = 404
            return response

        if request.method == 'PUT':
            data, error = BuckelistItemsSchema(partial=True).load(request.data)

            try:
                new_name = data['item_name']
            except KeyError:
                new_name = None

            try:
                status = data['done']
            except KeyError:
                status = None

            msg = ''
            if status is not None:
                if status == item.done:
                    pass
                else:
                    item.done = status
                    item.date_modified = datetime.utcnow()
                    item.save()
                    msg += ' Status updated '

            if new_name is not None:
                if new_name == item.item_name:
                    pass
                else:
                    item.item_name = new_name
                    item.date_modified = datetime.utcnow()
                    item.save()
                    msg += ' Name updated '

            if not msg:
                response = ({
                    'message': 'No update made'
                })
                return response, 409

            bucketlist.date_modified = datetime.utcnow()
            bucketlist.save()

            item_obj = BucketListItems.query.filter_by(item_name=item.item_name).first()

            response, error = BuckelistItemsSchema().dump(item_obj)

            if error:
                return error, 500

            response['message'] = '{}. Item {} successfully updated'.format(msg, item_id)

            return response, 201

        elif request.method == 'DELETE':

            item.delete()

            response = jsonify({
                'message': 'Bucketlist item No {} deleted successfully'.format(item.id)
            })
            response.status_code = 200
            return response

    return app
