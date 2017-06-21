from app.models import User, BucketListItems, Bucketlists
from base import BaseTestCase
import base


class ModelsTests(BaseTestCase):

    def test_query_user_by_email(self):
        # import pdb; pdb.set_trace()

        person = User('dan@example.org', 'password0122')
        person.save()

        query = User.query.filter_by(user_email='dan@example.org').first()

        self.assertTrue(query.user_email == 'dan@example.org')


