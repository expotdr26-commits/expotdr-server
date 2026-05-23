from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io, os, json, base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

FOLDER_ID = '1k1Exhk2UtZLW9t46i9bdS9UfsHEAGOTh'

def get_drive_service():
    creds_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    creds = service_account.Credentials.from_service_account_info(
        creds_json, scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=creds)

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.json
        file_data = base64.b64decode(data['data'])
        filename = data['filename']
        mime_type = data['mimeType']
        
        service = get_drive_service()
        file_metadata = {'name': filename, 'parents': [FOLDER_ID]}
        media = MediaIoBaseUpload(io.BytesIO(file_data), mimetype=mime_type)
        file = service.files().create(
            body=file_metadata, media_body=media, fields='id,webViewLink'
        ).execute()
        
        service.permissions().create(
            fileId=file['id'],
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        return jsonify({'url': file['webViewLink']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return 'ExpoTDR Upload Server OK'

if __name__ == '__main__':
    app.run()
