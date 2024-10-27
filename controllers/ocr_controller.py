import cv2
import numpy as np
import io
from flask import Blueprint, request, send_file, jsonify
from services import preprocessing_service, ocr_service

ocr_controller = Blueprint('ocr_controller', __name__)

# cuma buat ngetes aja
@ocr_controller.route('/api/ocr/preprocess', methods=['POST'])
def process_image():
    try:
        file = request.files['image']
        
        if not file:
            return {"error": "No image file provided"}, 400
        
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        
        gray_image = preprocessing_service.grayscale(image)
        deskew_image = preprocessing_service.deskew_image(gray_image)
        clahe_image = preprocessing_service.clahe(deskew_image)
        sharpening_image = preprocessing_service.sharpening_filter(clahe_image)
        preprocess_image = preprocessing_service.otsu_thresholding(sharpening_image)
        
        is_success, buffer = cv2.imencode('.jpg', preprocess_image)
        io_buf = io.BytesIO(buffer)

        return send_file(io_buf, mimetype='image/jpeg')
    except Exception as e:
        return(str(e))


@ocr_controller.route('/api/ocr/', methods=['POST'])
def detect_text_api():
    try:
        file = request.files.get('image')
        
        if not file:
            return jsonify({
                "status_code": 400,
                "message": "No image file provided",
                "data": None
            }), 400
        
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        
        gray_image = preprocessing_service.grayscale(image)
        deskew_image = preprocessing_service.deskew_image(gray_image)
        clahe_image = preprocessing_service.clahe(deskew_image)
        sharpening_image = preprocessing_service.sharpening_filter(clahe_image)
        preprocess_image = preprocessing_service.otsu_thresholding(sharpening_image)
        
        result_text = ocr_service.detect_text(preprocess_image)
        
        if result_text:
            return jsonify({
                "status_code": 200,
                "message": "Text detection successful",
                "data": result_text
            }), 200
        else:
            return jsonify({
                "status_code": 200,
                "message": "No text detected",
                "data": None
            }), 200

    except Exception as e:
        return jsonify({
            "status_code": 500,
            "message": "An error occurred while processing the image",
            "data": str(e)
        }), 500