from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_mission_db")


@app.route("/")
def index():
    mars_collections = mongo.db.mars_collections.find_one()
    return render_template("index.html", mars_collections=mars_collections)


@app.route("/scrape")
def scraper():
    mars_collections = mongo.db.mars_collections
    mars_data = scrape_mars.scrape()
    mars_data.update({}, mars_data, upsert=True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
