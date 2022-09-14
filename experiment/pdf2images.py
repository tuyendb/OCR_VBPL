from pdf2image import convert_from_path
import os


def pdf2jpg(path, pdf_path):
    if os.path.exists(path):
        pass
    else:
        os.mkdir(path)
    images = convert_from_path(pdf_path, grayscale=True, jpegopt=True)
    for i, image in enumerate(images):
        fname = os.path.join(path,'vbg_'+str(i)+'.jpg')
        image.save(fname, "JPEG")


if __name__ == "__main__":
    path = '../pdf_file/2'
    pdf_path = path + '.pdf'
    pdf2jpg(path, pdf_path)
