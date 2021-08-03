import os
import PyPDF2
import config

from fpdf import FPDF
from PIL import Image, ImageDraw 
from pdf2image import convert_from_path

Image.MAX_IMAGE_PIXELS = None

def matrix_formation(text, interval_x, interval_y):
    preparation = list(str(text))
    cipher = list()

    #Создание шифрованной матрицы
    for symb in preparation:
        cipher.append(config.codes_dictionary[f"{symb}"])


    #Добавление интервала в строке
    interval_string = list()

    for empty in range(interval_x):
        interval_string.append("0")

    interval_string = "".join(interval_string)
    
    for num_string, string in enumerate(cipher):
        cipher[num_string] = f"{interval_string}".join(map(str, string))


    #Добавление интервала в столбце
    len_str = len(cipher[0])
    interval_string = list()

    for empty in range(len_str):
        interval_string.append("0")

    interval_string = ''.join(interval_string)

    len_mtrx = len(cipher)

    for x in range(len(cipher)-1):
        for y in range(interval_y):
            cipher.insert(len_mtrx-x-1, interval_string)

    cipher = list(map(list, cipher))
    return cipher

def add_to_img(
        text,
        interval,
        start_pix,
        file_dpi,
        RGB,
        filename,
        path_input,
        path_output
        ):
    matrix = matrix_formation(text, interval[0], interval[1])

    pages = os.listdir(path_input)

    for page in pages:
        image_open = Image.open(f'{path_input}\\{page}')

        draw = ImageDraw.Draw(image_open)

        #Небольшой флаг для того чтобы найти левый верхний угол
        #draw.point((23,23), (0,0,0))
        #draw.point((24,24), (0,0,0))

        for num_y, y in enumerate(matrix):
            for num_x, x in enumerate(y):
                if x == "1":
                    draw.point((num_x + start_pix[0], num_y + start_pix[1]), RGB)

        image_open.save(f'{path_input}\\{page}')
        

