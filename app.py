from flask import Flask, g
from flask import render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
from werkzeug.utils import secure_filename
import os
import models 
import forms 
import json
from keyNeigh import keyNeigh

#///////////uncomment this for heroku///////////////
# from flask.ext.heroku import Heroku
# heroku = Heroku(app)

DEBUG = True
PORT = 8000

app = Flask(__name__)
app.secret_key= keyNeigh
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
# signup user
def handle_signup(form):
    flash('Welcome new member!!!', 'success')
    models.User.create_user(
        username=form.username.data,
        email=form.email.data,
        password=form.password.data,
        fullname=form.fullname.data,
        profileImgUrl=form.profileImgUrl.data
    )
    return redirect(url_for('index'))
# singin user
def handle_signin(form):
    try:
        user = models.User.get(models.User.email == form.email.data)
    except models.DoesNotExist:
        flash("your email or password doesn't match", "error")
    else:
        if check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Hi! You have successfully Signed In!!!', 'success signin')
            return redirect(url_for('index'))
        else:
            flash("your email or password doesn't match", "error")
# logout 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out", "success")
    return redirect(url_for('index'))

#landing page 
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

#Neighborhood page
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

# user profile page
@app.route('/profile/<username>', methods=['GET'])
def profilepage(username):
    user = models.User.get(models.User.username == username)
    posts = current_user.get_posts()

    return render_template('user.html', user=user,posts=posts) 

# delete a poste in user's profile page
@app.route('/profile/<postid>/delete')
@login_required 
def delete_post(postid):
    post = models.Post.get(models.Post.id == postid)
    post.delete_instance()

    return redirect(url_for('profilepage', username=g.user._get_current_object().username))

# edit post in the user's profile page
@app.route('/profile/<postid>/edit', methods=['GET','POST']) # when you submit to update it is always POST!!!, First you GET the form from 'neighborpage.html' each field now has value=post.title, and user edits that info and POST route will submit that form Finally, save()
@login_required 
def edit_post(postid):
    post_id = int(postid)
    post = models.Post.get(models.Post.id == post_id)
    neighbor_model = models.Neighbor.get_by_id(post.neighbor_id)
    # http://docs.peewee-orm.com/en/latest/peewee/querying.html
    form = forms.PostForm()
    if form.validate_on_submit():
        post.title = form.title.data 
        post.text = form.text.data
        post.address = form.address.data
        post.imgUrl = form.imgUrl.data
        post.category = form.category.data
        post.save()
        return redirect("/posts/{}".format(post_id))

    return render_template('neighborpage.html', neighbor=post.neighbor, post=post, form=form) 

# posts page
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

# route to add and display comments
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

# about us page
@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')

# like a post route
@app.route('/like/<int:post_id>')
@login_required
def upvote(post_id):
    userId = g.user._get_current_object()
    posts = models.Post.select().where(models.Post.id == post_id)
    if posts.count() == 0:
        abort(404)

    post = models.Post.select().where(models.Post.id == post_id).get()
    if models.UserUpVote.select().where(models.UserUpVote.user_id == userId,models.UserUpVote.post_id == post_id).exists():
        (models.UserUpVote.select().where(models.UserUpVote.user_id == userId,models.UserUpVote.post_id == post_id).get()).delete_instance()
        count = models.UserUpVote.select().where(models.UserUpVote.post_id == post_id).count()
        query = models.Post.update(priority = count).where(models.Post.id == post_id)
        query.execute()
        return redirect("/{}".format(post.neighbor_id))
    else:
        models.UserUpVote.create(user_id=userId, post_id = post_id)
        flash("Your vote has been registered.","success")
        count = models.UserUpVote.select().where(models.UserUpVote.post_id == post_id).count()
        query = models.Post.update(priority = count).where(models.Post.id == post_id)
        query.execute()
        return redirect("/{}".format(post.neighbor_id))

    return redirect("/{}".format(post.neighbor_id))

# This is checking to see if we are in the Heroku environment, if we are, build our tables. Note you can use this variable anywhere to check if you are on Heroku, you can figure out how to adapt your code to work locally and on heroku.
if 'ON_HEROKU' in os.environ:
    print('hitting ')
    models.initialize()

if __name__ == '__main__':
    models.initialize()
    try:
        models.Neighbor.create_neighborhood(
            neighbname = 'Financial District',
            city = 'San Francisco',
            state = 'California',
            country = 'USA',
            imageNeighb = 'https://images.unsplash.com/photo-1538445289442-ac987a2637e6?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1500&q=80'
            )
        models.Neighbor.create_neighborhood(
            neighbname = 'Chinatown',
            city = 'San Francisco',
            state = 'California',
            country = 'USA',
            imageNeighb ='https://media.timeout.com/images/102875459/630/472/image.jpg'
            )
        models.Neighbor.create_neighborhood(
            neighbname = 'North Beach',
            city = 'San Francisco',
            state = 'California',
            country = 'USA',
            imageNeighb = 'https://images.unsplash.com/photo-1506047610595-ab105976d1ef?ixlib=rb-1.2.1&auto=format&fit=crop&w=1500&q=80'
            )
        models.Neighbor.create_neighborhood(
            neighbname = 'SoMa',
            city = 'San Francisco',
            state = 'California',
            country = 'USA',
            imageNeighb = 'https://images.unsplash.com/photo-1506047526346-2bad9ca0cec4?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1500&q=80'
            )
        models.Neighbor.create_neighborhood(
            neighbname = 'Richmond District',
            city = 'San Francisco',
            state = 'California',
            country = 'USA',
            imageNeighb = 'https://gmcdn-sxcqif3sepi.netdna-ssl.com/city-guides/img/uploads/nhood/original/1492218427.86190.jpg'
            )
        models.Neighbor.create_neighborhood(
            neighbname = 'Russian Hill',
            city = 'San Francisco',
            state = 'California',
            country = 'USA',
            imageNeighb ='https://images.unsplash.com/photo-1526404423292-15db8c2334e5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80'
            )
        models.Neighbor.create_neighborhood(
            neighbname = 'Sunset',
            city = 'San Francisco',
            state = 'California',
            country = 'USA',
            imageNeighb = 'https://images.unsplash.com/photo-1506222444025-c2b1d9fb7691?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60'
            )
        models.Neighbor.create_neighborhood(
            neighbname = 'Alamo Square',
            city = 'San Francisco',
            state = 'California',
            country = 'USA',
            imageNeighb = 'https://images.unsplash.com/photo-1519227355453-8f982e425321?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1789&q=80'
            )
        models.User.create_user(
            username='nass',
            email="nass@ga.com",
            password='123',
            fullname= 'Nassima Bouz',
            profileImgUrl= "http://localhost:8000/static/NassimaB.jpeg"
            )
        models.User.create_user(
            username='alom',
            email="alom@ga.com",
            password='123',
            fullname= 'Alom Hossain',
            profileImgUrl= 'http://localhost:8000/static/alom.jpg'
            )
        models.User.create_user(
            username='Heggy',
            email="heggy@ga.com",
            password='123',
            fullname= 'Beautiful Heggy',
            profileImgUrl= "http://localhost:8000/static/heggyprofile.png"
            )
        models.User.create_user(
            username='Homer',
            email="homer@ga.com",
            password='123',
            fullname= 'Homer Simpson',
            profileImgUrl= 'http://interactive.nydailynews.com/2016/05/simpsons-quiz/img/simp1.jpg'
            )

        models.Post.create_post(
            user=1,
            neighbor=1,
            title='Downtown',
            text= 'Downtown has lots of traffic',
            address= 'downtown san francisco',
            imgUrl= 'https://s.hdnux.com/photos/36/13/34/7911185/13/920x920.jpg',
            category='downtown'
            )
        models.Post.create_post(
            user=1,
            neighbor=1,
            title='Coding School',
            text= 'General Assembly is a great coding school',
            address= '225 bush st san francisco',
            imgUrl= 'https://s3.amazonaws.com/bloc-global-assets/almanac-assets/bootcamps/logos/000/002/669/original/General-Assembly.png?1467187329',
            category='School'
            )
        models.Post.create_post(
            user=4,
            neighbor=3,
            title='Piiza Pizza',
            text= 'Golden Boy is a great pizza place!',
            address= 'Golden Boy san francisco',
            imgUrl= 'https://media.cntraveler.com/photos/5a9488dc0e2cf839e9dbfba4/4:5/w_767,c_limit/Golden-Boy-Pizza_SORAYA-MATOS_2018__MG_0514.jpg',
            category='Food'
            )
        models.Post.create_post(
            user=4,
            neighbor=6,
            title='Crooked Street',
            text= 'Why is lombard st so crooked? Driving down this street makes me naseous.',
            address= 'Lombard st san francisco',
            imgUrl= 'https://i.pinimg.com/originals/5a/8d/ff/5a8dff7a0c12e614da2f5d401fa47592.jpg',
            category='Complaints'
            )
        models.Post.create_post(
            user=4,
            neighbor=7,
            title='Nice Beach',
            text= 'This beach has too much sand! And is too windy!',
            address= 'Ocean beach st san francisco',
            imgUrl= 'https://www.tripsavvy.com/thmb/Kq9SBqeJ6RPQvkyo3WTBnMtMv3I=/960x0/filters:no_upscale():max_bytes(150000):strip_icc()/IMG_9157-1000x1500-56a387c93df78cf7727ddf1b.jpg',
            category='Complaints'
            )
        models.Post.create_post(
            user=2,
            neighbor=4,
            title='Craft beer!',
            text= 'Soma has a lot of breweries and beer bars for craft beers!',
            address= 'Cellar Maker st san francisco',
            imgUrl= 'https://fastly.4sqi.net/img/general/699x268/558158_cbJM1STlRy-sZCtkLFCryq2CaXpfwL_Wl9P-tq2e_d4.jpg',
            category='Food and Drink'
            )
        models.Post.create_post(
            user=3,
            neighbor=8,
            title='Painted Ladies',
            text= 'These are the houses where they filmed full house!',
            address= 'Painted Ladies st san francisco',
            imgUrl= 'https://de-web-media.s3.amazonaws.com/specs_images/the-painted-ladies-of-san-francisco/jondoeforty1.jpg',
            category='Tourist things'
            )

    except ValueError:
        pass

    app.run(debug=DEBUG, port=PORT)