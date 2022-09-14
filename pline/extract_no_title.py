import cv2
from pdf2image import convert_from_path, convert_from_bytes
import pytesseract

pdf_path = '../pdf_file/bill.pdf'
images = convert_from_path(pdf_path, grayscale=True, jpegopt=True)
for img in images:
    text = pytesseract.image_to_string(img, lang='vie')[:-1]
    print(text)
