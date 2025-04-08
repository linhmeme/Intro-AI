from flask import Blueprint, render_template

map_bp = Blueprint("map", __name__)

@map_bp.route("/")
def index():
    return render_template("index.html")
