from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64, os, json, time

from print import printText, printImage, printStamp

app = FastAPI(title="Cloud Receipt Printer System", 
    description="Post Method for receipt paper printer",
    version="1.0.0")

#set up secrets
with open("secrets.json") as f:
    secrets = json.load(f)
WINDOW = secrets["WINDOW"]
ALLOWEDCORS = secrets["ALLOWEDCORS"]
lastRequest = {}


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWEDCORS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

#request limiting based on ip
@app.middleware("http")
async def rateLimit(request: Request, callNext):
    if request.method == "OPTIONS":
        return await callNext(request)
    
    if request.url.path == "/print" and request.method == "POST":
        ip = request.client.host
        now = time.time()
        lastTime = lastRequest.get(ip)

        if lastTime is not None and (now - lastTime) < WINDOW:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"}
            )
        lastRequest[ip] = now

    return await callNext(request)

#print job
@app.post("/print", response_model=PrintResponse)
async def createPrintJob(job: PrintJob):

    #Set later
    jobId = ""

    try:
        #decode base64 document
        fileContent = base64.b64decode(job.fileBase64)
        fileType = getFileType(fileContent)
        if (fileType == 'unknown'):
            raise HTTPException(status_code=415, detail="Unsupported File Type")
        
        filePath = job.filename+jobId

        try:
            #Determine which folder to save
            if (fileType == 'jpeg' or fileType == 'png'):
                filePath = "images/"+filePath
                saveFile(fileContent, filePath)
                printImage(filePath)

            elif (fileType == 'txt'):
                filePath = "text/"+filePath
                saveFile(fileContent, filePath)
                printText(filePath)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing print job: {str(e)}")

        #Delete image
        deleteFile(filePath)


        PrintResponse.status = 200
        PrintResponse.message = "Print Completed: "+job.filename
        PrintResponse.jobId = jobId

        #Return
        return PrintResponse
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing print job: {str(e)}")