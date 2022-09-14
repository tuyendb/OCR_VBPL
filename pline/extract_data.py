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
    parser.add_argument('-pp', '--pdf_file', type=str, required=True)
    parser.add_argument('-fp', '--first_page', type=int, default=None)
    parser.add_argument('-lp', '--last_page', type=int, default=None)
    args = parser.parse_args()
    return args


def extract(opt):
    extract_content = {}
    check_list1 = ["Số", "Luật số"]
    check_list2 = ["NGHỊ ĐỊNH", "LUẬT", "NGHI ĐỊNH", "NGHI ĐINH"]
    check_list3 = ["Điều", "Điêu"]
    pages = Pages(opt.pdf_file, opt.first_page, opt.last_page).pages
    max_hierachy = None
    for page_id, page_img in enumerate(pages):        
        if page_id == 0:
            h, w = page_img.shape
            first_page_crop = page_img[int(h/9.5):h, 0:w]
            cv2.imwrite('./test.jpg', first_page_crop)
            try:
                page_paragr_infor = ExtractParagrsFromImg(first_page_crop).extracted_paragraphs
            except:
                path = '../saved_imgs/{}.jpg'.format(uuid.uuid4())
                cv2.imwrite(path, first_page_crop)
                new_fp_crop = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                page_paragr_infor = ExtractParagrsFromImg(new_fp_crop).extracted_paragraphs
                os.remove(path)
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
                    extract_content[considered_paragr.paragraph_content] = {}
                elif considered_paragr.paragraph_content.split(' ')[0] in check_list3 and len(rm_keys(key_ls=keys_ls)) == 0:
                    extract_content[considered_paragr.paragraph_content] = [None]
                    max_hierachy = 1
                elif considered_paragr.paragraph_content.split(' ')[0] in check_list3 and len(rm_keys(key_ls=keys_ls)) != 0:
                    if type(extract_content[rm_keys(key_ls=keys_ls)[-1]]) == dict:
                        extract_content[rm_keys(key_ls=keys_ls)[-1]][considered_paragr.paragraph_content] = [None]
                        max_hierachy = 2
                    else:
                        pass
                elif not considered_paragr.is_upper() and len(keys_ls) != 0 and keys_ls[-1] == "Topic":
                    extract_content["Topic"]["Description"] = add_to_list(
                                                                          considered_paragr, 
                                                                          extract_content["Topic"]["Description"]
                                                                          )   
                else:
                    if max_hierachy == 1:
                        if type(extract_content[keys_ls[-1]]) == list:
                            extract_content[keys_ls[-1]] = add_to_list(
                                                                    considered_paragr, 
                                                                    extract_content[keys_ls[-1]]
                                                                    )
                        else:
                            pass
                    if max_hierachy == 2:
                        key_ls2 = list(extract_content[keys_ls[-1]].keys())
                        extract_content[keys_ls[-1]][key_ls2[-1]] = add_to_list(
                                                                                considered_paragr,
                                                                                extract_content[keys_ls[-1]][key_ls2[-1]]
                                                                                )
        else:
            try:
                page_paragr_infor = ExtractParagrsFromImg(page_img).extracted_paragraphs
            except:
                path = '../saved_imgs/{}.jpg'.format(uuid.uuid4())
                cv2.imwrite(path, page_img)
                new_img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                page_paragr_infor = ExtractParagrsFromImg(new_img).extracted_paragraphs
                os.remove(path)
            for paragr_infor in page_paragr_infor:
                considered_paragr = Paragraph(page_img, paragr_infor)
                keys_ls = list(extract_content.keys()) 
                if considered_paragr.is_upper():
                    extract_content[considered_paragr.paragraph_content] = {}
                elif considered_paragr.paragraph_content.split(' ')[0] in check_list3 and len(rm_keys(key_ls=keys_ls)) == 0:
                    extract_content[considered_paragr.paragraph_content] = [None]
                    max_hierachy = 1
                elif considered_paragr.paragraph_content.split(' ')[0] in check_list3 and len(rm_keys(key_ls=keys_ls)) != 0:
                    if type(extract_content[rm_keys(key_ls=keys_ls)[-1]]) == dict:
                        extract_content[rm_keys(key_ls=keys_ls)[-1]][considered_paragr.paragraph_content] = [None]
                        max_hierachy = 2
                    else:
                        extract_content[considered_paragr.paragraph_content] = [None]
                        max_hierachy = 1
                else:
                    if max_hierachy == 1:
                        if type(extract_content[keys_ls[-1]]) == list:
                            extract_content[keys_ls[-1]] = add_to_list(
                                                                    considered_paragr, 
                                                                    extract_content[keys_ls[-1]]
                                                                    )
                        else:
                            pass
                    if max_hierachy == 2:
                        print(keys_ls)
                        key_ls2 = list(extract_content[keys_ls[-1]].keys())
                        print(key_ls2)
                        print('...........................')
                        extract_content[keys_ls[-1]][key_ls2[-1]] = add_to_list(
                                                                                considered_paragr, 
                                                                                extract_content[keys_ls[-1]][key_ls2[-1]]
                                                                               )
    keys_ls = list(extract_content.keys())
    for key in keys_ls:
        if not bool(extract_content[key]):
            del extract_content[key]
    json.dump(extract_content, open('../extracted_data/1.json', 'w', encoding='utf-8'), ensure_ascii=False)
    
    
if __name__ == '__main__':
    opt = get_args()
    extract(opt)
    