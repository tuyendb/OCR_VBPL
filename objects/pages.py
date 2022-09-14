import os
import sys
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from utils.utils import pdf2imgs


class Pages:

    def __init__(self, pdf, first_page, last_page):
        self._pdf = pdf
        self._first_page = first_page
        self._last_page = last_page

    @property
    def pages(self):
        return pdf2imgs(self._pdf, self._first_page, self._last_page)

