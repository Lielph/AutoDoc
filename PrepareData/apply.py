# читаем модель и делаем сегментацию

import tensorflow as tf
from sklearn.model_selection import train_test_split
from keras.models import Model
from keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, concatenate, Conv2DTranspose, BatchNormalization, \
    Dropout, Lambda
import numpy as np
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, CSVLogger, TensorBoard


def get_segmentation_mask(image_: np.array) -> np.array:
    # вообще по хорошему держать файл с моделью на сервере и передавать путь к динамически
    path_model = r'E:\GitHub\AutoDoc\NN_3\result_model\model.h5'
    # загрузка модели
    model = tf.keras.models.load_model(path_model)
    # подготовка входного изображения
    image = image_ / 255.0
    image = np.expand_dims(image, axis=0)  #
    image = image.astype(np.float32)

    seg_image = model.predict(image, verbose=0)[0]
    seg_image = np.argmax(seg_image, axis=-1)  ## [0.1, 0.2, 0.1, 0.6] -> 3
    seg_image = seg_image.astype(np.int32)

    return seg_image
