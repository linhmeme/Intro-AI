from flask import Flask
from routes import map_bp, algo_bp
from condition import filter_bp, update_bp, final_bp
from config import WEIGHTS_FILE
from utils.sync_geojson import sync_geojson_selected
from utils.reset_weights import reset_weights

def create_app():
    app = Flask(__name__)
    
    reset_weights(WEIGHTS_FILE)
    sync_geojson_selected(['area.geojson', 'boundary.geojson'])
    
    app.register_blueprint(map_bp)
    app.register_blueprint(algo_bp)
    app.register_blueprint(filter_bp)
    app.register_blueprint(update_bp)
    app.register_blueprint(final_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
