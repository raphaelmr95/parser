import json
from bs4 import BeautifulSoup

class ReadFactory:
    def __init__(self):
        pass

    @staticmethod
    def read_file(file_name):
        if file_name.endswith('.xml'):
            return ReadXml()


class ReadXml(ReadFactory):
    def __init__(self):
        pass

    def read_file(self, file_name):
        soup = BeautifulSoup(file_name, 'lxml')
        return soup
