from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2 import service_account
import subprocess
import tempfile
import os
import json
import io

app = Flask(__name__)
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

@app.route('/embed', methods=['POST'])
def embed_metadata():
    data = request.get_json(force=True)
    
    file_id = data.get('file_id')
    title = data.get('title', '')
    description = data.get('description', '')
    keywords = data.get('keywords', '')
    copyright_text = data.get('copyright', '')
    filename = data.get('filename', 'output.jpg')

    service = get_drive_service()

    fh = io.BytesIO()
    request_dl = service.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(fh, request_dl)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        tmp.write(fh.getvalue())
        tmp_path = tmp.name

    output_path = tmp_path + '_out.jpg'

    cmd = [
        'exiftool',
        f'-Title={title}',
        f'-Description={description}',
        f'-Keywords={keywords}',
        f'-IPTC:ObjectName={title}',
        f'-IPTC:Caption-Abstract={description}',
        f'-IPTC:Keywords={keywords}',
        f'-XMP:Title={title}',
        f'-XMP:Description={description}',
        f'-XMP:Subject={keywords}',
        f'-Copyright={copyright_text}',
        '-o', output_path,
        tmp_path
    ]
    subprocess.run(cmd, check=True)
    os.unlink(tmp_path)

    media = MediaFileUpload(output_path, mimetype='image/jpeg')
    service.files().update(
        fileId=file_id,
        media_body=media
    ).execute()
    os.unlink(output_path)

    return jsonify({'status': 'success', 'file_id': file_id})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
