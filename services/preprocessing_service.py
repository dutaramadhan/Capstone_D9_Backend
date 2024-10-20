# service untuk melakukan preprocessing
import numpy as np
import random
import cv2
import math

def grayscale(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

def deskew_image(image):
     # ubah tiap pixel 'edge' ke dimensi (rho, theta)
    edges = cv2.Canny(image, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    # ambil semua nilai theta
    angles = [line[0][1] for line in lines] if lines is not None else []

    # ambil theta skew dari median theta
    median_theta = np.median(angles) if angles else 0

    # konversi derajat ke radian
    skew_angle = (median_theta * 180 / np.pi) - 90
    print(skew_angle)

    # rotasi gambar dengan padding cv2.BORDER_REPLICATE
    (h, w) = image.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -skew_angle, 1.0)
    abs_cos = abs(M[0, 0])
    abs_sin = abs(M[0, 1])
    new_w = int(h * abs_sin + w * abs_cos)
    new_h = int(h * abs_cos + w * abs_sin)
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    return cv2.warpAffine(image,
                          M,
                          (new_w, new_h),
                          flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)