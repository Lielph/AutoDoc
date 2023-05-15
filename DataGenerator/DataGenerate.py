import numpy as np
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
import sys
import cv2
import qimage2ndarray
import argparse
import os 
import json


class PaperGeometry:
    # точки листа 
    def __init__(self, size, new_size) -> None:
        self.ul = None
        self.ur = None 
        self.br = None  
        self.bl = None 
        self.height, self.width = size
        self.new_height, self.new_width = new_size
        self.check = False
    def set_all_coord(self, coord: list):
        self.ul = coord[0]
        self.ur = coord[1] 
        self.br = coord[2] 
        self.bl = coord[3] 
        
    def set_coord(self, coord: list):
        if len(coord)!=2:
            return
        coord = self.__convert_size(coord)

        if self.ul is None:
            self.ul = coord
        elif self.ur is None:
            self.ur = coord
        elif self.br is None:
            self.br = coord
        elif self.bl is None:
            self.bl = coord
            self.check = True

    def clear(self):
        self.ul = None
        self.ur = None 
        self.br = None  
        self.bl = None 
        self.check = False

    def convert_json(self, path):
        data = {
            'ul': self.ul,
            'ur': self.ur,
            'br': self.br,
            'bl': self.bl
        }

        json_string = json.dumps(data)
        with open(f'{path}.json', 'w') as outfile:
            outfile.write(json_string)
        
    def get_matrix_points(self):
        return np.float32([ self.ul,  self.ur, self.br,  self.bl])
    
    def __convert_size(self, coord):
        
        delt_y = self.height/self.new_height
        delt_x = self.width/self.new_width

        return (int(coord[0]*delt_x), int(coord[1]*delt_y))


# Класс для формочки
class Ui(QtWidgets.QMainWindow):
    def __init__(self, path_dir):
        super(Ui, self).__init__()
        uic.loadUi('/Users/dimka777/Documents/GitHub/AutoDoc/DataGenerator/main_form.ui',self)

        self.size_label = self.Oridinal_label.size()
        
        #  изображения 
 
        self.check_points = False
        # 2480х3508
        self.A4_hieght = 3508
        self.A4_width = 2480
        self.coord_sheet = None
        
        self.Next_pushButton.clicked.connect(self.load_image)
        self.Save_pushButton.clicked.connect(self.save_json)
        self.Change_pushButton.clicked.connect(self.clear)

        self.Oridinal_label.mousePressEvent = self.__click_image

        self.Oridinal_label.mouseMoveEvent = self.__view_enlargement

        
        
        self.path_dir = [ os.path.join(path_dir, path_image) for path_image in os.listdir(path_dir) ]
        self.path_dir = list(filter(lambda x: (x.split('.')[-1] != 'json'), self.path_dir))
        self.count_image = len(self.path_dir)
        self.load_image()
        
    def save_json(self):
        self.coord_sheet.convert_json(self.path_dir[-self.count_image-1])
        self.Name_lineEdit.setText("JSON SAVED")
        
    def load_image(self):
        """загрузка изображений"""

        if self.count_image!=0:
            self.check_points = True
            path_image = self.path_dir[-self.count_image]

            self.Name_lineEdit.setText(f"{path_image[len(self.path_dir)+1:]}")
            self.__getView_img(path_image, True)
            self.count_image-=1
        else:
            path = 'DataGenerator/utils/end.jpg'
            self.__getView_img(path, False)

    def __getView_img(self, path_image, save_size = False):
            # чтение
            image = cv2.imread(path_image)

            h, w  = self.size_label.height(), self.size_label.width()

            if save_size:
                size_image = image.shape[:2]
                self.coord_sheet = PaperGeometry(size_image, (h,w))

            
            image = cv2.resize(image,(w,h),cv2.INTER_CUBIC)
            # Перевод изображения в Qpixmap
            image2pixmap = QPixmap.fromImage(qimage2ndarray.array2qimage(image))
            # Отображение
            self.Oridinal_label.setPixmap(image2pixmap)

    def clear(self):
        self.coord_sheet.clear()
        path_image = self.path_dir[-self.count_image-1]
        image = cv2.imread(path_image)
        h, w  = self.size_label.height(), self.size_label.width()
        image = cv2.resize(image,(w,h),cv2.INTER_CUBIC)
            # Перевод изображения в Qpixmap
        image2pixmap = QPixmap.fromImage(qimage2ndarray.array2qimage(image))
        # Отображение
        self.Oridinal_label.setPixmap(image2pixmap)

    def __view_enlargement(self,event):
        '''Увеличение'''
        if not self.coord_sheet.check:
            pose = self.__getPos(event)
            image = self.Oridinal_label.pixmap().toImage()
            image = qimage2ndarray.rgb_view(image)
            size_cell = 10
            crop_img = image[pose[1]-size_cell:pose[1]+size_cell, pose[0]-size_cell:pose[0]+size_cell]

            try:
                h, w  = self.size_label.height(), self.size_label.width()
                result = cv2.resize(crop_img,(w,h),cv2.INTER_CUBIC)

                center = (int(w/2), int(h/2))
                size = 25
                cv2.line(result, (center[0]-size, center[1]),(center[0]+size, center[1]), (255,0,0),2)
                cv2.line(result, (center[0], center[1]-size),(center[0], center[1]+size), (255,0,0),2)

                image2pixmap = QPixmap.fromImage(qimage2ndarray.array2qimage(result))
                    # Отображение
                self.Warp_label.setPixmap(image2pixmap)
            except:
                pass
        pass 

    def __update_text(self):
        paper = self.coord_sheet
        text = f"ul: {paper.ul} | ur: {paper.ur} | br: {paper.br} | bl: {paper.bl} " 
        self.Points_lineEdit.setText(text)

    def __getPos(self , event):
        x = event.pos().x()
        y = event.pos().y() 
        return [x,y]
    
    def __drawPoint(self, pose, image_):
        image = image_.copy()
        lenght = 10
        cv2.line(image,(pose[0]-lenght, pose[1]),(pose[0]+lenght,pose[1]),(0,255,0),1)
        cv2.line(image,(pose[0],pose[1]-lenght),(pose[0],pose[1]+lenght),(0,255,0),1)
        cv2.circle(image, pose,2,(255,0,0),-1)

        return image 
    
    def __click_image(self,event):
        if not self.coord_sheet.check:
            image = self.Oridinal_label.pixmap().toImage()
            image = qimage2ndarray.rgb_view(image)
            pose = self.__getPos(event)

            # кординаты точек
            self.coord_sheet.set_coord(pose)
            self.__update_text()

            image = self.__drawPoint(pose, image)
            image2pixmap = QPixmap.fromImage(qimage2ndarray.array2qimage(image))
                # Отображение
            self.Oridinal_label.setPixmap(image2pixmap)
        else:
            self.__get_percpective(self.path_dir[-self.count_image-1],self.coord_sheet)
        pass 
    
    def __get_percpective(self, path_image, points: PaperGeometry):
        image_ = cv2.imread(path_image)
        pts1 = points.get_matrix_points()
        pts2 = np.float32([[0, 0], [self.A4_width, 0],
                       [self.A4_width, self.A4_hieght], [0, self.A4_hieght] ])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        result = cv2.warpPerspective(image_, matrix, (self.A4_width, self.A4_hieght))
        
        h, w  = self.size_label.height(), self.size_label.width()
        result = cv2.resize(result,(w,h),cv2.INTER_CUBIC)

        image2pixmap = QPixmap.fromImage(qimage2ndarray.array2qimage(result))
                # Отображение
        self.Warp_label.setPixmap(image2pixmap)


# parser = argparse.ArgumentParser(description='Директория для папок')
# parser.add_argument('--Folder', type=str)
# args = parser.parse_args()

# folder = args.Folder

folder = '/Users/dimka777/Documents/GitHub/AutoDoc/TestImages'
app = QtWidgets.QApplication(sys.argv)
window = Ui(folder)
window.show()
app.exec_()