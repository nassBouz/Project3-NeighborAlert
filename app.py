from flask import Flask, g
from flask import render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash

import models
import forms
import json


DEBUG = True
PORT = 8000

app = Flask(__name__)
app.secret_key= 'NeighborAlertsecretword'

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

# @login_required
# def handle_logout():
#     logout_user()
#     flash("You've been logged out", "success")
#     return redirect(url_for('index'))

@app.route('/', methods=('GET', 'POST'))
def index():
    neighborhoods = models.Neighbor.select()
    sign_up_form = forms.SignUpForm()
    sign_in_form = forms.SignInForm()
    logout_user()

    if sign_up_form.validate_on_submit():
        handle_signup(sign_up_form)

    elif sign_in_form.validate_on_submit():
        handle_signin(sign_in_form)

    return render_template('auth.html', neighborhoods=neighborhoods,sign_up_form=sign_up_form, sign_in_form=sign_in_form)


#  with open('neighborhoods.json') as json_data:
#         neighborhoods = json.load(json_data)
#         return render_template('neighborhoods.html',neighborhoods=neighborhoods)
@app.route('/post')
def post_page():
    return redirect('post.html')

# @app.route('/signup', methods=('GET', 'POST'))
# def signup():
#     form = forms.SignUpForm()
#     if form.validate_on_submit():
#         flash('Welcome new member!!!', 'success')
#         models.User.create_user(
#             username=form.username.data,
#             email=form.email.data,
#             password=form.password.data,
#             fullname=form.fullname.data
#             )

#         return redirect(url_for('index'))
#     return render_template('signup.html', form=form)

# @app.route('/signin', methods=('GET', 'POST'))
# def signin():
#     form = forms.SignInForm()
#     if form.validate_on_submit():
#         try:
#             user = models.User.get(models.User.email == form.email.data)
#         except models.DoesNotExist:
#             flash("your email or password doesn't match", "error")
#         else:
#             if check_password_hash(user.password, form.password.data):
#                 ## creates session
#                 login_user(user)
#                 flash("You've been logged in", "success")
#                 return redirect(url_for('index'))
#             else:
#                 flash("your email or password doesn't match", "error")
#     return render_template('signin.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out", "success")
    return redirect(url_for('index'))

@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(), neighbor=g.neighbor.__get_current_object(),
                           text=form.content.data.strip())
        flash("Message posted! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('posts.html', form=form)

@app.route('/stream')
@app.route('/stream/<username>')
@login_required
def stream(username=None):
    template = 'stream.html'
    if current_user:
        if username and username != current_user.username:
            user = models.User.select().where(models.User.username == username).get()
            stream = user.posts.limit(100)
        else:
            stream = current_user.get_stream().limit(100)
            user = current_user

        if username:
            template = 'user_profile.html'
        return render_template(template, stream=stream, user=user)


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
    except ValueError:
        pass

    app.run(debug=DEBUG, port=PORT)