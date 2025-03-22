from flask import Flask
from routes import map_bp, algo_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(map_bp)
    app.register_blueprint(algo_bp)
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)