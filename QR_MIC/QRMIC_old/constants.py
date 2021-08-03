import os

"""Настройки сервера"""
host='127.0.0.1'
port = None

"""Главные пути для работы скрипта"""
main_path = os.getcwd()  

file_extension = [".xls", ".xlsx", ".doc", ".docm", ".docx", ".pdf"]
excel_extensions = [".xls", ".xlsx"]
word_extensions = [".doc", ".docm"]
pdf_extensions = [".pdf"]
logo_extensions = [".png", ".bmp", ".jpeg", ".jpg"]

path_inputfiles = f'{main_path}\\INPUT'
path_process = f'{main_path}\\PROCESS'
path_outputfiles = f'{main_path}\\OUTPUT'

"""Machine Identification Code"""

codes_dictionary = {
    "0" : [0, 1, 0, 0],
    "1" : [0, 0, 0, 1],
    "2" : [0, 0, 0, 0],
    "3" : [0, 0, 1, 0],
    "4" : [1, 1, 0, 0],
    "5" : [0, 1, 0, 1],
    "6" : [0, 1, 1, 0],
    "7" : [0, 0, 1, 1],
    "8" : [1, 0, 0, 0],
    "9" : [1, 0, 0, 1]
    }