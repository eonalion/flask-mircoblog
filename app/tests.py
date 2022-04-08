from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_follow(self):
        u1 = User(username='anna')
        u2 = User(username='alex')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertEqual(u1.subscriptions.all(), [])
        self.assertEqual(u2.subscriptions.all(), [])

        u1.follow(u2)
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.subscriptions.count(), 1)
        self.assertEqual(u1.subscriptions.all(), [u2])
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.all(), [u1])

        # Subscriptions are not duplicated
        u1.follow(u2)
        self.assertEqual(u1.subscriptions.count(), 1)

        u1.unfollow(u2)
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.subscriptions.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_subscription_posts(self):
        u1 = User(username='susan', email='susan@email.com')
        u2 = User(username='alan', email='alan@email.com')
        u3 = User(username='pavel', email='pavel@email.com')
        u4 = User(username='inna', email='inna@email.com')
        db.session.add_all([u1, u2, u3, u4])

        now = datetime.utcnow()
        p1 = Post(author=u1, body='Post from susan', timestamp=now + timedelta(seconds=1))
        p2 = Post(author=u2, body='Post from alan', timestamp=now + timedelta(seconds=1))
        p3 = Post(author=u3, body='Post from pavel', timestamp=now + timedelta(seconds=1))
        p4 = Post(author=u4, body='Post from inna', timestamp=now + timedelta(seconds=1))

        u1.follow(u2)  # susan follows alan
        u1.follow(u3)  # susan follows pavel
        u2.follow(u1)  # alan follows susan
        u3.follow(u4)  # pavel follows inna
        db.session.commit()

        self.assertEqual(u1.subscription_posts().all(), [p1, p2, p3])
        self.assertEqual(u2.subscription_posts().all(), [p1, p2])
        self.assertEqual(u3.subscription_posts().all(), [p3, p4])
        self.assertEqual(u4.subscription_posts().all(), [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)