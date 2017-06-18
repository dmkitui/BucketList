from .main_app import db
from flask_bcrypt import Bcrypt


class User(db.Model):
    '''The users table'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(256), nullable=False, unique=True)
    user_password = db.Column(db.String(256), nullable=False)
    bucketlists = db.relationship('BucketList', order_by='BucketList.id', cascade='all, delete-orphan')

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

    def delete_user(self):
        '''Delete a user from db and all list items created by them'''
        db.session.remove(self)
        db.session.commit()

class BucketList(db.Model):
    '''The bucketlist table'''

    ___tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    list_item_name = db.Column(db.String(255))  # Name of the bucket list item
    date_posted = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, list_item_name, created_by):
        '''method to initialize the list item with list_item_name and creator'''
        self.list_item_name = list_item_name
        self.created_by = created_by

    def save(self):
        '''Method to add a bucketlist item or save changes to an existing one'''
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(user_id):
        '''Returns all bucketlist objects created by the supplied user.id'''
        return BucketList.query.filter_by(created_by=user_id)

    def delete(self):
        '''Deletes the current bucket list item from database'''
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        '''Returns the list item representation'''
        return '<Bucketlist: {}>'.format(self.list_item_name)
