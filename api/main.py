from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import qrcode
import os
from io import BytesIO
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings

# Loading Environment variable (AWS Access Key and Secret Key)
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Allowing CORS for local testing
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Blob Storage Configuration
account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
container_name = os.getenv("AZURE_CONTAINER_NAME")

blob_service_client = BlobServiceClient(
    f"https://{account_name}.blob.core.windows.net",
    credential=account_key
)

class QRRequest(BaseModel):
    url: str

@app.post("/generate-qr/")
async def generate_qr(request: QRRequest):
    url = request.url
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save QR Code to BytesIO object
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Generate file name for Azure Blob Storage
    file_name = f"qr_codes/{url.split('//')[-1]}.png"

    try:
        # Upload to Azure Blob Storage
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
        content_settings = ContentSettings(content_type="image/png")
        blob_client.upload_blob(img_byte_arr, blob_type="BlockBlob", content_settings=content_settings)

        # Generate the Blob URL
        blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{file_name}"
        return {"qr_code_url": blob_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
