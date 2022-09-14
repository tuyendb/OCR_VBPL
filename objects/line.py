import cv2
import os
import numpy as np
import sys
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))


class Line:

    def __init__(self, img, line_coord, line_ct):
        self._img = img
        self._line_coord = line_coord
        self._line_ct = line_ct
        self._line_img_crop = None
        self._binary_img = None
        self._y_coords = None
        self._line_img_shape = None
        self._x_cooords = None
    
    @property
    def line_content(self):
        line = ''
        for word in self._line_ct:
            line += word + ' '
        return line
    
    @property
    def line_img_crop(self):
        if self._line_img_crop is None:
            x1, y1, x2, y2 = self._line_coord
            self._line_img_crop = self._img[y1:y2, x1:x2]
        return self._line_img_crop
    
    @property
    def line_img_shape(self):
        if self._line_img_shape is None:
            self._line_img_shape = self.line_img_crop.shape[:2]
        return self._line_img_shape

    @property
    def binary_img(self):
        if self._binary_img is None:
            self._binary_img = cv2.threshold(self.line_img_crop.copy(), 200, 255, cv2.THRESH_BINARY)[1]
        return self._binary_img
    
    @property
    def y_coords(self) -> tuple:
        if self._y_coords is None:            
            self._y_coords = (self._line_coord[1], self._line_coord[3])
        return self._y_coords

    @property
    def x_coords(self) -> tuple:
        if self._x_cooords is None:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))
            erode_img = cv2.erode(self.binary_img.copy(), kernel=kernel, iterations=1)
            center_y = int(self.line_img_shape[0] / 2)
            center_line = erode_img[center_y:center_y + 1, 0:self.line_img_shape[1]].flatten()
            start_point = end_point = 0
            for i in range(0, self.line_img_shape[1] - 1):
                if center_line[i] == 0 and center_line[i + 1] == 0:
                    start_point = i
                    break
            for j in range(1, self.line_img_shape[1]):
                if center_line[-j] == 0 and center_line[-j - 1] == 0:
                    end_point = self.line_img_shape[1] - j
                    break
            self._x_coords = (start_point + self._line_coord[0], end_point + self._line_coord[0])
        return self._x_coords

    @property
    def letter_stroke_thickness(self):
        h, w = self.line_img_crop.shape[:2]
        center_hor_line = self.line_img_crop[int(h/2):int(h/2) + 1, 0:w].flatten()
        thickness_list = []
        start_pt = None
        end_pt = None
        for id in range(center_hor_line.__len__() - 1):
            if id == 0 and center_hor_line[id] <= 3:
                start_pt = id
            elif id != 0 and center_hor_line[id] > 3 and center_hor_line[id + 1] <= 3:
                start_pt = id + 1
            if id != 0 and center_hor_line[id] <= 3 and center_hor_line[id + 1] > 3 and start_pt is not None:
                end_pt = id
            elif center_hor_line[id + 1] <= 3 and id == center_hor_line.__len__() - 2 and start_pt is not None:
                end_pt = id + 1
            if start_pt is not None and end_pt is not None:
                thickness_list.append(end_pt - start_pt)
                start_pt = None
                end_pt = None
        median_thickness = np.median(np.array(thickness_list))
        return median_thickness
    