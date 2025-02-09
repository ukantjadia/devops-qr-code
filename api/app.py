from flask import Flask, request, jsonify
import qrcode
import os
from io import BytesIO
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

app = Flask(__name__)

# Azure Blob Storage Configuration
account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
container_name = os.getenv("AZURE_CONTAINER_NAME")

blob_service_client = BlobServiceClient(
    f"https://{account_name}.blob.core.windows.net",
    credential=account_key
)

@app.route("/generate-qr/", methods=["POST"])
def generate_qr():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    # Upload to Azure Blob Storage
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{url}.png")
    blob_client.upload_blob(buffer, overwrite=True)

    return jsonify({"message": "QR code generated and uploaded successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)