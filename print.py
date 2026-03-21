import win32print
import win32ui
import win32con
import os
from PIL import Image, ImageWin
#Contains all the print functions

def printStamp(text):
    try:
        printerName = win32print.GetDefaultPrinter()
        printer = win32print.OpenPrinter(printerName)
        win32print.StartDocPrinter(printer, 1, ("Print Job", None, "RAW"))
        win32print.StartPagePrinter(printer)
        
        # initialize
        data = bytearray()

        #print the initial text
        data.extend(b'' + text.encode() + b'\n\n')
        
        data.extend(b'\x1B\x33\x00')
        data.extend(b'\n\n')
        data.extend(b'\n\n')

        #send to printer without cutting
        win32print.WritePrinter(printer, data)
        
        win32print.EndPagePrinter(printer)
        win32print.EndDocPrinter(printer)
        win32print.ClosePrinter(printer)
    except Exception as e:
        print("Error getting printer")


def printText(filepath):

    #Access text file
    try:
        if not os.path.exists(filepath):
            print("file does not exist")
            return

        with open(filepath, 'r') as f:
            text = f.read()

        print(text)
        #Get the default printer
        printer_name = win32print.GetDefaultPrinter()
    except Exception as e:
        print("No file found")
        return
        

    # Send to printer
    try:
        printer = win32print.OpenPrinter(printer_name)
        win32print.StartDocPrinter(printer, 1, ("Print Job", None, "RAW"))
        win32print.StartPagePrinter(printer)
        
        # initialize
        data = bytearray()
        data.extend(b'' + text.encode() + b'\n\n')
        
        #Use this for wider spacing between text
        #data.extend(b'\x1B\x40' + text.encode() + b'\n\n')
        
        data.extend(b'\x1B\x33\x00')
        
        data.extend(b'\n\n') #feed
        data.extend(b'\n\n')
        data.extend(b'\x1D\x56\x00') #cut
        win32print.WritePrinter(printer, data)
        
        win32print.EndPagePrinter(printer)
        win32print.EndDocPrinter(printer)
        win32print.ClosePrinter(printer)
        
        print("Print submitted")
        return True
    except Exception as e:
        print("Error printing")
        return False
    
def printImage(filePath):
    printer_name = win32print.GetDefaultPrinter()
    
    #access image file
    try:
        #Open image
        bmp = Image.open(filePath)
    except Exception as e:
        print("No file found")
        return

    #Create a Printer Device Context
    hDC = win32ui.CreateDC()
    hDC.CreatePrinterDC(printer_name)
    
    #Start Document
    hDC.StartDoc("Python Graphic Job") 
    hDC.StartPage()
    
    #rotate 90 clockwise if width is longer than height
    if bmp.width > bmp.height:
        bmp = bmp.rotate(-90, expand=True)

    # Thermal printers need strict sizing to avoid 'trailing' gibberish
    # Common widths are 384, 512, or 576 pixels. Check your printer manual.
    MAX_WIDTH = 512 
    if bmp.size[0] > MAX_WIDTH:
        ratio = MAX_WIDTH / float(bmp.size[0])
        new_height = int(float(bmp.size[1]) * float(ratio))
        bmp = bmp.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
    
    # Convert to 1-bit monochrome (Standard for thermal graphics)
    bmp = bmp.convert("1") 
    
    #Render to DC
    # Using Dib.draw on a DC handle is the definitive "Graphics Mode" method
    dib = ImageWin.Dib(bmp)
    
    # Use GetDeviceCaps to scale properly to the printable area
    printable_width = hDC.GetDeviceCaps(win32con.HORZRES)
    printable_height = hDC.GetDeviceCaps(win32con.VERTRES)
    
    # Scaling to fit the width of the receipt
    target_width = printable_width
    target_height = int(bmp.size[1] * (target_width / bmp.size[0]))
    
    dib.draw(hDC.GetHandleOutput(), (0, 0, target_width, target_height))
    
    # Clean up
    hDC.EndPage()
    hDC.EndDoc()
    hDC.DeleteDC()
    print("Print submitted")