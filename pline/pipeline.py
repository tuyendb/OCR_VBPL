import os
import argparse
import sys
import json
from matplotlib.font_manager import json_dump
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from utils.utils import ExtractParagrsFromImg, Hierachy, find_threshold
from objects.pages import Pages
from objects.paragraph import Paragraph
from objects.data_request import GetDataFromPDF
from objects.line import Line


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pp', '--pdf_file', type=str, required=True)
    parser.add_argument('-fp', '--first_page', type=int, default=None)
    parser.add_argument('-lp', '--last_page', type=int, default=None)
    args = parser.parse_args()
    return args


def main(opt):
    extract_content = {}
    pages = Pages(opt.pdf_file, first_page=opt.first_page, last_page=opt.last_page).pages
    pages_tn = []
    for page_img in pages:
        page_paragr_infor = ExtractParagrsFromImg(page_img).extracted_paragraphs
        for paragr_infor in page_paragr_infor:
            pages_tn.append(Paragraph(page_img, paragr_infor).median_tn_thresh)
    fn_tn = [f for f in pages_tn if f is not None]
    threshold = find_threshold(fn_tn)
    for page_img in pages:
        page_paragr_infor = ExtractParagrsFromImg(page_img).extracted_paragraphs
        for paragr_infor in page_paragr_infor:
            considered_paragr = Paragraph(page_img, paragr_infor)
            if Hierachy(considered_paragr, threshold).hierachy == '1':
                extract_content[considered_paragr.paragraph_content] = {}
            elif Hierachy(considered_paragr, threshold).hierachy == '2' and bool(extract_content):
                keys_list = list(extract_content.keys())
                extract_content[keys_list[-1]][considered_paragr.paragraph_content] = [None]
            else:
                if bool(extract_content) and bool(extract_content[list(extract_content.keys())[-1]]):
                    keys_list1 = list(extract_content.keys())
                    keys_list2 = list(extract_content[keys_list1[-1]].keys())
                    if extract_content[keys_list1[-1]][keys_list2[-1]][0] is None:
                        extract_content[keys_list1[-1]][keys_list2[-1]].append(considered_paragr.paragraph_content)
                        extract_content[keys_list1[-1]][keys_list2[-1]][0] == Line(
                            considered_paragr._img,
                            considered_paragr.lines_coords[0],
                            considered_paragr.lines_ct[0]
                            ).x_cooords[0]
                    else:
                        if Line(considered_paragr._img, considered_paragr._lines_coords[0], considered_paragr.lines_ct[0]).x_cooords[0]\
                                <= extract_content[keys_list1[-1]][keys_list2[-1]][0] - 10:
                            extract_content[keys_list1[-1]][keys_list2[-1]][-1] = extract_content[keys_list1[-1]][keys_list2[-1]][-1] + considered_paragr.paragraph_content
                        else:
                            extract_content[keys_list1[-1]][keys_list2[-1]][0] == Line(
                                considered_paragr._img,
                                considered_paragr.lines_coords[0],
                                considered_paragr.lines_ct[0]
                                ).x_cooords[0]
                            extract_content[keys_list1[-1]][keys_list2[-1]].append(considered_paragr.paragraph_content)
    key_ls = list(extract_content.keys())
    for key in key_ls:
        if not bool(extract_content[key]):
            del extract_content[key]
    for key in extract_content.keys():
        for sub_key in extract_content[key]:
            del extract_content[key][sub_key][0]
    json.dump(extract_content, open('../extracted_data/1.json', 'w', encoding='utf-8'), ensure_ascii=False)


class ExtractDataFromPDF:
    
    def __init__(self):
        pass
    
    def extract_data(self, pdf_file, first_page, last_page):
        extract_content = {}
        pages = Pages(pdf_file, first_page=first_page, last_page=last_page).pages
        pages_tn = []
        for page_img in pages:
            page_paragr_infor = ExtractParagrsFromImg(page_img).extracted_paragraphs
            for paragr_infor in page_paragr_infor:
                pages_tn.append(Paragraph(page_img, paragr_infor).median_tn_thresh)
        fn_tn = [f for f in pages_tn if f is not None]
        print(fn_tn)
        threshold = find_threshold(fn_tn)
        print(threshold)
        for page_img in pages:
            page_paragr_infor = ExtractParagrsFromImg(page_img).extracted_paragraphs
            for paragr_infor in page_paragr_infor:
                considered_paragr = Paragraph(page_img, paragr_infor)
                if Hierachy(considered_paragr, threshold).hierachy == '1':
                    extract_content[considered_paragr.paragraph_content] = {}
                elif Hierachy(considered_paragr, threshold).hierachy == '2' and bool(extract_content):
                    keys_list = list(extract_content.keys())
                    extract_content[keys_list[-1]][considered_paragr.paragraph_content] = [None]
                else:
                    if bool(extract_content) and bool(extract_content[list(extract_content.keys())[-1]]):
                        keys_list1 = list(extract_content.keys())
                        keys_list2 = list(extract_content[keys_list1[-1]].keys())
                        if extract_content[keys_list1[-1]][keys_list2[-1]][0] == None:
                            extract_content[keys_list1[-1]][keys_list2[-1]].append(considered_paragr.paragraph_content)
                            extract_content[keys_list1[-1]][keys_list2[-1]][0] == Line(
                                considered_paragr._img,
                                considered_paragr.lines_coords[0],
                                considered_paragr.lines_ct[0]
                                ).x_cooords[0]
                        else:
                            if Line(considered_paragr._img, considered_paragr._lines_coords[0], considered_paragr.lines_ct[0]).x_cooords[0]\
                                    <= extract_content[keys_list1[-1]][keys_list2[-1]][0] - 10:
                                extract_content[keys_list1[-1]][keys_list2[-1]][-1] = extract_content[keys_list1[-1]][keys_list2[-1]][-1] + considered_paragr.paragraph_content
                            else:
                                extract_content[keys_list1[-1]][keys_list2[-1]][0] == Line(
                                    considered_paragr._img,
                                    considered_paragr.lines_coords[0],
                                    considered_paragr.lines_ct[0]
                                    ).x_cooords[0]
                                extract_content[keys_list1[-1]][keys_list2[-1]].append(considered_paragr.paragraph_content)
        key_ls = list(extract_content.keys())
        for key in key_ls:
            if not bool(extract_content[key]):
                del extract_content[key]
        for key in extract_content.keys():
            for sub_key in extract_content[key]:
                del extract_content[key][sub_key][0]              
        return extract_content  
                        
    def __call__(self, data: GetDataFromPDF) -> GetDataFromPDF:
        data.extracted_data = self.extract_data(data.pdf_file, data.first_page, data.last_page)
        return data 
        

if __name__ == '__main__':
    opt = get_args()
    main(opt)
    