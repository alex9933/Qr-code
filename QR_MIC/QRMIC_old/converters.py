import os
from PyPDF2 import pdf
import pythoncom
import win32com.client as win32

from PIL import Image
from win32com import client
from pdf2image import pdfinfo_from_path,convert_from_path



#--------------------------------------------------------------
#---------------------Microsoft Office-------------------------
#--------------------------------------------------------------

def word_converter(
                filename, 
                extension, 
                path_input, 
                path_output
                ):
    pythoncom.CoInitializeEx(0)
    word = client.Dispatch('Word.Application')
    wb = word.Documents.Open(f"{path_input}\\{filename}{extension}")
    wb.SaveAs2(f"{path_output}\\{filename}.docx", FileFormat=16)
    wb.Close()
    pythoncom.CoUninitialize(0)

def word_deconverter(
                filename, 
                extension, 
                path_input, 
                path_output
                ):
    pythoncom.CoInitializeEx(0)
    word = client.Dispatch('Word.Application')
    wb = word.Documents.Open(f"{path_input}\\{filename}.docx")
    wb.SaveAs2(f"{path_output}\\{filename}{extension}", FileFormat=16)
    wb.Close()
    pythoncom.CoUninitialize(0)

def word_to_pdf(
    filename, 
    extension,
    path_input, 
    path_output
    ):
    pythoncom.CoInitializeEx(0)
    word = client.Dispatch('Word.Application')
    wb = word.Documents.Open(f"{path_input}\\{filename}{extension}")
    wb.SaveAs(f"{path_output}\\{filename}.pdf", FileFormat=17)
    wb.Close()
    pythoncom.CoUninitialize(0)


#--------------------------------------------------------------
#-----------------------------PDF------------------------------
#--------------------------------------------------------------

def pdf_converter(
                filename, 
                extension,
                file_dpi,
                path_input, 
                path_output,               
                ):
    info = pdfinfo_from_path(f"{path_input}\\{filename}.pdf", userpw=None, poppler_path=None)
    maxPages = info["Pages"]

    for num_page in range(1, maxPages+1):
        pages = convert_from_path(f"{path_input}\\{filename}.pdf", file_dpi, first_page=num_page, last_page=num_page)
        for page in pages:
            page.save(f'{path_output}\\{filename}_{num_page}.png')
    else:
        print(f"{num_page}||{maxPages}")
    
def excel_converter(
                    filename, 
                    extension, 
                    path_input, 
                    path_output
                    ):
    pythoncom.CoInitializeEx(0)
    #app = win32.gencache.EnsureDispatch('Excel.Application')
    app = client.DispatchEx("Excel.Application")
    app.Interactive = False
    app.Visible = False
    Workbook = app.Workbooks.Open(f"{path_input}\\{filename}{extension}")
    try:
        Workbook.ActiveSheet.ExportAsFixedFormat(0, f"{path_output}\\{filename}.pdf")
    except Exception as error:
        print("ERROR: Failed to convert in PDF format.Please confirm environment meets all the requirements  and try again")
        print(str(error))
    finally:
        Workbook.Close(SaveChanges=0)
        Workbook = None

        app.Application.Quit()
        app = None

    pythoncom.CoUninitialize(0)
    
def png_converter(
                filename,
                path_input,
                path_output
                ):
    list_image = list()
    image_first = Image.open(f"{path_input}\\{filename}_1.png").convert('RGB')

    count = 2
    while True:
        try:
            image_open = Image.open(f"{path_input}\\{filename}_{count}.png").convert('RGB')
        except:
            break
        list_image.append(image_open)
        count += 1

    image_first.save(f"{path_output}\\{filename}.pdf", save_all = True, append_images = list_image)
