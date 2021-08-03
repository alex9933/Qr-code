# -*- coding: utf-8 -*-
import os
import qr
import mic
import qrcode
import config
import converters

from multiprocessing import Value
from flask import Flask, request, send_from_directory



#--------------------------------------------------------------
#--------------------------Запуск------------------------------
#--------------------------------------------------------------

"""Главный запуск Flask"""
app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['UPLOAD_FOLDER'] = config.path_outputfiles

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Счетчик запросов 
counter = Value('i', 0)



#--------------------------------------------------------------
#---------------------------Функции----------------------------
#--------------------------------------------------------------

def start():
    #Счетчик запросов 
    with counter.get_lock():
        counter.value += 1

    #Создание рабочих директорий
    if not os.path.exists(f"{config.path_inputfiles}\\{config.username}\\{counter.value}"):
        os.makedirs(f"{config.path_inputfiles}\\{config.username}\\{counter.value}")

    if not os.path.exists(f"{config.path_process}\\{config.username}\\{counter.value}\\pages"):
        os.makedirs(f"{config.path_process}\\{config.username}\\{counter.value}\\pages")

    if not os.path.exists(f"{config.path_outputfiles}"):
        os.makedirs(f"{config.path_outputfiles}")

    """РАБОТА С QR"""
    #Логотип
    if request.files.get('qr_logo') is not None:
        qr_logo = request.files['qr_logo']
        if os.path.splitext(qr_logo.filename)[1] in config.logo_extensions:
            qr_logo.save(os.path.join(f"{config.path_inputfiles}\\{config.username}\\{counter.value}", qr_logo.filename))
            logo_filename = str(qr_logo.filename)      
        else:
            return f'{config.error_message_400} - qr_logo', 400
    else:
        logo_filename = None

    #Информация в QR
    if request.args.get('qr_data') is not None:
        attempt = request.args['qr_data']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_data = str(attempt)
        else:
            return f'{config.error_message_400} - qr_data', 400
    else:
        qr_data = config.qr_data

    #Основной цвет QR
    if request.args.get('qr_rgb') is not None:
        verifiable = request.args['qr_rgb'][1:-1].split(',')
        
        try:
            attempt = list(map(int, verifiable))
        
        except ValueError:
            return f'{config.error_message_400} - qr_rgb', 400
        
        if (isinstance(attempt, list) or isinstance(attempt, tuple)) and len(attempt) == 3:
            for color in attempt:
                if isinstance(color, int) and color <= 255 and color >= 0:
                    continue
                else:
                    return f'{config.error_message_400} - qr_rgb', 400
        else:
            return f'{config.error_message_400} - qr_rgb', 400

        qr_rgb = list(attempt)
    else:
        qr_rgb = [0, 0, 0]

    #Версия QR
    if request.args.get('qr_version') is not None:
        attempt = request.args['qr_version']
        try:
            if isinstance(int(attempt), int) or isinstance(attempt, str):
                qr_version = int(attempt)
                if qr_version < 1 and qr_version > 40:
                    return f'{config.error_message_400} - qr_version', 400
            else:
                return f'{config.error_message_400} - qr_version', 400
        except ValueError:
            return f'{config.error_message_400} - qr_version', 400
    else:
        qr_version = 4 

    #Рамка
    if request.args.get('qr_border') is not None:
        attempt = request.args['qr_border']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_border = int(attempt)
        else:
            return f'{config.error_message_400} - qr_border', 400
    else:
        qr_border = 0   

    #Градиент
    if request.args.get('qr_rgb_gradient') is not None:
        verifiable = request.args['qr_rgb_gradient'][1:-1].split(',')
        try:
            attempt = list(map(int, verifiable))
        except ValueError:
            return f'{config.error_message_400} - qr_rgb_gradient', 400
        if (isinstance(attempt, list) or isinstance(attempt, tuple)) and len(attempt) == 3:
            for color in attempt:
                if isinstance(color, int) and color <= 255 and color >= 0:
                    continue
                else:
                    break
        else:
            return f'{config.error_message_400} - qr_rgb_gradient', 400
        
        qr_rgb_gradient = attempt
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
                    return f'{config.error_message_400} - qr_logo_size', 400
            else:
                return f'{config.error_message_400} - qr_logo_size', 400
        except ValueError:
            return f'{config.error_message_400} - qr_logo_size', 400
    else:
        qr_logo_size = 0
        qr_error_correct = qrcode.constants.ERROR_CORRECT_L

    #Размер QR
    if request.args.get('qr_box_size') is not None:
        attempt = request.args['qr_box_size']
        if isinstance(attempt, int) or isinstance(attempt, str):
            qr_box_size = int(attempt)
        else:
            return f'{config.error_message_400} - qr_box_size', 400
    else:
        qr_box_size = 10

        #Основной файл
   
    """РАБОТА С ФАЙЛАМИ"""
    if request.files.get('file') is not None:
        docum = request.files['file']
        if str(os.path.splitext(docum.filename)[1]) in config.file_extension:
            docum.save(os.path.join(f"{config.path_inputfiles}\\{config.username}\\{counter.value}", docum.filename))
            file_filename = docum.filename
        else:
            return f'{config.error_message_400} - file - {str(os.path.splitext(docum.filename)[1])}', 400
    else:
        file_filename = None

    #dpi файла
    if request.args.get('file_dpi') is not None:
        attempt = request.args['file_dpi']
        if isinstance(attempt, int) or isinstance(attempt, str):
            file_dpi = int(attempt)
        else:
            return f'{config.error_message_400} - file_dpi', 400
    else:
        file_dpi = 400 
    
    #Размер QR в дюймах для Word Office
    if request.args.get(f'qr_inches') is not None:
        try:
            attempt = tuple(map(float, request.args[f'qr_inches'][1:-1].split(',')))       
        except ValueError:
            return f'{config.error_message_400} - qr_inches', 400
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue
                else:
                    return f'{config.error_message_400} - qr_inches', 400            
            qr_inches = tuple(attempt)
        else:
            return f'{config.error_message_400} - qr_inches', 400
    else:
        qr_inches = (0.5, 0.5)

    #qr_box
    if request.args.get(f'qr_box') is not None:
        try:
            attempt = tuple(map(int, request.args['qr_box'][1:-1].split(',')))         
        except ValueError:
            return f'{config.error_message_400} - qr_box', 400       
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue                
                else:
                    return f'{config.error_message_400} - qr_box', 400                        
            qr_box = tuple(attempt)
        else:
            return f'{config.error_message_400} - qr_box', 400
    else:
        qr_box = None

    """Machine Identification Code"""

    #Шифруемый 6-значный код
    if request.args.get('mic_data') is not None:
        attempt = request.args['mic_data']
        if isinstance(attempt, int) or isinstance(attempt, str):
            mic_data = int(attempt)
        else:
            return f'{config.error_message_400} - mic_data', 400
    else:
        mic_data = None

    #Основной цвет MIC
    if request.args.get('mic_rgb') is not None:
        verifiable = request.args['mic_rgb'][1:-1].split(',')       
        try:
            attempt = list(map(int, verifiable))       
        except ValueError:
            return f'{config.error_message_400} - mic_rgb', 400
        if (isinstance(attempt, list) or isinstance(attempt, tuple)) and len(attempt) == 3:
            for color in attempt:
                if isinstance(color, int) and color <= 255 and color >= 0:
                    continue
                else:
                    return f'{config.error_message_400} - mic_rgb', 400
            mic_rgb = tuple(attempt)
        else:
            return f'{config.error_message_400} - mic_rgb', 400
    else:
        mic_rgb = (255, 255, 102) 

    #Толщина точки
    if request.args.get('mic_thickness') is not None:
        attempt = request.args['mic_thickness']
        if isinstance(attempt, int) or isinstance(attempt, str):
            mic_thickness = int(attempt)
        else:
            return f'{config.error_message_400} - mic_thickness', 400
    else:
        mic_thickness = 1

    #Размер QR в дюймах для Word Office
    if request.args.get(f'mic_interval') is not None:
        try:
            attempt = tuple(map(int, request.args[f'mic_interval'][1:-1].split(',')))       
        except ValueError:
            return f'{config.error_message_400} - mic_interval', 400
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue
                else:
                    return f'{config.error_message_400} - mic_interval', 400            
            mic_interval = tuple(attempt)
        else:
            return f'{config.error_message_400} - mic_interval', 400
    else:
        mic_interval = (25, 25)

    #Левый верхний угол MIC
    if request.args.get(f'mic_box') is not None:
        try:
            attempt = tuple(map(int, request.args[f'mic_box'][1:-1].split(',')))       
        except ValueError:
            return f'{config.error_message_400} - mic_box', 400
        if isinstance(attempt, tuple) and len(attempt) == 2:  
            for param in attempt:
                if param >= 0:
                    continue
                else:
                    return f'{config.error_message_400} - mic_box', 400            
            mic_box = tuple(attempt)
        else:
            return f'{config.error_message_400} - mic_box', 400
    else:
        mic_box = (25, 25)

    result = {
        'logo_filename' : logo_filename,
        'qr_data' : qr_data,
        'qr_rgb' : qr_rgb,
        'qr_version' : qr_version,
        'qr_border' : qr_border,
        'qr_rgb_gradient' : qr_rgb_gradient,
        'qr_logo_size' : qr_logo_size,
        'qr_error_correct' : qr_error_correct,
        'qr_box_size' : qr_box_size,
        'file_filename' : file_filename,
        'file_dpi' : file_dpi,
        'qr_inches' : qr_inches,
        'qr_box' : qr_box,
        'mic_data' : mic_data,
        'mic_rgb' : mic_rgb,
        'mic_thickness' : mic_thickness,
        'mic_interval' : mic_interval,
        'mic_box' : mic_box,
    }
    
    return result



#--------------------------------------------------------------
#-----------------------------API------------------------------
#--------------------------------------------------------------

@app.route('/file_constructor', methods=['POST'])
def file_constructor():
    param = start()
    if isinstance(param,tuple):
        print(param[0], param[1])
        return param[0], param[1]

    resp = qr.create(
        param['logo_filename'],
        param['qr_data'],
        param['qr_rgb'],
        param['qr_rgb_gradient'],
        param['qr_version'],
        param['qr_border'],
        param['qr_box_size'],
        param['qr_logo_size'],
        param['qr_error_correct'],
        counter.value,
        config.username
        )
    
    path_qr = os.path.join(resp[0], resp[1])

    """Работа с файлами"""
    if param['file_filename'] is None:
        return f'{config.error_message_400} - file', 400
    
    if param['mic_data'] is None:
        return f'{config.error_message_400} - mic_data', 400

    filename = os.path.splitext(param['file_filename'])[0]
    extension = os.path.splitext(param['file_filename'])[1].lower()

    if extension == ".docx":            #docx -> qr -> pdf -> mic
        qr.add_to_word(
            filename, 
            path_qr,
            param['qr_inches'],
            f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}"       
            )
        converters.word_to_pdf(
            filename, 
            ".docx",
            f"{config.path_process}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}"
            )
        converters.pdf_to_png(
            filename, 
            extension,
            param['file_dpi'],
            f"{config.path_process}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",               
            )
        mic.add_to_img(
            param['mic_data'],
            param['mic_interval'],
            param['mic_box'],
            param['file_dpi'],
            param['mic_rgb'],
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        converters.png_to_pdf(
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            config.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    elif extension in config.word_extensions:  #word -> docx -> qr -> pdf -> mic
        converters.word_to_docx(
                filename, 
                extension, 
                f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
                f"{config.path_process}\\{config.username}\\{counter.value}"
                )
        qr.add_to_word(
            filename, 
            path_qr,
            param['qr_inches'],
            f"{config.path_process}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}"     
            )
        converters.word_to_pdf(
            filename, 
            ".docx",
            f"{config.path_process}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}"
            )
        converters.pdf_to_png(
            filename, 
            extension,
            param['file_dpi'],
            f"{config.path_process}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",               
            )
        mic.add_to_img(
            param['mic_data'],
            param['mic_interval'],
            param['mic_box'],
            param['file_dpi'],
            param['mic_rgb'],
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        converters.png_to_pdf(
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            config.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")
        
    elif extension in config.excel_extensions: #excel -> pdf -> png -> qr -> mic -> pdf
        converters.excel_to_pdf(
            filename, 
            extension, 
            f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}"
            )
        converters.pdf_to_png(
            filename, 
            extension,
            param['file_dpi'],
            f"{config.path_process}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",               
            )
        qr.add_to_img(
            filename,
            path_qr, 
            param['qr_box'],
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        mic.add_to_img(
            param['mic_data'],
            param['mic_interval'],
            param['mic_box'],
            param['file_dpi'],
            param['mic_rgb'],
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        converters.png_to_pdf(
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            config.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    elif extension in config.pdf_extensions:   #pdf -> img(png) -> qr -> mic -> img(png) -> pdf
        converters.pdf_to_png(
            filename, 
            extension,
            param['file_dpi'],
            f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",               
            )
        qr.add_to_img(
            filename,
            path_qr, 
            param['qr_box'],
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        mic.add_to_img(
            param['mic_data'],
            param['mic_interval'],
            param['mic_box'],
            param['file_dpi'],
            param['mic_rgb'],
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        converters.png_to_pdf(
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            config.path_outputfiles
            )


        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    else:
        return f'{config.error_message_400} - FILE - {extension}', 400

@app.route('/mic_constructor', methods=['POST'])
def mic_constructor():    
    param = start()
    if isinstance(param,tuple):
        return param[0], param[1]
    if param['mic_data'] is None:
        return f'{config.error_message_400} - mic_data', 400

    filename = os.path.splitext(param['file_filename'])[0]
    extension = os.path.splitext(param['file_filename'])[1].lower()

    if extension == ".docx":            #docx -> pdf -> img(png) -> mic -> img(png) -> pdf
        converters.word_to_pdf(
            filename, 
            extension,
            f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}"
            )
        converters.pdf_to_png(
            filename, 
            extension,
            param['file_dpi'],
            f"{config.path_process}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",               
            )
        mic.add_to_img(
            param['mic_data'],
            param['mic_interval'],
            param['mic_box'],
            param['file_dpi'],
            param['mic_rgb'],
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        converters.png_to_pdf(
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            config.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    elif extension in config.word_extensions:  #word -> docx -> pdf -> img(png) -> mic -> img(png) -> pdf
        converters.word_to_docx(
            filename, 
            extension, 
            f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}"
            )
        converters.word_to_pdf(
            filename, 
            extension,
            f"{config.path_process}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}"
            )
        converters.pdf_to_png(
            filename, 
            extension,
            param['file_dpi'],
            f"{config.path_process}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",               
            )
        mic.add_to_img(
            param['mic_data'],
            param['mic_interval'],
            param['mic_box'],
            param['file_dpi'],
            param['mic_rgb'],
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        converters.png_to_pdf(
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            config.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")
        
    elif extension in config.excel_extensions: #excel -> pdf -> img(png) -> mic -> img(png) -> pdf
        converters.excel_to_pdf(
                    filename, 
                    extension, 
                    f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
                    f"{config.path_process}\\{config.username}\\{counter.value}"
                    )
        converters.pdf_to_png(
            filename, 
            extension,
            param['file_dpi'],
            f"{config.path_process}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",               
            )
        mic.add_to_img(
            param['mic_data'],
            param['mic_interval'],
            param['mic_box'],
            param['file_dpi'],
            param['mic_rgb'],
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        converters.png_to_pdf(
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            config.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    elif extension in config.pdf_extensions:   #pdf -> img(png) -> mic -> img(png) -> pdf
        converters.pdf_to_png(
            filename, 
            extension,
            param['file_dpi'],
            f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",               
            )
        mic.add_to_img(
            param['mic_data'],
            param['mic_interval'],
            param['mic_box'],
            param['file_dpi'],
            param['mic_rgb'],
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        converters.png_to_pdf(
            filename,
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            config.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    else:
        return f'{config.error_message_400} - FILE - {extension}', 400

@app.route('/qr_constructor', methods=['POST'])
def qr_constructor():
    param = start()
    if isinstance(param,tuple):
        return param[0], param[1]

    resp = qr.create(
        param['logo_filename'],
        param['qr_data'],
        param['qr_rgb'],
        param['qr_rgb_gradient'],
        param['qr_version'],
        param['qr_border'],
        param['qr_box_size'],
        param['qr_logo_size'],
        param['qr_error_correct'],
        counter.value,
        config.username
        )    
    path_qr = os.path.join(resp[0], resp[1])

    """Работа с файлами"""
    if param['file_filename'] is None:
        return f'{config.error_message_400} - file', 400

    filename = os.path.splitext(param['file_filename'])[0]
    extension = os.path.splitext(param['file_filename'])[1].lower()

    if extension == ".docx":            #docx -> qr -> docx -> pdf
        qr.add_to_word(
            filename, 
            path_qr,
            param['qr_inches'],
            f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}"      
            )
        converters.word_to_pdf(
            filename, 
            extension,
            f"{config.path_process}\\{config.username}\\{counter.value}"  , 
            config.path_outputfiles
            )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    elif extension in config.word_extensions:  #word -> docx -> qr -> docx -> pdf
        converters.word_to_docx(
                filename, 
                extension, 
                f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
                f"{config.path_process}\\{config.username}\\{counter.value}"
                )
        qr.add_to_word(
            filename, 
            path_qr,
            param['qr_inches'],
            f"{config.path_process}\\{config.username}\\{counter.value}", 
            f"{config.path_process}\\{config.username}\\{counter.value}"     
            )
        converters.word_to_pdf(
                filename, 
                extension, 
                f"{config.path_process}\\{config.username}\\{counter.value}", 
                config.path_outputfiles
                )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")
        
    elif extension in config.excel_extensions: #excel -> pdf -> img(png) -> qr -> img(png) -> pdf
        converters.excel_to_pdf(
                    filename, 
                    extension, 
                    f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
                    f"{config.path_process}\\{config.username}\\{counter.value}"
                    )
        converters.pdf_to_png(
                filename, 
                extension,
                param['file_dpi'],
                f"{config.path_process}\\{config.username}\\{counter.value}", 
                f"{config.path_process}\\{config.username}\\{counter.value}\\pages",               
                )
        qr.add_to_img(
            filename,
            path_qr, 
            param['qr_box'],
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        converters.png_to_pdf(
                filename,
                f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
                config.path_outputfiles
                )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    elif extension in config.pdf_extensions:   #pdf -> img(png) -> qr -> img(png) -> pdf
        converters.pdf_to_png(
                filename, 
                extension,
                param['file_dpi'],
                f"{config.path_inputfiles}\\{config.username}\\{counter.value}", 
                f"{config.path_process}\\{config.username}\\{counter.value}\\pages",               
                )
        qr.add_to_img(
            filename,
            path_qr, 
            param['qr_box'],
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
            f"{config.path_process}\\{config.username}\\{counter.value}\\pages"
            )
        converters.png_to_pdf(
                filename,
                f"{config.path_process}\\{config.username}\\{counter.value}\\pages",
                config.path_outputfiles
                )

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")

    else:
        return f'{config.error_message_400} - FILE - {extension}', 400

@app.route('/qr_create', methods=['POST'])
def qr_create():
    param = start()
    if isinstance(param,tuple):
        return param[0], param[1]
    resp = qr.create(
        param['logo_filename'],
        param['qr_data'],
        param['qr_rgb'],
        param['qr_rgb_gradient'],
        param['qr_version'],
        param['qr_border'],
        param['qr_box_size'],
        param['qr_logo_size'],
        param['qr_error_correct'],
        counter.value,
        config.username
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
    app.run(host = config.host, port = config.port)



