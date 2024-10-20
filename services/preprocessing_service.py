# service untuk melakukan preprocessing
import numpy as np
import random
import cv2
import math
from numpy.lib.stride_tricks import sliding_window_view

def grayscale(image):
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Input image must be a color image with 3 channels (BGR).")

    B = image[:, :, 0].astype(np.float32)
    G = image[:, :, 1].astype(np.float32)
    R = image[:, :, 2].astype(np.float32)

    Y = 0.299 * R + 0.587 * G + 0.114 * B
    
    return Y.astype(np.uint8)

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

def median_filter(image, kernel_size=3, padding_mode='constant'):
    pad_size = kernel_size // 2
    padded_image = np.pad(image, pad_size, mode=padding_mode)

    window_shape = (kernel_size, kernel_size)
    windows = sliding_window_view(padded_image, window_shape)

    return np.median(windows, axis=(-1, -2)).astype(np.uint8)

def clahe(image, clip_limit=2.0, grid_size=(8, 8)):
    # Mendapatkan ukuran gambar
    h, w = image.shape
    
    # Ukuran tile (blok)
    tile_h, tile_w = h // grid_size[0], w // grid_size[1]
    
    # Membuat gambar keluaran
    result_image = np.zeros_like(image)
    
    # Memproses setiap tile
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            # Mendapatkan blok gambar
            x_start = i * tile_h
            x_end = (i + 1) * tile_h if (i + 1) * tile_h <= h else h
            y_start = j * tile_w
            y_end = (j + 1) * tile_w if (j + 1) * tile_w <= w else w
            
            tile = image[x_start:x_end, y_start:y_end]
            
            # Lakukan histogram equalization dengan limitasi kontras (contrast limiting)
            equalized_tile = clahe_on_tile(tile, clip_limit)
            
            # Letakkan hasil pada blok yang sesuai di gambar keluaran
            result_image[x_start:x_end, y_start:y_end] = equalized_tile
    
    return result_image

def clahe_on_tile(tile, clip_limit):
    # Histogram tile
    hist, bins = np.histogram(tile.flatten(), 256, [0, 256])
    
    # Batasi histogram dengan clip limit
    excess = np.maximum(hist - clip_limit, 0).sum()  # Hitung kelebihan
    hist = np.minimum(hist, clip_limit)  # Potong nilai histogram dengan clip limit
    hist = hist + (excess // 256)  # Redistribusikan kelebihan ke seluruh bin

    # Normalisasi CDF
    cdf = hist.cumsum()  # Kumulatif histogram
    cdf = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())  # Skala ulang CDF
    cdf = cdf.astype('uint8')  # Konversi ke uint8
    
    # Terapkan transformasi dari CDF
    result_tile = cdf[tile]
    
    return result_tile

def sharpening_filter(image):
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])

    sharpened_image = cv2.filter2D(image, -1, kernel)

    return sharpened_image

# def otsu_thresholding(image):
#     # Mendapatkan histogram dari citra
#     hist, bins = np.histogram(image.flatten(), bins=256, range=[0,256])
    
#     # Probabilitas untuk tiap level intensitas
#     pixel_total = image.size
#     prob = hist / pixel_total
    
#     # Inisialisasi variabel yang dibutuhkan
#     current_max = 0
#     threshold = 0
#     mean_weight1 = 0
#     mean_weight2 = 0
    
#     # Variabel untuk akumulasi
#     sum_all = np.dot(np.arange(256), hist)
#     sumB = 0
#     weightB = 0
#     weightF = 0
    
#     # Loop untuk menghitung varians antar-kelas
#     for t in range(256):
#         weightB += hist[t]  # Bobot latar belakang
#         weightF = pixel_total - weightB  # Bobot latar depan
        
#         if weightB == 0 or weightF == 0:
#             continue
        
#         sumB += t * hist[t]  # Rata-rata latar belakang
#         meanB = sumB / weightB
#         meanF = (sum_all - sumB) / weightF  # Rata-rata latar depan
        
#         # Hitung varians antar-kelas
#         var_between = weightB * weightF * (meanB - meanF) ** 2
        
#         # Cek apakah varians ini lebih besar dari varians maksimal sebelumnya
#         if var_between > current_max:
#             current_max = var_between
#             threshold = t
    
#     # Terapkan threshold pada gambar
#     otsu_image = image.copy()
#     otsu_image[image > threshold] = 255
#     otsu_image[image <= threshold] = 0
    
#     return otsu_image

def otsu_thresholding(image):
    img_otsu = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return img_otsu