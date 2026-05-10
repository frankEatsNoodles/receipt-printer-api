from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import base64, os, json, time

from print import printText, printImage, printStamp

app = FastAPI(title="Cloud Receipt Printer System", 
    description="Post Method for receipt paper printer",
    version="1.0.0")

#set up secrets
with open("secrets.json") as f:
    secrets = json.load(f)
RATEWINDOW = secrets["RATEWINDOW"]
IDEMPOTENCYWINDOW = secrets["IDEMPOTENCYWINDOW"]
ALLOWEDCORS = secrets["ALLOWEDCORS"]
lastRequest = {}
processedKeys = {}

#api post job request body template
class PrintJob(BaseModel):
    user: str
    filename: str
    fileBase64: str 
    idempotencyKey: str

#api response body template
class PrintResponse(BaseModel):
    status: int
    message: str
    jobId: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWEDCORS,
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

def CorsResponse(request, status_code, content):
    origin = request.headers.get("origin")

    if origin in ALLOWEDCORS:
        allowOrigin = origin
    else:
        allowOrigin = "null"
    
    return JSONResponse(
        status_code = status_code,
        content = content,
        headers = {
            "Access-Control-Allow-Origin": allowOrigin,
            "Access-Control-Allow-Credentials" : "true",
            "Access-Control-Allow-Methods" : "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.middleware("http")
async def idempotencyAndRateLimit(request: Request, callNext):
    if request.method == "OPTIONS":
        return await callNext(request)
    
    if request.url.path == "/print" and request.method == "POST":
        try:
            body = await request.body()
            import json
            body_json = json.loads(body)
            idempotencyKey = body_json.get("idempotencyKey")

            #idempotency check
            if not idempotencyKey:
                return CorsResponse(
                    request,
                    400,
                    {"detail": "idempotencyKey is required"}
                )
            
            now = time.time()
            lastTime = processedKeys.get(idempotencyKey)
            
            # Check if key exists and is within the time window
            if lastTime is not None and (now - lastTime) < IDEMPOTENCYWINDOW:
                return CorsResponse(
                    request,
                    status_code=409,
                    content={"detail": "Duplicate request"}
                )
            
            # Store the key with current timestamp
            processedKeys[idempotencyKey] = now
            
            ##################################################################################################
            # Rate limit check
            ip = request.client.host
            lastRateTime = lastRequest.get(ip)
            
            if lastRateTime is not None and (now - lastRateTime) < RATEWINDOW:
                return CorsResponse(
                    request,
                    status_code=429,
                    content={"detail": "Too Many Requests"}
                )
            lastRequest[ip] = now
            
            request._body = body
            
        except Exception as e:
            return CorsResponse(
                request,
                status_code=400,
                content={"detail": f"Error processing request: {str(e)}"}
            )
    
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
                printStamp(datetime.now().strftime("%B %d, %Y %I:%M%p"))
                printImage(filePath)

            elif (fileType == 'txt'):
                filePath = "text/"+filePath
                saveFile(fileContent, filePath)
                printStamp(datetime.now().strftime("%B %d, %Y %I:%M%p"))
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