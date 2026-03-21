from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import base64
import os

from print import printText, printImage, printStamp

#API_KEY = os.environ.get("API_KEY")
API_KEY = "key"

app = FastAPI(title="Cloud Receipt Printer System", 
    description="Post Method for receipt paper printer",
    version="1.0.0")

#api post job request body template
class PrintJob(BaseModel):
    user: str
    filename: str
    fileBase64: str 

#api response body template
class PrintResponse(BaseModel):
    status: int
    message: str
    jobId: str

#get the filetype from base64 document
def getFileType(fileContent):
    if fileContent.startswith(b'\xff\xd8\xff'):
        return 'jpeg'
    elif fileContent.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    elif all(c < 128 for c in fileContent[:100]):
        # Check for txt files
        try:
            fileContent.decode('utf-8')
            return 'txt'
        except UnicodeDecodeError:
            return 'unknown'
    else:
        return 'unknown'

#save file locally
def saveFile(fileContent, filePath):
    print("Saving file to local")
    try:
        with open(filePath, 'wb') as file:
            file.write(fileContent)
        print("file saved to local")
        return 1
    except Exception as e:
        print("Error saving file")
        return 0

#delete file locally
def deleteFile(filePath):
    print("Deleting file from local")
    try:
        os.remove(filePath)
        print("file deleted from local")
        return 1
    except Exception as e:
        print("Error deleting file")
        return 0

#api key
@app.middleware("http")
async def check_key(request: Request, call_next):
    key = request.headers.get("key")
    if key != API_KEY:
        return JSONResponse(status_code=403, content={"detail": "no"})
    return await call_next(request)

#print job
@app.post("/print", response_model=PrintResponse)
async def createPrintJob(job: PrintJob):

    #Set later
    jobId = ""
    print(jobId+" Job Received with job id: "+jobId)
    print(jobId+" User as: "+job.user)
    print(job.filename+" Filename as: "+job.filename)

    try:
        #decode base64 document
        fileContent = base64.b64decode(job.fileBase64)
        fileType = getFileType(fileContent)
        print(jobId+" File Type: "+fileType)
        if (fileType == 'unknown'):
            raise HTTPException(status_code=415, detail="Unsupported File Type")
        
        filePath = job.filename+jobId

        try:
            #Determine which folder to save
            if (fileType == 'jpeg' or fileType == 'png'):
                print(jobId+" send print image")
                filePath = "images/"+filePath
                saveFile(fileContent, filePath)

                print(jobId+" Printing image")
                printImage(filePath)

            elif (fileType == 'txt'):
                print(jobId+" send print text")
                filePath = "text/"+filePath
                saveFile(fileContent, filePath)

                print(jobId+" Printing text")
                printText(filePath)
        except Exception as e:
            print(jobId+ " Error in printing file "+filePath)
            raise HTTPException(status_code=500, detail=f"Error processing print job: {str(e)}")

        #Delete image
        print(jobId + " Deleting image at path:"+ filePath)
        deleteFile(filePath)


        PrintResponse.status = 200
        PrintResponse.message = "Print Completed: "+job.filename
        PrintResponse.jobId = jobId

        #Return
        return PrintResponse
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing print job: {str(e)}")