from .main_app import db

class BucketList(db.Model):
    '''The bucketlist table'''

    ___tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    list_item_name = db.Column(db.String(255))  # Name of the bucket list item
    date_posted = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, list_item_name):
        '''method to initialize the list item with list_item_name'''
        self.list_item_name = list_item_name

    def save(self):
        '''Method to add a bucketlist item'''
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        '''Returns all bucketlist objects'''
        return BucketList.query.all()

    def delete(self):
        '''Deletes the current bucket list item from database'''
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        '''Returns the list item representation'''
        return '<Bucketlist: {}>'.format(self.list_item_name)
