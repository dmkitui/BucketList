import jwt
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from string import ascii_lowercase, ascii_uppercase, digits
from instance.config import app_config
from flask import request, jsonify, g
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

# Local import to avoid circular import nightmares
from .models import User, UserSchema, BucketlistItemsSchema, BucketlistsSchema

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
        g.user = user
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
        g.user = User.get_user(user_id)
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
    # Sqlachemy has signicant overheads and will be deprecated in future, hence disabled
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():  # Bind the app to current context
        db.create_all()  # create the tables

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
            msg = 'Registration Failure. User {} already registered'.format(user_email)
            return custom_response(msg, 409)

        # User does not exist, create one
        else:

            if user_password != confirm_password:
                msg = 'Password fields do not match'
                return custom_response(msg, 400)

            if not strong_password(user_password):
                msg = 'Weak password. Make sure password contains at least 8 characters, ' \
                      'an uppercase letter, and a digit'
                return custom_response(msg, 400)

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
                return custom_response(str(error), 500)

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
                msg = 'User {} does not exist. Register to access the service'.format(user_email)
                return custom_response(msg, 401)
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
                    msg = 'Incorrect email or password'
                    return custom_response(msg, 401)
        # To return any uncaught server errors
        except Exception as error:
            return custom_response(str(error), 500)

    @app.route('/api/v1/bucketlists/', methods=['GET', 'POST'])
    @multi_auth.login_required
    def bucketlists_all():
        """Route to create or get list of bucketlist items"""
        all_args = request.args.to_dict()
        try:
            q = all_args['q']
            # Check for empty search parameter
            if q == '':
                return custom_response('Search parameter cannot be empty', 400)
        except KeyError:
            q = None

        if request.method == 'POST':
            data, error = BucketlistsSchema(partial=('owner_id', 'id',)).load(request.data)
            if error:
                return error, 400

            name = data['name']

            user_bucketlists = g.user.bucketlists
            bucketlist_names = [bucketlist.name for bucketlist in user_bucketlists]

            if name in bucketlist_names:
                msg = 'Bucketlist already exists'
                return custom_response(msg, 409)

            bucketlist = Bucketlists(name=name, owner_id=g.user.id)
            bucketlist.save()

            obj = Bucketlists.query.filter_by(name=name).first()
            response, error = BucketlistsSchema().dump(obj)
            response.update({'id': len(list(user_bucketlists))+1})

            return response, 201

        elif request.method == 'GET':

            user_bucketlists = g.user.bucketlists
            # request setting for use in bucketlist_data method for setting returned bucketlist id
            g.get_type = 'many'
            if list(user_bucketlists):
                if q:
                    # Apply search
                    search_results = [bucketlist for bucketlist in
                                      user_bucketlists if q.lower() in bucketlist.name.lower()]

                    if not list(search_results):
                        return custom_response('No bucketlists with provided search parameter', 404)

                    response = bucketlist_data(search_results)

                    return response, 200

                else:
                    response = bucketlist_data(user_bucketlists)

                    return response, 200

            else:
                msg = 'No bucketlists available'
                return custom_response(msg, 200)

    @app.route('/api/v1/bucketlists/<int:bucketlist_id>', methods=['GET', 'PUT', 'DELETE'])
    @multi_auth.login_required
    def bucketlist_manipulations(bucketlist_id, **kwargs):
        """Route for operating on a specific bucketlist specified by the integer id argument"""

        if bucketlist_id < 1:
            msg = 'Bucketlist ID should be greater than or equal to 1'
            return custom_response(msg, 400)

        user_bucketlists = g.user.bucketlists

        try:
            bucketlist = user_bucketlists[bucketlist_id - 1]
            g.bucketlist_id = bucketlist_id
        except IndexError:
            msg = 'That bucketlist item does not exist'
            return custom_response(msg, 404)

        if request.method == 'DELETE':

            bucketlist.delete()
            msg = 'Bucketlist No {} deleted successfully'.format(bucketlist.id)
            return custom_response(msg, 200)

        elif request.method == 'PUT':
            data, error = BucketlistsSchema(partial=('name', 'id', 'owner_id')).load(request.data)
            if error:
                return error, 400

            try:
                name = data['name']
            except KeyError:
                msg = 'Update name not given'
                return custom_response(msg, 400)

            current_bucketlist_names = [bucketlist.name for bucketlist in user_bucketlists]
            if name == bucketlist.name:
                msg = 'No changes made.'
                return custom_response(msg, 409)

            if name in current_bucketlist_names:
                msg = 'Bucketlist name with specified name already exists'
                return custom_response(msg, 409)

            bucketlist.name = name
            bucketlist.date_modified = datetime.utcnow()
            bucketlist.save()
            response, error = BucketlistsSchema().dump(bucketlist)
            response.update({'message': 'Bucketlist updated', 'id': bucketlist_id})

            if error:
                return error, 500

            return response, 200

        elif request.method == 'GET':
            # Global setting for use in bucketlist_data method for assigning bucketlist id
            g.get_type = 'one'
            response = bucketlist_data([bucketlist])

            return response, 200

    @app.route('/api/v1/bucketlists/<int:bucketlist_id>/items/', methods=['POST'])
    @multi_auth.login_required
    def bucketlist_items(bucketlist_id):
        """Route to add items to a bucketlist <bucketlist_id>"""

        user_bucketlists = g.user.bucketlists

        try:
            bucketlist = user_bucketlists[(bucketlist_id - 1)]
        except IndexError:
            msg = 'That bucketlist does not exist'
            return custom_response(msg, 404)

        items = bucketlist.bucketlist_items

        data, error = BucketlistItemsSchema(partial=('done',)).load(request.data)
        if error:
            return error, 400

        list_name = data['item_name']

        if list(items):
            item_names = [item.item_name for item in items]
            if list_name in item_names:
                msg = 'The item already in list'
                return custom_response(msg, 409)

        new_item = BucketListItems(item_name=list_name, bucketlist_id=bucketlist.id)
        new_item.save()

        response, error = BucketlistItemsSchema().dump(new_item)
        response.update({'id': len(list(items)), 'bucketlist_id': bucketlist_id})

        if error:
            return error, 500

        return response, 201

    @app.route('/api/v1/bucketlists/<int:bucketlist_id>/items/<item_id>', methods=['PUT',
                                                                                       'DELETE'])
    @multi_auth.login_required
    def bucketlist_edit_items(bucketlist_id, item_id):

        """Route to edit or delete bucketlist items <item_id> of bucketlist <bucketlist_id>"""

        user_bucketlists = g.user.bucketlists

        try:
            bucketlist = user_bucketlists[int(bucketlist_id) - 1]
        except IndexError:
            msg = 'That bucketlist does not exist'
            return custom_response(msg, 404)

        items = bucketlist.bucketlist_items

        try:
            item = items[int(item_id)-1]

        except IndexError:
            msg = 'That bucketlist item does not exist'
            return custom_response(msg, 404)

        if request.method == 'PUT':
            data, error = BucketlistItemsSchema(partial=True).load(request.data)

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
                msg =  'No update made'
                return custom_response(msg, 409)

            bucketlist.date_modified = datetime.utcnow()
            bucketlist.save()

            response, error = BucketlistItemsSchema().dump(item)

            if error:
                return error, 500

            response['message'] = '{}. Item {} successfully updated'.format(msg, item_id)
            response.update({'id': bucketlist_id})

            return response, 201

        elif request.method == 'DELETE':

            item.delete()
            msg = 'Bucketlist item No {} deleted successfully'.format(item_id)
            return custom_response(msg, 200)

    def custom_response(msg, status_code):
        """
        Method to prepare and return json response
        :param msg: Message body
        :param status_code: response status code
        :return: 
        """
        response = jsonify({
            'message': msg
        })
        response.status_code = status_code
        return response

    def bucketlist_data(bucketlists):
        """
        Helper method to get details of bucketlist items
        :param bucketlists: list of bucketlist objects
        :return: json data of the bucketlists data and bucketlist items
        """

        bucketlists_details = []
        for x in range(len(list(bucketlists))):
            bucketlist = bucketlists[x]
            items = bucketlist.bucketlist_items
            items_data = []
            if list(items):
                for y in range(len(list(items))):
                    item = items[y]
                    item_data, error = BucketlistItemsSchema().dump(item)
                    item_data.update({'id': y + 1, 'bucketlist_id': x + 1})
                    items_data.append(item_data)

            bucketlist_obj, error = BucketlistsSchema().dump(bucketlist)
            if g.get_type == 'many':
                current_id = x+1
            else:
                current_id = g.bucketlist_id
            bucketlist_obj.update({'id': current_id, 'items': items_data})
            bucketlists_details.append(bucketlist_obj)

        return bucketlists_details

    return app
