from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, UserForm, NameForm, PasswordForm, PostForm

# Create a Flask Instance
app = Flask(__name__)       # allows Flask to know where to look for templates and static files

# Old SQLite Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# New MySQL Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/users'

# Create a CSRF key to protect the form when submitting
app.config['SECRET_KEY'] = "my super secret key for form submition"

# Initialize the database / database instance 
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader      # this loads the user when we log in
def load_user(user_id):
    return Users.query.get(int(user_id))

# Create a route decorator for index page
@app.route('/')
def index():
    first_name = "John"
    stuff = "This is <strong>Bold</strong> Text"
    favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]
    return render_template("index.html",first_name=first_name,
                           stuff=stuff,favorite_pizza=favorite_pizza)

# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)    # this is part of flask_login, will login user and create sessions
                flash("You're logged in!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That user doesn't exist!ds")
    return render_template('login.html', form=form)

# Create logout function
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out! Thanks for surfing.")
    return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required             # checks if user is logged in
def dashboard():
    form = UserForm()           # We can used the same user form we already have
    id = current_user.id
    name_to_update = Users.query.get_or_404(id) # get this id or show 404 error if it does not exist
    if request.method == 'POST':        # remember to import request  
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("dashboard.html",
                                   form=form,name_to_update=name_to_update,id=id)
        except Exception as e:
            flash(f"Error! Looks like there was a problem: {e}")
            return render_template("dashboard.html",
                                   form=form,name_to_update=name_to_update,id=id)
    else:
        return render_template("dashboard.html",form=form,
                               name_to_update=name_to_update,
                               id=id)


@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)

    # Delete Post
    try:
        db.session.delete(post_to_delete)
        db.session.commit()

        # Return a message
        flash('Blog Post was deleted!')

        # Grab all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)
    
    except:
        # Return an error message
        flash("Ooops! Post not deleted! Try Again...")

        # Grab all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)

@app.route('/posts')
def posts():
    # Grab all posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

# Open a single post
@app.route('/post/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, 
                     author=form.author.data, slug=form.slug.data)
        # Clear the form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        flash("Blog Post Submitted Successfully")
    # Redirect to the webpage
    return render_template("add_post.html", form=form)

# Edit a Blog
@app.route('/posts/edit/<int:id>', methods=['GET','POST'])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for('post', id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html',form=form)

# Return JSON API
@app.route('/date')
def get_current_date():
    return {"Date": date.today()}


@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete =  Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully.")

        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", 
                           form=form,name=name, 
                           our_users=our_users)
    except:
        flash("Whoops! There was a problem deleting user. Try again!!!")
        return render_template("add_user.html", 
                           form=form,name=name, 
                           our_users=our_users)
# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()           # We can used the same user form we already have
    name_to_update = Users.query.get_or_404(id) # get this id or show 404 error if it does not exist
    if request.method == 'POST':        # remember to import request  
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("update.html",
                                   form=form,name_to_update=name_to_update,id=id)
        except Exception as e:
            flash(f"Error! Looks like there was a problem: {e}")
            return render_template("update.html",
                                   form=form,name_to_update=name_to_update,id=id)
    else:
        return render_template("update.html",form=form,
                               name_to_update=name_to_update,
                               id=id)

# localhost:5000/user/Colani
@app.route('/user/<name>')
def user(name):
    return render_template("user.html",user_name=name)

# Create a route decorator for UserForm
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    # Validate Form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:        # Add the user to the database
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data)
            user = Users(name=form.name.data, 
                        username=form.username.data, 
                        email=form.email.data,
                         favorite_color=form.favorite_color.data, 
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data      # if form has data, assign it to name
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color = ''
        form.password_hash = ''
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", 
                           form=form,name=name, 
                           our_users=our_users)

# Create Custom Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    # Validate Form
    if form.validate_on_submit():
        name =  form.name.data      # if form has data, assign it to name
        form.name.data = ''         # clear the form once data is captured
        flash("Form Submitted Successfully")
        
    return render_template("name.html",name = name, form = form)

# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # Validate Form
    if form.validate_on_submit():
        email =  form.email.data      # if form has data, assign it to name
        password = form.password_hash.data

        form.email.data = ''         # clear the form once data is captured
        form.password_hash.data = ''

        # Lookup user by email address
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check hashed password
        passed = check_password_hash(pw_to_check.password_hash,password)
        # flash("Submitted Successfully")
        
    return render_template("test_pw.html",
                           email = email, 
                           password = password,
                           pw_to_check = pw_to_check, passed = passed,
                           form = form)


# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer,primary_key=True) 
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    slug = db.Column(db.String(255))


# Create a Users model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # Perform some password hashing
    password_hash = db.Column(db.String(300))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name
    
