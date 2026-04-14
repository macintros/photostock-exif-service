from flask import Flask, request, send_file
import subprocess
import tempfile
import os

app = Flask(__name__)

@app.route('/embed', methods=['POST'])
def embed_metadata():
    image = request.files['image']
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    keywords = request.form.get('keywords', '')
    category = request.form.get('category', '')
    copyright_text = request.form.get('copyright', '')

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        image.save(tmp.name)
        tmp_path = tmp.name

    output_path = tmp_path.replace('.jpg', '_out.jpg')

    cmd = [
        'exiftool',
        f'-Title={title}',
        f'-Description={description}',
        f'-Keywords={keywords}',
        f'-Subject={keywords}',
        f'-Category={category}',
        f'-Copyright={copyright_text}',
        f'-IPTC:ObjectName={title}',
        f'-IPTC:Caption-Abstract={description}',
        f'-IPTC:Keywords={keywords}',
        f'-XMP:Title={title}',
        f'-XMP:Description={description}',
        f'-XMP:Subject={keywords}',
        '-o', output_path,
        tmp_path
    ]

    subprocess.run(cmd, check=True)
    os.unlink(tmp_path)

    return send_file(output_path, mimetype='image/jpeg')

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
