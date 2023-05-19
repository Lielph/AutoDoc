# получаем точки с изображения и выдаем перспективу

import cv2
import numpy as np
import os
import tensorflow as tf
from PrepareData.apply import get_segmentation_mask


class DocumentAlignment:
    def __init__(self, path_image: str):
        self.warp_image = None
        self.points = None
        self.path_image = path_image
        self.new_h, self.new_w = 256, 256
        self.__A4_height = 512
        self.__A4_width = 512

        self.__generate_data()
        self.get_points()
        self.alignment_image()

    def get_points(self):
        # сегментированное изображение 256x256
        mask = np.uint8(get_segmentation_mask(self.prepare_image))

        # вернуть первоначальный размер
        mask = cv2.resize(mask, (self.initial_w, self.initial_h))
        mask = tf.one_hot(mask, 5).numpy()
        # получаем контуры углов

        points_ = []
        for i in range(1, 5):
            mask_ = mask[..., i]

            # убрать шумы (возникаю в результате изменения размера)
            kernel = np.ones((20, 20), np.uint8)
            mask_ = cv2.erode(mask_, kernel)
            mask_ = cv2.dilate(mask_, kernel)
            # контуры
            contour, hierarchy = cv2.findContours(np.uint8(mask_), cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_NONE)
            moment = cv2.moments(contour[0])
            points_.append([int(moment['m10'] / moment['m00']), int(moment['m01'] /
                                                                    moment['m00'])])

        self.points = points_
        # отладка
        # self.draw_points()

    def __draw_points(self):
        image_ = self.image.copy()
        points = self.points
        for point in points:
            cv2.circle(image_, point, 10, (0, 0, 255), -1)
        image_ = cv2.resize(image_, (1024, 1024))
        cv2.imshow('d', image_)
        cv2.waitKey()

    def alignment_image(self):
        """Получение перспективы"""
        pts1 = np.float32(self.points)
        pts2 = np.float32([[0, 0], [self.__A4_width, 0],
                           [self.__A4_width, self.__A4_height], [0, self.__A4_height]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        result = cv2.warpPerspective(self.image, matrix, (self.__A4_width, self.__A4_height))
        self.warp_image = result

    def __generate_data(self):
        """Формирование данные """
        self.image = self.__read_image(self.path_image)
        self.initial_h, self.initial_w, _ = self.image.shape
        self.__prepare_data()

    def __prepare_data(self):
        """Пердобработка изображения"""
        self.prepare_image = cv2.resize(self.image, (256, 256))

    @staticmethod
    def __read_image(path_image: str):
        """Чтение изображения"""
        image = cv2.imread(path_image)
        return image


"""пример использования"""
# test_path = r'E:\GitHub\AutoDoc\TestImages\IMG_3228.JPG'
# test = DocumentAlignment(test_path).warp_image
#
# cv2.imshow('d', test)
# cv2.waitKey()
