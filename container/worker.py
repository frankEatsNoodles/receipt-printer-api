from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

PRINTER_URL = "http://host.docker.internal:9100/print"

class PrintJob(BaseModel):
    user: str
    filename: str
    fileBase64: str

@app.post("/print")
async def worker_print(job: PrintJob):
    print("Request Recieved!")
    print(job.user)
    print(job.filename)

    try:

        r = requests.post(PRINTER_URL, json=job.model_dump())

        return {
            "status": r.status_code,
            "message": "Sent to printer"
        }
    except Exception as e:
        print("Error sending print request")
        return{
            "status": 400,
            "message": "Error sending to printer"
        }
