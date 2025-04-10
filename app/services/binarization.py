import cv2
import numpy as np
from PIL import Image


def binarize_image(image: Image.Image, algorithm: str) -> Image.Image:
    # Преобразуем картинку в массив чисел (пиксели)
    img_array = np.array(image)

    # Если картинка цветная, делаем её серой
    if len(img_array.shape) == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # Выбираем алгоритм
    if algorithm.lower() == "otsu":
        # Отсу сам находит лучший порог
        _, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    elif algorithm.lower() == "balanced":
        # Сбалансированная гистограмма
        binary = balanced_histogram_thresholding(img_array)

    elif algorithm.lower() == "niblack":
        # Адаптивный Ниблэк (смотрит на окрестности пикселя)
        binary = cv2.ximgproc.niBlackThreshold(img_array, maxValue=255,
                                               type=cv2.THRESH_BINARY,
                                               blockSize=15, k=-0.2)

    elif algorithm.lower() == "sauvola":
        # Адаптивный Саувола (улучшенный Ниблэк)
        window_size = 15
        k = 0.2
        R = 128
        mean = cv2.boxFilter(img_array, cv2.CV_32F, (window_size, window_size))
        mean_sq = cv2.boxFilter(img_array.astype(np.float32) ** 2, cv2.CV_32F, (window_size, window_size))
        variance = mean_sq - mean ** 2
        threshold = mean * (1 + k * ((np.sqrt(variance) / R) - 1))
        binary = np.where(img_array > threshold, 255, 0).astype(np.uint8)

    else:
        raise ValueError(f"Неизвестный алгоритм: {algorithm}")

    # Преобразуем результат обратно в картинку
    return Image.fromarray(binary)


def balanced_histogram_thresholding(image):
    # Считаем гистограмму (сколько пикселей каждого уровня яркости)
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).ravel()
    hist = hist / hist.sum()  # Нормализуем

    # Ищем "сбалансированный" порог
    left_sum = right_sum = 0
    left_count = right_count = 0

    for i in range(256):
        if i < 128:
            left_sum += i * hist[i]
            left_count += hist[i]
        else:
            right_sum += i * hist[i]
            right_count += hist[i]

    if left_count == 0 or right_count == 0:
        threshold = 128
    else:
        threshold = int((left_sum / left_count + right_sum / right_count) / 2)

    _, binary = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return binary