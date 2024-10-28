from flask import Flask, jsonify
from config import Config
from controllers.ocr_controller import ocr_controller
from controllers.weighing_controller import weighing_controller
from models.weighing_record import db
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    app.register_blueprint(ocr_controller)
    app.register_blueprint(weighing_controller)

    @app.route('/')
    def info():
        return jsonify({
            "message": "Server is running",
            "port": app.config.get('APP_PORT', 5000)
        })

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=int(os.getenv('APP_PORT', 5000)))
