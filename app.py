from flask import Flask, jsonify
from config import Config
from controllers.ocr_controller import ocr_controller
from controllers.weighing_controller import weighing_controller
from controllers.login_controller import login_controller
from models.weighing_record import db
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)
    
    app.register_blueprint(ocr_controller)
    app.register_blueprint(weighing_controller)
    app.register_blueprint(login_controller)

    @app.route('/')
    def info():
        return jsonify({
            "message": "Server is running",
            "port": app.config.get('APP_PORT', 5000)
        })

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('APP_PORT', 5000)))