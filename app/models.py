from .bucketlist_app import db
from marshmallow import Schema, fields, validates, ValidationError
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
from instance import config


class User(db.Model):
    """The users table"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(256), nullable=False, unique=True)
    user_password = db.Column(db.String(256), nullable=False)
    date_registered = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, user_email, user_password):
        """Initialize user with details"""

        self.user_email = user_email
        self.user_password = Bcrypt().generate_password_hash(user_password).decode()

    def password_validator(self, user_password):
        """
        Checks user provide password against its hash to confirm validity
        :param user_password: User supplied password
        :return: True if provided password is valid against the hash
        """
        return Bcrypt().check_password_hash(self.user_password, user_password)

    def save(self):
        """Creates and saves user to the db, or edits and saves changes to existing an existing one"""
        db.session.add(self)
        db.session.commit()

    def generate_user_token(self, user_id):
        """
        Method to generate a unique user token for authentication.
        :param user_id: User's id
        :return: a user token
        """
        payload = {
         'exp': datetime.utcnow() + timedelta(seconds=3000),
         'iat': datetime.utcnow(),  # Time the jwt was made
         'sub': user_id  # Subject of the payload
        }
        jwt_string = jwt.encode(payload, config.Config.SECRET, algorithm='HS256')
        return jwt_string

    def delete_user(self):
        """Delete a user from db and all list items created by them"""
        db.session.remove(self)
        db.session.commit()


class UserSchema(Schema):
    """Class mapping for User objects to marshmallow fields"""
    
    id = fields.Int()
    date_registered = fields.DateTime()
    user_email = fields.Email(required=True,
                              error_messages={'required': 'Email address not provided'})
    user_password = fields.Str(required=True, load_only=True,
                               error_messages={'required': 'Password not provided'})
    confirm_password = fields.Str(required=True,
                                  error_messages={'required': 'Confirmation password not provided'})


class BucketlistBaseModel(db.Model):
    """Base class for the bucketlists, and bucketlistitems models"""

    __abstract__ = True  # Abstract class for use only inheriting classes.
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.now())
    date_modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def save(self):
        """Method to save a new item"""
        db.session.add(self)
        db.session.commit()
        return self

    def update(self):
        """Method to apply changes to an item, user"""
        db.session.commit()
        return self

    def delete(self):
        """function to remove an item from db"""
        db.session.delete(self)
        db.session.commit()


class BucketListItems(BucketlistBaseModel):
    """The bucketlist items table"""

    ___tablename__ = 'bucketlist_items'

    id = db.Column(db.Integer, primary_key=True)
    # Id the bucketlist belongs to
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlists.id', ondelete='CASCADE'))
    item_name = db.Column(db.String(255))  # Name of the bucket list item
    done = db.Column(db.Boolean, default=False)

    def __init__(self, item_name, bucketlist_id):
        self.item_name = item_name
        self.bucketlist_id = bucketlist_id

    @staticmethod
    def get(item_id):
        return BucketListItems.query.filter_by(item_id=item_id)


class Bucketlists(BucketlistBaseModel):
    """Class for Bucketlist data"""
    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Owner of the bucketlist

    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id

class MarshmallowSchemaBase(Schema):
    """Base class for the marshmallow classes"""
    __abstract__ = True  # Abstract class for use by inheriting classes.
    id = fields.Int()
    date_created = fields.DateTime()
    date_modified = fields.DateTime()


class BuckelistItemsSchema(MarshmallowSchemaBase):
    """Class to map marshmallow fields and bucketlistitems class"""

    bucketlist_id = fields.Int()
    item_name = fields.Str(required=True, error_messages={'required':'Item name not provided'})
    done = fields.Boolean(required=True, error_messages={'required':'Item status not provided'})


class BucketlistsSchema(MarshmallowSchemaBase):
    """Class to map the bucketlists objects to marshmallow fields"""

    name = fields.Str(required=True, error_messages={'required':'Bucketlist name not provided'})
    owner_id = fields.Int(required=True, error_messages={'required':'Bucketlist Owner not provided'})

    @validates('name')
    def name_validator(self, name):
        """Method to validate the name fields"""
        if not name:
            raise ValidationError('Error. No bucketlist name specified')
        try:
            int(name)
            raise ValidationError('Integers only not allowed for the names field')
        except ValueError:
            pass
        except:
            raise ValidationError('Integers only not allowed for the names field')
