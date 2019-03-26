import datetime
import os

from peewee import *
# use the playhouse extension to connect to postgres on heroku
#  https://git.generalassemb.ly/sf-wdi-51/flask-deployment/blob/master/README.md
from playhouse.db_url import connect 

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase('neighbors.db')
#  this will no longer work on my local machine b/ we are connectin tto heroku
# DATABASE = connect(os.environ.get('DATABASE_URL'))

# ------------------- ----------------------------------- #
# -------------------Neighbor Model --------------------- #
# ------------------- ----------------------------------- #
class Neighbor(Model):
    neighbname = CharField(unique=True)
    city = CharField()
    state = CharField()
    country = CharField(default='USA')
    imageNeighb = CharField(default = 'https://baycityguide.com/media/00PU000000EkWTuMAN/Financial-District-from-Coit-Tower1500x872.jpg') 

    class Meta:
        database = DATABASE
        order_by = ('-neighbname',)

    @classmethod
    def get_neighbor(self):
        return Neighbor.select().where(Neighbor.neighname == self)

    @classmethod
    def create_neighborhood(cls, neighbname, city, state, country,imageNeighb):
        try:
            cls.create(
                neighbname = neighbname,
                city = city,
                state = state,
                country = country,
                imageNeighb = imageNeighb
            )
        except IntegrityError:
            raise ValueError("Neighborhood already exists")

# ------------------- ----------------------------------- #
# -------------------User Model ------------------------- #
# ------------------- ----------------------------------- #
class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now())
    is_admin = BooleanField(default=False)
    fullname = CharField(max_length=120)
    profileImgUrl = CharField(default='/static/userDefault.png')
    
    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)
        
    @classmethod
    def create_user(cls, username, email,fullname, password, profileImgUrl, admin=False):
        try:
            cls.create(
                username=username,
                email=email,
                fullname =fullname,
                password=generate_password_hash(password),
                is_admin=admin,
                profileImgUrl=profileImgUrl 
            )
        except IntegrityError:
            raise ValueError("User already exists")

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user == self)
        )

# ------------------- ----------------------------------- #
# ------------------- Post Model ------------------------ #
# ------------------- ----------------------------------- #
class Post(Model):
    datePostCreated = DateTimeField(default=datetime.datetime.now())
    user = ForeignKeyField(
        model=User,
        backref='posts'
    )
    neighbor = ForeignKeyField(
        model= Neighbor,
        backref='posts' 
    )

    title = TextField()
    address = TextField()
    imgUrl = CharField()
    text = TextField()
    category = CharField()
    priority = IntegerField(default=0)

    class Meta:
        database = DATABASE
        order_by = ('-priority',)
    
    @classmethod
    # create a method to get all the comments for a post
    def get_comments(self):
        return Comment.select().where(Comment.post == self)

    @classmethod
    def create_post(cls,user,neighbor, title, text, address, imgUrl,category):
        try:
            cls.create(
                user=user, 
                neighbor=neighbor,
                title = title,
                text= text,
                address = address,
                imgUrl = imgUrl,
                category = category
            )
        except IntegrityError:
            raise ValueError("Post error")


    @classmethod
    def delete_post(cls, post_id):
        post = Post.get(Post.id == post_id)
        try:
            post.delete()
        except IntegrityError:
            raise ValueError("No posts exist!!!")
        return 
# ------------------- ----------------------------------- #
# ------------------- Comment Model --------------------- #
# ------------------- ----------------------------------- #
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
    user_id= IntegerField()
    post_id= IntegerField()
    class Meta:
        database = DATABASE

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Neighbor,UserUpVote,Comment], safe=True)
    DATABASE.close()       