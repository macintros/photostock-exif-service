from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import base64

app = Flask(__name__)

@app.route('/embed', methods=['POST'])
def embed_metadata():
    data = request.get_json(force=True)
    
    image_b64 = data.get('image', '')
    title = data.get('title', '')
    description = data.get('description', '')
    keywords = data.get('keywords', '')
    category = data.get('category', '')
    copyright_text = data.get('copyright', '')
    filename = data.get('filename', 'output.jpg')

    image_bytes = base64.b64decode(image_b64)
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        tmp.write(image_bytes)
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

    with open(output_path, 'rb') as f:
        result_b64 = base64.b64encode(f.read()).decode()
    os.unlink(output_path)

    return jsonify({
        'image': result_b64,
        'filename': filename
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
