import os

"""Настройки сервера"""
host='127.0.0.1'
port = None

"""Главные пути для работы скрипта"""
main_path = os.path.dirname(os.path.abspath(__file__))

username = "admin"
qr_data = "https://www.google.com/"

file_extension = [".xls", ".xlsx", ".doc", ".docm", ".docx", ".pdf"]
excel_extensions = [".xls", ".xlsx"]
word_extensions = [".doc", ".docm"]
docx_extension = [".docx"]
pdf_extensions = [".pdf"]
logo_extensions = [".png", ".bmp", ".jpeg", ".jpg"]

path_inputfiles = os.path.join(main_path, "data", "input")
path_process = os.path.join(main_path, "data", "process")
path_outputfiles = os.path.join(main_path, "data", "output")

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

error_message_400 = "Invalid parametr"