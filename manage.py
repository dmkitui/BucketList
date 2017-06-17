import os
import unittest

from app.main_app import db, create_app
# For handling a set of commands
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# Import the commands manager

app = create_app(config_name=os.getenv('APP_SETTINGS'))
migrate = Migrate(app, db)
manager = Manager(app)


# Define the migration command to always be preceded bt the word 'db'
manager.add_command('db', MigrateCommand)

# Testing command
@manager.command
def test():
    '''Runs the unittest'''
    tests = unittest.TestLoader().discover('./tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)

    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    manager.run()
