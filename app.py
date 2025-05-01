from flask import Flask
from routes import map_bp, algo_bp, condition_bp
from utils.sync_geojson import sync_geojson

def create_app():
    app = Flask(__name__)

    sync_geojson()
    
    app.register_blueprint(map_bp)
    app.register_blueprint(algo_bp)
    app.register_blueprint(condition_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)