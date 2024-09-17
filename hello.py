from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# Create a Flask Instance
app = Flask(__name__)       # allows Flask to know where to look for templates and static files

# Create a CSRS key to protect the form when submitting
app.config['SECRET_KEY'] = "my super secret key for form submition"

# Create a form class
class NameForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a route decorator
@app.route('/')


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
        
    return render_template("name.html",name = name, form = form)

