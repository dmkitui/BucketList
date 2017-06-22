from .bucketlist_app import db
from flask_bcrypt import Bcrypt
from flask import jsonify
import jwt
from datetime import datetime, timedelta
from instance import config


class User(db.Model):
    '''The users table'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(256), nullable=False, unique=True)
    user_password = db.Column(db.String(256), nullable=False)
    date_registered = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, user_email, user_password):
        '''Initialize user with details'''

        self.user_email = user_email
        self.user_password = Bcrypt().generate_password_hash(user_password).decode()

    def password_validity(self, user_password):
        '''
        Checks user provide password against its hash to confirm validity
        :param user_password: User supplied password
        :return: True if provided password is valid against the hash
        '''
        return Bcrypt().check_password_hash(self.user_password, user_password)

    def save(self):
        '''Creates and saves user to the db, or edits and saves changes to existing an existing one'''
        db.session.add(self)
        db.session.commit()

    def generate_user_token(self, user_id):
        '''
        Method to generate a unique user token for authentication.
        :param user_id: User's id
        :return: a user token
        '''
        payload = {
         'exp': datetime.utcnow() + timedelta(seconds=300),
         'iat': datetime.utcnow(),  # Time the jwt was made
         'sub': user_id  # Subject of the payload
        }
        jwt_string = jwt.encode(payload, config.Config.SECRET, algorithm='HS256')
        return jwt_string

    def get_user(self):
        '''Method to return a user from db'''
        return {
            'id': self.id,
            'user_email': self.user_email,
            'user_password': self.user_password,
            'date_registered': self.date_registered
        }

    def delete_user(self):
        '''Delete a user from db and all list items created by them'''
        db.session.remove(self)
        db.session.commit()


class BucketlistBaseModel(db.Model):
    '''Base class for the bucketlists, and bucketlistitems models'''

    __abstract__ = True  # Abstract class for use only in overriding classes

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.now())
    date_modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def save(self):
        '''Method to save a new item'''
        db.session.add(self)
        db.session.commit()

        return self

    def update(self):
        '''Method to apply changes to an item, user'''
        db.session.commit()
        return self

    def delete(self):
        '''function to remove an item from db'''
        db.session.delete(self)
        db.session.commit()

    def get_all(self, queryset):
        '''method to return all items/objects'''

        output = []
        for result in queryset:
            output.append(result.get())

        return output

class BucketListItems(BucketlistBaseModel):
    '''The bucketlist items table'''

    ___tablename__ = 'bucketlist_items'

    item_id = db.Column(db.Integer, db.ForeignKey('bucketlists.id', ondelete='CASCADE'))
    list_item_name = db.Column(db.String(255))  # Name of the bucket list item
    done = db.Column(db.Boolean, default=False)

    def __init__(self, name, bucketlist_id):
        self.list_item_name = name
        self.item_id = bucketlist_id

    @staticmethod
    def get(item_id):
        return BucketListItems.query.filter_by(item_id=item_id)


class Bucketlists(BucketlistBaseModel):
    '''Bucketlist items table'''
    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id

    @staticmethod
    def get(user_id):
        '''method to return a bucketlist'''
        return Bucketlists.query.filter_by(owner_id=user_id)

