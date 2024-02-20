from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from wtforms import EmailField, StringField, SubmitField, URLField, BooleanField, IntegerField, SelectField, PasswordField, RadioField
from wtforms.validators import DataRequired, URL, Length
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Boolean, Integer, Nullable, String, Text, Float, select
from functools import wraps
import os

# ------------------------- FLASK SETUP ------------------------- #
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap5(app)
# ------------------------- LOGIN SETUP ------------------------- #

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function

# ------------------------- DB SETUP ------------------------- #
class Base(DeclarativeBase):
    pass

# MAIN BREWERY DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    account_type = db.Column(String(10))
    email = db.Column(String(30), unique=True)
    username = db.Column(String(20), unique=True)
    password = db.Column(String(20))


class Brewery(db.Model):
    __tablename__ = 'breweries'
    # required
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), unique=True, nullable=False)
    site_url = db.Column(String(250), unique=True, nullable=False)
    img_url = db.Column(String(250), unique=True, nullable=False)
    city = db.Column(String(25), unique=False, nullable=False)
    maps_url = db.Column(String(250), unique=True, nullable=False)
    latitude = db.Column(Float, unique=True, nullable=False)
    longitude = db.Column(Float, unique=True, nullable=False)
    # optional/add later
    dog_friendly = db.Column(Boolean, nullable=True)
    kid_friendly = db.Column(Boolean, nullable=True)
    group_capacity = db.Column(Integer, nullable=True)
    beer_to_go = db.Column(Boolean, nullable=True)
    avg_review = db.Column(Float, nullable=True)
    num_reviews = db.Column(Integer, nullable=True)
    todays_food = db.Column(String(100), nullable=True) # to be added via post request from scraper


class FoodTruck(db.Model):
    __tablename__ = 'trucks'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), unique=True, nullable=False)
    site_url = db.Column(String(250), unique=True, nullable=True)
    img_url = db.Column(String(250), unique=True, nullable=True)
    food_type = db.Column(String(25), unique=False, nullable=False)
    avg_review = db.Column(Float, nullable=True)
    num_reviews = db.Column(Integer, nullable=True)


with app.app_context():
    db.create_all()


# ------------------------- FORM SETUP ------------------------- #
    
class SignupForm(FlaskForm):
    email = EmailField(label="Email address", validators=[DataRequired()])
    username = StringField(label="Username", validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField(label="Password", validators=[DataRequired()])
    vendor_type = RadioField(label="I am a:", choices=["Admin", "Brewery", "Food Truck"])
    submit = SubmitField(label="Create Account")

class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Log In")

class BreweryForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    site_url = URLField(label="Food Schedule URL", validators=[DataRequired()])
    img_url = URLField(label="Brewery Preview Image URL", validators=[DataRequired()])
    city = StringField(label="City", validators=[DataRequired()])
    maps_url = URLField(label="Google Maps URL", validators=[DataRequired()])
    dog_friendly = BooleanField(label="Dog Friendly")
    kid_friendly = BooleanField(label="Kid Friendly")
    group_capactiy = IntegerField(label="Group Capacity")
    beer_to_go = BooleanField(label="Beer To Go")
    submit = SubmitField(label="Add Brewery")

class BreweryReviewForm(FlaskForm):
    beer_ratings = [('1', '🍺'), ('2', '🍺🍺'), ('3', '🍺🍺🍺'), ('4', '🍺🍺🍺🍺'), ('5', '🍺🍺🍺🍺🍺')]
    rating = SelectField(label="Rating", choices=beer_ratings)
    review = CKEditorField(label="Review")
    submit = SubmitField(label="Submit")


class TruckForm(FlaskForm):
    food_types = ['American', 'BBQ', 'Chicken', 'Mexican', 'MN Street Food', 'Other', 'Pizza', 'Taco', 'Tibetan']
    name = StringField(label="Name", validators=[DataRequired()])
    site_url = URLField(label="Website")
    img_url = URLField(label="Image URL")
    type = SelectField(label="Food Type", choices=food_types, validators=[DataRequired()])
    submit = SubmitField(label="Add Truck")

class TruckReviewForm(FlaskForm):
    truck_ratings = [('1', '🚚'), ('2', '🚚🚚'), ('3', '🚚🚚🚚'), ('4', '🚚🚚🚚🚚'), ('5', '🚚🚚🚚🚚🚚')]
    rating = SelectField(label="Rating", choices=truck_ratings)
    review = CKEditorField(label="Review")
    submit = SubmitField(label="Submit")


# ------------------------- ROUTES ------------------------- #
def is_admin():
    if current_user.is_authenticated:
        if current_user.account_type == "Admin":
            return True
        else:
            return False
    else:
        return False

@app.route("/")
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated, admin=is_admin())

@app.route("/breweries")
def breweries():
    breweries = db.session.execute(db.select(Brewery).order_by(Brewery.name)).scalars().all()
    return render_template("breweries.html", breweries=breweries, logged_in=current_user.is_authenticated, admin=is_admin())

@app.route("/trucks")
def trucks():
    trucks = db.session.execute(db.select(FoodTruck).order_by(FoodTruck.name)).scalars().all()
    return render_template("trucks.html", trucks=trucks, logged_in=current_user.is_authenticated, admin=is_admin())
    
@app.route("/about")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated, admin=is_admin())

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    form = SignupForm()

    if form.validate_on_submit():
        new_user = User(
            account_type = form.vendor_type.data,
            email = form.email.data,
            username = form.username.data,
            password = form.password.data
        )

        result_username = db.session.execute(db.select(User).where(User.username == new_user.username))
        user_username = result_username.scalar()

        result_email = db.session.execute(db.select(User).where(User.email == new_user.email))
        user_email = result_email.scalar()

        if user_username:
            flash("User already exists. Please try logging in.") # need to add mesage flash to page
            return redirect(url_for("login"))
        elif user_email:
            flash("Email address already in use. Please try logging in.")
            return redirect(url_for("login"))
        else:
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully. Please log in.")
            return redirect(url_for("login"))

    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        result = db.session.execute(db.select(User).where(User.username == username))
        user = result.scalar()

        if user:
            if user.password == password:
                login_user(user)
                return redirect(url_for("home"))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/add/<string:type>", methods=["GET", "POST"])
@login_required
@admin_only
def add(type):

    if type == "brewery":
        form = BreweryForm()
        if form.validate_on_submit():
            url = form.maps_url.data
            
            lat_lon_str = url.split('@')[1].split(',')[0:2]

            lat = float(lat_lon_str[0])
            lon = float(lat_lon_str[1])

            new_brewery = Brewery(
                name=form.name.data,
                site_url=form.site_url.data,
                img_url=form.img_url.data, 
                city=form.city.data,
                maps_url=form.maps_url.data,
                latitude=lat,
                longitude=lon,
                dog_friendly=form.dog_friendly.data, 
                kid_friendly=form.kid_friendly.data,
                group_capacity=form.group_capactiy.data, 
                beer_to_go=form.beer_to_go.data
            )

            db.session.add(new_brewery)
            db.session.commit()

            return redirect(url_for("breweries"))
        else:
            return render_template("add.html", form=form, type=type.title(), logged_in=current_user.is_authenticated, admin=is_admin())

    elif type == "truck":
        form = TruckForm()
        if form.validate_on_submit():

            new_truck = FoodTruck(
                name = form.name.data,
                site_url = form.site_url.data,
                img_url = form.img_url.data,
                food_type = form.type.data
            )

            db.session.add(new_truck)
            db.session.commit()

            return redirect(url_for("trucks"))
        else:
            return render_template("add.html", form=form, type=type.title(), logged_in=current_user.is_authenticated, admin=is_admin())
    
    else:
        return redirect(url_for("home"))
    
@app.route("/edit/<string:type>/<int:id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit(type, id):
    if type == "brewery":
        brewery = db.get_or_404(Brewery, id)
        edit_form = BreweryForm(
            name = brewery.name,
            site_url = brewery.site_url,
            img_url = brewery.img_url,
            city = brewery.city,
            maps_url = brewery.maps_url,
            dog_friendly = brewery.dog_friendly,
            kid_friendly = brewery.kid_friendly,
            group_capactiy = brewery.group_capacity,
            beer_to_go = brewery.beer_to_go
        )

        edit_form.submit.label.text = "Edit Brewery"

        if edit_form.validate_on_submit():
            brewery.name = edit_form.name.data
            brewery.site_url = edit_form.site_url.data
            brewery.img_url = edit_form.img_url.data
            brewery.city = edit_form.city.data
            brewery.maps_url = edit_form.maps_url.data
            brewery.dog_friendly = edit_form.dog_friendly.data
            brewery.kid_friendly = edit_form.kid_friendly.data
            brewery.group_capacity = edit_form.group_capactiy.data
            brewery.beer_to_go = edit_form.beer_to_go.data
            
            db.session.commit()

            return redirect(url_for('breweries'))


    elif type == "truck":
        truck = db.get_or_404(FoodTruck, id)
        edit_form = TruckForm(
            name = truck.name,
            site_url = truck.site_url,
            img_url = truck.img_url,
            type = truck.food_type
        )

        edit_form.submit.label.text = "Edit Truck"

        if edit_form.validate_on_submit():
            truck.name = edit_form.name.data
            truck.site_url = edit_form.site_url.data
            truck.img_url = edit_form.img_url.data
            truck.food_type = edit_form.type.data

            db.session.commit()

            return redirect(url_for("trucks"))

    return render_template("edit.html", form=edit_form, type=type.title())

@app.route("/map")
def map():
    return render_template("map.html", logged_in=current_user.is_authenticated, admin=is_admin())

if __name__ == "__main__":
    app.run(debug=True)