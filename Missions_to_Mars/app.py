from flask import Flask, render_template, redirect
from jinja2 import ChainableUndefined
from flask_pymongo import PyMongo
import scrape_mars
import json

app = Flask(__name__)
app.jinja_env.undefined = ChainableUndefined

# Use flask_pymongo to set up mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mission_db")


@app.route("/")
def index():
    mars_col = mongo.db.mars_col.find_one()
    return render_template("index.html", mars_col=mars_col)


@app.route("/scrape")
def scraper():
    mars_col = mongo.db.mars_col
    mars_data = scrape_mars.scrape()
    mars_dict = json.loads(mars_data)
    mars_col.update({}, mars_dict, upsert=True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
