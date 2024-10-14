#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

# api = Api(app)    ********REST


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants")
def get_retaurants():
    res = Restaurant.query.all()
    response_body = [r.to_dict(only=('address','id','name')) for r in res]
    return make_response(response_body,200)

@app.route("/restaurants/<int:id>")
def get_retautrant(id):
    rest = Restaurant.query.filter_by(id=id).first()
    if not rest:
        response_body = {"error": "Restaurant not found"}
        return make_response(response_body,404)
    response_body = rest.to_dict()
    return make_response(response_body,200)

@app.route("/restaurants/<int:id>", methods=['DELETE'])
def delete_retaurant(id):
    rest = Restaurant.query.get(id)
    if not rest:
        response_body = {"error": "Restaurant not found"}
        return make_response(response_body,404)
    
    db.session.delete(rest)
    db.session.commit()
    response_body = {}
    return make_response(response_body,204)

@app.route("/pizzas")
def get_pizzas():
    piz = Pizza.query.all()
    response_body = [p.to_dict(only=('id','ingredients','name')) for p in piz]
    return make_response(response_body,200)

@app.route("/restaurant_pizzas", methods=['POST'])
def add_restaurant_pizzas():
    try:
        data = request.get_json()

        #extract values from JSON data
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")
        
        new_rp = RestaurantPizza(price = price,
                                pizza_id = pizza_id,
                                restaurant_id = restaurant_id)
        
        db.session.add(new_rp)
        db.session.commit()

        response_body = new_rp.to_dict()
        return make_response(response_body,201)
    except ValueError as ve:
        db.session.rollback()
        response_body = {"errors": ["validation errors"]}
        return make_response(response_body, 400)
    
    except Exception as e:
        db.session.rollback()
        response_body = {"errors": e}
        return make_response(response_body,400)



if __name__ == "__main__":
    app.run(port=5555, debug=True)
