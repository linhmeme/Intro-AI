from flask import Blueprint, jsonify, render_template
from utils.graph import get_boundary

map_bp = Blueprint("map", __name__)

@map_bp.route("/")
def index():
    return render_template("index.html")


@map_bp.route("/get_boundary")
def boundary():
    return jsonify({"boundary": get_boundary()})