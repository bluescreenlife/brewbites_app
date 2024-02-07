from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Boolean, Integer, Nullable, String, Text, Float
import requests


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
    allows_dogs = brewery_db.Column(Boolean, nullable=True)
    child_friendly = brewery_db.Column(Boolean, nullable=True)
    group_capactiy = brewery_db.Column(Integer, nullable=True)
    todays_food = brewery_db.Column(String(100), nullable=True)

# FOOD TRUCK DB
app.config['SQLALCHEMY_BINDS'] = {
    'food_truck_db': 'sqlite:///foodtrucks.db'
}
food_truck_db = SQLAlchemy(model_class=Base)
food_truck_db.init_app(app)

class FoodTruck(food_truck_db.Model):
    id = food_truck_db.Column(Integer, primary_key=True)
    name = food_truck_db.Column(String(100), unique=True, nullable=False)
    site_url = food_truck_db.Column(String(250), unique=True, nullable=True)
    img_url = food_truck_db.Column(String(250), unique=True, nullable=True)
    food_type = food_truck_db.Column(String(25), unique=False, nullable=False)

with app.app_context():
    brewery_db.create_all()
    food_truck_db.create_all()

# ------------------------- ROUTES ------------------------- #

@app.route("/")
def home():
    return render_template("index.html")
    
@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)