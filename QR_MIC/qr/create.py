import os
import math
import qrcode

import sys
sys.path.append("..")
from config import *
from PIL import Image




def create(
    logo_filename,
    qr_data,
    qr_rgb,
    qr_rgb_gradient,
    qr_version,
    qr_border,
    qr_box_size,
    qr_logo_size,
    qr_error_correct,
    counter,
    username
    ): 

    path_qr = f"{path_inputfiles}\\{username}\\{counter}\\qr.png"
    if not os.path.exists(f"{path_inputfiles}\\{username}\\{counter}") :
        os.makedirs(f"{path_inputfiles}\\{username}\\{counter}")

    #создание черно-белого qr в png 
    qr = qrcode.QRCode(
        version = qr_version,
        error_correction = qr_error_correct,
        box_size = qr_box_size,
        border = qr_border,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path_qr)

    qr = Image.open(path_qr).convert("RGB")

    #Градиент
    if qr_rgb_gradient is not None:
        #изменение цвета qr на градиент
        changed_red = (qr_rgb_gradient[0] - qr_rgb[0]) / qr.height
        changed_green = (qr_rgb_gradient[1] - qr_rgb[1]) / qr.height
        changed_blue = (qr_rgb_gradient[2] - qr_rgb[2]) / qr.height

        for y in range(0, qr.height):
            color_red = round(qr_rgb[0] + changed_red * y)
            color_green = round(qr_rgb[1] + changed_green * y)
            color_blue = round(qr_rgb[2] + changed_blue * y) 

            for x in range(0, qr.width):  
                if qr.getpixel((x, y)) == (0, 0, 0):                      
                    qr.putpixel((x, y), (color_red, color_green, color_blue))
                                
    else:
        #изменение цвета qr 
        qr_rgb_gradient = None
        for y in range(0, qr.width):
            for x in range(0, qr.height):  
                if qr.getpixel((x, y)) == (0, 0, 0):
                    qr.putpixel((x, y), qr_rgb)

    
    #изменение логотипа до нужного размера под qr (не более 30%) и вставка в qr
    if qr_logo_size is not None and logo_filename is not None and os.path.splitext(logo_filename)[1] in logo_extensions:       
 
        logo_box = (math.floor(qr.width // 100 * qr_logo_size) , math.floor(qr.height // 100 * qr_logo_size))
        paste_box = (math.floor((qr.width - logo_box[0])/ 2), math.floor((qr.height - logo_box[0])/ 2))      
        logo = Image.open(os.path.join(f"{path_inputfiles}\\{username}\\{counter}", logo_filename)).convert("RGBA")
        try:
            logo_resized = logo.resize(logo_box).convert("RGB")
            qr.paste(logo_resized, paste_box)
        except ValueError:
            print("ERROR: ValueError: height and width must be > 0")
            
    
    path_qr_ready = os.path.join(path_outputfiles, f"{counter}.png")   
    qr.save(path_qr_ready)

    return str(path_outputfiles), f"{counter}.png"


