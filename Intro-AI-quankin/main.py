from flask import Flask
from routes import map_bp, algo_bp, condition_bp
from utils.sync_geojson import sync_geojson_selected

def create_app():
    app = Flask(__name__)

    sync_geojson_selected(['area.geojson', 'boundary.geojson'])

    app.register_blueprint(map_bp)
    app.register_blueprint(algo_bp)
    app.register_blueprint(condition_bp)

    return app

app = create_app()

if __name__ == "__main__":
    print(">>> Flask server starting on http://127.0.0.1:5000")
    app.run(debug=True)


