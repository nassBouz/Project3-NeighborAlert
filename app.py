from flask import Flask, g
from flask import render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
from werkzeug.utils import secure_filename
import os
import models
import forms
import json
# to upload photo
from flask import send_from_directory
from flask.ext.heroku import Heroku

DEBUG = True
PORT = 8000

app = Flask(__name__)
app.secret_key= 'NeighborAlertsecretword'
heroku = Heroku(app)
login_manager = LoginManager()
##sets up our login for the app
login_manager.init_app(app)
login_manager.login_view = '/'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


def handle_signup(form):
    flash('Welcome new member!!!', 'success')
    models.User.create_user(
        username=form.username.data,
        email=form.email.data,
        password=form.password.data,
        fullname=form.fullname.data)
    return redirect(url_for('index'))

def handle_signin(form):
    try:
        user = models.User.get(models.User.email == form.email.data)
    except models.DoesNotExist:
        flash("your email or password doesn't match", "error")
    else:
        if check_password_hash(user.password, form.password.data):
            ## creates session
            login_user(user)
            flash('Hi! You have successfully Signed In!!!', 'success signin')
            return redirect(url_for('index'))
        else:
            flash("your email or password doesn't match", "error")


# ///////////////// this code is from https://flask-wtf.readthedocs.io/en/latest/form.html, http://www.patricksoftwareblog.com/tag/flask-uploads/


@app.route('/photo', methods=['GET', 'POST'])
def upload():
    form = forms.ImageUpload()
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename )
        f.save(os.path.join(
            app.instance_path, 'photos', filename
        ))
        return redirect(url_for('upload'))
    return render_template('downloadPicture.html', form=form)
# see the pictures in the browser
@app.route('/photo/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

# //////////////////

@app.route('/', methods=('GET', 'POST'))
def index():
    neighborhoods = models.Neighbor.select()
    sign_up_form = forms.SignUpForm()
    sign_in_form = forms.SignInForm()

    if sign_up_form.validate_on_submit():
        handle_signup(sign_up_form)

    elif sign_in_form.validate_on_submit():
        handle_signin(sign_in_form)

    return render_template('auth.html', neighborhoods=neighborhoods, sign_up_form=sign_up_form, sign_in_form=sign_in_form)


@app.route('/<neighborid>', methods=['GET','POST'])
def neighborpage(neighborid):
    sign_in_form = forms.SignInForm()
    sign_up_form = forms.SignUpForm()
    neighbor_model = models.Neighbor.get_by_id(int(neighborid))
    posts = models.Post.select().where(models.Post.neighbor_id==int(neighborid))

    if sign_up_form.validate_on_submit():
        handle_signup(sign_up_form)

    elif sign_in_form.validate_on_submit():
        handle_signin(sign_in_form)


    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(
            user=g.user._get_current_object(),
            title=form.title.data, 
            text=form.text.data,
            address=form.address.data,
            imgUrl=form.imgUrl.data,
            category=form.category.data,
            neighbor=neighbor_model)
        return redirect("/{}".format(neighborid))

    return render_template('posts.html', neighbor=neighbor_model, sign_in_form=sign_in_form, sign_up_form=sign_up_form, posts=posts, form=form, post={"title":"","text":"","address":"","imgUrl":"","category":""}) 

@app.route('/profile/<username>', methods=['GET'])
def profilepage(username):
    user = models.User.get(models.User.username == username)
    posts = current_user.get_posts()

    return render_template('user.html', user=user,posts=posts) 

# name of the post sf= 1 whicb here is postid
@app.route('/profile/<postid>/delete')
# @login_required # todo: before submitting activate this to prevent users to delete w/o login
def delete_post(postid):
    post = models.Post.get(models.Post.id == postid)
    post.delete_instance()

    return redirect(url_for('profilepage', username=g.user._get_current_object().username))


@app.route('/profile/<postid>/edit', methods=['GET','POST']) # when you submit to update it is always POST!!!, First you GET the form from 'neighborpage.html' each field now has value=post.title, and user edits that info and POST route will submit that form Finally, save()
# @login_required # todo: before submitting activate this to prevent users to delete w/o login
def edit_post(postid):
    # maybe we need to create form??
    # 1st Let's render template!
    post_id = int(postid) #convert id into integer 
    post = models.Post.get(models.Post.id == post_id)
    neighbor_model = models.Neighbor.get_by_id(post.neighbor_id)

    form = forms.PostForm()
    if form.validate_on_submit():
        post.title = form.title.data # form.title.data this is form data getting reassigned
        post.text = form.text.data
        post.address = form.address.data
        post.imgUrl = form.imgUrl.data
        post.category = form.category.data
        post.save() # http://docs.peewee-orm.com/en/latest/peewee/querying.html
        return redirect("/{}".format(post.neighbor_id))

    return render_template('neighborpage.html', neighbor=post.neighbor, post=post, form=form) 




@app.route('/posts')
@app.route('/posts/<id>', methods =['GET','POST'])
def posts(id=None):
    sign_up_form = forms.SignUpForm()
    sign_in_form = forms.SignInForm()

    if sign_up_form.validate_on_submit():
        handle_signup(sign_up_form)

    elif sign_in_form.validate_on_submit():
        handle_signin(sign_in_form)


    if id == None:
        posts = models.Post.select().limit(100)
        return render_template('posts.html', posts=posts)
    else:
        post_id = int(id)
        post = models.Post.get(models.Post.id == post_id)
        comments = post.comments

        form = forms.CommentForm()
        if form.validate_on_submit():
            models.Comment.create(
                user=g.user._get_current_object(),
                commentText= form.commentText.data,
                post=post
            )

            return redirect("/posts/{}".format(post_id))


        return render_template('post.html', post=post, form=form, comments=comments, sign_in_form=sign_in_form, sign_up_form=sign_up_form)

@app.route('/comment')
@app.route('/comment/<id>', methods=['GET','POST'])
def comments(id=None):
      if id == None:
        comments = models.Comment.select().limit(100)
        return render_template('comments.html', comments=comments)
      else:
        comment_id = int(id)
        comment = models.Comment.get(models.Comment.id == comment_id)

        return render_template('comment.html', comment=comment)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out", "success")
    return redirect(url_for('index'))

@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def new_post():
    form = forms.PostForm()
    
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(), neighbor=g.neighbor.__get_current_object(),
                           text=form.content.data.strip())
        flash("Message posted! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('posts.html', form=form)

# This is checking to see if we are in the Heroku environment, if we are, build our tables. Note you can use this variable anywhere to check if you are on Heroku, you can figure out how to adapt your code to work locally and on heroku.
if 'ON_HEROKU' in os.environ:
    print('hitting ')
    models.initialize()

if __name__ == '__main__':
    models.initialize()
    try:
        models.Neighbor.create_neighborhood(
            neighbname = 'FIDI',
            city = 'San Francisco',
            state = 'California',
            country = 'USA'
            )
        models.Neighbor.create_neighborhood(
            neighbname = 'China Town',
            city = 'San Francisco',
            state = 'California',
            country = 'USA'
            )
        models.Neighbor.create_neighborhood(
            neighbname = 'North Beach',
            city = 'San Francisco',
            state = 'California',
            country = 'USA'
            )
        models.Neighbor.create_neighborhood(
            neighbname = 'SoMa',
            city = 'San Francisco',
            state = 'California',
            country = 'USA'
            )
        models.User.create_user(
            username='nass',
            email="nasm@ga.com",
            password='123',
            fullname= 'Nass Bou'
            )
    except ValueError:
        pass

    app.run(debug=DEBUG, port=PORT)