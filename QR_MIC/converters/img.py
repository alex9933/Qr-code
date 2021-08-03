import os

from PIL import Image

def png_to_pdf(
                filename,
                path_input,
                path_output
                ):
    list_image = list()
    image_first = Image.open(f"{path_input}\\{filename}_0.png").convert('RGB')

    count = 1
    while True:
        try:
            image_open = Image.open(f"{path_input}\\{filename}_{count}.png").convert('RGB')
        except:
            break
        list_image.append(image_open)
        count += 1

    image_first.save(f"{path_output}\\{filename}.pdf", save_all = True, append_images = list_image)
    
    for imgs in os.listdir(path_input):
        os.remove(f"{path_input}\\{imgs}")