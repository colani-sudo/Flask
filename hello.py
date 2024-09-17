from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


# Create a Flask Instance
app = Flask(__name__)       # allows Flask to know where to look for templates and static files

# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Create a CSRF key to protect the form when submitting
app.config['SECRET_KEY'] = "my super secret key for form submition"

# Initialize the database
db = SQLAlchemy(app)

# Create a model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name

# Create a form class for the Users Model
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")    

# Create a form class
class NameForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

#-FILTERS---------
# safe
# capitalize
# lower
# upper
# title
# trim
# striptags

# def index():
#     return "<h1>Hello, World!</h1>"

# Create a route decorator for index page
@app.route('/')
def index():
    first_name = "John"
    stuff = "This is <strong>Bold</strong> Text"
    favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]
    return render_template("index.html",first_name=first_name,
                           stuff=stuff,favorite_pizza=favorite_pizza)

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
        if user is None:
            # Add the user to the database
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data      # if form has data, assign it to name
        form.name.data = ''
        form.email.data = ''
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", 
                           form=form, name=name, 
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

