from flask import Flask, request, jsonify, send_file
from config import Config
from controllers.ocr_controller import ocr_controller


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(ocr_controller)

@app.route('/')
def info():
    return ('Server is Running on port ' + app.config['APP_PORT']) 

if __name__ == '__main__':
    app.run(debug=True, port=app.config['APP_PORT'])