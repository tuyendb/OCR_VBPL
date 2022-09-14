import os, sys
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from objects.paragraph import Paragraph
from objects.line import Line


class MergeParagraph:
    
    def __init__(self, paragr1: Paragraph, paragr2: Paragraph):
        self._paragr1 = paragr1
        self._paragr2 = paragr2
        self._merged_paragrs = None
       
    @property 
    def merged_paragrs(self):
        if self._merged_paragrs is None:
            st_x_begin = Line(self._paragr1._img, self._paragr1.lines_coords[0], self._paragr1.lines_ct[0]).x_cooords[0]
            considered_x_begin = Line(self._paragr2._img, self._paragr2.lines_coords[0], self._paragr2.lines_ct[0]).x_cooords[0]
            if considered_x_begin <= st_x_begin - 20:
                self._merged_paragrs = ("", self._paragr1.paragraph_content + self._paragr2.paragraph_content)
            else:
                self._merged_paragrs = (self._paragr1.paragraph_content, self._paragr2.paragraph_content)
        return self._merged_paragrs
    