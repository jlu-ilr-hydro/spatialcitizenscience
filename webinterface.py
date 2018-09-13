from flask import Flask, render_template,  request

from .configuration import get_config

config = get_config()
posts = [
    {"author": "Max",
     "maintitle": config.name,
     "date_posted": "April 20, 2018",
     "comment": "Das sind allgemeine Informatinen ueber die Seite."
     },
    {"author": "Bob",
     "maintitle": "Titel",
     "date_posted": "April 22, 2018",
     "comment": " Nochmal, das sind allgemeine Informatinen ueber die Seite."
     }
]

app = Flask(__name__)


@app.route('/')  # mehere Namen sind gleichzietig moeglich
def mainpage():
    return render_template("main.html", posts=posts)


@app.route('/blog')
def blog():
    return render_template("blog.html", posts=posts, title="blog")


@app.route('/map')
def map():
    return render_template("map.html", posts=posts, title="map")


@app.route('/form')
def form():
    longitude = float(request.args.get('longitude'))
    latitude = float(request.args.get('latitude'))
    ##    longitude = request.args.get('longitude', type=float)
    ##    latitude = request.args.get('latitude', type=float)

    return render_template("form.html", longitude=longitude, latitude=latitude, title="form")


@app.route('/about')
def about():
    return render_template("about.html", posts=posts, title="About")


# routs können dann raus
@app.route('/login')
def login():
    return render_template("about.html", posts=posts, title="About")


@app.route('/register')
def register():
    return render_template("about.html", posts=posts, title="About")
