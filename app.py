from flask import Flask
from routes import map_bp, algo_bp
from condition import filter_bp, update_bp, final_bp
from utils.reset import reset_weights
from utils.sync_geojson import sync_geojson_selected

def create_app():
    reset_weights()
    app = Flask(__name__)

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
