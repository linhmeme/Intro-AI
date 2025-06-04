from flask import Blueprint, render_template
from utils.reset_weights import reset_weights
from config import WEIGHTS_FILE

map_bp = Blueprint("map", __name__)

@map_bp.route("/")
def index():
    reset_weights(WEIGHTS_FILE)
    return render_template("index.html")
