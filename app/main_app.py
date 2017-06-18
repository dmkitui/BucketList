from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config
from flask import request, jsonify, abort
# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    from app.models import BucketList

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/bucketlists/', methods=['GET', 'POST'])
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

    @app.route('/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
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
