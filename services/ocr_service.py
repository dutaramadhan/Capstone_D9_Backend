# service untuk ocr dan ekstraksi informasi
from google.cloud import vision
import cv2
import os
from config import Config

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.API_CREDENTIALS

def detect_text(preprocessed_image):
    client = vision.ImageAnnotatorClient()
    
    content = cv2.imencode('.jpg', preprocessed_image)[1].tobytes()
    image = vision.Image(content=content)
    
    response = client.text_detection(image=image)
    
    if response.error.message:
        raise Exception(
            f"{response.error.message}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors"
        )
    
    texts = response.text_annotations
    return texts[0].description if texts else None