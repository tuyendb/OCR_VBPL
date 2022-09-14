import os
import sys
import numpy as np
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from objects.line import Line


class Paragraph:

    def __init__(self, img, para_info):
        self._para_info = para_info
        self._img = img
        self._lines_coords = None
        self._lines_ct = None
        self._paragr_coord = None
        self._paragr_content = None
        
    @property
    def lines_ct(self):
        if self._lines_ct is None:
            self._lines_ct = self._para_info[0]
        return self._lines_ct

    @property
    def lines_coords(self):
        if self._lines_coords is None:
            self._lines_coords = self._para_info[1]
        return self._lines_coords  

    @property
    def paragraph_content(self):
        if self._paragr_content is None:
            self._paragr_content = ''
            for line in self.lines_ct:
                for word in line:
                    self._paragr_content += word + ' '
        return self._paragr_content
    
    @property
    def paragraph_coord(self):
        if self._paragr_coord is None:
            x1 = min([f[0] for f in self.lines_coords])
            y1 = self.lines_coords[0][1]
            x2 = max([f[2] for f in self.lines_coords])
            y2 = self.lines_coords[-1][3]
            self._paragr_coord = [x1, y1, x2, y2]
        return self._paragr_coord
    
    @property
    def paragraph_img_crop(self):
        x1, y1, x2, y2 = self.paragraph_coord
        paragr_img = self._img[y1:y2, x1:x2]
        return paragr_img

    @property
    def median_tn_thresh(self):
        paragr_lines_tn = []
        median_thresh = None
        for line_id in range(len(self.lines_coords)):
            considered_line_img = Line(self._img, self.lines_coords[line_id], self.lines_ct[line_id])
            median_thickness = considered_line_img.letter_stroke_thickness
            if np.isnan(median_thickness) or median_thickness == 0:
                pass
            else:
                paragr_lines_tn.append(median_thickness)
        if len(paragr_lines_tn) != 0:
            median_thresh = np.median(np.array(paragr_lines_tn))
        else:
            median_thresh = None
        return median_thresh

    def is_upper(self):
        upper = False
        word_list = self.paragraph_content.split(' ')
        for i in range(len(word_list) - 1):
            if word_list[i].isupper() and word_list[i + 1].isupper():
                upper = True
                break
        return upper
