import os
import cv2
import argparse
import uuid
import sys
import json
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from utils.utils import ExtractParagrsFromImg, rm_keys, add_to_list
from objects.pages import Pages
from objects.paragraph import Paragraph
from support_module.spell_correct import spelling_correct


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pd', '--pdf_dir', type=str, required=True)
    parser.add_argument('-fp', '--first_page', type=int, default=None)
    parser.add_argument('-lp', '--last_page', type=int, default=None)
    args = parser.parse_args()
    return args


def extract(pdf_path, first_page, last_page):
    pdf_name = pdf_path.split('/')[-1][:-4]
    extract_content = {}
    check_list1 = ["Số", "Luật số"]
    check_list2 = ["NGHỊ ĐỊNH", "LUẬT", "NGHI ĐỊNH", "NGHI ĐINH"]
    check_list3 = ["Điều", "Điêu"]
    pages = Pages(pdf_path, first_page, last_page).pages
    for page_id, page_img in enumerate(pages):        
        if page_id == 0:
            h, w = page_img.shape
            first_page_crop = page_img[int(h/9.5):h, 0:w]
            cv2.imwrite('./test.jpg', first_page_crop)
            page_paragr_infor = ExtractParagrsFromImg(first_page_crop).extracted_paragraphs
            for paragr_infor in page_paragr_infor:
                considered_paragr = Paragraph(first_page_crop, paragr_infor)
                keys_ls = list(extract_content.keys())
                if "Number" not in keys_ls:
                    flag1 = False
                    for check1 in check_list1:
                        if check1 in considered_paragr.paragraph_content[:9]:
                            extract_content['Number'] = considered_paragr.paragraph_content
                            flag1 = True
                            break
                    if flag1:
                        continue
                if "Topic" not in keys_ls:
                    flag2 = False     
                    for check2 in check_list2:
                        if check2 in considered_paragr.paragraph_content[:10]:
                            extract_content["Topic"] = {
                                "Name": considered_paragr.paragraph_content,
                                "Description" : [None]
                            }
                            flag2 = True
                            break
                if flag1 or flag2:
                    flag1 = flag2 = False
                    continue
                if considered_paragr.is_upper():
                    extract_content[considered_paragr.paragraph_content] = [None]
                elif considered_paragr.paragraph_content.split(' ')[0] in check_list3:
                    extract_content[considered_paragr.paragraph_content] = [None]
                else:
                    necessary_keys = rm_keys(keys_ls)
                    if len(necessary_keys) == 0:
                        pass
                    else:
                        extract_content[necessary_keys[-1]] = add_to_list(considered_paragr, extract_content[necessary_keys[-1]])
        else:
            cv2.imwrite('2.jpg', page_img)
            page_paragr_infor = ExtractParagrsFromImg(page_img).extracted_paragraphs
            for paragr_infor in page_paragr_infor:
                considered_paragr = Paragraph(page_img, paragr_infor)
                keys_ls = list(extract_content.keys())
                if considered_paragr.is_upper():
                    extract_content[considered_paragr.paragraph_content] = [None]
                elif considered_paragr.paragraph_content.split(' ')[0] in check_list3:
                    extract_content[considered_paragr.paragraph_content] = [None]
                else:
                    necessary_keys = rm_keys(keys_ls)
                    if len(necessary_keys) == 0:
                        pass
                    else:
                        extract_content[necessary_keys[-1]] = add_to_list(considered_paragr, extract_content[necessary_keys[-1]])
    keys_ls = list(extract_content.keys())
    for key in keys_ls:
        if not bool(extract_content[key]):
            del extract_content[key]
    json.dump(extract_content, open('../extracted_data/{}.json'.format(pdf_name), 'w', encoding='utf-8'), ensure_ascii=False)
    

if __name__ == '__main__':
    opt = get_args()
    pdf_files = [f for f in os.listdir(opt.pdf_dir) if f.find('.pdf') != -1]
    for pdf_file in pdf_files[:10]:
        pdf_path = os.path.join(opt.pdf_dir, pdf_file)
        extract(pdf_path, opt.first_page, opt.last_page)
    