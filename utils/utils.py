from pdf2image import convert_from_path, convert_from_bytes
import numpy as np
import pytesseract
import cv2
from pytesseract import Output
import os, sys
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from objects.paragraph import Paragraph
from objects.line import Line


def pdf2imgs(pdf: bytes or str, first_page, last_page):
    if type(pdf) is str:
        images = convert_from_path(
            pdf,
            grayscale=True,
            first_page=first_page,
            last_page=last_page,
            jpegopt=True
        )
    else:
        images = convert_from_bytes(
            pdf,
            grayscale=True,
            first_page=first_page,
            last_page=last_page,
            jpegopt=True
        )
    pages = []
    for image in images:
        image = image.convert('RGB')
        cv2_img = np.array(image)
        #rgb2bgr
        cv2_img = cv2_img[:, :, ::-1]
        gray_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
        pages.append(gray_img)
    return pages


###### CHECK, REMOVE UNNECESSARY CONTENT #####
def check_lenght(text):
    check_len = len(text) <= 2
    return check_len


def check_remove(text):
    check_rm = check_lenght(text)
    return check_rm


class ExtractParagrsFromImg:

    def __init__(self, img):
        self._img = img
        self._img_height, self._img_width = img.shape[:2]
        self._texts_infor = None

    @property
    def texts_infor(self) -> dict:
        if self._texts_infor is None:
            self._texts_infor = pytesseract.image_to_data(
                self._img,
                lang='vie',
                output_type=Output.DICT
            )
            remove_ids = []
            for id, conf in enumerate(self._texts_infor['conf']):
                if conf  == "-1" or conf <= 40:
                    remove_ids.append(id)
            for id, text in enumerate(self._texts_infor['text']):
                if text == "" or text == " ":
                    remove_ids.append(id)
            remove_ids = sorted(list(set(remove_ids)))
            for key in self._texts_infor.keys():
                for id, val in enumerate(remove_ids):
                    del self._texts_infor[key][val - id]
        return self._texts_infor
    
    @property
    def extracted_paragraphs(self):
        extract_ids = {}
        for ch_id in range(self.texts_infor['block_num'].__len__()):
            if not bool(extract_ids):
                extract_ids = {1: {1: {1: [ch_id]}}}
            else:
                max_block_num = (list(extract_ids.keys()))[-1]
                max_par_num = (list(extract_ids[max_block_num].keys()))[-1]
                max_line_num = (list(extract_ids[max_block_num][max_par_num].keys()))[-1]
                if self.texts_infor['block_num'][ch_id] != max_block_num:
                    extract_ids[max_block_num + 1] = {1: {1: [ch_id]}}
                else: 
                    if self.texts_infor['par_num'][ch_id] != max_par_num:
                        extract_ids[max_block_num][max_par_num + 1] = {1: [ch_id]}
                    else:
                        if self.texts_infor['line_num'][ch_id] != max_line_num:
                            extract_ids[max_block_num][max_par_num][max_line_num + 1] = [ch_id]
                        else:
                            extract_ids[max_block_num][max_par_num][max_line_num].append(ch_id)
        paragraphs_infor = []
        for bl in extract_ids.keys():
            for par in extract_ids[bl].keys():
                pr_lines_ct = []
                pr_lines_coords = []
                for line in extract_ids[bl][par].keys():
                    begin_id = extract_ids[bl][par][line][0]
                    end_id = extract_ids[bl][par][line][-1]
                    b_x, b_y, b_w, b_h = self.texts_infor['left'][begin_id], self.texts_infor['top'][begin_id], self.texts_infor['width'][begin_id], self.texts_infor['height'][begin_id]
                    e_x, e_y, e_w, e_h = self.texts_infor['left'][end_id], self.texts_infor['top'][end_id], self.texts_infor['width'][end_id], self.texts_infor['height'][end_id]
                    x1, y1, x2, y2 = b_x, min(b_y, e_y), e_x + e_w, max(b_y + b_h, e_y, e_h)
                    pr_lines_coords.append([x1, y1, x2, y2])
                    line_ct = []
                    for word_idx in extract_ids[bl][par][line]:
                        line_ct.append(self.texts_infor['text'][word_idx])
                    pr_lines_ct.append(line_ct)
                if check_remove(Paragraph(self._img, [pr_lines_ct, pr_lines_coords]).paragraph_content):
                    pass
                else:
                    paragraphs_infor.append([pr_lines_ct, pr_lines_coords])
        return paragraphs_infor


def find_threshold(thickness_list: list):
    b = np.zeros((5,), dtype=np.int16)
    upper_thresh = max(thickness_list)
    lower_thresh = min(thickness_list)
    step = (upper_thresh - lower_thresh)/5
    for i in thickness_list:
        for j in range(1, 6):
            if i <= lower_thresh + j*step:
                b[j - 1] += 1
                break
    index = np.argmax(b)
    threshold = lower_thresh + (index + 1)*step
    return threshold


class Hierachy:

    def __init__(self, paragraph: Paragraph, threshold):
        self._paragraph = paragraph
        self._threshold = threshold
        self._hierachy = None

    def is_bold(self):
        if self._paragraph.median_tn_thresh is not None:
            return self._paragraph.median_tn_thresh >= self._threshold
        else:
            return False
            
    def is_upper(self):
        return self._paragraph.is_upper()

    @property
    def hierachy(self):
        if self._hierachy is None:
            check_list = ['Điều', 'Điêu', 'điều']
            if self.is_upper() and self.is_bold():
                self._hierachy = '1'
            # elif self.is_bold() and not self.is_upper():
            #     return "2"    
            else:
                for check in check_list:
                    if check in self._paragraph.paragraph_content[:4]:
                        self._hierachy = '2'
                        break
        return self._hierachy        


def rm_keys(key_ls):
    if "Number" in key_ls:
        key_ls.remove("Number")
    if "Topic" in key_ls:
        key_ls.remove("Topic")
    return key_ls


def add_to_list(considered_paragr: Paragraph, considered_list):
    if considered_list[0] is None:
        considered_list.append(considered_paragr.paragraph_content)
        considered_list[0] = Line(
            considered_paragr._img,
            considered_paragr.lines_coords[0],
            considered_paragr.lines_ct[0]
        ).x_coords[0]
    else:
        if Line(
            considered_paragr._img,
            considered_paragr.lines_coords[0],
            considered_paragr.lines_ct[0]
        ).x_coords[0] <= considered_list[0] - 10:
            considered_list[-1] = considered_list[-1] + considered_paragr.paragraph_content
        else:
            considered_list[0] = Line(
                considered_paragr._img,
                considered_paragr.lines_coords[0],
                considered_paragr.lines_ct[0]
            ).x_coords[0]
            considered_list.append(considered_paragr.paragraph_content)
    return considered_list
