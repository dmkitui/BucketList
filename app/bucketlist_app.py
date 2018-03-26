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
from sqlalchemy import func
from flask_cors import CORS  # This is the magic


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
    :param user_email: user's email address
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
    :return: the decoded user_id or error string
    """
    try:
        payload = jwt.decode(token, config.Config.SECRET, algorithm='HS256')
        return payload['sub']

    except jwt.ExpiredSignatureError: # when token is expired
        return 'Expired token. Please login again to get a new token'

    except jwt.InvalidTokenError:  # When token is invalid
        return 'Invalid token. Register or Login to access the service'


def create_app(config_name):
    """Method to create an flask application, and allow access to the various endpoint routes"""
    # Local imports
    from app.models import Bucketlists, BucketListItems

    app = FlaskAPI(__name__, instance_relative_config=True)
    CORS(app)

    # Preload configurations from app_config object
    app.config.from_object(app_config[config_name])

    # Override configuration above from a configuration file if it exists
    app.config.from_pyfile('config.py')

    # Sqlachemy has signicant overheads and will be deprecated in future, hence we disable.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Create database tables, if they dont exist and tie the db to the app context
    with app.app_context():
        db.create_all()

    @app.route('/')
    def homepage():
        """ The homepage route
        :return: A welcome message
        """
        from flask import render_template
        return render_template('index.html')

    @app.route('/api/v1/auth/register', methods=['POST'])
    def auth_register():
        """Route for new users to register for the service"""

        data, error = UserSchema(partial=('username', 'avatar_url')).load(request.data)

        if error:
            return error, 400

        user_email = data['user_email']
        user_password = data['user_password']
        confirm_password = data['confirm_password']
        try:
            username = data['username']
        except KeyError:
            username = None

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

            new_user = User(user_email=user_email, user_password=user_password, username=username)
            new_user.save()
            response, error = UserSchema().dump(new_user)
            response.update({'message':'Registration successful, welcome to Bucketlist'})

            return response, 201

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
        data, error = UserSchema(partial=('confirm_password', 'username', 'avatar_url')).load(request.data)
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
                access_token = user.generate_user_token(user)
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

    @app.route('/api/v1/auth/update', methods=['POST'])
    @multi_auth.login_required
    def auth_update():
        """Route for updating user info"""
        data, error = UserSchema(partial=('user_password', 'user_email', 'confirm_password', 'username', 'avatar_url')).load(request.data)
        print('DATA: ', data, ' ERRORS: ', error)

        if error:
            return error, 400

        try:
            username = data['username']
        except KeyError:
            username = None

        try:
            avatar_url = data['avatar_url']
        except KeyError:
            avatar_url = None

        if username or avatar_url:
            if username:
                g.user.username = username

            if avatar_url:
                g.user.avatar_url = avatar_url
        else:
            return custom_response('No update supplied', 400)

        try:
            g.user.save()
        except:
            return custom_response('Username Chosen is already taken. Try another one', 400)

        response, error = UserSchema().dump(g.user)
        response.update({'message':'Update successful'})

        return response, 201

    @app.route('/api/v1/bucketlists/', methods=['GET', 'POST'])
    @multi_auth.login_required
    def bucketlists_all(page=1):
        """Route to create or get list of bucketlist items"""
        if request.method == 'POST':
            data, error = BucketlistsSchema(partial=('owner_id', 'id',)).load(request.data)
            if error:
                return error, 400

            name = data['name']

            bucketlists = g.user.bucketlists
            bucketlist_names = [bucketlist.name for bucketlist in bucketlists]

            if name in bucketlist_names:
                msg = 'Bucketlist already exists'
                return custom_response(msg, 409)

            bucketlist = Bucketlists(name=name, owner_id=g.user.id)
            bucketlist.save()

            obj = Bucketlists.query.filter_by(name=name).first()
            output, error = BucketlistsSchema().dump(obj)

            bucketlist_id = len(list(bucketlists)) + 1
            # output.update({'id': bucketlist_id})
            response = jsonify(output)
            response.headers['Location'] = (str(request.url_root) + 'api/v1/bucketlists/' +
                                            str(bucketlist_id))

            return response, 201

        elif request.method == 'GET':
            q = request.args.get('q', type=str)
            limit = request.args.get('limit', default=20, type=None)
            page = request.args.get('page', default=1, type=int)
            
            if q == '':
                return custom_response('Query parameter cannot be empty', 400)

            try:
                limit = int(limit)
            except ValueError:
                return custom_response('Limit parameter can only be a positive integer', 400)

            if not (0 < limit < 101):
                return custom_response('Invalid limit value. Valid values are 1-100', 400)

            # global setting for use in bucketlist_data method for setting returned bucketlist id
            g.get_type = 'many'

            if q:
                # Apply search
                match = Bucketlists.query.filter(func.lower(Bucketlists.name).contains(q.lower()))
                bucketlists = match.filter_by(owner_id=g.user.id).paginate(page, limit, False)

                if not bucketlists.items:
                    return custom_response('No bucketlists with provided search parameter', 404)

            else:
                bucketlists = Bucketlists.query\
                    .filter_by(owner_id=g.user.id)\
                    .order_by(Bucketlists.id)\
                    .paginate(page, limit, False)
                if not bucketlists.items:
                    return custom_response('No bucketlists available', 200)

            g.page = page
            g.total_pages = bucketlists.pages

            response = bucketlist_data(bucketlists.items)

            # Link for the next, previous and last pages, if they exist
            link = ''
            if bucketlists.has_prev:
                response.has_prev = True
                response.prev_num = bucketlists.prev_num
                previous_page = (str(request.url_root) + "api/v1/bucketlists?" + "limit=" +
                                 str(limit) + "&page=" + str(page - 1))
                link += '<'+previous_page+'>' + '; rel="prev", '

            if bucketlists.has_next:
                response.has_next = True
                response.next_num = bucketlists.next_num
                next_page = (request.url_root + "api/v1/bucketlists?" + "limit=" + str(limit) +
                             "&page=" + str(page + 1))
                link += '<'+next_page+'>' + '; rel="next", '

            if bucketlists.pages:
                last_page = (request.url_root + "api/v1/bucketlists?" + "limit=" + str(limit) +
                             "&page=" + str(bucketlists.pages))
                link += '<'+last_page+'>' + '; rel="last"'

            if link:
                response.headers['Link'] = link

            return response, 200

    @app.route('/api/v1/bucketlists/<int:bucketlist_id>', methods=['GET', 'PUT', 'DELETE'])
    @multi_auth.login_required
    def bucketlist_manipulations(bucketlist_id):
        """Route for operating on a specific bucketlist specified by the integer bucketlist_id 
        argument
        """

        if bucketlist_id < 1:
            msg = 'Bucketlist ID should be greater than or equal to 1'
            return custom_response(msg, 400)
        user_bucketlists = g.user.bucketlists
        current_bucketlist_names = [bucketlist.name for bucketlist in user_bucketlists]

        try:
            bucketlist = [x for x in user_bucketlists if x.id == bucketlist_id][0]
            g.bucketlist_id = bucketlist_id
        except IndexError:
            msg = 'That bucketlist item does not exist'
            return custom_response(msg, 404)

        if request.method == 'DELETE':
            bucketlist.delete()
            msg = 'Bucketlist No {} deleted successfully'.format(bucketlist_id)
            return custom_response(msg, 200)

        elif request.method == 'PUT':
            data, error = BucketlistsSchema(partial=('name', 'id', 'owner_id')).load(request.data)
            if error:
                return error, 400

            try:
                name = data['name']
            except KeyError:
                return custom_response('Update name not given', 400)

            if name == bucketlist.name:
                return custom_response('No changes made.', 409)

            if name in current_bucketlist_names:
                return custom_response('Bucketlist name with specified name already exists', 409)

            bucketlist.name = name
            bucketlist.save()
            response, error = BucketlistsSchema().dump(bucketlist)
            response.update({'message': 'Bucketlist updated'})

            return response, 200

        elif request.method == 'GET':
            # Global setting for use in bucketlist_data method for assigning bucketlist id
            g.get_type = 'one'
            response = bucketlist_data([bucketlist])

            return response, 200

    @app.route('/api/v1/bucketlists/<int:bucketlist_id>/items/', methods=['POST'])
    @multi_auth.login_required
    def bucketlist_items(bucketlist_id):
        """Route to add items to a bucketlist with id bucketlist_id"""

        user_bucketlists = g.user.bucketlists

        bucketlist = [bucketlist for bucketlist in user_bucketlists if bucketlist.id == bucketlist_id][0]
        if not bucketlist:
            return custom_response('That bucketlist does not exist', 404)

        items = bucketlist.bucketlist_items

        data, error = BucketlistItemsSchema(partial=('done',)).load(request.data)
        if error:
            return error, 400

        item_name = data['item_name']

        if list(items):
            item_names = [item.item_name for item in items]
            if item_name in item_names:
                return custom_response('The item already in list', 409)

        new_item = BucketListItems(item_name=item_name, bucketlist_id=bucketlist.id)
        new_item.save()
        bucketlist.date_modified = datetime.now()
        bucketlist.save()

        output, error = BucketlistItemsSchema().dump(new_item)

        list_id = len(list(items)) + 1
        output.update({'id': list_id, 'bucketlist_id': bucketlist_id})
        response = jsonify(output)

        response.headers['Location'] = (str(request.url_root) +
                                        'api/v1/bucketlists/{}/items/{}'
                                        .format(str(bucketlist_id), str(list_id)))

        return response, 201

    @app.route('/api/v1/bucketlists/<int:bucketlist_id>/items/<item_id>', methods=['PUT',
                                                                                       'DELETE'])
    @multi_auth.login_required
    def bucketlist_edit_items(bucketlist_id, item_id):

        """Route to edit or delete bucketlist items <item_id> of bucketlist <bucketlist_id>"""

        user_bucketlists = g.user.bucketlists

        bucketlist = [bucketlist for bucketlist in user_bucketlists if bucketlist.id == bucketlist_id][0]
        if not bucketlist:
            return custom_response('That bucketlist does not exist', 404)

        items = bucketlist.bucketlist_items

        try:
            item = items[int(item_id)-1]

        except IndexError:
            return custom_response('That bucketlist item does not exist', 404)

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
                    item.date_modified = datetime.now()
                    item.save()
                    msg += ' Status updated '

            if new_name is not None:
                if new_name == item.item_name:
                    pass
                else:
                    item.item_name = new_name
                    item.date_modified = datetime.now()
                    item.save()
                    msg += ' Name updated '

            if not msg:
                msg = 'No update made'
                return custom_response(msg, 409)

            bucketlist.date_modified = datetime.now()
            bucketlist.save()

            response, error = BucketlistItemsSchema().dump(item)

            response['message'] = '{}. Item {} successfully updated'.format(msg, item_id)
            response.update({'id': bucketlist_id})

            return response, 201

        elif request.method == 'DELETE':

            item.delete()
            return custom_response('Bucketlist item No {} deleted successfully'.format(item_id), 200)

    # ----------------------------------------------------------------------------------------------

    # HELPER METHODS

    # ----------------------------------------------------------------------------------------------

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
                    items_data.append(item_data)

            bucketlist_obj, error = BucketlistsSchema().dump(bucketlist)
            bucketlist_obj.update({'items': items_data})
            bucketlists_details.append(bucketlist_obj)

        if g.get_type == 'many':
            bucketlists_details.append({'current_page': g.page, 'total_pages': g.total_pages})

        return jsonify(bucketlists_details)

    return app
