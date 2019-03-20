import datetime
from peewee import *

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase('neighbors.db')

class Neighbor(Model):
    neighbname = CharField(unique=True)
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
        order_by = ('-joined_at',)
        
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
    datePostCreated = DateTimeField(default=datetime.datetime.now())
    user = ForeignKeyField(
        model=User,
        backref='posts'
    )
    neighbor = ForeignKeyField(
        model= Neighbor,
        # not sure backref to posts ?
        backref='posts' 
    )
    # CATEGORY_CHOICES = (
    #     (0, 'Event'),
    #     (1, 'Garage Sale'),
    #     (2, 'Play Dates'),
    #     (3, 'Burglary/theft'),
    #     (4, 'Lost and Found'),
    #     (5, 'Play Date'),
    #     (6, 'Other'))
    # category = IntegerField(choices=CATEGORY_CHOICES)
    # def get_category_label(self):
    #     return dict(self.CATEGORY_CHOICES)[self.category]

    address = TextField()
    imgUrl = CharField()
    text = TextField()
    category = CharField()
    priority = IntegerField()

    class Meta:
        database = DATABASE
        order_by = ('-datePostCreated',)
    
    @classmethod
    # create a method to get all the comments for a post
    def get_comments(self):
        return Comment.select().where(Comment.post == self)

    # def get_stream(self):
    #     return Comment.select().where(
    #         (Comment.post == self)
    #     )
class Comment(Model):
    dateCommentCreated= DateTimeField(default=datetime.datetime.now())
    user = ForeignKeyField(
        model=User,
        backref='comments'
    )
    post= ForeignKeyField(
        model=Post,
        backref='comments'
    )
    commentText = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-dateCommentCreated',)

class UserUpVote(Model):
    userId = IntegerField()
    postId = IntegerField()
    class Meta:
        database = DATABASE

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Neighbor,UserUpVote], safe=True)
    DATABASE.close()       