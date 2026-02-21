# simplest_print.py
import win32print
import os

def printText(filepath):

    #Access file
    try:
        filepath = os.path.join(os.path.dirname(__file__), filename)

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
    

if __name__ == "__main__":
    printText("test.txt")
