import datetime
from peewee import *

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase('neighbors.db')

class Neighbor(Model):
    neighname = CharField(unique=True)
    city = CharField()
    state = CharField()
    coutry = CharField(default='USA')
    class Meta:
        database = DATABASE

    @classmethod
    def get_neighbor(self):
        return Neighbor.select().where(Neighbor.neighname == self)


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now())
    is_admin = BooleanField(default=False)
    fullname = CharField(max_length=120)
    
    class Meta:
        database = DATABASE
        
    @classmethod
    def create_user(cls, username, email,fullname, password, admin=False):
        try:
            cls.create(
                username=username,
                email=email,
                fullname =fullname,
                password=generate_password_hash(password),
                is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user == self)
        )


class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now())
    user = ForeignKeyField(
        model=User,
        backref='posts'
    )
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)
        
        
def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post], safe=True)
    DATABASE.close()       