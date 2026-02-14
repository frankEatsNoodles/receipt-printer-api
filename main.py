# simplest_print.py
import win32print
import os

def printTxt(filename = "test.txt"):
    filepath = os.path.join(os.path.dirname(__file__), filename)


def print_text_file_simple(filename="print_this.txt"):
    """Super simple text file printing"""
    # Get file path
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    if not os.path.exists(filepath):
        # Create a test file
        with open(filepath, 'w') as f:
            f.write("Hello from Python!\nThis is a test print.\n\n")
    
    # Read file
    with open(filepath, 'r') as f:
        text = f.read()
    
    # Get default printer
    printer_name = win32print.GetDefaultPrinter()
    
    # Send to printer
    try:
        printer = win32print.OpenPrinter(printer_name)
        win32print.StartDocPrinter(printer, 1, ("Print Job", None, "RAW"))
        win32print.StartPagePrinter(printer)
        
        # For thermal printer: initialize first
        data = b'\x1B\x40' + text.encode() + b'\n\n'
        win32print.WritePrinter(printer, data)
        
        win32print.EndPagePrinter(printer)
        win32print.EndDocPrinter(printer)
        win32print.ClosePrinter(printer)
        
        print("✅ Print job sent!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False




def print_receipt_with_cut():
    printer_name = "FrankPrint"
    
    try:
        # Connect to printer
        printer = win32print.OpenPrinter(printer_name)
        
        # Start job+
        win32print.StartDocPrinter(printer, 1, ("Receipt", None, "RAW"))
        win32print.StartPagePrinter(printer)
        
        # ESC/POS commands
        data = bytearray()
        
        # Initialize
        data.extend(b'\x1B\x40')
        
        # Set 80mm mode (576 dots)
        # For 58mm: use 384 dots width
        data.extend(b'\x1B\x33\x00')  # Min line spacing
        
        
        # Feed before cut
        data.extend(b'\n\n')
        data.extend(b'\n\n')

        # PAPER CUT - try these one by one:
        # Option 1: Full cut
        data.extend(b'\x1D\x56\x00')
        
        # Option 2: Partial cut (if above doesn't work)
        # data.extend(b'\x1D\x56\x41\x00')
        
        # Send to printer
        win32print.WritePrinter(printer, data)
        
        # Clean up
        win32print.EndPagePrinter(printer)
        win32print.EndDocPrinter(printer)
        win32print.ClosePrinter(printer)
        
        print("✅ Receipt printed with cut command")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Example usage:
if __name__ == "__main__":
    # Print a file called "my_text.txt" in the same folder
    print_text_file_simple("test.txt")
# Run it
    print_receipt_with_cut()
