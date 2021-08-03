# -*- coding: utf-8 -*-
'''
import db

import os
import json
import math
import time
import flask
import shutil
import random
import qrcode
import img2pdf
import datetime
import pythoncom
import win32com.client as win32

from PIL import Image
from docx import Document
from win32com import client
from datetime import datetime
from flask_restful import Api
from docx.shared import Inches
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from werkzeug.utils import secure_filename
from pdf2image import pdfinfo_from_path,convert_from_path
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
'''
import os
import qr
import mic
import qrcode
import constants
import converters

from multiprocessing import Value
from flask import Flask, request, send_from_directory, redirect, url_for



#--------------------------------------------------------------
#-----------------------Константы------------------------------
#--------------------------------------------------------------

"""Главный запуск Flask"""
app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['UPLOAD_FOLDER'] = constants.path_outputfiles

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Счетчик запросов 
counter = Value('i', 0)



#--------------------------------------------------------------
#-----------------------------API------------------------------
#--------------------------------------------------------------

@app.route('/file_constructor', methods=['POST'])
def file_constructor():
    username = "KMA"

    with counter.get_lock():
        counter.value += 1

    if not os.path.exists(f"{constants.path_inputfiles}\\{username}\\{counter.value}"):
        os.makedirs(f"{constants.path_inputfiles}\\{username}\\{counter.value}")

    if not os.path.exists(f"{constants.path_process}\\{username}\\{counter.value}\\pages"):
        os.makedirs(f"{constants.path_process}\\{username}\\{counter.value}\\pages")

    """Работа с QR"""
    #Логотип
    if request.files.get('qr_logo') is not None:
        qr_logo = request.files['qr_logo']
        if os.path.splitext(qr_logo.filename)[1] in constants.logo_extensions:
            qr_logo.save(os.path.join(f"{constants.path_inputfiles}\\{username}\\{counter.value}", qr_logo.filename))
            logo_filename = str(qr_logo.filename)      
        else:
            return "Invalid qr_logo", 400
    else:
        logo_filename = None

    #Информация в QR
    if request.args.get('qr_data') is not None:
        attempt = request.args['qr_data']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_data = str(attempt)
        else:
            return "Invalid qr_data", 400
    else:
        qr_data = "https://www.metalloinvest.com/"

    #Основной цвет QR
    if request.args.get('qr_rgb') is not None:
        verifiable = request.args['qr_rgb'][1:-1].split(',')
        
        try:
            attempt = list(map(int, verifiable))
        
        except ValueError:
            return "Invalid qr_rgb", 400
        
        if (isinstance(attempt, list) or isinstance(attempt, tuple)) and len(attempt) == 3:
            for color in attempt:
                if isinstance(color, int) and color <= 255 and color >= 0:
                    continue
                else:
                    return "Invalid qr_rgb", 400
        else:
            return "Invalid qr_rgb", 400

        qr_rgb = tuple(attempt)

    else:
        qr_rgb = (0, 0, 0)

    #Версия QR
    if request.args.get('qr_version') is not None:
        attempt = request.args['qr_version']
        try:
            if isinstance(int(attempt), int) or isinstance(attempt, str):
                qr_version = int(attempt)
                if qr_version < 1 and qr_version > 40:
                    return "Invalid qr_version", 400
            else:
                return "Invalid qr_version", 400
        except ValueError:
            return "Invalid qr_version", 400
    else:
        qr_version = 4 

    #Рамка
    if request.args.get('qr_border') is not None:
        attempt = request.args['qr_border']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_border = int(attempt)
        else:
            return "Invalid qr_border", 400
    else:
        qr_border = 0   

    #Градиент
    if request.args.get('qr_rgb_gradient') is not None:
        verifiable = request.args['qr_rgb_gradient'][1:-1].split(',')
        try:
            attempt = list(map(int, verifiable))
        except ValueError:
            return "Invalid qr_rgb_gradient", 400
        if (isinstance(attempt, list) or isinstance(attempt, tuple)) and len(attempt) == 3:
            for color in attempt:
                if isinstance(color, int) and color <= 255 and color >= 0:
                    continue
                else:
                    break
        else:
            return "Invalid qr_rgb_gradient", 400
        
        qr_rgb_gradient = tuple(attempt)
    
    else:
        qr_rgb_gradient = None

    #Настройка корректировка ошибки
    if request.args.get('qr_logo_size') is not None:
        attempt = request.args['qr_logo_size']
        try:
            if isinstance(int(attempt), int):
                qr_logo_size = int(attempt)
                if qr_logo_size >= 0 and qr_logo_size <= 7:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_L

                elif qr_logo_size > 7 and qr_logo_size <= 15:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_Q
            
                elif qr_logo_size > 15 and qr_logo_size <= 25:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_Q
            
                elif qr_logo_size > 25 and qr_logo_size <= 30:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_H

                else:
                    return "Invalid qr_logo_size", 400
            else:
                return "Invalid qr_logo_size", 400
        except ValueError:
            return "Invalid qr_logo_size", 400
    else:
        qr_logo_size = 0
        qr_error_correct = qrcode.constants.ERROR_CORRECT_L

    #Размер QR
    if request.args.get('qr_box_size') is not None:
        attempt = request.args['qr_box_size']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_box_size = int(attempt)
        else:
            return "Invalid qr_box_size", 400
    else:
        qr_box_size = 10

    resp = qr.create(
        logo_filename,
        qr_data,
        qr_rgb,
        qr_rgb_gradient,
        qr_version,
        qr_border,
        qr_box_size,
        qr_logo_size,
        qr_error_correct,
        counter.value,
        "KMA"
        )
    
    path_qr = os.path.join(resp[0], resp[1])

    """Работа с файлами"""
    #Основной файл
    if request.files.get('file') is not None:
        docum = request.files['file']
        if str(os.path.splitext(docum.filename)[1]) in constants.file_extension:
            docum.save(os.path.join(f"{constants.path_inputfiles}\\{username}\\{counter.value}", docum.filename))
            file_filename = docum.filename
        else:
            return "Invalid incoming file", 400
    else:
        return "Invalid incoming file", 400

    #dpi файла
    if request.args.get('file_dpi') is not None:
        attempt = request.args['file_dpi']
        if isinstance(attempt, int) or isinstance(attempt, str):
            file_dpi = int(attempt)
        else:
            return "Invalid file_dpi", 400
    else:
        file_dpi = 400 
    
    #Размер QR в дюймах для Word Office
    if request.args.get(f'qr_inches') is not None:
        try:
            attempt = tuple(map(float, request.args[f'qr_inches'][1:-1].split(',')))       
        except ValueError:
            return "Invalid qr_inches", 400
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue
                else:
                    return "Invalid qr_inches", 400            
            else:
                qr_inches = tuple(attempt)
        else:
            return "Invalid qr_inches", 400
    else:
        qr_inches = (0.5, 0.5)

    #qr_box
    if request.args.get(f'qr_box') is not None:
        try:
            attempt = tuple(map(int, request.args['qr_box'][1:-1].split(',')))         
        except ValueError:
            return "Invalid qr_box", 400       
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue                
                else:
                    return "Invalid qr_inches", 400                        
            else:
                qr_box = tuple(attempt)
        else:
            return "Invalid qr_box", 400
    else:
        qr_box = None

    """Machine Identification Code"""
        #Шифруемый 6-значный код
    if request.args.get('mic_data') is not None:
        attempt = request.args['mic_data']
        if isinstance(attempt, int) or isinstance(attempt, str):
            mic_data = int(attempt)
        else:
            return "Invalid mic_data", 400
    else:
        return "Invalid mic_data", 400

    #Основной цвет MIC
    if request.args.get('mic_rgb') is not None:
        verifiable = request.args['mic_rgb'][1:-1].split(',')       
        try:
            attempt = list(map(int, verifiable))       
        except ValueError:
            return "Invalid mic_rgb", 400
        if (isinstance(attempt, list) or isinstance(attempt, tuple)) and len(attempt) == 3:
            for color in attempt:
                if isinstance(color, int) and color <= 255 and color >= 0:
                    continue
                else:
                    return "Invalid mic_rgb", 400
            else:
                mic_rgb = tuple(attempt)
        else:
            return "Invalid mic_rgb", 400
    else:
        mic_rgb = (255, 255, 102) 

    #Толщина точки
    if request.args.get('mic_thickness') is not None:
        attempt = request.args['mic_thickness']
        if isinstance(attempt, int) or isinstance(attempt, str):
            mic_thickness = int(attempt)
        else:
            return "Invalid mic_thickness", 400
    else:
        mic_thickness = 1

    #Размер QR в дюймах для Word Office
    if request.args.get(f'mic_interval') is not None:
        try:
            attempt = tuple(map(int, request.args[f'mic_interval'][1:-1].split(',')))       
        except ValueError:
            return "Invalid mic_interval", 400
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue
                else:
                    return "Invalid mic_interval", 400            
            else:
                mic_interval = tuple(attempt)
        else:
            return "Invalid mic_interval", 400
    else:
        mic_interval = (25, 25)

    #Левый верхний угол MIC
    if request.args.get(f'mic_box') is not None:
        try:
            attempt = tuple(map(int, request.args[f'mic_box'][1:-1].split(',')))       
        except ValueError:
            return "Invalid mic_box", 400
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue
                else:
                    return "Invalid mic_box", 400            
            else:
                mic_box = tuple(attempt)
        else:
            return "Invalid mic_box", 400
    else:
        mic_box = (25, 25)

    filename = os.path.splitext(file_filename)[0]
    extension = os.path.splitext(file_filename)[1].lower()

    if extension == ".docx":            #docx -> qr -> pdf -> mic
        qr.add_to_office(
            filename, 
            path_qr,
            qr_inches,
            f"{constants.path_inputfiles}\\{username}\\{counter.value}", 
            f"{constants.path_process}\\{username}\\{counter.value}"       
            )
        converters.word_to_pdf(
            filename, 
            extension,
            f"{constants.path_process}\\{username}\\{counter.value}", 
            f"{constants.path_process}\\{username}\\{counter.value}"
            )
        mic.add_to_pdf(
            mic_data,
            mic_interval,
            mic_box,
            file_dpi,
            mic_rgb,
            filename,
            f"{constants.path_process}\\{username}\\{counter.value}",
            constants.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    elif extension in constants.word_extensions:  #word -> docx -> qr -> pdf -> mic
        converters.word_converter(
                filename, 
                extension, 
                f"{constants.path_inputfiles}\\{username}\\{counter.value}", 
                f"{constants.path_process}\\{username}\\{counter.value}"
                )
        qr.add_to_office(
            filename, 
            path_qr,
            qr_inches,
            f"{constants.path_process}\\{username}\\{counter.value}", 
            f"{constants.path_process}\\{username}\\{counter.value}"     
            )
        converters.word_to_pdf(
            filename, 
            ".docx",
            f"{constants.path_process}\\{username}\\{counter.value}", 
            f"{constants.path_process}\\{username}\\{counter.value}"
            )
        mic.add_to_pdf(
            mic_data,
            mic_interval,
            mic_box,
            file_dpi,
            mic_rgb,
            filename,
            f"{constants.path_process}\\{username}\\{counter.value}",
            constants.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")
        
    elif extension in constants.excel_extensions: #excel -> pdf -> png -> qr -> mic -> pdf
        converters.excel_converter(
                    filename, 
                    extension, 
                    f"{constants.path_inputfiles}\\{username}\\{counter.value}", 
                    f"{constants.path_process}\\{username}\\{counter.value}"
                    )
        converters.pdf_converter(
                filename, 
                extension,
                file_dpi,
                f"{constants.path_process}\\{username}\\{counter.value}", 
                f"{constants.path_process}\\{username}\\{counter.value}\\pages",               
                )
        qr.add_to_pdf(
            filename,
            path_qr, 
            qr_box,
            f"{constants.path_process}\\{username}\\{counter.value}\\pages",
            f"{constants.path_process}\\{username}\\{counter.value}\\pages"
            )
        converters.png_converter(
                filename,
                f"{constants.path_process}\\{username}\\{counter.value}\\pages",
                f"{constants.path_process}\\{username}\\{counter.value}\\pages"
                )
        mic.add_to_pdf(
            mic_data,
            mic_interval,
            mic_box,
            file_dpi,
            mic_rgb,
            filename,
            f"{constants.path_process}\\{username}\\{counter.value}",
            constants.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    elif extension in constants.pdf_extensions:   #pdf -> jpg -> qr -> jpg -> pdf
        converters.pdf_converter(
                filename, 
                extension,
                file_dpi,
                f"{constants.path_inputfiles}\\{username}\\{counter.value}", 
                f"{constants.path_process}\\{username}\\{counter.value}\\pages",               
                )
        qr.add_to_pdf(
            filename,
            path_qr, 
            qr_box,
            f"{constants.path_process}\\{username}\\{counter.value}\\pages",
            f"{constants.path_process}\\{username}\\{counter.value}\\pages"
            )
        converters.png_converter(
                filename,
                f"{constants.path_process}\\{username}\\{counter.value}\\pages",
                f"{constants.path_process}\\{username}\\{counter.value}"
                )
        mic.add_to_pdf(
            mic_data,
            mic_interval,
            mic_box,
            file_dpi,
            mic_rgb,
            filename,
            f"{constants.path_process}\\{username}\\{counter.value}",
            constants.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    else:
        return "Invalid file", 400

@app.route('/mic_constructor', methods=['POST'])
def mic_constructor():
    username = "KMA"
    with counter.get_lock():
        counter.value += 1
 
    if not os.path.exists(f"{constants.path_inputfiles}\\{username}\\{counter.value}"):
        os.makedirs(f"{constants.path_inputfiles}\\{username}\\{counter.value}")

    if not os.path.exists(f"{constants.path_process}\\{username}\\{counter.value}\\pages"):
        os.makedirs(f"{constants.path_process}\\{username}\\{counter.value}\\pages")

    #Основной файл
    if request.files.get('file') is not None:
        docum = request.files['file']
        if str(os.path.splitext(docum.filename)[1]) in constants.file_extension:
            docum.save(os.path.join(f"{constants.path_inputfiles}\\{username}\\{counter.value}", docum.filename))
            file_filename = docum.filename
        else:
            return "Invalid incoming file", 400
    else:
        return "Incoming file is empty", 400

    #Шифруемый 6-значный код
    if request.args.get('mic_data') is not None:
        attempt = request.args['mic_data']
        if isinstance(attempt, int) or isinstance(attempt, str):
            mic_data = int(attempt)
        else:
            return "Invalid mic_data", 400
    else:
        return "Invalid mic_data", 400

    #Основной цвет MIC
    if request.args.get('mic_rgb') is not None:
        verifiable = request.args['mic_rgb'][1:-1].split(',')       
        try:
            attempt = list(map(int, verifiable))       
        except ValueError:
            return "Invalid mic_rgb", 400
        if (isinstance(attempt, list) or isinstance(attempt, tuple)) and len(attempt) == 3:
            for color in attempt:
                if isinstance(color, int) and color <= 255 and color >= 0:
                    continue
                else:
                    return "Invalid mic_rgb", 400
            else:
                mic_rgb = tuple(attempt)
        else:
            return "Invalid mic_rgb", 400
    else:
        mic_rgb = (255, 255, 102) 

    #dpi файла для проставления MIC
    if request.args.get('file_dpi') is not None:
        attempt = request.args['file_dpi']
        if isinstance(attempt, int) or isinstance(attempt, str):
            file_dpi = int(attempt)
        else:
            return "Invalid file_dpi", 400
    else:
        file_dpi = 400

    #Толщина точки
    if request.args.get('mic_thickness') is not None:
        attempt = request.args['mic_thickness']
        if isinstance(attempt, int) or isinstance(attempt, str):
            mic_thickness = int(attempt)
        else:
            return "Invalid mic_thickness", 400
    else:
        mic_thickness = 1

    #Размер QR в дюймах для Word Office
    if request.args.get(f'mic_interval') is not None:
        try:
            attempt = tuple(map(int, request.args[f'mic_interval'][1:-1].split(',')))       
        except ValueError:
            return "Invalid mic_interval", 400
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue
                else:
                    return "Invalid mic_interval", 400            
            else:
                mic_interval = tuple(attempt)
        else:
            return "Invalid mic_interval", 400
    else:
        mic_interval = (25, 25)

    #Левый верхний угол MIC
    if request.args.get(f'mic_box') is not None:
        try:
            attempt = tuple(map(int, request.args[f'mic_box'][1:-1].split(',')))       
        except ValueError:
            return "Invalid mic_box", 400
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue
                else:
                    return "Invalid mic_box", 400            
            else:
                mic_box = tuple(attempt)
        else:
            return "Invalid mic_box", 400
    else:
        mic_box = (25, 25)

    filename = os.path.splitext(file_filename)[0]
    extension = os.path.splitext(file_filename)[1].lower()

    if extension == ".docx":            #docx -> pdf -> mic
        converters.word_to_pdf(
            filename, 
            extension,
            f"{constants.path_inputfiles}\\{username}\\{counter.value}", 
            f"{constants.path_process}\\{username}\\{counter.value}"
            )
        mic.add_to_pdf(
            mic_data,
            mic_interval,
            mic_box,
            file_dpi,
            mic_rgb,
            filename,
            f"{constants.path_process}\\{username}\\{counter.value}",
            f"{constants.path_process}\\{username}\\{counter.value}"
            )
        converters.word_to_pdf(
            filename, 
            extension,
            f"{constants.path_process}\\{username}\\{counter.value}", 
            constants.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    elif extension in constants.word_extensions:  #word -> pdf -> mic
        converters.word_to_pdf(
            filename, 
            extension,
            f"{constants.path_inputfiles}\\{username}\\{counter.value}", 
            f"{constants.path_process}\\{username}\\{counter.value}"
            )
        mic.add_to_pdf(
            mic_data,
            mic_interval,
            mic_box,
            file_dpi,
            mic_rgb,
            filename,
            f"{constants.path_process}\\{username}\\{counter.value}",
            constants.path_outputfiles
            )
        converters.word_to_pdf(
            filename, 
            extension,
            f"{constants.path_process}\\{username}\\{counter.value}", 
            constants.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")
        
    elif extension in constants.excel_extensions: #excel -> pdf -> mic
        converters.excel_converter(
                    filename, 
                    extension, 
                    f"{constants.path_inputfiles}\\{username}\\{counter.value}", 
                    f"{constants.path_process}\\{username}\\{counter.value}"
                    )
        mic.add_to_pdf(
            mic_data,
            mic_interval,
            mic_box,
            file_dpi,
            mic_rgb,
            filename,
            f"{constants.path_process}\\{username}\\{counter.value}",
            constants.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    elif extension in constants.pdf_extensions:   #pdf -> mic
        mic.add_to_pdf(
            mic_data,
            mic_interval,
            mic_box,
            file_dpi,
            mic_rgb,
            filename,
            f"{constants.path_inputfiles}\\{username}\\{counter.value}",
            constants.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    else:
        return "Invalid file", 400

@app.route('/qr_constructor', methods=['POST'])
def qr_constructor():
    username = "KMA"
    with counter.get_lock():
        counter.value += 1

    if not os.path.exists(f"{constants.path_inputfiles}\\{username}\\{counter.value}"):
        os.makedirs(f"{constants.path_inputfiles}\\{username}\\{counter.value}")

    if not os.path.exists(f"{constants.path_process}\\{username}\\{counter.value}\\pages"):
        os.makedirs(f"{constants.path_process}\\{username}\\{counter.value}\\pages")
        

    """Работа с QR"""

    #Логотип
    if request.files.get('qr_logo') is not None:
        qr_logo = request.files['qr_logo']
        if os.path.splitext(qr_logo.filename)[1] in constants.logo_extensions:
            qr_logo.save(os.path.join(f"{constants.path_inputfiles}\\{username}\\{counter.value}", qr_logo.filename))
            logo_filename = str(qr_logo.filename)      
        else:
            return "Invalid qr_data", 400
    else:
        logo_filename = None

    #Информация в QR
    if request.args.get('qr_data') is not None:
        attempt = request.args['qr_data']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_data = str(attempt)
        else:
            return "Invalid qr_data", 400
    else:
        qr_data = "https://www.metalloinvest.com/"

    #Основной цвет QR
    if request.args.get('qr_rgb') is not None:
        verifiable = request.args['qr_rgb'][1:-1].split(',')
        
        try:
            attempt = list(map(int, verifiable))
        
        except ValueError:
            return "Invalid qr_rgb", 400
        
        if (isinstance(attempt, list) or isinstance(attempt, tuple)) and len(attempt) == 3:
            for color in attempt:
                if isinstance(color, int) and color <= 255 and color >= 0:
                    continue
                else:
                    return "Invalid qr_rgb", 400
        else:
            return "Invalid qr_rgb", 400

        qr_rgb = tuple(attempt)

    else:
        qr_rgb = (0, 0, 0)

    #Версия QR
    if request.args.get('qr_version') is not None:
        attempt = request.args['qr_version']
        try:
            if isinstance(int(attempt), int) or isinstance(attempt, str):
                qr_version = int(attempt)
                if qr_version < 1 and qr_version > 40:
                    return "Invalid qr_version", 400
            else:
                return "Invalid qr_version", 400
        except ValueError:
            return "Invalid qr_version", 400
    else:
        qr_version = 4 

    #Рамка
    if request.args.get('qr_border') is not None:
        attempt = request.args['qr_border']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_border = int(attempt)
        else:
            return "Invalid qr_border", 400
    else:
        qr_border = 0   

    #Градиент
    if request.args.get('qr_rgb_gradient') is not None:
        verifiable = request.args['qr_rgb_gradient'][1:-1].split(',')
        try:
            attempt = list(map(int, verifiable))
        except ValueError:
            return "Invalid qr_rgb_gradient", 400
        if (isinstance(attempt, list) or isinstance(attempt, tuple)) and len(attempt) == 3:
            for color in attempt:
                if isinstance(color, int) and color <= 255 and color >= 0:
                    continue
                else:
                    break
        else:
            return "Invalid qr_rgb_gradient", 400
        
        qr_rgb_gradient = tuple(attempt)
    
    else:
        qr_rgb_gradient = None

    #Настройка корректировка ошибки
    if request.args.get('qr_logo_size') is not None:
        attempt = request.args['qr_logo_size']
        try:
            if isinstance(int(attempt), int):
                qr_logo_size = int(attempt)
                if qr_logo_size >= 0 and qr_logo_size <= 7:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_L

                elif qr_logo_size > 7 and qr_logo_size <= 15:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_Q
            
                elif qr_logo_size > 15 and qr_logo_size <= 25:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_Q
            
                elif qr_logo_size > 25 and qr_logo_size <= 30:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_H

                else:
                    return "Invalid qr_logo_size", 400
            else:
                return "Invalid qr_logo_size", 400
        except ValueError:
            return "Invalid qr_logo_size", 400
    else:
        qr_logo_size = 0
        qr_error_correct = qrcode.constants.ERROR_CORRECT_L

    #Размер QR
    if request.args.get('qr_box_size') is not None:
        attempt = request.args['qr_box_size']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_box_size = int(attempt)
        else:
            return "Invalid qr_box_size", 400
    else:
        qr_box_size = 10

    resp = qr.create(
        logo_filename,
        qr_data,
        qr_rgb,
        qr_rgb_gradient,
        qr_version,
        qr_border,
        qr_box_size,
        qr_logo_size,
        qr_error_correct,
        counter.value,
        "KMA"
        )
    
    path_qr = os.path.join(resp[0], resp[1])

    """Работа с файлами"""
    #Основной файл
    if request.files.get('file') is not None:
        docum = request.files['file']
        if str(os.path.splitext(docum.filename)[1]) in constants.file_extension:
            docum.save(os.path.join(f"{constants.path_inputfiles}\\{username}\\{counter.value}", docum.filename))
            file_filename = docum.filename
        else:
            return "Invalid incoming file", 400
    else:
        return "Invalid incoming file", 400

    #dpi файла
    if request.args.get('file_dpi') is not None:
        attempt = request.args['file_dpi']
        if isinstance(attempt, int) or isinstance(attempt, str):
            file_dpi = int(attempt)
        else:
            return "Invalid file_dpi", 400
    else:
        file_dpi = 400 
    
    #Размер QR в дюймах для Word Office
    if request.args.get(f'qr_inches') is not None:
        try:
            attempt = tuple(map(float, request.args[f'qr_inches'][1:-1].split(',')))       
        except ValueError:
            return "Invalid qr_inches", 400
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue
                else:
                    return "Invalid qr_inches", 400            
            else:
                qr_inches = tuple(attempt)
        else:
            return "Invalid qr_inches", 400
    else:
        qr_inches = (0.5, 0.5)

    #qr_box
    if request.args.get(f'qr_box') is not None:
        try:
            attempt = tuple(map(int, request.args['qr_box'][1:-1].split(',')))         
        except ValueError:
            return "Invalid qr_box", 400       
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue                
                else:
                    return "Invalid qr_inches", 400                        
            else:
                qr_box = tuple(attempt)
        else:
            return "Invalid qr_box", 400
    else:
        qr_box = None

    filename = os.path.splitext(file_filename)[0]
    extension = os.path.splitext(file_filename)[1].lower()

    if extension == ".docx":            #docx -> qr -> docx
        qr.add_to_office(
            filename, 
            path_qr,
            qr_inches,
            f"{constants.path_inputfiles}\\{username}\\{counter.value}", 
            constants.path_outputfiles       
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.docx")

    elif extension in constants.word_extensions:  #word -> docx -> qr -> docx -> word
        converters.word_converter(
                filename, 
                extension, 
                f"{constants.path_inputfiles}\\{username}\\{counter.value}", 
                f"{constants.path_process}\\{username}\\{counter.value}"
                )
        qr.add_to_office(
            filename, 
            path_qr,
            qr_inches,
            f"{constants.path_process}\\{username}\\{counter.value}", 
            f"{constants.path_process}\\{username}\\{counter.value}"     
            )
        converters.word_deconverter(
                filename, 
                extension, 
                f"{constants.path_process}\\{username}\\{counter.value}", 
                constants.path_outputfiles
                )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}{extension}")
        
    elif extension in constants.excel_extensions: #excel -> pdf -> jpg -> qr -> jpg -> pdf
        converters.excel_converter(
                    filename, 
                    extension, 
                    f"{constants.path_inputfiles}\\{username}\\{counter.value}", 
                    f"{constants.path_process}\\{username}\\{counter.value}"
                    )
        converters.pdf_converter(
                filename, 
                extension,
                file_dpi,
                f"{constants.path_process}\\{username}\\{counter.value}", 
                f"{constants.path_process}\\{username}\\{counter.value}\\pages",               
                )
        qr.add_to_pdf(
            filename,
            path_qr, 
            qr_box,
            f"{constants.path_process}\\{username}\\{counter.value}\\pages",
            f"{constants.path_process}\\{username}\\{counter.value}\\pages"
            )
        converters.png_converter(
                filename,
                f"{constants.path_process}\\{username}\\{counter.value}\\pages",
                constants.path_outputfiles
                )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    elif extension in constants.pdf_extensions:   #pdf -> jpg -> qr -> jpg -> pdf
        converters.pdf_converter(
                filename, 
                extension,
                file_dpi,
                f"{constants.path_inputfiles}\\{username}\\{counter.value}", 
                f"{constants.path_process}\\{username}\\{counter.value}\\pages",               
                )
        qr.add_to_pdf(
            filename,
            path_qr, 
            qr_box,
            f"{constants.path_process}\\{username}\\{counter.value}\\pages",
            f"{constants.path_process}\\{username}\\{counter.value}\\pages"
            )
        converters.png_converter(
                filename,
                f"{constants.path_process}\\{username}\\{counter.value}\\pages",
                constants.path_outputfiles
                )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    else:
        return "Invalid file", 400

@app.route('/qr_create', methods=['POST'])
def qr_create():
    username = "KMA"

    with counter.get_lock():
        counter.value += 1

    #Логотип
    if request.files.get('qr_logo') is not None:
        qr_logo = request.files['qr_logo']
        if os.path.splitext(qr_logo.filename)[1] in constants.logo_extensions:
            qr_logo.save(os.path.join(f"{constants.path_inputfiles}\\{username}\\{counter.value}", qr_logo.filename))
            logo_filename = str(qr_logo.filename)      
        else:
            return "Invalid qr_logo", 400
    else:
        logo_filename = None

    #Информация в QR
    if request.args.get('qr_data') is not None:
        attempt = request.args['qr_data']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_data = str(attempt)
        else:
            return "Invalid qr_data", 400
    else:
        qr_data = "https://www.metalloinvest.com/"

    #Основной цвет QR
    if request.args.get('qr_rgb') is not None:
        verifiable = request.args['qr_rgb'][1:-1].split(',')
        
        try:
            attempt = list(map(int, verifiable))
        
        except ValueError:
            return "Invalid qr_rgb", 400
        
        if (isinstance(attempt, list) or isinstance(attempt, tuple)) and len(attempt) == 3:
            for color in attempt:
                if isinstance(color, int) and color <= 255 and color >= 0:
                    continue
                else:
                    return "Invalid qr_rgb", 400
        else:
            return "Invalid qr_rgb", 400

        qr_rgb = tuple(attempt)

    else:
        qr_rgb = (0, 0, 0)

    #Версия QR
    if request.args.get('qr_version') is not None:
        attempt = request.args['qr_version']
        try:
            if isinstance(int(attempt), int) or isinstance(attempt, str):
                qr_version = int(attempt)
                if qr_version < 1 and qr_version > 40:
                    return "Invalid qr_version", 400
            else:
                return "Invalid qr_version", 400
        except ValueError:
            return "Invalid qr_version", 400
    else:
        qr_version = 4 

    #Рамка
    if request.args.get('qr_border') is not None:
        attempt = request.args['qr_border']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_border = int(attempt)
        else:
            return "Invalid qr_border", 400
    else:
        qr_border = 0   

    #Градиент
    if request.args.get('qr_rgb_gradient') is not None:
        verifiable = request.args['qr_rgb_gradient'][1:-1].split(',')
        try:
            attempt = list(map(int, verifiable))
        except ValueError:
            return "Invalid qr_rgb_gradient", 400
        if (isinstance(attempt, list) or isinstance(attempt, tuple)) and len(attempt) == 3:
            for color in attempt:
                if isinstance(color, int) and color <= 255 and color >= 0:
                    continue
                else:
                    break
        else:
            return "Invalid qr_rgb_gradient", 400
        
        qr_rgb_gradient = tuple(attempt)
    
    else:
        qr_rgb_gradient = None

    #Настройка корректировка ошибки
    if request.args.get('qr_logo_size') is not None:
        attempt = request.args['qr_logo_size']
        try:
            if isinstance(int(attempt), int):
                qr_logo_size = int(attempt)
                if qr_logo_size >= 0 and qr_logo_size <= 7:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_L

                elif qr_logo_size > 7 and qr_logo_size <= 15:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_Q
            
                elif qr_logo_size > 15 and qr_logo_size <= 25:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_Q
            
                elif qr_logo_size > 25 and qr_logo_size <= 30:
                    qr_error_correct = qrcode.constants.ERROR_CORRECT_H

                else:
                    return "Invalid qr_logo_size", 400
            else:
                return "Invalid qr_logo_size", 400
        except ValueError:
            return "Invalid qr_logo_size", 400
    else:
        qr_logo_size = 0
        qr_error_correct = qrcode.constants.ERROR_CORRECT_L

    #Размер QR
    if request.args.get('qr_box_size') is not None:
        attempt = request.args['qr_box_size']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_box_size = int(attempt)
        else:
            return "Invalid qr_box_size", 400
    else:
        qr_box_size = 10

    resp = qr.create(
        logo_filename,
        qr_data,
        qr_rgb,
        qr_rgb_gradient,
        qr_version,
        qr_border,
        qr_box_size,
        qr_logo_size,
        qr_error_correct,
        counter.value,
        "KMA"
        )

    return send_from_directory(app.config['UPLOAD_FOLDER'], resp[1])

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['POST'])
def test():    
    return "Server is work!", 200




#--------------------------------------------------------------
#-----------------------------Запуск------------------------------
#--------------------------------------------------------------

if __name__ == '__main__':  
    app.run(host="192.168.1.151", port=1327)



