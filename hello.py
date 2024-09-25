from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


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

# Create a model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name

# Create a form class for the Users Model
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("Submit")    

# Create a form class
class NameForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

    # BooleanField
    # DateField
    # DateTimeField
    # DecimalField
    # FileField
    # HiddenField
    # MultipleField
    # FieldList
    # FloatField
    # FormField
    # IntegerField
    # PasswordField
    # RadioField
    # SelectField
    # SelectMultipleField
    # SubmitField
    # StringField
    # TextAreaField

    # Validators
    # DataRequired
    # Email
    # EqualTo
    # InputRequired
    # IPAddress
    # Length
    # MacAddress
    # NumberRange
    # Optional
    # Regexp
    # URL
    # UUID
    # AnyOf
    # NoneOf

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
def update(id):
    form = UserForm()           # We can used the same user form we already have
    name_to_update = Users.query.get_or_404(id) # get this id or show 404 error if it does not exist
    if request.method == 'POST':        # remember to import request
              
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
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
        if user is None:
            # Add the user to the database
            user = Users(name=form.name.data, email=form.email.data,
                         favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data      # if form has data, assign it to name
        form.name.data = ''
        form.email.data = ''
        form.favorite_color = ''
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

