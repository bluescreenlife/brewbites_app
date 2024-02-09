from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from wtforms import StringField, SubmitField, URLField, BooleanField, IntegerField, SelectField, PasswordField
from wtforms.validators import DataRequired, URL, Length
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Boolean, Integer, Nullable, String, Text, Float, select

# brewery_list = ["56 Brewing", "Alloy Brewing", "Bad Weather Brewing", "Bauhaus Brew Labs", ]

# ------------------------- FLASK SETUP ------------------------- #
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPERSECRETKEY'
Bootstrap5(app)
# ------------------------- LOGIN SETUP ------------------------- #

login_manager = LoginManager()
login_manager.init_app(app)

# ------------------------- DB SETUP ------------------------- #
class Base(DeclarativeBase):
    pass

# MAIN BREWERY DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brewbites.db'

# Bind keys for additional databases
app.config['SQLALCHEMY_BINDS'] = {
    'truck_db': 'sqlite:///trucks.db',
    'admin_db': 'sqlite:///admin.db'
}

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Brewery(db.Model):
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
    __bind_key__ = 'truck_db'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), unique=True, nullable=False)
    site_url = db.Column(String(250), unique=True, nullable=True)
    img_url = db.Column(String(250), unique=True, nullable=True)
    food_type = db.Column(String(25), unique=False, nullable=False)
    avg_review = db.Column(Float, nullable=True)
    num_reviews = db.Column(Integer, nullable=True)

class Admin(UserMixin, db.Model):
    __bind_key__ = 'admin_db'
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(20), unique=True)
    password = db.Column(String(20))

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Admin, user_id)

with app.app_context():
    db.create_all()


# ------------------------- FORM SETUP ------------------------- #
class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired(), Length(min=6, max=20)])
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

@app.route("/")
def home():
    breweries = db.session.execute(db.select(Brewery).order_by(Brewery.name)).scalars().all()
    return render_template("index.html", breweries=breweries, logged_in=current_user.is_authenticated)
    
@app.route("/about")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        result = db.session.execute(db.select(Admin).where(Admin.username == username))
        admin = result.scalar()

        if admin:
            if admin.password == password:
                login_user(admin)
                return redirect(url_for("add", type="select"))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/add/<string:type>", methods=["GET", "POST"])
@login_required
def add(type):
    
    if type == "select":
        return render_template("select.html", logged_in=current_user.is_authenticated)


    elif type == "brewery":
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

            return redirect(url_for("home"))
        else:
            return render_template("add.html", form=form, type=type.title(), logged_in=current_user.is_authenticated)

    elif type == "truck":
        form = TruckForm()
        if form.validate_on_submit():

            new_truck = FoodTruck(
                name = form.name.data,
                site_url = form.site_url.data,
                img_url = form.img_url.data,
                type = form.type.data
            )

            db.session.add(new_truck)
            db.session.commit()

            return redirect(url_for("home"))
        else:
            return render_template("add.html", form=form, type=type.title(), logged_in=current_user.is_authenticated)
    
    else:
        return redirect(url_for("home"))

@app.route("/map")
def map():
    # parse lat and lon from maps url if necessary
    return render_template("map.html")

if __name__ == "__main__":
    app.run(debug=True)