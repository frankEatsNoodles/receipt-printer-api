import win32print
import win32ui
import win32con
from PIL import Image, ImageWin, ImageOps

def print_image_graphic_mode(image_path, printer_name=None):
    if printer_name is None:
        printer_name = win32print.GetDefaultPrinter()
    
    # 1. Create a Printer Device Context
    # This automatically puts the job in 'Graphics Mode' handled by the driver
    hDC = win32ui.CreateDC()
    hDC.CreatePrinterDC(printer_name)
    
    # 2. Start Document
    # Ensure the name is simple; long paths can sometimes confuse older spoolers
    hDC.StartDoc("Python Graphic Job") 
    hDC.StartPage()
    
    # 3. Open and prepare image
    bmp = Image.open(image_path)
    
    #rotate 90 clockwise
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
    
    # 4. Render to DC
    # Using Dib.draw on a DC handle is the definitive "Graphics Mode" method
    dib = ImageWin.Dib(bmp)
    
    # Use GetDeviceCaps to scale properly to the printable area
    printable_width = hDC.GetDeviceCaps(win32con.HORZRES)
    printable_height = hDC.GetDeviceCaps(win32con.VERTRES)
    
    # Scaling to fit the width of the receipt
    target_width = printable_width
    target_height = int(bmp.size[1] * (target_width / bmp.size[0]))
    
    dib.draw(hDC.GetHandleOutput(), (0, 0, target_width, target_height))
    
    # 5. Clean up
    hDC.EndPage()
    hDC.EndDoc()
    hDC.DeleteDC()
    print(f"Graphics job sent to {printer_name}")

print_image_graphic_mode("bc.jpg")
#print_image_graphic_mode("train1.jpg")
