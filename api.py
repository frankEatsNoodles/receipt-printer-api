from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import base64
import os

from print import printText, printImage, printStamp

#app
app = FastAPI(title="Cloud Receipt Printer System", 
    description="Post Method for receipt paper printer",
    version="1.0.0")

#api post job request body template
class PrintJob(BaseModel):
    user: str
    filename: str
    file_content_base64: str 
    timestamp: datetime = datetime.now()

#api response body template
class PrintResponse(BaseModel):
    status: str
    message: str
    job_id: str

#get the filetype from base64 document
def getFileType(fileContent):
    if fileContent.startswith(b'\xff\xd8\xff'):
        return 'jpeg'
    elif fileContent.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    elif all(c < 128 for c in file_content[:100]):
        # Check for txt files
        try:
            fileContent.decode('utf-8')
            return 'txt'
        except UnicodeDecodeError:
            return 'unknown'
    else:
        return 'unknown'

#save file locally for printing
def saveFile(fileContent, filename):
    print("Saving file to local")
    subfolder = "images/"
    
    os.makedirs(os.path.dirname(subfolder),exist_ok=True)
    filePath = os.path.join(subfolder, filename)
    with open(filePath, 'wb') as file:
        file.write(fileContent)
    print("file saved to local")
    print(filePath)
def deleteFile(filename):
    print("Deleting file from local")
    subfolder = "images/"
    filePath = os.path.join(subfolder, filename)
    os.remove(filePath)


#testing
@app.get("/hello")
async def hello():
    print("jello")
    #printStamp("hello")
    #printImage("images/oc.jpg")
    saveFile(base64.b64decode("Z29vZCBtb3JuaW4ganVuZSBpIGxvdmUgeWEgPDM="), "hello.txt")
    printText("images/hello.txt")
    deleteFile("hello.txt")
    print("mello")

#print job
@app.post("/print", response_model=PrintResponse)
async def createPrintJob(job: PrintJob):
    try:
        # set job id
        job_id = "1"

        try:
            #decode base64 document
            fileContent = base64.b64decode(job.file_content_base64)
            fileType = getFileType(fileContent)
            if (fileType == 'unknown'):
                return
            
            if (fileType == 'jpeg' or fileType == 'png'):
                #send request to print image
                print("send print image")
            elif (fileType == 'txt'):
                #print the txt file.
                print("send print text")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 encoding: {str(e)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing print job: {str(e)}")