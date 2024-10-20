import cv2
import numpy as np
import io
from flask import Blueprint, request, send_file
from services import preprocessing_service

ocr_controller = Blueprint('ocr_controller', __name__)

# cuma buat ngetes aja
@ocr_controller.route('/preprocess', methods=['POST'])
def process_image():
    try:
        file = request.files['image']
        
        if not file:
            return {"error": "No image file provided"}, 400
        
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        
        gray_image = preprocessing_service.grayscale(image)
        preprocess_image = preprocessing_service.grayscale(gray_image)
        
        is_success, buffer = cv2.imencode('.jpg', preprocess_image)
        io_buf = io.BytesIO(buffer)

        return send_file(io_buf, mimetype='image/jpeg')
    except Exception as e:
        return(str(e))