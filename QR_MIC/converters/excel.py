import os
import pythoncom

from win32com import client

def excel_to_pdf(
                    filename, 
                    extension, 
                    path_input, 
                    path_output
                    ):
    pythoncom.CoInitializeEx(0)
    app = client.DispatchEx("Excel.Application")
    app.Interactive = False
    app.Visible = False
    Workbook = app.Workbooks.Open(f"{path_input}\\{filename}{extension}")
    try:
        Workbook.ActiveSheet.ExportAsFixedFormat(0, f"{path_output}\\{filename}.pdf")
    except Exception:
        pass
    finally:
        Workbook.Close(SaveChanges=0)
        Workbook = None

        app.Application.Quit()
        app = None

    pythoncom.CoUninitialize(0)
    os.remove(f"{path_input}\\{filename}{extension}")