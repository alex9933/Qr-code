import os
import pythoncom

from win32com import client

dispatcher = 'Word.Application'

def word_to_docx(
                filename, 
                extension, 
                path_input, 
                path_output
                ):
    pythoncom.CoInitializeEx(0)
    word = client.Dispatch(dispatcher)
    wb = word.Documents.Open(f"{path_input}\\{filename}{extension}")
    wb.SaveAs2(f"{path_output}\\{filename}.docx", FileFormat=16)
    wb.Close()
    pythoncom.CoUninitialize(0)
    os.remove(f"{path_input}\\{filename}{extension}")

def docx_to_word(
                filename, 
                extension, 
                path_input, 
                path_output
                ):
    pythoncom.CoInitializeEx(0)
    word = client.Dispatch(dispatcher)
    wb = word.Documents.Open(f"{path_input}\\{filename}.docx")
    wb.SaveAs2(f"{path_output}\\{filename}{extension}", FileFormat=16)
    wb.Close()
    pythoncom.CoUninitialize(0)
    os.remove(f"{path_input}\\{filename}.docx")

def word_to_pdf(
    filename, 
    extension,
    path_input, 
    path_output
    ):
    pythoncom.CoInitializeEx(0)
    word = client.Dispatch(dispatcher)
    wb = word.Documents.Open(f"{path_input}\\{filename}.docx")
    wb.SaveAs(f"{path_output}\\{filename}.pdf", FileFormat=17)
    wb.Close()
    pythoncom.CoUninitialize(0)
    os.remove(f"{path_input}\\{filename}.docx")

