import os
import sys
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from apis.routes.base_route import BaseRoute
from objects.data_request import GetDataFromPDF
from pline.pipeline import ExtractDataFromPDF
from fastapi import File, Form


class ManualRoute(BaseRoute):
    def __init__(self):
        super(ManualRoute, self).__init__(prefix="/getdata")
        self.pipeline = ExtractDataFromPDF()

    def create_routes(self):
        router = self.router

        @router.get("/")
        def get_data(pdf_file: bytes = File(), first_page=Form(...), last_page=Form(...)):
            data = GetDataFromPDF(pdf_file, int(first_page), int(last_page))
            data = self.pipeline(data)
            return data.extracted_data

        @router.get("/fullbook")
        def get_data2(pdf_file: bytes = File()):
            data = GetDataFromPDF(pdf_file, None, None)
            data = self.pipeline(data)
            return data.extracted_data
        