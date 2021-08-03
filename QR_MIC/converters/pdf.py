import os

from pdf2image import pdfinfo_from_path,convert_from_path


def pdf_to_png(
                filename, 
                extension,
                file_dpi,
                path_input, 
                path_output,               
                ):
    info = pdfinfo_from_path(f"{path_input}\\{filename}.pdf", userpw=None, poppler_path=None)
    maxPages = info["Pages"]

    for num_page in range(0, maxPages):
        pages = convert_from_path(f"{path_input}\\{filename}.pdf", file_dpi, first_page=num_page, last_page=num_page)
        for page in pages:
            page.save(f'{path_output}\\{filename}_{num_page}.png')

    os.remove(f"{path_input}\\{filename}.pdf")
    
