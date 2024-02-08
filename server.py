from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, URLField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, URL
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Boolean, Integer, Nullable, String, Text, Float
import requests

# brewery_list = ["56 Brewing", "Alloy Brewing", "Bad Weather Brewing", "Bauhaus Brew Labs", ]

# ------------------------- FLASK SETUP ------------------------- #
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPERSECRETKEY'

# ------------------------- DB SETUP ------------------------- #
class Base(DeclarativeBase):
    pass

# BREWERY DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///breweries.db'
brewery_db = SQLAlchemy(model_class=Base)
brewery_db.init_app(app)

class Brewery(brewery_db.Model):
    id = brewery_db.Column(Integer, primary_key=True)
    name = brewery_db.Column(String(100), unique=True, nullable=False)
    site_url = brewery_db.Column(String(250), unique=True, nullable=False)
    img_url = brewery_db.Column(String(250), unique=True, nullable=False)
    maps_url = brewery_db.Column(String(250), unique=True, nullable=False)
    latitude = brewery_db.Column(Float, unique=True, nullable=False)
    longitude = brewery_db.Column(Float, unique=True, nullable=False)
    dog_friendly = brewery_db.Column(Boolean, nullable=True)
    kid_friendly = brewery_db.Column(Boolean, nullable=True)
    group_capactiy = brewery_db.Column(Integer, nullable=True)
    beer_to_go = brewery_db.Column(Boolean, nullable=True)
    avg_review = brewery_db.Column(Float, nullable=True)
    num_reviews = brewery_db.Column(Integer, nullable=True)
    todays_food = brewery_db.Column(String(100), nullable=True) # to be added via post request from scraper

# FOOD TRUCK DB
app.config['SQLALCHEMY_BINDS'] = {
    'food_truck_db': 'sqlite:///foodtrucks.db'
}
food_truck_db = SQLAlchemy(model_class=Base)
food_truck_db.init_app(app)

class FoodTruck(food_truck_db.Model):
    id = food_truck_db.Column(Integer, primary_key=True)
    name = food_truck_db.Column(String(100), unique=True, nullable=False)
    url = food_truck_db.Column(String(250), unique=True, nullable=True)
    img_url = food_truck_db.Column(String(250), unique=True, nullable=True)
    type = food_truck_db.Column(String(25), unique=False, nullable=False)
    avg_review = brewery_db.Column(Float, nullable=True)
    num_reviews = brewery_db.Column(Integer, nullable=True)

with app.app_context():
    brewery_db.create_all()
    food_truck_db.create_all()

# ------------------------- FORM SETUP ------------------------- #
class BreweryForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    url = URLField(label="Food Schedule URL", validators=[DataRequired()])
    img_url = URLField(label="Brewery Preview Image URL", validators=[DataRequired()])
    maps_url = URLField(label="Google Maps URL", validators=[DataRequired()])
    dog_friendly = BooleanField(label="Dog Friendly")
    kid_friendly = BooleanField(label="Kid Friendly")
    group_capactiy = IntegerField(label="Group Capacity")
    beer_to_go = BooleanField(label="Beer To Go")
    submit = SubmitField(label="Add Brewery")

class BreweryReviewForm(FlaskForm):
    # breweries = brewery_db.session.execute(brewery_db.select(Brewery).order_by(Brewery.name)).scalars().all()
    # brewery_names = [brewery.name for brewery in breweries]
    # select_brewery = SelectField(label="Brewery", choices=brewery_names, validators=[DataRequired()])
    # brewery can be selected by id when called from review get route

    beer_ratings = [('1', '🍺'), ('2', '🍺🍺'), ('3', '🍺🍺🍺'), ('4', '🍺🍺🍺🍺'), ('5', '🍺🍺🍺🍺🍺')]
    rating = SelectField(label="Rating", choices=beer_ratings)
    comment = CKEditorField(label="Review")
    submit = SubmitField(label="Submit")


class TruckForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    url = URLField(label="Website")
    img_url = URLField(label="Image URL")
    type = StringField(label="Food Type", validators=[DataRequired()])
    submit = SubmitField(label="Add Truck")

class TruckReviewForm(FlaskForm):
    truck_ratings = [('1', '🚚'), ('2', '🚚🚚'), ('3', '🚚🚚🚚'), ('4', '🚚🚚🚚🚚'), ('5', '🚚🚚🚚🚚🚚')]
    rating = SelectField(label="Rating", choices=truck_ratings)
    comment = CKEditorField(label="Review")
    submit = SubmitField(label="Submit")


# ------------------------- ROUTES ------------------------- #

@app.route("/")
def home():
    return render_template("index.html")
    
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/add/<str:type>") # admin only
def add(type):
    if type == "brewery":
        form = BreweryForm()
        if form.validate_on_submit():
            lat_lon_segment = form.maps_url.data.strip("@")[1].strip(",")
            lat = lat_lon_segment[0]
            lon = lat_lon_segment[1]
            print(f"Retrieved coordinates: {latitude},{longitude}")

            new_brewery = Brewery(
                name=form.name.data, site_url=form.site_url.data, img_url=form.site_url.data, 
                maps_url=form.maps_url.data, latitude=lat, longitude=lon, dog_friendly=form.dog_friendly.data, 
                kid_friendly=form.kid_friendly.data, group_capacity=form.group_capactiy.data, 
                beer_to_go=form.beer_to_go.data
            )

            brewery_db.session.add(new_brewery)
            brewery_db.session.commit()

            return redirect(url_for("add"))

    elif type == "truck":
        pass

    return render_template(url_for("add.html"), type=type)

@app.route("/map")
def map():
    # parse lat and lon from maps url if necessary
    return render_template("map.html")

if __name__ == "__main__":
    app.run(debug=True)