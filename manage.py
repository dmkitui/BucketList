import os
from app.bucketlist_app import db, create_app
# For handling a set of commands
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# Import the commands manager

app = create_app(config_name=os.getenv('APP_SETTINGS'))
migrate = Migrate(app, db)
manager = Manager(app)


# Define the migration command to always be preceded by the word 'db'
manager.add_command('db', MigrateCommand)

# Testing command
@manager.command
def test():
    """Runs the unittest"""
    os.environ['APP_SETTINGS'] = "testing"
    os.system('nosetests --with-coverage --cover-erase --cover-package=app')

if __name__ == '__main__':
    manager.run()
