from .bucketlist_app import db
from marshmallow import Schema, fields, validates, ValidationError
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
from instance import config
from ago import human


class User(db.Model):
    """The users table"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(256), nullable=False, unique=True)
    user_password = db.Column(db.String(256), nullable=False)
    date_registered = db.Column(db.DateTime, default=db.func.now())
    bucketlists = db.relationship('Bucketlists')
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

    @staticmethod
    def get_user(user_id):
        """Method to return user object by user_id"""
        return User.query.filter_by(id=user_id).first()

    # def delete_user(self):
    #     """Delete a user from db and all list items created by them"""
    #     db.session.remove(self)
    #     db.session.commit()


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

    def delete(self):
        """function to remove an item from db"""
        db.session.delete(self)
        db.session.commit()


class BucketListItems(BucketlistBaseModel):
    """The bucketlist items table"""

    ___tablename__ = 'bucketlist_items'

    # Id the bucketlist belongs to
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlists.id', ondelete='CASCADE'))
    item_name = db.Column(db.String(255))  # Name of the bucket list item
    done = db.Column(db.Boolean, default=False)

    def __init__(self, item_name, bucketlist_id):
        self.item_name = item_name
        self.bucketlist_id = bucketlist_id

    @staticmethod
    def get_all(bucketlist_id):
        """Method to return a bucketlist items specified by bucketlist_id"""
        return BucketListItems.query.filter_by(bucketlist_id=bucketlist_id)


class Bucketlists(BucketlistBaseModel):
    """Class for Bucketlist data"""
    __tablename__ = 'bucketlists'

    name = db.Column(db.String(256))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))    # Owner
    bucketlist_items = db.relationship('BucketListItems')

    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id

    @staticmethod
    def get_all(owner_id):
        """Method to get list of all bucketlist items"""
        return Bucketlists.query.filter_by(owner_id=owner_id)


class MarshmallowSchemaBase(Schema):
    """Base class for the marshmallow classes"""
    __abstract__ = True  # Abstract class for use by inheriting classes.
    id = fields.Int()
    date_created = fields.Method('time_lapse_created', deserialize='created')
    date_modified = fields.Method('time_lapse_modified', deserialize='modified')

    def created(self, obj):
        """method for deserializing date_created field"""
        return obj.date_created

    def modified(self, obj):
        """method for deserializing date_modified field"""
        return obj.date_modified

    def time_lapse_created(self, obj):
        """method to return time since created, modified in human readable fomart"""
        return human(obj.date_created, 2)

    def time_lapse_modified(self, obj):
        """method to return time since created, modified in human readable fomart"""
        if obj.date_created == obj.date_modified:
            return '--'
        return human(obj.date_modified, 2)


class BucketlistItemsSchema(MarshmallowSchemaBase):
    """Class to map marshmallow fields and bucketlistitems class"""
    class Meta:
        ordered = True

    bucketlist_id = fields.Int()
    item_name = fields.Str(required=True, error_messages={'required':'Item name not provided'})
    done = fields.Boolean(required=True, error_messages={'required':'Item status not provided'})


class BucketlistsSchema(MarshmallowSchemaBase):
    """Class to map the bucketlists objects to marshmallow fields"""
    # Class meta ordered set to true so the serialized dictionary will always be ordered
    # in the order the fields are declared
    class Meta:
        ordered = True

    name = fields.Str(required=True, error_messages={'required':'Bucketlist name not provided'})
    owner_id = fields.Int(required=True, error_messages={'required':'Bucketlist Owner Id not '
                                                                    'provided'})
    # has_next = fields.Boolean(dump_only=True)
    # has_prev = fields.Boolean(dump_only=True)
    # next_num = fields.Int(dump_only=True)
    # prev_num = fields.Int(dump_only=True)

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
